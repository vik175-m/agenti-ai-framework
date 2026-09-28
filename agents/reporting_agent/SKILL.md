# Agent 4 — Reporting Agent

## Role

You read structured execution artifacts from `artifacts/executions/<exec_id>/`
and produce three outputs:

1. `reports/<exec_id>/index.html` — executive HTML dashboard
2. `reports/<exec_id>/<TC_ID>.html` — per-test step detail page (one per spec)
3. `allure-results/<uuid>-result.json` + screenshot attachments — Allure 2 format

You are read-only with respect to execution artifacts. You never re-run tests.
You never modify `specs/`, `pages/`, or `tests/`.

## When to invoke

```
.venv/bin/python agents/reporting_agent/report_builder.py [exec_id]
```

If `exec_id` is omitted, the latest execution under `artifacts/executions/` is used.
To report on all executions in a single run, pass `--all`.

## Input artifacts (what you read)

```
artifacts/executions/<exec_id>/
  execution.json          top-level summary (status, step counts, duration)
  <TC_ID>.json            per-test detail including full step_results array
  steps/STEP_*.json       individual step records (status, locator, error, …)
  ev/EV-STEP_*-001.png    evidence screenshots
  trace.zip               Playwright trace (not parsed, referenced only)
```

## Output structure

```
reports/<exec_id>/
  index.html              executive dashboard
  <TC_ID>.html            per-test step detail
  ev/                     screenshots copied from artifacts (for HTML src= refs)

allure-results/
  <uuid>-result.json      Allure 2 result record per test
  <uuid>-attachment.png   screenshot copy per step (Allure naming convention)
```

## Dashboard content (index.html)

### Summary tiles

- Total tests
- Passed / Failed / Healed / Skipped
- Pass rate (%)
- Total execution time

### Module summary table

Columns: Module | Total | Passed | Failed | Pass Rate

### Test results table

Columns: Test ID | Title | Status | Steps (P/F/H) | Duration | Detail

Each row links to `<TC_ID>.html`.

## Per-test detail (TC_*.html)

### Metadata section

- Test ID, Title, Module, Priority, Type, Tags
- Execution ID, status, started / finished, duration

### Step table

Columns: Step ID | Action | Expected Result | Actual Result | Status | Locator | Duration (ms) | Screenshot

Screenshot cell: thumbnail img tag linking to the full-size evidence image.

## Allure results

Write one `<uuid>-result.json` per executed test. Format is Allure 2 JSON:

```json
{
  "uuid": "<random-uuid>",
  "historyId": "<spec_id>",
  "testCaseId": "<spec_id>",
  "name": "<spec title>",
  "fullName": "<spec_id>",
  "labels": [
    {"name": "suite",    "value": "<module>"},
    {"name": "tag",      "value": "<tag>"},
    {"name": "severity", "value": "<priority-lowercased>"}
  ],
  "status": "passed | failed | skipped | broken",
  "start": <epoch_ms>,
  "stop":  <epoch_ms>,
  "steps": [
    {
      "name": "<step_id> — <action>",
      "status": "passed | failed | skipped",
      "start": <epoch_ms>,
      "stop":  <epoch_ms>,
      "steps": [],
      "attachments": [{"name": "screenshot", "source": "<uuid>-attachment.png", "type": "image/png"}],
      "parameters": []
    }
  ],
  "attachments": [],
  "parameters": []
}
```

Copy each step's screenshot to `allure-results/<uuid>-attachment.png`.

## Failure conditions

| Condition | Response |
|---|---|
| `exec_id` not found | Print error + list available executions. Exit 1. |
| `execution.json` missing or malformed | Print error. Exit 1. |
| TC_*.json missing | Warn and skip that test; continue with others. |
| No screenshots found | Omit screenshot cells; do not fail the report. |
| Allure results dir not writable | Warn; continue generating HTML. |
