#!/usr/bin/env python3
"""Check that the bootstrap workflow and shared Phase 10 make route still replay the shared Phase 10 route."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys


WORKFLOW_PATH = Path(".github/workflows/zigux-bootstrap.yml")
CLOSURE_NOTE_PATH = Path("Documentation/zigux/phase10-closure-evidence.md")
MAKEFILE_PATH = Path("zigux/Makefile")

SELF_TEST_STEP = "Self-test current Phase 10 bootstrap route checker"
SELF_TEST_CMD = "python3 scripts/zigux/check-phase10-bootstrap-route.py --self-test"
CHECK_STEP = "Check current Phase 10 bootstrap route"
CHECK_CMD = "python3 scripts/zigux/check-phase10-bootstrap-route.py"
VALIDATE_STEP = "Validate Phase 10 checker-backed review packet"
VALIDATE_CMD = "make -C zigux phase10-validate"
TEST_STEP = "Run Phase 10 helper tests"
TEST_CMD = "make -C zigux phase10-test"
SELF_TEST_RUN_LINE = f"run: {SELF_TEST_CMD}\n"
CHECK_RUN_LINE = f"run: {CHECK_CMD}\n"
VALIDATE_RUN_LINE = f"run: {VALIDATE_CMD}\n"
TEST_RUN_LINE = f"run: {TEST_CMD}\n"
MAKE_VALIDATE_TARGET = "phase10-validate:\n"
MAKE_VALIDATE_CMD = "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase10.py\n"
MAKE_CLOSURE_CMD = "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase10-closure.py\n"
MAKE_COUNTS_CMD = (
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase10-closure-manifest-counts.py\n"
)
MAKE_TESTS_README_CMD = (
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase10-tests-readme-core-surfaces.py\n"
)
MAKE_TEST_TARGET = "phase10-test:\n"
NOTE_SCRIPT_MARKER = "`scripts/zigux/check-phase10-bootstrap-route.py`"
NOTE_ROUTE_PHRASE = (
    "fails closed if the bootstrap workflow drops `make -C zigux "
    "phase10-validate` or reorders it behind `make -C zigux phase10-test`"
)
NOTE_COUNTS_MARKER = "`scripts/zigux/check-phase10-closure-manifest-counts.py`"
NOTE_COUNTS_PHRASE = (
    "fails closed if its summary counts drift from the listed docs, manifests, "
    "drivers, or tests surfaces"
)


def require_marker(text: str, marker: str, label: str) -> None:
    if marker not in text:
        raise SystemExit(f"phase10 bootstrap route checker missing {label}: {marker}")


def require_exact_count(text: str, marker: str, expected: int, label: str) -> None:
    actual = text.count(marker)
    if actual != expected:
        raise SystemExit(
            "phase10 bootstrap route checker expected exactly "
            f"{expected} occurrences of {label} {marker}, found {actual}"
        )


def require_order(text: str, earlier: str, later: str, label: str) -> None:
    earlier_index = text.find(earlier)
    later_index = text.find(later)
    if earlier_index == -1 or later_index == -1:
        raise SystemExit(
            f"phase10 bootstrap route checker missing ordered markers for {label}"
        )
    if earlier_index >= later_index:
        raise SystemExit(
            "phase10 bootstrap route checker expected "
            f"{label} `{earlier}` before `{later}`"
        )


def section_between(text: str, start: str, end: str, label: str) -> str:
    start_index = text.find(start)
    if start_index == -1:
        raise SystemExit(f"phase10 bootstrap route checker missing {label} start: {start}")
    end_index = text.find(end, start_index)
    if end_index == -1:
        raise SystemExit(f"phase10 bootstrap route checker missing {label} end: {end}")
    return text[start_index:end_index]


def check_workflow(text: str) -> None:
    require_marker(text, SELF_TEST_STEP, "workflow self-test step name")
    require_marker(text, SELF_TEST_CMD, "workflow self-test command")
    require_marker(text, CHECK_STEP, "workflow checker step name")
    require_marker(text, CHECK_CMD, "workflow checker command")
    require_marker(text, VALIDATE_STEP, "workflow validate step name")
    require_marker(text, VALIDATE_CMD, "workflow validate command")
    require_marker(text, TEST_STEP, "workflow test step name")
    require_marker(text, TEST_CMD, "workflow test command")
    require_exact_count(text, SELF_TEST_RUN_LINE, 1, "workflow run line")
    require_exact_count(text, CHECK_RUN_LINE, 1, "workflow run line")
    require_exact_count(text, VALIDATE_RUN_LINE, 1, "workflow run line")
    require_exact_count(text, TEST_RUN_LINE, 1, "workflow run line")
    require_order(text, SELF_TEST_STEP, CHECK_STEP, "workflow step order")
    require_order(text, CHECK_STEP, VALIDATE_STEP, "workflow step order")
    require_order(text, VALIDATE_STEP, TEST_STEP, "workflow step order")
    require_order(text, SELF_TEST_RUN_LINE, CHECK_RUN_LINE, "workflow command order")
    require_order(text, CHECK_RUN_LINE, VALIDATE_RUN_LINE, "workflow command order")
    require_order(text, VALIDATE_RUN_LINE, TEST_RUN_LINE, "workflow command order")


def check_makefile(text: str) -> None:
    section = section_between(text, MAKE_VALIDATE_TARGET, MAKE_TEST_TARGET, "phase10 make route")
    require_marker(section, MAKE_COUNTS_CMD, "phase10 manifest-count checker command")
    require_marker(section, MAKE_VALIDATE_CMD, "phase10 make validate command")
    require_marker(section, MAKE_CLOSURE_CMD, "phase10 make closure command")
    require_exact_count(section, MAKE_COUNTS_CMD, 1, "phase10 make route command")
    require_exact_count(section, MAKE_VALIDATE_CMD, 1, "phase10 make route command")
    require_exact_count(section, MAKE_CLOSURE_CMD, 1, "phase10 make route command")
    require_order(section, MAKE_TESTS_README_CMD, MAKE_COUNTS_CMD, "phase10 make route order")
    require_order(section, MAKE_COUNTS_CMD, MAKE_VALIDATE_CMD, "phase10 make route order")
    require_order(section, MAKE_VALIDATE_CMD, MAKE_CLOSURE_CMD, "phase10 make route order")


def check_note(text: str) -> None:
    require_marker(text, NOTE_SCRIPT_MARKER, "closure note script marker")
    require_marker(text, NOTE_ROUTE_PHRASE, "closure note route phrase")
    require_marker(text, NOTE_COUNTS_MARKER, "closure note count-guard marker")
    require_marker(text, NOTE_COUNTS_PHRASE, "closure note count-guard phrase")
    require_exact_count(text, NOTE_SCRIPT_MARKER, 1, "closure note script marker")
    require_exact_count(text, NOTE_COUNTS_MARKER, 1, "closure note count-guard marker")
    require_exact_count(text, VALIDATE_CMD, 1, "closure note validate command")
    require_exact_count(text, TEST_CMD, 1, "closure note test command")


def run_self_test() -> int:
    good_workflow = """name: zigux-bootstrap
