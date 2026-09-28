"""
Agent 3 — Healing Agent implementation.

Usage:
  .venv/bin/python agents/healing_agent/healer.py --break-pom
      Introduce a controlled locator break (for demo / Phase 5 testing).

  .venv/bin/python agents/healing_agent/healer.py [exec_id]
      Heal the named execution (or the latest FAILED one if omitted).
"""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Optional

PROJECT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT))

from utils.config import EXECUTIONS_ROOT
from utils.spec_parser import parse_spec_file
from playwright.sync_api import sync_playwright, Page

PAGES_DIR = PROJECT / "pages"
TESTS_DIR = PROJECT / "tests"

# ── locator parsing ──────────────────────────────────────────────────────────

_LOCATOR_RE = re.compile(r'page\.locator\(["\']([^"\']+)["\']\)')


def _pom_locators(pom_file: Path) -> list[dict]:
    """Return every locator() call found in a POM file."""
    results = []
    for i, line in enumerate(pom_file.read_text(encoding="utf-8").splitlines(), 1):
        m = _LOCATOR_RE.search(line)
        if m:
            results.append({
                "file":      pom_file,
                "line":      i,
                "line_text": line.strip(),
                "selector":  m.group(1),
            })
    return results


def _count(page: Page, selector: str) -> int:
    try:
        return page.locator(selector).count()
    except Exception:
        return -1


# ── broken-locator detection ─────────────────────────────────────────────────

def _find_broken_locators(page: Page) -> list[dict]:
    """
    A locator is "broken" when it returns count=0 on the current page AND
    at least one other locator in the same POM file returns count>0.

    This avoids false positives for POM files that belong to other pages
    (all their locators would also return 0 — but that's expected, not broken).
    """
    broken = []
    for pom_file in sorted(PAGES_DIR.glob("*.py")):
        locs = _pom_locators(pom_file)
        if not locs:
            continue
        counts = [(loc, _count(page, loc["selector"])) for loc in locs]
        has_working = any(c > 0 for _, c in counts)
        if has_working:
            for loc, c in counts:
                if c == 0:
                    broken.append(loc)
    return broken


# ── replacement discovery ─────────────────────────────────────────────────────

def _discover_replacement(page: Page, broken_selector: str, action: str) -> tuple[str, str] | None:
    """
    Return (locator_str, raw_selector) for a working replacement, or None.

    Strategy order:
      1. ID-keyword search in live DOM (most specific — prefer unique IDs)
      2. Type/role-based semantics derived from action description
    """
    # 1. Strip noise suffixes from the broken selector to get search keywords
    cleaned = re.sub(r'[-_](broken|old|v\d+|bak|backup|removed|deleted)',
                     '', broken_selector, flags=re.I)
    keywords = [k for k in re.split(r'[^a-z0-9]+', cleaned.lower()) if len(k) > 2]

    # Query DOM for elements whose IDs contain ALL keywords.
    # Sort so that submit inputs and buttons come first (most likely to be the
    # correct replacement for a broken button/submit locator).
    if keywords:
        js_filter = " && ".join(f'id.includes("{k}")' for k in keywords)
        candidates_from_dom: list[str] = page.evaluate(f"""
            () => {{
                const els = Array.from(document.querySelectorAll('[id]'));
                const matches = els.filter(el => {{
                    const id = el.id.toLowerCase();
                    return {js_filter} && el.offsetWidth > 0 && el.offsetHeight > 0;
                }});
                const rank = el => (el.type === 'submit' || el.tagName === 'BUTTON') ? 2
                                 : (el.tagName === 'INPUT' ? 1 : 0);
                matches.sort((a, b) => rank(b) - rank(a));
                return matches.map(el => el.id);
            }}
        """) or []
        for eid in candidates_from_dom:
            sel = f"#{eid}"
            if sel != broken_selector and _count(page, sel) == 1:
                return f'locator("{sel}")', sel

    # 2. Semantic fallback based on action description
    action_lower = action.lower()

    if any(w in action_lower for w in ("submit", "search button", "click go")):
        # Try structured submit-button locators
        structural = [
            ("form#nav-search-bar-form input[type='submit']",
             "locator(\"form#nav-search-bar-form input[type='submit']\")"),
            ("input[type='submit'][value='Go']",
             "locator(\"input[type='submit'][value='Go']\")"),
            ("input[name='submit']",
             "locator(\"input[name='submit']\")"),
        ]
        for sel, loc_str in structural:
            if _count(page, sel) == 1:
                try:
                    if page.locator(sel).is_visible():
                        return loc_str, sel
                except Exception:
                    return loc_str, sel

        # Role-based (exact=True avoids strict-mode violations)
        for name in ("Go", "Search"):
            try:
                loc = page.get_by_role("button", name=name, exact=True)
                if loc.count() == 1 and loc.is_visible():
                    return f'get_by_role("button", name="{name}", exact=True)', f"role:button:{name}"
            except Exception:
                pass

    return None


