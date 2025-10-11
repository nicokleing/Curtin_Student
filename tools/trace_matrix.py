#!/usr/bin/env python3
from __future__ import annotations
"""
Traceability Matrix updater.

- Links Features -> Code files -> Tests (pytest nodeids)
- Validates file paths (supports comma-separated and glob wildcards)
- Validates tests via pytest --collect-only
- Runs tests unless --no-tests
- Writes/updates the section "## 12) Traceability Matrix (fill during tests)" in docs/postgrad_rubrica_checklist.md

Usage:
    python tools/trace_matrix.py           # run tests and update table
    python tools/trace_matrix.py --no-tests  # only verify existence/collection

Requires:
    pytest (for test collection/execution). If missing, tests are marked "Skipped:pytest-missing".
"""
import argparse
import subprocess
import sys
import shlex
from pathlib import Path
from datetime import datetime, timezone, timedelta
import re
import glob
import json

# Config
CHECKLIST_PATH = Path("docs/postgrad_rubrica_checklist.md")

# Edit these to match your repo (you already scanned real names; keep them here).
# You can list multiple code files comma-separated, and use wildcards like adventure/sim/*.py
ROWS = [
    ("1.0", "Ride layout", "adventure/config/loader.py, adventure/rides/base_ride.py", "tests/test_bbox.py::BBoxTests::test_rides_do_not_overlap_in_preset"),
    ("1.1", "Queue limit", "adventure/rides/base_ride.py", "tests/test_queues.py::QueueCapacityTests::test_enqueue_respects_queue_limit"),
    ("1.2", "Patron decision score", "adventure/patrons/behaviors/decision_behavior.py", "tests/test_strategy.py::StrategyTests::test_shorter_queue_preferred"),
    ("1.3", "Patron timers", "adventure/patrons/patron.py", "tests/test_cli_and_batch.py::ConfigLoaderTests::test_seed_controls_initial_patron_timers"),
    ("1.4", "CLI defaults", "adventure/interface/cli.py", "tests/test_cli_and_batch.py::CLIArgumentTests::test_defaults_are_applied"),
    ("1.5", "Headless flags", "adventure/config/loader.py", "tests/test_cli_and_batch.py::ConfigLoaderTests::test_gui_flags_set_headless_mode"),
    ("1.6", "Stats export", "adventure/stats/export.py", "tests/test_stats_io.py::test_kpi_csv_written_and_headers"),
]

# Perth time (AWST, UTC+8) for audit clarity
AWST = timezone(timedelta(hours=8))

# Utilities

def _glob_exists(path_expr: str) -> bool:
    # Accepts exact file or a glob with wildcards
    path_expr = path_expr.strip()
    if "*" in path_expr or "?" in path_expr or "[" in path_expr:
        return any(Path(p).exists() for p in glob.glob(path_expr))
    return Path(path_expr).exists()


def code_paths_exist(code_field: str) -> bool:
    # Supports multiple comma-separated entries
    parts = [p.strip() for p in code_field.split(",") if p.strip()]
    if not parts:
        return False
    return all(_glob_exists(p) for p in parts)


def which_pytest() -> str | None:
    # Try python -m pytest first to avoid PATH issues
    try:
        r = subprocess.run([sys.executable, "-m", "pytest", "--version"],
                           stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        if r.returncode == 0:
            return f"{shlex.quote(sys.executable)} -m pytest"
    except Exception:
        pass
    # Fallback to pytest on PATH
    try:
        r = subprocess.run(["pytest", "--version"],
                           stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        if r.returncode == 0:
            return "pytest"
    except Exception:
        pass
    return None


def collect_has_nodeid(pytest_cmd: str, nodeid: str) -> bool:
    # Verify the test exists by collecting tests; nodeid may fail collection if wrong
    try:
        r = subprocess.run(f"{pytest_cmd} --collect-only -q {shlex.quote(nodeid)}",
                           shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        return r.returncode == 0
    except Exception:
        return False


def run_nodeid(pytest_cmd: str, nodeid: str) -> str:
    # Return "Done" if pass, "WIP" if fail
    r = subprocess.run(f"{pytest_cmd} -q {shlex.quote(nodeid)}",
                       shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    return "Done" if r.returncode == 0 else "WIP"


def render_table(rows_with_status):
    header = "No  Feature                        Code                          Test                                  Status                   Date"
    lines = [header]
    for no, feat, code, test, status, date in rows_with_status:
        lines.append(f"{no} {feat:<30} {code:<30} {test:<40} {status:<22} {date}")
    return "\n".join(lines)


def update_checklist(table_text: str):
    if not CHECKLIST_PATH.exists():
        base = "## 12) Traceability Matrix (fill during tests)\n\n" + table_text + "\n"
        CHECKLIST_PATH.write_text(base, encoding="utf-8")
        return

    content = CHECKLIST_PATH.read_text(encoding="utf-8")
    pattern = r"(## 12\) Traceability Matrix[^\n]*\n)(.*?)(\n(?=## |\Z))"
    m = re.search(pattern, content, flags=re.DOTALL)
    if m:
        new_content = content[:m.start(2)] + table_text + content[m.end(2):]
    else:
        new_content = content.rstrip() + "\n\n## 12) Traceability Matrix (fill during tests)\n\n" + table_text + "\n"
    CHECKLIST_PATH.write_text(new_content, encoding="utf-8")


# Main entry point

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-tests", action="store_true", help="Do not execute tests; only verify code/test presence.")
    args = parser.parse_args()

    today = datetime.now(AWST).strftime("%Y-%m-%d")
    pytest_cmd = which_pytest()

    if not pytest_cmd and not args.no_tests:
        # We will mark as "Skipped:pytest-missing" rather than exiting
        pass

    out = []
    for no, feat, code_field, nodeid in ROWS:
        code_ok = code_paths_exist(code_field)
        test_file = nodeid.split("::", 1)[0].strip()
        test_file_ok = _glob_exists(test_file)

        # Default status/date
        status = "Unknown"
        date = "-"

        if not code_ok and not test_file_ok:
            status = "Missing code+test"
        elif not code_ok:
            status = "Missing code"
        elif not test_file_ok:
            status = "Missing test"
        else:
            # Both code and test file exist; check collection or run
            if args.no_tests:
                status = "Collected-not-run" if (pytest_cmd and collect_has_nodeid(pytest_cmd, nodeid)) else "Test-not-collected"
                date = today
            else:
                if not pytest_cmd:
                    status = "Skipped:pytest-missing"
                    date = today
                else:
                    # Ensure nodeid collects; if not, mark Missing test (nodeid wrong)
                    if collect_has_nodeid(pytest_cmd, nodeid):
                        status = run_nodeid(pytest_cmd, nodeid)  # Done or WIP
                        date = today
                    else:
                        status = "Missing test (bad nodeid)"

        out.append((no, feat, code_field, nodeid, status, date))

    table = render_table(out)
    update_checklist(table)

    # Also print a JSON summary to help in CI logs
    summary = [{"No": r[0], "Feature": r[1], "Code": r[2], "Test": r[3], "Status": r[4], "Date": r[5]} for r in out]
    print("\nTraceability Matrix updated:\n")
    print(table)
    print("\nJSON summary:\n" + json.dumps(summary, indent=2))

if __name__ == "__main__":
    main()