jobs:
  bootstrap:
    steps:
      - name: Self-test current Phase 10 bootstrap route checker
        run: python3 scripts/zigux/check-phase10-bootstrap-route.py --self-test
      - name: Check current Phase 10 bootstrap route
        run: python3 scripts/zigux/check-phase10-bootstrap-route.py
      - name: Validate Phase 10 checker-backed review packet
        run: make -C zigux phase10-validate
      - name: Run Phase 10 helper tests
        run: make -C zigux phase10-test
"""
    good_makefile = """phase10-validate:
\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase10-bootstrap-route.py
\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase10-shared-freeze-boundary.py
\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase10-ring-packet.py
\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase10-input-packet.py
\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase10-mmio-packet.py
\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase10-harness-coverage.py
\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase10-tests-readme-core-surfaces.py
\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase10-closure-manifest-counts.py
\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase10.py
\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase10-closure.py

phase10-test:
\tcd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase10_build.zig --summary all
"""
    good_note = """# Phase 10 Closure Evidence
The shared bootstrap-route guard now stays explicit through `scripts/zigux/check-phase10-bootstrap-route.py` so the closure packet fails closed if the bootstrap workflow drops `make -C zigux phase10-validate` or reorders it behind `make -C zigux phase10-test`.
The shared closure-manifest count guard now stays explicit through `scripts/zigux/check-phase10-closure-manifest-counts.py` so the closure packet fails closed if its summary counts drift from the listed docs, manifests, drivers, or tests surfaces.
"""
    check_workflow(good_workflow)
    check_makefile(good_makefile)
    check_note(good_note)

    bad_workflow_missing_self_test = good_workflow.replace(
        SELF_TEST_CMD,
        "python3 scripts/zigux/check-phase10-bootstrap-route-missing.py --self-test",
        1,
    )
    try:
        check_workflow(bad_workflow_missing_self_test)
    except SystemExit as exc:
        assert SELF_TEST_CMD in str(exc)
    else:
        raise AssertionError("expected missing self-test command failure")

    bad_workflow_missing_check = good_workflow.replace(
        CHECK_CMD,
        "python3 scripts/zigux/check-phase10-bootstrap-route-missing.py",
        1,
    )
    try:
        check_workflow(bad_workflow_missing_check)
    except SystemExit as exc:
        assert CHECK_CMD in str(exc)
    else:
        raise AssertionError("expected missing checker command failure")

    bad_workflow_missing_validate = good_workflow.replace(
        VALIDATE_CMD,
        "python3 scripts/zigux/validate-phase10.py",
        1,
    )
    try:
        check_workflow(bad_workflow_missing_validate)
    except SystemExit as exc:
        assert VALIDATE_CMD in str(exc)
    else:
        raise AssertionError("expected missing validate command failure")

    bad_workflow_reordered = good_workflow.replace(
        f"      - name: {CHECK_STEP}\n        run: {CHECK_CMD}\n"
        f"      - name: {VALIDATE_STEP}\n        run: {VALIDATE_CMD}\n",
        f"      - name: {VALIDATE_STEP}\n        run: {VALIDATE_CMD}\n"
        f"      - name: {CHECK_STEP}\n        run: {CHECK_CMD}\n",
        1,
    )
    try:
        check_workflow(bad_workflow_reordered)
    except SystemExit as exc:
        assert "workflow step order" in str(exc) or "workflow command order" in str(exc)
    else:
        raise AssertionError("expected reordered workflow failure")

    bad_makefile_missing_counts = good_makefile.replace(
        MAKE_COUNTS_CMD,
        "",
        1,
    )
    try:
        check_makefile(bad_makefile_missing_counts)
    except SystemExit as exc:
        assert "phase10 manifest-count checker command" in str(exc)
    else:
        raise AssertionError("expected missing phase10 manifest-count command failure")

    bad_makefile_missing_validate = good_makefile.replace(
        MAKE_VALIDATE_CMD,
        "",
        1,
    )
    try:
        check_makefile(bad_makefile_missing_validate)
    except SystemExit as exc:
        assert "phase10 make validate command" in str(exc)
    else:
        raise AssertionError("expected missing phase10 validate route failure")

    bad_makefile_reordered = good_makefile.replace(
        f"{MAKE_COUNTS_CMD}{MAKE_VALIDATE_CMD}",
        f"{MAKE_VALIDATE_CMD}{MAKE_COUNTS_CMD}",
        1,
    )
    try:
        check_makefile(bad_makefile_reordered)
    except SystemExit as exc:
        assert "phase10 make route order" in str(exc)
    else:
        raise AssertionError("expected reordered phase10 make route failure")

    bad_note_missing_script = good_note.replace(
        NOTE_SCRIPT_MARKER,
        "`scripts/zigux/check-phase10-other.py`",
        1,
    )
    try:
        check_note(bad_note_missing_script)
    except SystemExit as exc:
        assert NOTE_SCRIPT_MARKER in str(exc)
    else:
        raise AssertionError("expected missing note script marker failure")

    bad_note_missing_counts = good_note.replace(
        NOTE_COUNTS_MARKER,
        "`scripts/zigux/check-phase10-other-counts.py`",
        1,
    )
    try:
        check_note(bad_note_missing_counts)
    except SystemExit as exc:
        assert NOTE_COUNTS_MARKER in str(exc)
    else:
        raise AssertionError("expected missing note count marker failure")

    bad_note_missing_phrase = good_note.replace("reorders it behind", "moves it away from", 1)
    try:
        check_note(bad_note_missing_phrase)
    except SystemExit as exc:
        assert "closure note route phrase" in str(exc)
    else:
        raise AssertionError("expected missing note route phrase failure")

    print("PHASE10_BOOTSTRAP_ROUTE_CHECKER_SELF_TEST=pass")
    print("PHASE10_BOOTSTRAP_ROUTE_CHECKER_SELF_TEST_CASE_COUNT=10")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument(
        "--workflow",
        type=Path,
        default=WORKFLOW_PATH,
        help="path to .github/workflows/zigux-bootstrap.yml",
    )
    parser.add_argument(
        "--closure-note",
        type=Path,
        default=CLOSURE_NOTE_PATH,
        help="path to Documentation/zigux/phase10-closure-evidence.md",
    )
    parser.add_argument(
        "--makefile",
        type=Path,
        default=MAKEFILE_PATH,
        help="path to zigux/Makefile",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    check_workflow(args.workflow.read_text(encoding="utf-8"))
    check_makefile(args.makefile.read_text(encoding="utf-8"))
    check_note(args.closure_note.read_text(encoding="utf-8"))
    print("PHASE10_BOOTSTRAP_ROUTE_CHECK=pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