# ── page-state setup ─────────────────────────────────────────────────────────

def _setup_page_state(page: Page, spec, step_idx: int) -> None:
    """
    Replay the steps before step_idx so the browser is in the right state
    for DOM inspection of the failing step.
    """
    test_data = spec.test_data

    # STEP_001 equivalent: navigate to the base URL from preconditions
    base_url = None
    for pre in spec.preconditions:
        m = re.search(r'(https?://[^\s\)]+)', pre)
        if m:
            base_url = m.group(1)
            break

    if base_url:
        page.goto(base_url, wait_until="domcontentloaded")
        # Wait for the page to be interactive
        try:
            page.wait_for_load_state("domcontentloaded", timeout=15_000)
            page.wait_for_timeout(1500)
        except Exception:
            pass

    if step_idx < 2:
        return

    # STEP_002 equivalent: fill any visible text inputs with test_data values
    # (catches "Enter search term", "Enter username", etc.)
    for value in test_data.values():
        if not value or value.startswith("${"):
            continue
        for sel in ("#twotabsearchtextbox", "input[type='text']", "input[type='search']"):
            try:
                loc = page.locator(sel)
                if loc.count() > 0 and loc.first.is_visible():
                    loc.first.fill(str(value))
                    break
            except Exception:
                pass


# ── POM patching ─────────────────────────────────────────────────────────────

def _patch_pom(pom_file: Path, broken_selector: str, new_locator_str: str) -> tuple[int, str, str]:
    """
    Replace the line containing broken_selector with one using new_locator_str.
    Returns (1-based line number, old line text, new line text).
    """
    lines = pom_file.read_text(encoding="utf-8").splitlines()
    for i, line in enumerate(lines):
        if broken_selector in line:
            m = _LOCATOR_RE.search(line)
            if m:
                old_expr = m.group(0)
                new_expr = f"page.{new_locator_str}"
                new_line = line.replace(old_expr, new_expr, 1)
                lines[i] = new_line
                pom_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
                return i + 1, line.strip(), new_line.strip()
    raise ValueError(f"Cannot find selector {broken_selector!r} in {pom_file}")


# ── artifact writer ───────────────────────────────────────────────────────────

def _write_healing_artifact(
    exec_dir: Path,
    spec_id: str,
    step_id: str,
    pom_file: Path,
    patch_line: int,
    original_locator: str,
    healed_locator: str,
    reason: str,
    spec_unchanged: bool,
    rerun_rc: int,
) -> Path:
    heal_dir = exec_dir / "healing"
    heal_dir.mkdir(exist_ok=True)
    status = "HEALING_PASSED" if rerun_rc == 0 else "HEALING_FAILED"
    record = {
        "exec_id":          exec_dir.name,
        "spec_id":          spec_id,
        "step_id":          step_id,
        "healing_status":   status,
        "original_locator": original_locator,
        "healed_locator":   healed_locator,
        "patch_file":       str(pom_file.relative_to(PROJECT)),
        "patch_line":       patch_line,
        "reason":           reason,
        "spec_unchanged":   spec_unchanged,
        "re_run_status":    "PASSED" if rerun_rc == 0 else "FAILED",
    }
    out = heal_dir / f"{step_id}_healed.json"
    out.write_text(json.dumps(record, indent=2), encoding="utf-8")
    return out


# ── controlled break (for Phase 5 demo) ──────────────────────────────────────

def introduce_break() -> None:
    """Replace #nav-search-submit-button with a broken selector in the POM."""
    target = PAGES_DIR / "amazon_home_page.py"
    text = target.read_text(encoding="utf-8")
    if "#nav-search-submit-BROKEN" in text:
        print("Break already in place.")
        return
    if "#nav-search-submit-button" not in text:
        print("Target locator not found — POM may already be in a different state.")
        return
    patched = text.replace("#nav-search-submit-button", "#nav-search-submit-BROKEN")
    target.write_text(patched, encoding="utf-8")
    print(f"Break introduced: {target}")
    print("  #nav-search-submit-button  →  #nav-search-submit-BROKEN")


# ── main heal flow ────────────────────────────────────────────────────────────

