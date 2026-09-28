from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from utils.config import EXECUTIONS_ROOT


def _next_exec_id(date_str: str) -> str:
    """Return EXEC_YYYYMMDD_NNN, incrementing above the highest existing today."""
    prefix = f"EXEC_{date_str}_"
    if not EXECUTIONS_ROOT.exists():
        return f"{prefix}001"
    numbers = [
        int(d.name[len(prefix):])
        for d in EXECUTIONS_ROOT.iterdir()
        if d.is_dir() and d.name.startswith(prefix) and d.name[len(prefix):].isdigit()
    ]
    return f"{prefix}{max(numbers, default=0) + 1:03d}"


class ExecutionContext:
    """
    Owns the artifact directory for one test execution (one spec run).

    Creates:
      artifacts/executions/EXEC_<date>_<NNN>/
        execution.json          written by write_execution_json()
        <SPEC_ID>.json          written by write_execution_json() (includes step_results)
        steps/STEP_*.json       written by StepLogger.record()
        ev/EV-STEP_*-001.png    written by evidence.capture_screenshot()
    """

    def __init__(self, spec_id: str, exec_id: Optional[str] = None) -> None:
        self.spec_id = spec_id
        now = datetime.now(timezone.utc)
        self.started_at: str = now.isoformat()
        self.exec_id: str = exec_id or _next_exec_id(now.strftime("%Y%m%d"))

        self.exec_dir: Path = EXECUTIONS_ROOT / self.exec_id
        self.steps_dir: Path = self.exec_dir / "steps"
        self.evidence_dir: Path = self.exec_dir / "ev"

        self.exec_dir.mkdir(parents=True, exist_ok=True)
        self.steps_dir.mkdir(exist_ok=True)
        self.evidence_dir.mkdir(exist_ok=True)

    def step_path(self, step_id: str) -> Path:
        return self.steps_dir / f"{step_id}.json"

    def evidence_path(self, step_id: str, ext: str = "png") -> Path:
        return self.evidence_dir / f"EV-{step_id}-001.{ext}"

    def trace_path(self) -> Path:
        return self.exec_dir / "trace.zip"

    def write_execution_json(self, status: str, step_results: list[dict]) -> Path:
        finished = datetime.now(timezone.utc).isoformat()
        self.finished_at = finished

        counts: dict[str, int] = {}
        for s in step_results:
            k = s.get("status", "UNKNOWN")
            counts[k] = counts.get(k, 0) + 1

        record: dict = {
            "exec_id": self.exec_id,
            "spec_id": self.spec_id,
            "started_at": self.started_at,
            "finished_at": finished,
            "status": status,
            "total_steps": len(step_results),
            "passed_steps": counts.get("PASSED", 0),
            "failed_steps": counts.get("FAILED", 0),
            "healed_steps": counts.get("HEALING_PASSED", 0),
            "skipped_steps": counts.get("SKIPPED", 0),
            "duration_ms": sum(s.get("duration_ms", 0) for s in step_results),
            "steps": [s["step_id"] for s in step_results],
        }

        out = self.exec_dir / "execution.json"
        out.write_text(json.dumps(record, indent=2), encoding="utf-8")

        tc_out = self.exec_dir / f"{self.spec_id}.json"
        tc_out.write_text(
            json.dumps({**record, "step_results": step_results}, indent=2),
            encoding="utf-8",
        )

        return out
