"""
Agent 4 — Reporting Agent implementation.

Reads structured execution artifacts from artifacts/executions/<exec_id>/
and produces:
  reports/<exec_id>/index.html       — executive HTML dashboard
  reports/<exec_id>/<TC_ID>.html     — per-test step detail
  allure-results/<uuid>-result.json  — Allure 2 result per test
  allure-results/<uuid>-attachment.* — screenshot copies for Allure
"""
from __future__ import annotations

import json
import shutil
import sys
import uuid as _uuid_mod
from datetime import datetime, timezone
from pathlib import Path

from jinja2 import Environment, BaseLoader

# ── project bootstrap ────────────────────────────────────────────────────────
PROJECT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT))

from utils.config import EXECUTIONS_ROOT, REPORTS_ROOT, ALLURE_RESULTS_DIR

# ── CSS shared between both templates ───────────────────────────────────────

_CSS = """
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

:root {
  --bg:          #f9fafb;
  --surface:     #ffffff;
  --border:      #e5e7eb;
  --text:        #111827;
  --muted:       #6b7280;
  --accent:      #2563eb;

  --pass-bg:     #dcfce7;  --pass-text:    #166534;
  --fail-bg:     #fee2e2;  --fail-text:    #991b1b;
  --heal-bg:     #fef3c7;  --heal-text:    #92400e;
  --skip-bg:     #f3f4f6;  --skip-text:    #374151;

  --tile-radius: 10px;
  --radius:       6px;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  font-size: 14px;
  color: var(--text);
  background: var(--bg);
}

@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    --bg:      #111827;  --surface: #1f2937;  --border:  #374151;
    --text:    #f9fafb;  --muted:   #9ca3af;  --accent:  #60a5fa;
    --pass-bg: #14532d;  --pass-text: #86efac;
    --fail-bg: #7f1d1d;  --fail-text: #fca5a5;
    --heal-bg: #78350f;  --heal-text: #fcd34d;
    --skip-bg: #1f2937;  --skip-text: #9ca3af;
  }
}

body { padding: 24px 32px; }

header { margin-bottom: 28px; }
header h1 { font-size: 22px; font-weight: 700; letter-spacing: -0.3px; }
header p  { color: var(--muted); margin-top: 4px; font-size: 13px; }

.tiles {
  display: flex; flex-wrap: wrap; gap: 12px; margin-bottom: 32px;
}
.tile {
  background: var(--surface); border: 1px solid var(--border);
  border-radius: var(--tile-radius); padding: 16px 20px; min-width: 120px;
}
.tile .label { font-size: 11px; text-transform: uppercase;
  letter-spacing: 0.6px; color: var(--muted); margin-bottom: 6px; }
.tile .value { font-size: 26px; font-weight: 700; line-height: 1; }
.tile.pass .value { color: #16a34a; }
.tile.fail .value { color: #dc2626; }
.tile.heal .value { color: #d97706; }

section { margin-bottom: 36px; }
section h2 { font-size: 15px; font-weight: 600; margin-bottom: 12px;
  padding-bottom: 8px; border-bottom: 1px solid var(--border); }

table { width: 100%; border-collapse: collapse; background: var(--surface);
  border-radius: var(--radius); overflow: hidden;
  border: 1px solid var(--border); }
th { background: var(--border); text-align: left; padding: 9px 14px;
  font-size: 12px; font-weight: 600; text-transform: uppercase;
  letter-spacing: 0.4px; color: var(--muted); }
td { padding: 10px 14px; border-top: 1px solid var(--border);
  vertical-align: top; }
tr:hover td { background: var(--bg); }

.badge {
  display: inline-block; padding: 2px 8px; border-radius: 999px;
  font-size: 11px; font-weight: 600; letter-spacing: 0.3px;
}
.badge-PASSED, .badge-passed       { background: var(--pass-bg); color: var(--pass-text); }
.badge-FAILED, .badge-failed       { background: var(--fail-bg); color: var(--fail-text); }
.badge-HEALING_PASSED, .badge-HEAL { background: var(--heal-bg); color: var(--heal-text); }
.badge-SKIPPED, .badge-skipped     { background: var(--skip-bg); color: var(--skip-text); }

a { color: var(--accent); text-decoration: none; }
a:hover { text-decoration: underline; }

.mono { font-family: "SFMono-Regular", Consolas, monospace; font-size: 12px;
  color: var(--muted); word-break: break-all; }

.thumb { max-width: 120px; max-height: 80px; border-radius: 4px;
  border: 1px solid var(--border); cursor: pointer; }
.thumb:hover { opacity: 0.85; }

.meta-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 12px; margin-bottom: 24px; }
.meta-card { background: var(--surface); border: 1px solid var(--border);
  border-radius: var(--radius); padding: 12px 16px; }
.meta-card .label { font-size: 11px; text-transform: uppercase;
  letter-spacing: 0.5px; color: var(--muted); margin-bottom: 4px; }
.meta-card .val { font-weight: 600; }

.tag { display: inline-block; background: var(--border); color: var(--muted);
  border-radius: 4px; padding: 1px 7px; font-size: 11px; margin-right: 4px; }

.breadcrumb { font-size: 13px; color: var(--muted); margin-bottom: 20px; }
.breadcrumb a { color: var(--accent); }

@media (max-width: 640px) {
  body { padding: 16px; }
  .tiles { gap: 8px; }
  .tile { min-width: 80px; padding: 12px; }
  .tile .value { font-size: 20px; }
}
"""

