"""
Agent 0 — Intake Agent

Converts any source document (PDF, PRD, Markdown, plain text, URL) into
MDAEF-spec-compliant Markdown test cases and writes them to specs/.

Usage:
  .venv/bin/python agents/intake_agent/intake.py path/to/doc.pdf
  .venv/bin/python agents/intake_agent/intake.py path/to/prd.md --module CHECKOUT
  .venv/bin/python agents/intake_agent/intake.py "User can search..." --module SEARCH
  .venv/bin/python agents/intake_agent/intake.py https://example.com/spec
  .venv/bin/python agents/intake_agent/intake.py path/to/doc.pdf --dry-run
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path
from typing import Optional

PROJECT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT))

from utils.spec_parser import parse_spec_text, SpecParseError

SPECS_DIR = PROJECT / "specs"

_MODEL = os.environ.get("MDAEF_INTAKE_MODEL", "claude-haiku-4-5-20251001")
_MAX_TOKENS = int(os.environ.get("MDAEF_INTAKE_MAX_TOKENS", "8000"))
_TEXT_CAP = 50_000


# ── text extraction ───────────────────────────────────────────────────────────

def _extract_url(url: str) -> str:
    from urllib.request import urlopen, Request
    req = Request(url, headers={"User-Agent": "MDAEF-IntakeAgent/1.0"})
    with urlopen(req, timeout=20) as resp:
        raw = resp.read().decode("utf-8", errors="replace")
    text = re.sub(r"<style[^>]*>.*?</style>", " ", raw, flags=re.DOTALL | re.I)
    text = re.sub(r"<script[^>]*>.*?</script>", " ", text, flags=re.DOTALL | re.I)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _extract_pdf(path: Path) -> str:
    try:
        import pdfplumber
    except ImportError:
        raise ImportError(
            "PDF support requires pdfplumber:\n"
            "  .venv/bin/pip install pdfplumber"
        )
    pages: list[str] = []
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            t = page.extract_text()
            if t:
                pages.append(t)
    return "\n\n".join(pages)


def extract_text(source: str) -> str:
    """
    Detect source type and return plain text content, capped at _TEXT_CAP chars.
    """
    if source.startswith(("http://", "https://")):
        text = _extract_url(source)
    else:
        p = Path(source)
        if p.exists():
            if p.suffix.lower() == ".pdf":
                text = _extract_pdf(p)
            else:
                text = p.read_text(encoding="utf-8")
        else:
            text = source  # treat as raw text

    if len(text) > _TEXT_CAP:
        print(f"  [warn] source truncated from {len(text):,} to {_TEXT_CAP:,} chars")
        text = text[:_TEXT_CAP]
    return text


# ── ID management ─────────────────────────────────────────────────────────────

def _existing_tc_numbers(module: str) -> set[int]:
    pattern = re.compile(rf"^TC_{re.escape(module)}_(\d+)\.md$")
    nums: set[int] = set()
    for f in SPECS_DIR.glob(f"TC_{module}_*.md"):
        m = pattern.match(f.name)
        if m:
            nums.add(int(m.group(1)))
    return nums


def _next_tc_numbers(module: str, count: int) -> list[int]:
    existing = _existing_tc_numbers(module)
    start = max(existing, default=0) + 1
    result: list[int] = []
    n = start
    while len(result) < count:
        if n not in existing:
            result.append(n)
        n += 1
    return result


# ── Claude spec generation ────────────────────────────────────────────────────

_SYSTEM_PROMPT = """\
You are MDAEF Agent 0 (Intake Agent). Analyse the source document and produce \
MDAEF-spec-compliant Markdown test cases — one spec per distinct test scenario.

## Output format

Wrap EACH spec in XML tags — no other text outside these tags:

<TC filename="TC_{MODULE}_{NNN}.md">
[full spec content here]
</TC>

Multiple scenarios → multiple <TC> blocks, numbered sequentially (001, 002, …).

## Exact spec format

