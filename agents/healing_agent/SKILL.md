# Agent 3 — Healing Agent

## Role

You repair broken Page Object implementations caused by UI changes.
You inspect the live DOM, find a working replacement locator, patch the Page
Object with the minimum possible change, verify the fix holds, and write a
structured healing artifact.

## Inviolable rules

1. **Never edit `specs/`.** Markdown is ground truth. Healing does not touch it.
2. **Never weaken an assertion** to make a test pass. Fix the implementation, not the expectation.
3. **Minimum-diff patches.** Change only the broken locator. Nothing else.
4. **If healing cannot confidently fix the problem → emit `HEALING_FAILED`.** Do not hide failures.
5. **Verify the spec hash is unchanged** before and after patching. Assert equality.

## When to invoke

```bash
# Introduce a controlled break for testing the healer:
.venv/bin/python agents/healing_agent/healer.py --break-pom

# Heal the latest FAILED execution (auto-detects):
.venv/bin/python agents/healing_agent/healer.py

# Heal a specific execution:
.venv/bin/python agents/healing_agent/healer.py EXEC_20260928_007
```

## Input

```
artifacts/executions/<exec_id>/
  execution.json       — status=FAILED, spec_id
  steps/STEP_*.json    — records for steps that completed before the failure
```

The first missing STEP_*.json (by spec order) identifies the failing step.

## Algorithm

### 1. Identify failing step

Compare spec steps against recorded `steps/STEP_*.json` files. The first step
with no corresponding PASSED json is the failing step.

### 2. Navigate to failing step's page state

Replay the steps that precede the failing step using Playwright directly
(not pytest, not MCP). For each prior step:
- Navigate action → `page.goto(url)`
- Enter/type action → fill the input with spec test_data value
- Other → skip (not needed to set up page state)

### 3. Find the broken locator

Check all locators in `pages/*.py` against the current live DOM using
`page.locator(selector).count()`. A locator is **broken** when:
- It returns **count=0** AND
- **At least one other locator in the same POM file** returns count>0

This distinguishes "broken" (should be here, isn't) from "absent because
we're on the wrong page" (all locators in that POM are 0 → we're not on
that page).

### 4. Discover replacement locator

From the broken selector, derive search keywords (strip suffixes like
`-BROKEN`, `-OLD`, `-V1`). Query the live DOM for:

```javascript
document.querySelectorAll('[id*="<keyword1>"][id*="<keyword2>"]')
```

Also try role-based and type-based selectors based on the action description.

Rank candidates using Playwright locator priority:
```
locator(#id)            ← most specific, prefer unique IDs
get_by_role(...)        ← semantic, good fallback
locator(form input[type="submit"])  ← structural
locator(CSS)            ← less preferred
```

Select the first candidate that: count=1 AND is visible.

### 5. Patch Page Object (minimum change)

Replace **only** the one broken `page.locator(...)` or `page.get_by_*(...)`
call on the identified line. No other changes.

### 6. Write healing artifact

```
artifacts/executions/<exec_id>/healing/<step_id>_healed.json
```

```json
{
  "exec_id": "...",
  "spec_id": "...",
  "step_id": "STEP_003",
  "healing_status": "HEALING_PASSED",
  "original_locator": "locator(\"#nav-search-submit-BROKEN\")",
  "healed_locator": "locator(\"#nav-search-submit-button\")",
  "patch_file": "pages/amazon_home_page.py",
  "patch_line": 18,
  "reason": "Selector not found in DOM; replacement discovered via ID keyword search",
  "spec_unchanged": true,
  "re_run_status": "PASSED"
}
```

### 7. Verify spec unchanged

```python
assert hashlib.md5(spec_path.read_bytes()).hexdigest() == spec_hash_before
```

### 8. Re-run test

```bash
.venv/bin/pytest tests/test_<TEST_ID>.py --browser chromium -v
```

If it passes → `HEALING_PASSED`.
If it fails → `HEALING_FAILED` (do not retry indefinitely or mask the failure).

## Output files

```
artifacts/executions/<exec_id>/healing/<step_id>_healed.json
pages/<affected_page>.py  (patched in-place)
```

## Failure conditions

| Condition | Response |
|---|---|
| No FAILED execution found | Print message. Exit 0 (nothing to do). |
| Cannot navigate to page state | Print error. Exit 1. Emit `HEALING_FAILED`. |
| No broken locators found on page | Print error. May be wrong page. Exit 1. |
| No replacement candidate found | Emit `HEALING_FAILED` artifact. Exit 1. |
| Spec hash changed after patch | ABORT. Restore POM from git. This should never happen. |
| Re-run still fails after patch | Emit `HEALING_FAILED`. Do not mask. |