# ── Dashboard template ───────────────────────────────────────────────────────

_DASHBOARD_TMPL = """\
<!doctype html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>MDAEF Dashboard — {{ exec_id }}</title>
<style>{{ css }}</style>
</head>
<body>
<header>
  <h1>MDAEF — Executive Dashboard</h1>
  <p>Execution <strong>{{ exec_id }}</strong>
     &nbsp;·&nbsp; Generated {{ generated_at }}
     {% if spec_ids %}&nbsp;·&nbsp; {{ spec_ids | join(', ') }}{% endif %}
  </p>
</header>

<div class="tiles">
  <div class="tile">
    <div class="label">Total Tests</div>
    <div class="value">{{ summary.total }}</div>
  </div>
  <div class="tile pass">
    <div class="label">Passed</div>
    <div class="value">{{ summary.passed }}</div>
  </div>
  <div class="tile fail">
    <div class="label">Failed</div>
    <div class="value">{{ summary.failed }}</div>
  </div>
  <div class="tile heal">
    <div class="label">Healed</div>
    <div class="value">{{ summary.healed }}</div>
  </div>
  <div class="tile">
    <div class="label">Pass Rate</div>
    <div class="value">{{ summary.pass_rate }}%</div>
  </div>
  <div class="tile">
    <div class="label">Duration</div>
    <div class="value">{{ summary.duration_s }}s</div>
  </div>
</div>

{% if modules %}
<section>
  <h2>Module Summary</h2>
  <table>
    <thead><tr>
      <th>Module</th><th>Total</th><th>Passed</th>
      <th>Failed</th><th>Healed</th><th>Pass Rate</th>
    </tr></thead>
    <tbody>
    {% for m in modules %}
    <tr>
      <td>{{ m.module }}</td>
      <td>{{ m.total }}</td>
      <td>{{ m.passed }}</td>
      <td>{{ m.failed }}</td>
      <td>{{ m.healed }}</td>
      <td>{{ m.pass_rate }}%</td>
    </tr>
    {% endfor %}
    </tbody>
  </table>
</section>
{% endif %}

<section>
  <h2>Test Results</h2>
  <table>
    <thead><tr>
      <th>Test ID</th><th>Title</th><th>Status</th>
      <th>Steps (P/F/H)</th><th>Duration</th><th>Detail</th>
    </tr></thead>
    <tbody>
    {% for t in tests %}
    <tr>
      <td class="mono">{{ t.spec_id }}</td>
      <td>{{ t.title }}</td>
      <td><span class="badge badge-{{ t.status }}">{{ t.status }}</span></td>
      <td>{{ t.passed_steps }}/{{ t.failed_steps }}/{{ t.healed_steps }}</td>
      <td>{{ t.duration_s }}s</td>
      <td><a href="{{ t.detail_url }}">View steps</a></td>
    </tr>
    {% endfor %}
    </tbody>
  </table>
</section>

</body>
</html>
"""

# ── Per-test detail template ─────────────────────────────────────────────────

