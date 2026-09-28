# Agent 0 — Intake Agent

## Role

You are the entry point of the MDAEF pipeline.  
Accept **any document** — PDF, PRD, user story, plain text, Markdown, or URL —
extract all testable scenarios, and produce `specs/TC_*.md` files that are
immediately consumable by Agents 1–4 without modification.

## Pipeline position

```
[PDF / PRD / user story / plain text / URL]
          │
          ▼
  Agent 0 — Intake Agent          ← YOU ARE HERE
          │  generates specs/TC_*.md
          ▼
  Agent 1 — Specification Agent   ← reviews / refines specs
          │
          ▼
  Agent 2 — Execution Agent       ← runs against live browser, generates POM + pytest
          │
          ▼
  Agent 4 — Reporting Agent       ← HTML dashboard + Allure results
          │
          ▼
  Agent 3 — Healing Agent         ← fixes broken locators after UI changes
```

## When to invoke

```bash
# From a PDF (PRD, requirements doc, test plan):
.venv/bin/python agents/intake_agent/intake.py path/to/prd.pdf

# From a Markdown or text doc:
.venv/bin/python agents/intake_agent/intake.py path/to/requirements.md

# From a URL:
.venv/bin/python agents/intake_agent/intake.py https://example.com/spec

# From a plain-text description (quote it):
.venv/bin/python agents/intake_agent/intake.py "User should be able to log in with email and password" --module AUTH

# With explicit module name:
.venv/bin/python agents/intake_agent/intake.py path/to/doc.pdf --module CHECKOUT

# Dry-run (print generated specs, do NOT write to disk):
.venv/bin/python agents/intake_agent/intake.py path/to/doc.pdf --dry-run
```

## Algorithm

### 1. Detect and extract content

| Source type | Detection | Extraction |
|---|---|---|
| PDF file (`*.pdf`) | file extension | `pdfplumber` (optional dep) |
| URL (`http://…`) | prefix | `urllib.request` + HTML strip |
| Markdown / text file | path exists | `Path.read_text()` |
| Raw text | not a path | use as-is |

Cap extracted text at 50 000 chars. Warn if truncated.

### 2. Determine module name

- If `--module MODULE` supplied → use it (UPPERCASE, alphanumeric + underscore).
- Otherwise → ask Claude to infer a concise module name from the document.

### 3. Call Claude API

Model: `claude-haiku-4-5-20251001` (fast, cheap, sufficient for structured generation).

System prompt enforces:
- Exact MDAEF spec Markdown format
- `<TC filename="TC_MODULE_NNN.md">…</TC>` output delimiters
- One TC block per distinct test scenario
- Stable step IDs (STEP_001, STEP_002, …)
- `${variable_name}` substitution syntax for test data references
- No invented URLs or credentials

### 4. Parse response

Extract all `<TC …>…</TC>` blocks. Each block is one raw spec string.

### 5. Assign stable IDs

Scan `specs/` for existing `TC_{MODULE}_*.md` files.  
Assign the next sequential NNN (zero-padded to 3 digits) for each spec.  
Replace the Claude-generated placeholder ID with the real ID throughout the content.

### 6. Validate and write

For each spec:
1. Call `utils.spec_parser.parse_spec_text()` — structural validation.
2. On parse error: print a warning, skip writing, continue to next spec.
3. On success: write to `specs/TC_{MODULE}_{NNN}.md`.

### 7. Print summary

```
[OK]   specs/TC_AUTH_001.md  — 4 steps
[OK]   specs/TC_AUTH_002.md  — 5 steps
[WARN] TC_AUTH_003: validation warning: Metadata missing field Priority
       → File written with warning; review before executing.

2 spec(s) written. 1 warning(s).

Next: .venv/bin/python agents/execution_agent/runner.py TC_AUTH_001
```

## Inviolable rules

1. **Never edit existing specs.** Only write NEW `TC_*.md` files.
2. **Never invent credentials, URLs, or PII.** Use `<app_url>`, `<email>`, `<password>` placeholders when the source does not supply them.
3. **One test scenario = one spec file.** Never merge multiple scenarios into one TC.
4. **Respect existing IDs.** Never reuse an existing `TC_{MODULE}_{NNN}` combination.
5. **Dry-run is non-destructive.** `--dry-run` prints to stdout only; zero disk writes.

## Supported input types

| Type | Requires |
|---|---|
| `.pdf` | `pip install pdfplumber` |
| `.md` / `.txt` / `.rst` | built-in |
| URL (`http://https://`) | built-in |
| Raw text string | built-in |

## Environment

| Variable | Default | Purpose |
|---|---|---|
| `ANTHROPIC_API_KEY` | required | Anthropic API key |
| `MDAEF_INTAKE_MODEL` | `claude-haiku-4-5-20251001` | Override LLM model |
| `MDAEF_INTAKE_MAX_TOKENS` | `8000` | Override max output tokens |

## Output

```
specs/TC_{MODULE}_{NNN}.md    ← one file per test scenario
```

No other files are created or modified.