def heal(exec_id: Optional[str] = None) -> int:
    # 1. Locate the execution to heal
    if exec_id:
        exec_dir = EXECUTIONS_ROOT / exec_id
        if not exec_dir.exists():
            print(f"Execution not found: {exec_id}")
            return 1
    else:
        candidates = sorted(EXECUTIONS_ROOT.iterdir())
        exec_dir = next(
            (d for d in reversed(candidates)
             if d.is_dir() and (d / "execution.json").exists()
             and json.loads((d / "execution.json").read_text()).get("status") == "FAILED"),
            None,
        )
        if exec_dir is None:
            print("No FAILED execution found.")
            return 0

    exec_data = json.loads((exec_dir / "execution.json").read_text())
    spec_id = exec_data["spec_id"]
    print(f"\n{'='*60}")
    print(f"MDAEF Healing Agent")
    print(f"Execution: {exec_dir.name}")
    print(f"Spec:      {spec_id}")
    print(f"{'='*60}")

    # 2. Load spec and record spec hash (must be unchanged after healing)
    spec_path = PROJECT / "specs" / f"{spec_id}.md"
    spec = parse_spec_file(str(spec_path))
    spec_hash_before = hashlib.md5(spec_path.read_bytes()).hexdigest()

    # 3. Find the failing step (first step with no PASSED JSON in artifacts)
    steps_dir = exec_dir / "steps"
    recorded_passed = {
        f.stem
        for f in steps_dir.glob("*.json")
        if json.loads(f.read_text()).get("status") == "PASSED"
    } if steps_dir.exists() else set()

    failed_step = next(
        (s for s in spec.steps if s["step_id"] not in recorded_passed), None
    )
    if failed_step is None:
        print("All steps recorded as PASSED — nothing to heal.")
        return 0

    step_idx = next(i for i, s in enumerate(spec.steps)
                    if s["step_id"] == failed_step["step_id"])
    print(f"\nFailing step: {failed_step['step_id']}: {failed_step['action']}")

    # 4. Navigate to page state and inspect DOM
    print("\nInspecting live DOM...")
    broken_locs: list[dict] = []
    replacement: tuple[str, str] | None = None

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        page = browser.new_context(
            viewport={"width": 1280, "height": 900},
            user_agent=(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            ),
        ).new_page()
        page.set_default_timeout(20_000)

        try:
            _setup_page_state(page, spec, step_idx)
        except Exception as exc:
            print(f"  ERROR setting up page state: {exc}")
            browser.close()
            return 1

        broken_locs = _find_broken_locators(page)

        if not broken_locs:
            print("  No broken locators found on current page.")
            browser.close()
            return 1

        for loc in broken_locs:
            print(f"  Broken: {loc['selector']!r}  in {loc['file'].name}:{loc['line']}")

        # Attempt replacement discovery for the first broken locator
        broken = broken_locs[0]
        replacement = _discover_replacement(page, broken["selector"], failed_step["action"])
        browser.close()

    if replacement is None:
        print(f"\nHEALING_FAILED — no replacement found for {broken['selector']!r}")
        _write_healing_artifact(
            exec_dir, spec_id, failed_step["step_id"],
            broken["file"], broken["line"],
            f'locator("{broken["selector"]}")', "NONE",
            "No replacement locator discovered in live DOM",
            True, 1,
        )
        return 1

    new_locator_str, new_selector = replacement
    print(f"\nReplacement: {new_locator_str}")

    # 5. Patch POM (minimum change)
    try:
        patch_line, old_text, new_text = _patch_pom(
            broken["file"], broken["selector"], new_locator_str
        )
    except ValueError as exc:
        print(f"Patch failed: {exc}")
        return 1

    print(f"\nPatched {broken['file'].name}:{patch_line}")
    print(f"  Before: {old_text}")
    print(f"  After:  {new_text}")

    # 6. Verify spec is unchanged
    spec_hash_after = hashlib.md5(spec_path.read_bytes()).hexdigest()
    spec_unchanged = spec_hash_before == spec_hash_after
    print(f"\nSpec unchanged: {spec_unchanged}")
    if not spec_unchanged:
        print("CRITICAL: spec hash changed — this should never happen. Aborting.")
        return 1

    # 7. Re-run test to verify the fix
    print(f"\nRe-running test...")
    result = subprocess.run(
        [str(PROJECT / ".venv/bin/pytest"),
         str(TESTS_DIR / f"test_{spec_id}.py"),
         "--browser", "chromium", "-v", "--tb=short",
         "--slowmo", "80"],
        capture_output=True, text=True,
    )
    output = (result.stdout + result.stderr).strip()
    print(output[-2000:] if len(output) > 2000 else output)

    # 8. Write healing artifact
    out = _write_healing_artifact(
        exec_dir, spec_id, failed_step["step_id"],
        broken["file"], patch_line,
        f'locator("{broken["selector"]}")',
        new_locator_str,
        f"Selector {broken['selector']!r} returned 0 elements; "
        f"replaced with {new_locator_str} (count=1, visible)",
        spec_unchanged,
        result.returncode,
    )

    status = "HEALING_PASSED" if result.returncode == 0 else "HEALING_FAILED"
    print(f"\n{'='*60}")
    print(f"Result: {status}")
    print(f"Healing artifact: {out}")
    print(f"{'='*60}\n")

    return result.returncode


# ── CLI ──────────────────────────────────────────────────────────────────────

def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if "--break-pom" in argv:
        introduce_break()
        return 0
    exec_id = next((a for a in argv if not a.startswith("--")), None)
    return heal(exec_id)


if __name__ == "__main__":
    raise SystemExit(main())