_DETAIL_TMPL = """\
<!doctype html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{{ spec_id }} — MDAEF</title>
<style>{{ css }}</style>
</head>
<body>
<div class="breadcrumb">
  <a href="index.html">Dashboard</a> / {{ spec_id }}
</div>

<header>
  <h1>{{ spec_id }} &nbsp;<span class="badge badge-{{ status }}">{{ status }}</span></h1>
  <p>{{ title }}</p>
</header>

<div class="meta-grid">
  <div class="meta-card"><div class="label">Module</div><div class="val">{{ module }}</div></div>
  <div class="meta-card"><div class="label">Priority</div><div class="val">{{ priority }}</div></div>
  <div class="meta-card"><div class="label">Type</div><div class="val">{{ type }}</div></div>
  <div class="meta-card"><div class="label">Exec ID</div><div class="val mono">{{ exec_id }}</div></div>
  <div class="meta-card"><div class="label">Duration</div><div class="val">{{ duration_s }}s</div></div>
  <div class="meta-card">
    <div class="label">Tags</div>
    <div class="val">{% for tag in tags %}<span class="tag">{{ tag }}</span>{% endfor %}</div>
  </div>
</div>

<section>
  <h2>Step Results</h2>
  <table>
    <thead><tr>
      <th>Step</th><th>Action</th><th>Expected</th><th>Actual</th>
      <th>Status</th><th>Locator</th><th>ms</th><th>Screenshot</th>
    </tr></thead>
    <tbody>
    {% for s in steps %}
    <tr>
      <td class="mono">{{ s.step_id }}</td>
      <td>{{ s.action }}</td>
      <td style="color:var(--muted)">{{ s.expected_result }}</td>
      <td>{{ s.actual_result }}{% if s.error %}<br><span style="color:var(--fail-text);font-size:11px">{{ s.error }}</span>{% endif %}</td>
      <td><span class="badge badge-{{ s.status }}">{{ s.status }}</span></td>
      <td class="mono">{{ s.locator }}</td>
      <td style="white-space:nowrap">{{ s.duration_ms }}</td>
      <td>
        {% if s.screenshot_rel %}
        <a href="{{ s.screenshot_rel }}" target="_blank">
          <img class="thumb" src="{{ s.screenshot_rel }}" alt="{{ s.step_id }}">
        </a>
        {% else %}—{% endif %}
      </td>
    </tr>
    {% endfor %}
    </tbody>
  </table>
</section>

</body>
</html>
"""


# ── helpers ──────────────────────────────────────────────────────────────────

_jinja = Environment(loader=BaseLoader(), autoescape=True)


def _render(template_str: str, **ctx) -> str:
    return _jinja.from_string(template_str).render(css=_CSS, **ctx)


def _iso_to_epoch_ms(iso: str) -> int:
    try:
        dt = datetime.fromisoformat(iso.replace("Z", "+00:00"))
        return int(dt.timestamp() * 1000)
    except Exception:
        return 0


def _ms_to_s(ms: int) -> str:
    return f"{ms / 1000:.2f}"


def _allure_status(status: str) -> str:
    return {
        "PASSED": "passed",
        "FAILED": "failed",
        "SKIPPED": "skipped",
        "HEALING_PASSED": "passed",
        "HEALING_FAILED": "failed",
        "BLOCKED": "skipped",
    }.get(status, "broken")


def _priority_to_severity(priority: str) -> str:
    return {
        "Critical": "blocker",
        "High": "critical",
        "Medium": "normal",
        "Low": "minor",
    }.get(priority, "normal")


# ── loader ───────────────────────────────────────────────────────────────────

def _load_execution(exec_dir: Path) -> dict:
    p = exec_dir / "execution.json"
    if not p.exists():
        raise FileNotFoundError(f"execution.json not found in {exec_dir}")
    return json.loads(p.read_text())


def _load_tc_json(exec_dir: Path, spec_id: str) -> dict | None:
    p = exec_dir / f"{spec_id}.json"
    if not p.exists():
        return None
    return json.loads(p.read_text())


# ── core builder ─────────────────────────────────────────────────────────────

