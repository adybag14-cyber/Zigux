#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path


WORKFLOW_PATH = Path(".github/workflows/zigux-bootstrap-split-helper.yml")

WORKFLOW_NAME = "name: zigux-bootstrap-split-helper"
PUSH_BRANCH = "    branches: [ master ]"
SCRIPTS_PATH = "      - 'scripts/zigux/**'"
THIRD_PARTY_PATH = "      - 'third_party/**'"
WORKFLOW_PATH_FILTER = "      - '.github/workflows/zigux-bootstrap-split-helper.yml'"
WORKFLOW_DISPATCH = "  workflow_dispatch:"
CONCURRENCY_GROUP = "  group: ${{ github.workflow }}-${{ github.ref }}"
CANCEL_IN_PROGRESS = "  cancel-in-progress: true"
JOB_NAME = "  split-helper:"
CHECKOUT_STEP = "      - name: Checkout"
PYTHON_STEP = "      - name: Setup Python"
COMPILE_STEP = "      - name: Compile current split-helper packet scripts"
COMPILE_CMD = (
    "        run: python3 -m py_compile scripts/zigux/split-pinned-zig-archive.py "
    "scripts/zigux/check-lane05-split-helper-selftest.py "
    "scripts/zigux/check-lane05-split-helper-workflow.py"
)
HELPER_SELF_TEST_STEP = "      - name: Self-test current split pinned Zig archive helper"
HELPER_SELF_TEST_CMD = "        run: python3 scripts/zigux/split-pinned-zig-archive.py --self-test"
SELFTEST_CHECKER_STEP = "      - name: Self-test current Lane 05 split helper selftest checker"
SELFTEST_CHECKER_CMD = (
    "        run: python3 scripts/zigux/check-lane05-split-helper-selftest.py --self-test"
)
WORKFLOW_CHECKER_SELF_TEST_STEP = "      - name: Self-test current Lane 05 split-helper workflow checker"
WORKFLOW_CHECKER_SELF_TEST_CMD = (
    "        run: python3 scripts/zigux/check-lane05-split-helper-workflow.py --self-test"
)
SELFTEST_PACKET_STEP = "      - name: Check current Lane 05 split helper selftest packet"
SELFTEST_PACKET_CMD = "        run: python3 scripts/zigux/check-lane05-split-helper-selftest.py"
WORKFLOW_PACKET_STEP = "      - name: Check current Lane 05 split-helper workflow packet"
WORKFLOW_PACKET_CMD = "        run: python3 scripts/zigux/check-lane05-split-helper-workflow.py"


def require_marker(text: str, marker: str, label: str) -> None:
    if marker not in text:
        raise SystemExit(f"lane05 split-helper workflow checker missing {label}: {marker}")


def require_exact_count(text: str, marker: str, expected: int, label: str) -> None:
    actual = text.count(marker)
    if actual != expected:
        raise SystemExit(
            f"lane05 split-helper workflow checker expected exactly {expected} occurrences "
            f"of {label} `{marker}`, found {actual}"
        )


def require_exact_line_count(text: str, marker: str, expected: int, label: str) -> None:
    actual = sum(1 for line in text.splitlines() if line == marker)
    if actual != expected:
        raise SystemExit(
            f"lane05 split-helper workflow checker expected exactly {expected} occurrences "
            f"of {label} `{marker}`, found {actual}"
        )


def require_order(text: str, earlier: str, later: str, label: str) -> None:
    earlier_index = text.find(earlier)
    later_index = text.find(later)
    if earlier_index == -1 or later_index == -1:
        raise SystemExit(
            f"lane05 split-helper workflow checker missing ordered markers for {label}"
        )
    if earlier_index >= later_index:
        raise SystemExit(
            f"lane05 split-helper workflow checker expected {label} `{earlier}` before `{later}`"
        )


