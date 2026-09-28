from __future__ import annotations

import pytest

from utils.config import DEFAULT_TIMEOUT_MS
from utils.execution_context import ExecutionContext
from utils.logger import StepLogger


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    """Set a realistic user-agent and viewport for all tests."""
    return {
        **browser_context_args,
        "user_agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "viewport": {"width": 1280, "height": 900},
    }


@pytest.fixture(autouse=True)
def _mdaef_timeout(page):
    """Apply MDAEF default timeout to every test's playwright page."""
    page.set_default_timeout(DEFAULT_TIMEOUT_MS)


@pytest.fixture
def exec_context(request) -> ExecutionContext:
    """
    One ExecutionContext per test. Keyed by the @pytest.mark.spec_id("TC_*")
    marker when present; falls back to the test node name.

    Teardown writes execution.json as FAILED if the test crashed before
    calling exec_context.write_execution_json() itself.  This ensures the
    Healing Agent always finds a readable artifact even when a step raises.
    """
    marker = request.node.get_closest_marker("spec_id")
    spec_id = marker.args[0] if marker else request.node.name
    ctx = ExecutionContext(spec_id=spec_id)
    ctx._step_logger: StepLogger | None = None  # back-ref set by step_logger fixture
    yield ctx
    # Teardown: only write if the test did not already write execution.json
    if not (ctx.exec_dir / "execution.json").exists():
        results = ctx._step_logger.results() if ctx._step_logger else []
        ctx.write_execution_json("FAILED", results)


@pytest.fixture
def step_logger(exec_context) -> StepLogger:
    logger = StepLogger(exec_ctx=exec_context)
    exec_context._step_logger = logger  # allow exec_context teardown to access results
    return logger
