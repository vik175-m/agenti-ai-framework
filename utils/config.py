from __future__ import annotations

import os
from pathlib import Path

_ROOT = Path(__file__).parent.parent


def _env_bool(key: str, default: bool) -> bool:
    v = os.environ.get(key, "").lower()
    return {"1": True, "true": True, "yes": True, "0": False, "false": False, "no": False}.get(v, default)


def _env_int(key: str, default: int) -> int:
    try:
        return int(os.environ[key])
    except (KeyError, ValueError):
        return default


BROWSER: str = os.environ.get("MDAEF_BROWSER", "chromium")
HEADLESS: bool = _env_bool("MDAEF_HEADLESS", True)
SLOW_MO_MS: int = _env_int("MDAEF_SLOW_MO_MS", 0)
DEFAULT_TIMEOUT_MS: int = _env_int("MDAEF_TIMEOUT_MS", 30_000)
SCREENSHOT_ON_STEP: bool = _env_bool("MDAEF_SCREENSHOT_ON_STEP", True)
TRACE_ON_FAIL: bool = _env_bool("MDAEF_TRACE_ON_FAIL", True)

ARTIFACTS_ROOT: Path = Path(os.environ.get("MDAEF_ARTIFACTS_ROOT", str(_ROOT / "artifacts")))
EXECUTIONS_ROOT: Path = ARTIFACTS_ROOT / "executions"
REPORTS_ROOT: Path = Path(os.environ.get("MDAEF_REPORTS_ROOT", str(_ROOT / "reports")))
ALLURE_RESULTS_DIR: Path = Path(
    os.environ.get("MDAEF_ALLURE_RESULTS", str(_ROOT / "allure-results"))
)
SPECS_DIR: Path = Path(os.environ.get("MDAEF_SPECS_DIR", str(_ROOT / "specs")))
