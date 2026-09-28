# MDAEF — Markdown-Driven Agentic Execution Framework

A spec-driven UI test framework where a **Markdown specification is the
source of truth**. An agentic executor (Claude Code + Playwright MCP)
reads the Markdown, drives a real browser, discovers locators from the live
DOM, and *compiles* what it did into maintainable Python (Page Object Model +
pytest). A separate healing agent repairs the compiled Python when the UI
changes — it never touches the Markdown. A reporting agent turns execution
artifacts into an executive HTML dashboard and Allure results.

```
Markdown spec (WHAT)  →  Agent (HOW)  →  Playwright MCP + Python/POM  →  Result  →  Healer  →  Reporter
```

No DeepEval, Ragas, RAG, vector DBs, embeddings, LLM-as-judge, or AI scoring
anywhere in this framework, by design.

## Status

**Phase 1 (Specification) — done.** `utils/spec_parser.py` parses and
validates specs; `agents/specification_agent/SKILL.md` is the Agent 1
contract. Two specs exist:

- `specs/TC_AMAZON_GUEST_001.md` — guest search for "iPhone 18 Pro Max" on
  Amazon → view product details. **This is the Phase 2+ POC scenario.**
- `specs/TC_BMS_SEARCH_001.md` — guest movie search on BookMyShow. Queued
  for after the Amazon POC proves the architecture end to end.

Phases 2–5 (agentic execution/compilation, code generation, reporting,
healing) are not built yet — see the project plan.

## Project layout

```
mdaef/
├── .mcp.json              # Playwright MCP server registration for this project
├── specs/                 # SOURCE OF TRUTH. Agent 1 writes here; nothing else does.
├── agents/                 # One SKILL.md contract per agent (the "how")
│   ├── specification_agent/
│   ├── execution_agent/
│   ├── healing_agent/
│   └── reporting_agent/
├── pages/                  # Generated Page Object Model (compiled artifact)
├── tests/                  # Generated pytest tests (compiled artifact)
├── fixtures/                # pytest fixtures (browser/context/page)
├── utils/                   # Deterministic plumbing only — no LLM calls, no scoring
│   ├── spec_parser.py        # Markdown -> structured spec, + validation
│   └── spec_schema.py        # JSON Schema for a parsed spec
├── artifacts/executions/    # Structured execution/step/healing JSON (Agent 2/3 output)
├── reports/                  # HTML dashboard + step reports (Agent 4 output)
└── allure-results/           # Allure raw results
```

## Setup

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/playwright install
```

The Playwright MCP server (`.mcp.json`) is launched via `npx`, which
requires Node.js on PATH — **not currently installed in this environment**;
install Node before running Phase 2 (agentic execution).

## Validating a spec

```bash
.venv/bin/python -m utils.spec_parser specs/TC_AMAZON_GUEST_001.md
```

## Golden rule

If the business requirement changes, the Markdown changes. If the UI
implementation changes, the Python/POM changes. Never the reverse.
