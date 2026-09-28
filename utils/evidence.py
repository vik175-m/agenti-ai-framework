from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from playwright.sync_api import BrowserContext, Page


def capture_screenshot(page: "Page", evidence_path: Path) -> Path:
    """Take a full-page screenshot and save to evidence_path. Returns the path."""
    evidence_path.parent.mkdir(parents=True, exist_ok=True)
    page.screenshot(path=str(evidence_path), full_page=True)
    return evidence_path


def stop_tracing(context: "BrowserContext", trace_path: Path) -> Path:
    """Stop Playwright tracing and save the zip to trace_path."""
    trace_path.parent.mkdir(parents=True, exist_ok=True)
    context.tracing.stop(path=str(trace_path))
    return trace_path