def build_report(exec_id: str | None = None) -> Path:
    # 1. Resolve exec directory
    if exec_id:
        exec_dir = EXECUTIONS_ROOT / exec_id
        if not exec_dir.exists():
            available = sorted(d.name for d in EXECUTIONS_ROOT.iterdir() if d.is_dir())
            raise FileNotFoundError(
                f"Execution '{exec_id}' not found.\nAvailable: {available}"
            )
    else:
        candidates = sorted(EXECUTIONS_ROOT.iterdir())
        if not candidates:
            raise FileNotFoundError(f"No executions found under {EXECUTIONS_ROOT}")
        exec_dir = candidates[-1]
        exec_id = exec_dir.name

    print(f"Reporting on: {exec_id}  ({exec_dir})")

    # 2. Load top-level execution summary
    exec_data = _load_execution(exec_dir)
    spec_ids: list[str] = [exec_data["spec_id"]]

    # 3. Load per-test detail records
    tc_records: list[dict] = []
    for sid in spec_ids:
        tc = _load_tc_json(exec_dir, sid)
        if tc is None:
            print(f"  WARNING: {sid}.json not found — skipping")
        else:
            tc_records.append(tc)

    if not tc_records:
        raise RuntimeError("No TC records loaded — nothing to report.")

    # 4. Build report directory
    report_dir = REPORTS_ROOT / exec_id
    report_dir.mkdir(parents=True, exist_ok=True)
    ev_dest = report_dir / "ev"
    ev_dest.mkdir(exist_ok=True)

    # Copy screenshots into report directory so HTML src= refs work
    ev_src = exec_dir / "ev"
    if ev_src.exists():
        for img in ev_src.iterdir():
            shutil.copy2(img, ev_dest / img.name)

    # 5. Prepare Allure results directory
    ALLURE_RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    # ── per-test processing ───────────────────────────────────────────────────
    module_map: dict[str, dict] = {}
    dashboard_tests: list[dict] = []

    for tc in tc_records:
        sid = tc["spec_id"]
        step_results: list[dict] = tc.get("step_results", [])
        status = tc["status"]
        passed_s = tc.get("passed_steps", 0)
        failed_s = tc.get("failed_steps", 0)
        healed_s = tc.get("healed_steps", 0)
        dur_ms = tc.get("duration_ms", 0)

        # ── parse spec to get metadata (title, module, etc.) ─────────────────
        from utils.spec_parser import parse_spec_file
        spec_path = PROJECT / "specs" / f"{sid}.md"
        spec_meta: dict = {}
        if spec_path.exists():
            try:
                parsed = parse_spec_file(str(spec_path))
                spec_meta = {
                    "title": parsed.title,
                    "module": parsed.module,
                    "priority": parsed.priority,
                    "type": parsed.type,
                    "tags": parsed.tags,
                }
            except Exception:
                pass
        spec_meta.setdefault("title", sid)
        spec_meta.setdefault("module", "Unknown")
        spec_meta.setdefault("priority", "Medium")
        spec_meta.setdefault("type", "UI")
        spec_meta.setdefault("tags", [])

        mod = spec_meta["module"]
        if mod not in module_map:
            module_map[mod] = {"module": mod, "total": 0, "passed": 0,
                               "failed": 0, "healed": 0}
        module_map[mod]["total"] += 1
        if status == "PASSED":
            module_map[mod]["passed"] += 1
        elif status == "FAILED":
            module_map[mod]["failed"] += 1
        elif status in ("HEALING_PASSED", "HEAL"):
            module_map[mod]["healed"] += 1

        # ── render per-test detail page ───────────────────────────────────────
        steps_ctx = []
        for sr in step_results:
            scr = sr.get("screenshot_path", "")
            scr_rel = ""
            if scr:
                scr_name = Path(scr).name
                if (ev_dest / scr_name).exists():
                    scr_rel = f"ev/{scr_name}"
            steps_ctx.append({
                "step_id":        sr.get("step_id", ""),
                "action":         sr.get("action", ""),
                "expected_result": sr.get("expected_result", ""),
                "actual_result":  sr.get("actual_result", ""),
                "status":         sr.get("status", ""),
                "locator":        sr.get("locator", ""),
                "duration_ms":    sr.get("duration_ms", 0),
                "error":          sr.get("error", ""),
                "screenshot_rel": scr_rel,
            })

        detail_html = _render(
            _DETAIL_TMPL,
            spec_id=sid,
            title=spec_meta["title"],
            module=spec_meta["module"],
            priority=spec_meta["priority"],
            type=spec_meta["type"],
            tags=spec_meta["tags"],
            exec_id=exec_id,
            status=status,
            duration_s=_ms_to_s(dur_ms),
            steps=steps_ctx,
        )
        detail_path = report_dir / f"{sid}.html"
        detail_path.write_text(detail_html, encoding="utf-8")
        print(f"  Written: {detail_path}")

        dashboard_tests.append({
            "spec_id":      sid,
            "title":        spec_meta["title"],
            "status":       status,
            "passed_steps": passed_s,
            "failed_steps": failed_s,
            "healed_steps": healed_s,
            "duration_s":   _ms_to_s(dur_ms),
            "detail_url":   f"{sid}.html",
        })

        # ── write Allure result ───────────────────────────────────────────────
        result_uuid = str(_uuid_mod.uuid4())
        started_ms = _iso_to_epoch_ms(tc.get("started_at", ""))
        finished_ms = _iso_to_epoch_ms(tc.get("finished_at", ""))

        allure_steps = []
        step_start = started_ms
        for sr in step_results:
            dur = sr.get("duration_ms", 0)
            step_stop = step_start + dur
            att_uuid = str(_uuid_mod.uuid4())

            attachments = []
            scr = sr.get("screenshot_path", "")
            if scr and Path(scr).exists():
                att_name = f"{att_uuid}-attachment.png"
                shutil.copy2(scr, ALLURE_RESULTS_DIR / att_name)
                attachments.append({"name": "screenshot", "source": att_name,
                                    "type": "image/png"})

            allure_steps.append({
                "name":        f"{sr.get('step_id', '')} — {sr.get('action', '')}",
                "status":      _allure_status(sr.get("status", "")),
                "start":       step_start,
                "stop":        step_stop,
                "steps":       [],
                "attachments": attachments,
                "parameters":  [],
            })
            step_start = step_stop

        labels = [
            {"name": "suite",    "value": spec_meta["module"]},
            {"name": "severity", "value": _priority_to_severity(spec_meta["priority"])},
        ]
        for tag in spec_meta["tags"]:
            labels.append({"name": "tag", "value": tag})

        allure_result = {
            "uuid":        result_uuid,
            "historyId":   sid,
            "testCaseId":  sid,
            "name":        spec_meta["title"],
            "fullName":    sid,
            "labels":      labels,
            "status":      _allure_status(status),
            "start":       started_ms,
            "stop":        finished_ms,
            "steps":       allure_steps,
            "attachments": [],
            "parameters":  [],
        }
        allure_path = ALLURE_RESULTS_DIR / f"{result_uuid}-result.json"
        allure_path.write_text(json.dumps(allure_result, indent=2), encoding="utf-8")
        print(f"  Written: {allure_path}")

    # ── module pass rates ─────────────────────────────────────────────────────
    modules_ctx = []
    for m in module_map.values():
        total = m["total"] or 1
        m["pass_rate"] = round(m["passed"] / total * 100, 1)
        modules_ctx.append(m)

    # ── summary tiles ─────────────────────────────────────────────────────────
    total_tests = len(tc_records)
    total_passed = sum(1 for t in dashboard_tests if t["status"] == "PASSED")
    total_failed = sum(1 for t in dashboard_tests if t["status"] == "FAILED")
    total_healed = sum(1 for t in dashboard_tests
                       if t["status"] in ("HEALING_PASSED", "HEAL"))
    pass_rate = round(total_passed / total_tests * 100, 1) if total_tests else 0.0
    total_dur_ms = sum(tc.get("duration_ms", 0) for tc in tc_records)

    summary_ctx = {
        "total":    total_tests,
        "passed":   total_passed,
        "failed":   total_failed,
        "healed":   total_healed,
        "pass_rate": pass_rate,
        "duration_s": _ms_to_s(total_dur_ms),
    }

    # ── render dashboard ──────────────────────────────────────────────────────
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    dashboard_html = _render(
        _DASHBOARD_TMPL,
        exec_id=exec_id,
        generated_at=generated_at,
        spec_ids=spec_ids,
        summary=summary_ctx,
        modules=modules_ctx,
        tests=dashboard_tests,
    )
    index_path = report_dir / "index.html"
    index_path.write_text(dashboard_html, encoding="utf-8")
    print(f"  Written: {index_path}")

    # ── summary ───────────────────────────────────────────────────────────────
    print(f"\nReport complete:")
    print(f"  Dashboard:  {index_path}")
    print(f"  Tests:      {len(dashboard_tests)}")
    print(f"  Pass rate:  {pass_rate}%")
    print(f"  Duration:   {_ms_to_s(total_dur_ms)}s")
    print(f"  Allure:     {ALLURE_RESULTS_DIR}")

    return index_path


# ── CLI ──────────────────────────────────────────────────────────────────────

def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv

    if "--all" in argv:
        if not EXECUTIONS_ROOT.exists():
            print(f"No executions directory found: {EXECUTIONS_ROOT}")
            return 1
        exec_ids = sorted(d.name for d in EXECUTIONS_ROOT.iterdir() if d.is_dir())
        if not exec_ids:
            print("No executions found.")
            return 1
        for eid in exec_ids:
            try:
                build_report(eid)
            except Exception as exc:
                print(f"  ERROR {eid}: {exc}")
        return 0

    exec_id = argv[0] if argv else None
    try:
        build_report(exec_id)
        return 0
    except FileNotFoundError as exc:
        print(f"ERROR: {exc}")
        return 1
    except Exception as exc:
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
