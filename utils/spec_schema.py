"""
JSON Schema for a parsed MDAEF test specification.

This is deliberately dumb: it checks structure only (required fields, ID
patterns, non-empty steps). It never judges test *quality*, never scores
anything, and never reasons about business correctness — that reasoning
belongs to Agent 1 (authoring) and a human reviewer, not to this validator.

The Markdown file is the source of truth. This schema exists only to catch
malformed specs (missing sections, empty steps, duplicate step IDs) before
Agent 2 ever tries to execute them.
"""

from __future__ import annotations

TEST_SPEC_SCHEMA: dict = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "MDAEF Test Specification",
    "type": "object",
    "required": [
        "id",
        "title",
        "module",
        "priority",
        "type",
        "tags",
        "preconditions",
        "test_data",
        "steps",
    ],
    "properties": {
        "id": {
            "type": "string",
            "pattern": r"^TC_[A-Z0-9_]+$",
            "description": "Stable Test ID. Must match the H1 heading and the Metadata ID field.",
        },
        "title": {"type": "string", "minLength": 1},
        "module": {"type": "string", "minLength": 1},
        "priority": {"type": "string", "enum": ["Low", "Medium", "High", "Critical"]},
        "type": {"type": "string", "enum": ["UI", "API", "E2E"]},
        "tags": {"type": "array", "items": {"type": "string"}},
        "preconditions": {
            "type": "array",
            "items": {"type": "string", "minLength": 1},
            "minItems": 1,
        },
        "test_data": {"type": "object"},
        "steps": {
            "type": "array",
            "minItems": 1,
            "items": {
                "type": "object",
                "required": ["step_id", "action", "expected_result"],
                "properties": {
                    "step_id": {"type": "string", "pattern": r"^STEP_\d{3,}$"},
                    "action": {"type": "string", "minLength": 1},
                    "expected_result": {"type": "string", "minLength": 1},
                },
            },
        },
    },
}