```markdown
# TC_{MODULE}_{NNN}

## Metadata

- ID: TC_{MODULE}_{NNN}
- Title: <concise, unique, action-oriented title>
- Module: {Module}
- Priority: Critical | High | Medium | Low
- Type: UI | API | E2E
- Tags: <lowercase, comma-separated, no spaces>

## Preconditions

- <one bullet per condition, e.g. "Application is accessible at <app_url>">
- <user state, e.g. "User is not logged in">

## Test Data

- variable_name: value

## Steps

### STEP_001

**Action**

<what the user or system does — atomic, one action>

**Expected Result**

<what should be observable after the action>

### STEP_002

**Action**

...

**Expected Result**

...
```

## Rules

1. Use ${variable_name} syntax in Action/Expected text to reference Test Data values.
2. NEVER invent URLs, credentials, or PII not present in the source.  \
   Use placeholders: <app_url>, <email>, <password>.
3. Steps must be atomic (one action per step) and independently observable.
4. Priority: Critical=data-loss/security, High=core-flow, Medium=secondary, Low=cosmetic.
5. Type: UI=browser, API=HTTP calls, E2E=full cross-system flow.
6. Tags: always include the test type (smoke/regression/sanity), feature name, and \
   any other relevant labels.
7. Preconditions must include the URL/system and user state at minimum.
8. If a scenario has no meaningful test data, write "- (none)" under Test Data.
9. Output ONLY the <TC> blocks — zero preamble, zero explanation.
"""


def _generate_specs(text: str, module: Optional[str]) -> tuple[str, list[str]]:
    """
    Call Claude API and return (detected_module, [raw_spec_content, ...]).
    """
    try:
        import anthropic
    except ImportError:
        raise ImportError(
            "anthropic SDK required:\n  .venv/bin/pip install anthropic"
        )

    module_instruction = (
        f"The module name you MUST use in all TC IDs is exactly: {module}"
        if module
        else (
            "Choose a concise UPPERCASE_ALPHA module name that reflects the "
            "feature being tested (e.g. CHECKOUT, AUTH, SEARCH, BOOKING). "
            "Use it consistently across all TC IDs."
        )
    )

    user_msg = f"{module_instruction}\n\nSource document:\n\n{text}"

    client = anthropic.Anthropic()
    response = client.messages.create(
        model=_MODEL,
        max_tokens=_MAX_TOKENS,
        system=_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_msg}],
    )

    raw: str = response.content[0].text

    # Parse <TC ...>...</TC> blocks
    blocks = re.findall(r"<TC[^>]*>(.*?)</TC>", raw, re.DOTALL)
    specs = [b.strip() for b in blocks if b.strip()]

    # Detect module from first TC ID in response (handles auto-detect case)
    first_id_match = re.search(r"TC_([A-Z0-9_]+)_\d+", raw)
    detected_module = (
        module
        or (first_id_match.group(1) if first_id_match else "MODULE")
    )

    return detected_module, specs


# ── ID assignment ─────────────────────────────────────────────────────────────

def _assign_ids(raw_specs: list[str], module: str) -> list[tuple[str, str]]:
    """
    Replace Claude's placeholder IDs with real sequential IDs.
    Returns list of (real_tc_id, final_content).
    """
    numbers = _next_tc_numbers(module, len(raw_specs))
    result: list[tuple[str, str]] = []
    for spec_content, real_num in zip(raw_specs, numbers):
        real_id = f"TC_{module}_{real_num:03d}"
        # Find what ID Claude assigned to this block
        id_match = re.search(r"TC_[A-Z0-9_]+_\d+", spec_content)
        if id_match:
            claude_id = id_match.group(0)
            content = spec_content.replace(claude_id, real_id)
        else:
            content = spec_content
        result.append((real_id, content))
    return result


# ── validation + write ────────────────────────────────────────────────────────

def _validate_and_write(
    tc_id: str, content: str, dry_run: bool
) -> tuple[bool, str]:
    """
    Validate content via spec_parser. Write to specs/ unless dry_run.
    Returns (success, message).
    """
    try:
        parsed = parse_spec_text(content, source_path=f"<generated:{tc_id}>")
    except SpecParseError as exc:
        return False, f"validation error: {exc}"

    out_path = SPECS_DIR / f"{tc_id}.md"
    step_count = len(parsed.steps)

    if dry_run:
        print(f"\n{'─'*60}")
        print(f"[DRY-RUN] {tc_id}  ({step_count} steps)")
        print(f"{'─'*60}")
        print(content)
        return True, f"dry-run OK — {step_count} steps"

    out_path.write_text(content + "\n", encoding="utf-8")
    return True, f"{step_count} steps → {out_path.relative_to(PROJECT)}"


# ── main entry point ──────────────────────────────────────────────────────────

def run(
    source: str,
    module: Optional[str] = None,
    dry_run: bool = False,
) -> list[Path]:
    """
    Full intake pipeline. Returns list of written spec paths (empty on dry-run).
    """
    print(f"\nMDAEF Intake Agent")
    print(f"{'='*60}")
    src_display = source if len(source) <= 80 else source[:77] + "..."
    print(f"Source:  {src_display}")
    if module:
        print(f"Module:  {module}")
    if dry_run:
        print(f"Mode:    DRY-RUN (no files written)")

    print("\nExtracting text...")
    try:
        text = extract_text(source)
    except Exception as exc:
        print(f"  ERROR: {exc}")
        return []
    print(f"  {len(text):,} chars extracted")

    print("\nGenerating specs via Claude...")
    try:
        detected_module, raw_specs = _generate_specs(text, module)
    except Exception as exc:
        print(f"  ERROR: {exc}")
        return []

    final_module = module or detected_module
    print(f"  Module: {final_module}")
    print(f"  {len(raw_specs)} test scenario(s) identified")

    if not raw_specs:
        print("\nNo test cases found in the source document.")
        print("Tip: try --module to provide a clearer context, or add more detail to your input.")
        return []

    assigned = _assign_ids(raw_specs, final_module)

    print("\nValidating and writing specs:")
    written: list[Path] = []
    warnings = 0
    for tc_id, content in assigned:
        ok, msg = _validate_and_write(tc_id, content, dry_run)
        status = "[OK]  " if ok else "[WARN]"
        print(f"  {status} {tc_id}: {msg}")
        if not ok:
            warnings += 1
        elif not dry_run:
            written.append(SPECS_DIR / f"{tc_id}.md")

    print(f"\n{'='*60}")
    if dry_run:
        print(f"Dry-run complete. {len(assigned)} spec(s) previewed.")
    else:
        print(f"{len(written)} spec(s) written.{f'  {warnings} warning(s).' if warnings else ''}")
        if written:
            print("\nNext steps:")
            print("  1. Review the generated specs in specs/ and adjust if needed.")
            print("  2. Run the Execution Agent to compile POM + pytest test:")
            for p in written:
                print(f"       # (Agent 2 execution for {p.stem})")
            print("  3. Run pytest:")
            for p in written:
                tc_id = p.stem
                print(f"       .venv/bin/pytest tests/test_{tc_id}.py --browser chromium -v")

    return written


def main() -> int:
    parser = argparse.ArgumentParser(
        description="MDAEF Agent 0 — convert any document to MDAEF spec files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  intake.py prd.pdf\n"
            "  intake.py requirements.md --module CHECKOUT\n"
            '  intake.py "User can log in with email and password" --module AUTH\n'
            "  intake.py https://example.com/requirements --dry-run\n"
        ),
    )
    parser.add_argument(
        "source",
        help="File path (.pdf/.md/.txt), URL (https://…), or raw text description",
    )
    parser.add_argument(
        "--module",
        help="Module name (UPPERCASE, e.g. CHECKOUT). Auto-detected from content if omitted.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print generated specs to stdout without writing to disk",
    )
    args = parser.parse_args()

    if args.module:
        # Normalise: uppercase, alphanumeric + underscore only
        args.module = re.sub(r"[^A-Z0-9_]", "_", args.module.upper()).strip("_")

    written = run(args.source, module=args.module, dry_run=args.dry_run)
    return 0 if (written or args.dry_run) else 1


if __name__ == "__main__":
    raise SystemExit(main())
