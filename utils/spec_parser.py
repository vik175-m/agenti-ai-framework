"""
Parses an MDAEF Markdown test specification (specs/TC_*.md) into the
structured dict defined by utils.spec_schema.TEST_SPEC_SCHEMA, and validates
it.

This module is intentionally non-agentic: it does line-based parsing of the
*fixed* template documented in mdaef/agents/specification_agent/SKILL.md. It
does not use an LLM, does not infer intent, and does not repair malformed
specs. Its only job is: "is this Markdown file structurally a valid MDAEF
spec, and if so, what does it say?"

Both Agent 1 (to self-check what it just authored) and Agent 2 (to load a
spec before execution) call into this module.
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

import jsonschema

from utils.spec_schema import TEST_SPEC_SCHEMA

STEP_ID_RE = re.compile(r"^STEP_\d{3,}$")


class SpecParseError(ValueError):
    """Raised when a spec Markdown file cannot be parsed or fails schema validation."""


@dataclass
class ParsedSpec:
    id: str
    title: str
    module: str
    priority: str
    type: str
    tags: list[str]
    preconditions: list[str]
    test_data: dict[str, str]
    steps: list[dict[str, str]]
    source_path: str
    raw_metadata: dict[str, str] = field(default_factory=dict)

    def as_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "module": self.module,
            "priority": self.priority,
            "type": self.type,
            "tags": self.tags,
            "preconditions": self.preconditions,
            "test_data": self.test_data,
            "steps": self.steps,
        }


def _split_sections(text: str) -> dict[str, str]:
    """Split on H2 ('## ') headings into {heading_lower: body_text}."""
    sections: dict[str, str] = {}
    current_heading = None
    buf: list[str] = []
    for line in text.splitlines():
        if line.startswith("## "):
            if current_heading is not None:
                sections[current_heading] = "\n".join(buf).strip()
            current_heading = line[3:].strip().lower()
            buf = []
        else:
            buf.append(line)
    if current_heading is not None:
        sections[current_heading] = "\n".join(buf).strip()
    return sections


def _parse_bullet_kv(body: str) -> dict[str, str]:
    """Parse '- Key: Value' bullet lines into a dict, preserving order."""
    out: dict[str, str] = {}
    for line in body.splitlines():
        line = line.strip()
        if not line.startswith("-"):
            continue
        line = line.lstrip("- ").strip()
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        out[key.strip()] = value.strip()
    return out


def _parse_bullet_list(body: str) -> list[str]:
    out: list[str] = []
    for line in body.splitlines():
        line = line.strip()
        if not line.startswith("-"):
            continue
        out.append(line.lstrip("- ").strip())
    return out


def _parse_steps(body: str) -> list[dict[str, str]]:
    """
    Split the '## Steps' body on '### STEP_xxx' headings, then pull the
    **Action** and **Expected Result** blocks out of each.
    """
    steps: list[dict[str, str]] = []
    step_id = None
    buf: list[str] = []

    def flush():
        if step_id is None:
            return
        block = "\n".join(buf)
        action = _extract_labeled_block(block, "Action")
        expected = _extract_labeled_block(block, "Expected Result")
        if action is None or expected is None:
            raise SpecParseError(
                f"{step_id}: missing **Action** or **Expected Result** block"
            )
        steps.append(
            {"step_id": step_id, "action": action, "expected_result": expected}
        )

    for line in body.splitlines():
        if line.startswith("### "):
            flush()
            step_id = line[4:].strip()
            buf = []
        else:
            buf.append(line)
    flush()
    return steps


def _extract_labeled_block(block: str, label: str) -> str | None:
    """
    Pull the paragraph following a '**Label**' marker, stopping at the next
    '**' marker or end of block.
    """
    marker = f"**{label}**"
    idx = block.find(marker)
    if idx == -1:
        return None
    rest = block[idx + len(marker) :]
    next_marker = rest.find("**")
    if next_marker != -1:
        rest = rest[:next_marker]
    text = rest.strip()
    return text or None


def parse_spec_text(text: str, source_path: str = "<string>") -> ParsedSpec:
    lines = text.splitlines()
    h1 = next((l for l in lines if l.startswith("# ")), None)
    if h1 is None:
        raise SpecParseError(f"{source_path}: missing H1 title (e.g. '# TC_LOGIN_001')")
    heading_id = h1[2:].strip()

    sections = _split_sections(text)

    if "metadata" not in sections:
        raise SpecParseError(f"{source_path}: missing '## Metadata' section")
    metadata = _parse_bullet_kv(sections["metadata"])

    required_meta = ["ID", "Title", "Module", "Priority", "Type", "Tags"]
    missing = [k for k in required_meta if k not in metadata]
    if missing:
        raise SpecParseError(f"{source_path}: Metadata missing fields: {missing}")

    if metadata["ID"] != heading_id:
        raise SpecParseError(
            f"{source_path}: H1 title '{heading_id}' does not match Metadata ID "
            f"'{metadata['ID']}'"
        )

    preconditions = _parse_bullet_list(sections.get("preconditions", ""))
    if not preconditions:
        raise SpecParseError(f"{source_path}: '## Preconditions' has no bullet items")

    test_data = _parse_bullet_kv(sections.get("test data", ""))

    if "steps" not in sections:
        raise SpecParseError(f"{source_path}: missing '## Steps' section")
    steps = _parse_steps(sections["steps"])
    if not steps:
        raise SpecParseError(f"{source_path}: '## Steps' has no '### STEP_xxx' entries")

    seen_ids = set()
    for step in steps:
        if not STEP_ID_RE.match(step["step_id"]):
            raise SpecParseError(
                f"{source_path}: invalid step id '{step['step_id']}' "
                f"(expected STEP_### e.g. STEP_001)"
            )
        if step["step_id"] in seen_ids:
            raise SpecParseError(f"{source_path}: duplicate step id '{step['step_id']}'")
        seen_ids.add(step["step_id"])

    tags = [t.strip() for t in metadata["Tags"].split(",") if t.strip()]

    spec = ParsedSpec(
        id=metadata["ID"],
        title=metadata["Title"],
        module=metadata["Module"],
        priority=metadata["Priority"],
        type=metadata["Type"],
        tags=tags,
        preconditions=preconditions,
        test_data=test_data,
        steps=steps,
        source_path=source_path,
        raw_metadata=metadata,
    )
    validate_spec(spec.as_dict(), source=source_path)
    return spec


def parse_spec_file(path: str | Path) -> ParsedSpec:
    path = Path(path)
    text = path.read_text(encoding="utf-8")
    return parse_spec_text(text, source_path=str(path))


def validate_spec(spec_dict: dict, source: str = "<dict>") -> None:
    """Raises SpecParseError with a clear message if spec_dict violates the schema."""
    try:
        jsonschema.validate(instance=spec_dict, schema=TEST_SPEC_SCHEMA)
    except jsonschema.ValidationError as exc:
        raise SpecParseError(f"{source}: schema validation failed: {exc.message}") from exc


def main(argv: list[str] | None = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    if not argv:
        print("usage: python -m utils.spec_parser <spec.md> [more.md ...]")
        return 2
    exit_code = 0
    for path in argv:
        try:
            spec = parse_spec_file(path)
        except SpecParseError as exc:
            print(f"INVALID  {path}\n  {exc}")
            exit_code = 1
            continue
        print(
            f"VALID    {path}\n"
            f"  id={spec.id} title={spec.title!r} module={spec.module} "
            f"steps={len(spec.steps)} tags={spec.tags}"
        )
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