def check_workflow(text: str) -> int:
    required_markers = (
        WORKFLOW_NAME,
        PUSH_BRANCH,
        SCRIPTS_PATH,
        THIRD_PARTY_PATH,
        WORKFLOW_PATH_FILTER,
        WORKFLOW_DISPATCH,
        CONCURRENCY_GROUP,
        CANCEL_IN_PROGRESS,
        JOB_NAME,
        CHECKOUT_STEP,
        PYTHON_STEP,
        COMPILE_STEP,
        COMPILE_CMD,
        HELPER_SELF_TEST_STEP,
        HELPER_SELF_TEST_CMD,
        SELFTEST_CHECKER_STEP,
        SELFTEST_CHECKER_CMD,
        WORKFLOW_CHECKER_SELF_TEST_STEP,
        WORKFLOW_CHECKER_SELF_TEST_CMD,
        SELFTEST_PACKET_STEP,
        SELFTEST_PACKET_CMD,
        WORKFLOW_PACKET_STEP,
        WORKFLOW_PACKET_CMD,
    )
    for marker in required_markers:
        require_marker(text, marker, "workflow marker")

    exact_once_markers = (
        WORKFLOW_NAME,
        WORKFLOW_DISPATCH,
        CONCURRENCY_GROUP,
        CANCEL_IN_PROGRESS,
        JOB_NAME,
        CHECKOUT_STEP,
        PYTHON_STEP,
        COMPILE_STEP,
        HELPER_SELF_TEST_STEP,
        SELFTEST_CHECKER_STEP,
        WORKFLOW_CHECKER_SELF_TEST_STEP,
        SELFTEST_PACKET_STEP,
        WORKFLOW_PACKET_STEP,
    )
    for marker in exact_once_markers:
        require_exact_count(text, marker, 1, "workflow marker")

    exact_once_lines = (
        COMPILE_CMD,
        HELPER_SELF_TEST_CMD,
        SELFTEST_CHECKER_CMD,
        WORKFLOW_CHECKER_SELF_TEST_CMD,
        SELFTEST_PACKET_CMD,
        WORKFLOW_PACKET_CMD,
    )
    for marker in exact_once_lines:
        require_exact_line_count(text, marker, 1, "workflow run line")

    require_order(text, SCRIPTS_PATH, THIRD_PARTY_PATH, "pull_request path order")
    require_order(text, THIRD_PARTY_PATH, WORKFLOW_PATH_FILTER, "pull_request path order")
    require_order(text, CHECKOUT_STEP, PYTHON_STEP, "step order")
    require_order(text, PYTHON_STEP, COMPILE_STEP, "step order")
    require_order(text, COMPILE_STEP, HELPER_SELF_TEST_STEP, "step order")
    require_order(text, HELPER_SELF_TEST_STEP, SELFTEST_CHECKER_STEP, "step order")
    require_order(text, SELFTEST_CHECKER_STEP, WORKFLOW_CHECKER_SELF_TEST_STEP, "step order")
    require_order(text, WORKFLOW_CHECKER_SELF_TEST_STEP, SELFTEST_PACKET_STEP, "step order")
    require_order(text, SELFTEST_PACKET_STEP, WORKFLOW_PACKET_STEP, "step order")

    return len(required_markers)


