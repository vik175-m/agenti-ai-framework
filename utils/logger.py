from __future__ import annotations

import json
from contextlib import contextmanager
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from utils.execution_context import ExecutionContext

try:
    import allure as _allure
    _HAS_ALLURE = True
except ImportError:
    _HAS_ALLURE = False

_PREFIX = {
    "PASSED": "[PASS]",
    "FAILED": "[FAIL]",
    "SKIPPED": "[SKIP]",
    "HEALING_PASSED": "[HEAL]",
    "HEALING_FAILED": "[HEAL-FAIL]",
    "BLOCKED": "[BLOCKED]",
}


class StepLogger:
    """
    Records per-step execution data:
    - writes STEP_NNN.json to the execution artifact directory
    - prints a one-line status summary to stdout
    - wraps steps in allure.step() when allure-pytest is present
    """

    def __init__(self, exec_ctx: "ExecutionContext") -> None:
        self.exec_ctx = exec_ctx
        self._results: list[dict] = []

    def record(
        self,
        step_id: str,
        action: str,
        expected_result: str,
        status: str,
        actual_result: str = "",
        locator: str = "",
        duration_ms: int = 0,
        screenshot_path: str = "",
        error: str = "",
    ) -> dict:
        entry: dict = {
            "exec_id": self.exec_ctx.exec_id,
            "spec_id": self.exec_ctx.spec_id,
            "step_id": step_id,
            "status": status,
            "action": action,
            "expected_result": expected_result,
            "actual_result": actual_result,
            "locator": locator,
            "duration_ms": duration_ms,
            "screenshot_path": screenshot_path,
            "error": error,
        }
        self.exec_ctx.step_path(step_id).write_text(
            json.dumps(entry, indent=2), encoding="utf-8"
        )
        prefix = _PREFIX.get(status, f"[{status}]")
        print(f"  {prefix} {step_id}: {action[:80]}")
        if error:
            print(f"         error: {error}")
        self._results.append(entry)
        return entry

    @contextmanager
    def allure_step(self, step_id: str, description: str):
        """Context manager that wraps a block in allure.step() when available."""
        if _HAS_ALLURE:
            with _allure.step(f"{step_id} — {description}"):
                yield
        else:
            yield

    def results(self) -> list[dict]:
        return list(self._results)