def run_self_test() -> int:
    good_workflow = """name: zigux-bootstrap-split-helper

on:
  push:
    branches: [ master ]
  pull_request:
    paths:
      - 'scripts/zigux/**'
      - 'third_party/**'
      - '.github/workflows/zigux-bootstrap-split-helper.yml'
  workflow_dispatch:

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

jobs:
  split-helper:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v6.0.2
        with:
          fetch-depth: 1

      - name: Setup Python
        uses: actions/setup-python@v6.2.0
        with:
          python-version: '3.x'

      - name: Compile current split-helper packet scripts
        run: python3 -m py_compile scripts/zigux/split-pinned-zig-archive.py scripts/zigux/check-lane05-split-helper-selftest.py scripts/zigux/check-lane05-split-helper-workflow.py

      - name: Self-test current split pinned Zig archive helper
        run: python3 scripts/zigux/split-pinned-zig-archive.py --self-test

      - name: Self-test current Lane 05 split helper selftest checker
        run: python3 scripts/zigux/check-lane05-split-helper-selftest.py --self-test

      - name: Self-test current Lane 05 split-helper workflow checker
        run: python3 scripts/zigux/check-lane05-split-helper-workflow.py --self-test

      - name: Check current Lane 05 split helper selftest packet
        run: python3 scripts/zigux/check-lane05-split-helper-selftest.py

      - name: Check current Lane 05 split-helper workflow packet
        run: python3 scripts/zigux/check-lane05-split-helper-workflow.py
"""
    check_workflow(good_workflow)
    case_count = 1

    cases = (
        (
            good_workflow.replace(
                " scripts/zigux/check-lane05-split-helper-workflow.py", "", 1
            ),
            "check-lane05-split-helper-workflow.py",
        ),
        (
            good_workflow.replace(
                WORKFLOW_CHECKER_SELF_TEST_STEP + "\n" + WORKFLOW_CHECKER_SELF_TEST_CMD + "\n\n",
                "",
                1,
            ),
            WORKFLOW_CHECKER_SELF_TEST_STEP,
        ),
        (
            good_workflow.replace(
                WORKFLOW_PACKET_STEP + "\n" + WORKFLOW_PACKET_CMD + "\n",
                "",
                1,
            ),
            WORKFLOW_PACKET_STEP,
        ),
        (
            good_workflow.replace("  cancel-in-progress: true", "", 1),
            CANCEL_IN_PROGRESS,
        ),
        (
            good_workflow.replace(
                "      - 'third_party/**'\n      - '.github/workflows/zigux-bootstrap-split-helper.yml'",
                "      - '.github/workflows/zigux-bootstrap-split-helper.yml'\n      - 'third_party/**'",
                1,
            ),
            "pull_request path order",
        ),
        (
            good_workflow.replace(
                "      - name: Self-test current Lane 05 split helper selftest checker\n"
                "        run: python3 scripts/zigux/check-lane05-split-helper-selftest.py --self-test\n\n"
                "      - name: Self-test current Lane 05 split-helper workflow checker\n"
                "        run: python3 scripts/zigux/check-lane05-split-helper-workflow.py --self-test\n",
                "      - name: Self-test current Lane 05 split-helper workflow checker\n"
                "        run: python3 scripts/zigux/check-lane05-split-helper-workflow.py --self-test\n\n"
                "      - name: Self-test current Lane 05 split helper selftest checker\n"
                "        run: python3 scripts/zigux/check-lane05-split-helper-selftest.py --self-test\n",
                1,
            ),
            "step order",
        ),
    )

    for candidate, expected_substring in cases:
        try:
            check_workflow(candidate)
        except SystemExit as exc:
            assert expected_substring in str(exc), str(exc)
            case_count += 1
        else:
            raise AssertionError(f"expected failure for {expected_substring}")

    print("LANE05_SPLIT_HELPER_WORKFLOW_SELF_TEST=pass")
    print(f"LANE05_SPLIT_HELPER_WORKFLOW_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the Lane 05 split-helper workflow keeps its checker-backed contract explicit."
    )
    parser.add_argument("--self-test", action="store_true", help="Run built-in checker coverage")
    parser.add_argument(
        "--workflow",
        type=Path,
        default=WORKFLOW_PATH,
        help="Path to .github/workflows/zigux-bootstrap-split-helper.yml",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    check_workflow(args.workflow.read_text(encoding="utf-8"))
    print("LANE05_SPLIT_HELPER_WORKFLOW=pass")
    print("LANE05_SPLIT_HELPER_WORKFLOW_STEP_COUNT=8")
    print("LANE05_SPLIT_HELPER_WORKFLOW_MARKER_COUNT=23")
    return 0


if __name__ == "__main__":
    sys.exit(main())
