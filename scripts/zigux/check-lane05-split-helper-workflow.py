#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path


WORKFLOW_PATH = Path(".github/workflows/zigux-bootstrap-split-helper.yml")

WORKFLOW_NAME = "name: zigux-bootstrap-split-helper"
PUSH_BRANCH = "branches: [ master ]"
SCRIPTS_PATH = "- 'scripts/zigux/**'"
THIRD_PARTY_PATH = "- 'third_party/**'"
WORKFLOW_PATH_FILTER = "- '.github/workflows/zigux-bootstrap-split-helper.yml'"
PYTHON_STEP = "- name: Setup Python"
COMPILE_STEP = "- name: Compile current split-helper packet scripts"
COMPILE_CMD = (
    "python3 -m py_compile "
    "scripts/zigux/split-pinned-zig-archive.py "
    "scripts/zigux/check-lane05-split-helper-selftest.py "
    "scripts/zigux/check-lane05-split-helper-workflow.py "
    "scripts/zigux/check-lane05-split-helper-archive-packet-contract.py"
)
HELPER_SELF_TEST_STEP = "- name: Self-test current split pinned Zig archive helper"
HELPER_SELF_TEST_CMD = "python3 scripts/zigux/split-pinned-zig-archive.py --self-test"
SELFTEST_CHECKER_STEP = "- name: Self-test current Lane 05 split helper selftest checker"
SELFTEST_CHECKER_CMD = "python3 scripts/zigux/check-lane05-split-helper-selftest.py --self-test"
CONTRACT_CHECKER_SELF_TEST_STEP = "- name: Self-test current Lane 05 split helper archive-packet contract checker"
CONTRACT_CHECKER_SELF_TEST_CMD = (
    "python3 scripts/zigux/check-lane05-split-helper-archive-packet-contract.py --self-test"
)
CONTRACT_CHECKER_STEP = "- name: Check current Lane 05 split helper archive-packet contract"
CONTRACT_CHECKER_CMD = "python3 scripts/zigux/check-lane05-split-helper-archive-packet-contract.py"
WORKFLOW_CHECKER_SELF_TEST_STEP = "- name: Self-test current Lane 05 split-helper workflow checker"
WORKFLOW_CHECKER_SELF_TEST_CMD = "python3 scripts/zigux/check-lane05-split-helper-workflow.py --self-test"
WORKFLOW_CHECKER_STEP = "- name: Check current Lane 05 split-helper workflow packet"
WORKFLOW_CHECKER_CMD = "python3 scripts/zigux/check-lane05-split-helper-workflow.py"


def require_marker(text: str, marker: str, label: str) -> None:
    if marker not in text:
        raise SystemExit(f"lane05 split-helper workflow checker missing {label}: {marker}")


def require_exact_line(text: str, line: str, label: str) -> None:
    count = sum(1 for current in text.splitlines() if current.strip() == line)
    if count != 1:
        raise SystemExit(
            "lane05 split-helper workflow checker expected exactly "
            f"1 {label} line `{line}`, found {count}"
        )


def require_order(text: str, earlier: str, later: str, label: str) -> None:
    earlier_index = text.find(earlier)
    later_index = text.find(later)
    if earlier_index == -1 or later_index == -1:
        raise SystemExit(f"lane05 split-helper workflow checker missing ordered markers for {label}")
    if earlier_index >= later_index:
        raise SystemExit(
            "lane05 split-helper workflow checker expected "
            f"{label} `{earlier}` before `{later}`"
        )


def check_workflow(text: str) -> None:
    for marker, label in (
        (WORKFLOW_NAME, "workflow name"),
        (PUSH_BRANCH, "master push trigger"),
        (SCRIPTS_PATH, "scripts path filter"),
        (THIRD_PARTY_PATH, "third-party path filter"),
        (WORKFLOW_PATH_FILTER, "workflow path filter"),
        (PYTHON_STEP, "python setup step"),
        (COMPILE_STEP, "compile step"),
        (COMPILE_CMD, "compile command"),
        (HELPER_SELF_TEST_STEP, "helper self-test step"),
        (HELPER_SELF_TEST_CMD, "helper self-test command"),
        (SELFTEST_CHECKER_STEP, "selftest checker step"),
        (SELFTEST_CHECKER_CMD, "selftest checker command"),
        (CONTRACT_CHECKER_SELF_TEST_STEP, "contract checker self-test step"),
        (CONTRACT_CHECKER_SELF_TEST_CMD, "contract checker self-test command"),
        (CONTRACT_CHECKER_STEP, "contract checker step"),
        (CONTRACT_CHECKER_CMD, "contract checker command"),
        (WORKFLOW_CHECKER_SELF_TEST_STEP, "workflow checker self-test step"),
        (WORKFLOW_CHECKER_SELF_TEST_CMD, "workflow checker self-test command"),
        (WORKFLOW_CHECKER_STEP, "workflow checker step"),
        (WORKFLOW_CHECKER_CMD, "workflow checker command"),
    ):
        require_marker(text, marker, label)

    for line, label in (
        (PUSH_BRANCH, "master push trigger"),
        (SCRIPTS_PATH, "scripts path filter"),
        (THIRD_PARTY_PATH, "third-party path filter"),
        (WORKFLOW_PATH_FILTER, "workflow path filter"),
        (f"run: {COMPILE_CMD}", "compile command"),
        (f"run: {HELPER_SELF_TEST_CMD}", "helper self-test command"),
        (f"run: {SELFTEST_CHECKER_CMD}", "selftest checker command"),
        (f"run: {CONTRACT_CHECKER_SELF_TEST_CMD}", "contract checker self-test command"),
        (f"run: {CONTRACT_CHECKER_CMD}", "contract checker command"),
        (f"run: {WORKFLOW_CHECKER_SELF_TEST_CMD}", "workflow checker self-test command"),
        (f"run: {WORKFLOW_CHECKER_CMD}", "workflow checker command"),
    ):
        require_exact_line(text, line, label)

    for line, label in (
        (COMPILE_STEP, "compile step"),
        (HELPER_SELF_TEST_STEP, "helper self-test step"),
        (SELFTEST_CHECKER_STEP, "selftest checker step"),
        (CONTRACT_CHECKER_SELF_TEST_STEP, "contract checker self-test step"),
        (CONTRACT_CHECKER_STEP, "contract checker step"),
        (WORKFLOW_CHECKER_SELF_TEST_STEP, "workflow checker self-test step"),
        (WORKFLOW_CHECKER_STEP, "workflow checker step"),
    ):
        require_exact_line(text, line, label)

    require_order(text, SCRIPTS_PATH, THIRD_PARTY_PATH, "pull_request path order")
    require_order(text, THIRD_PARTY_PATH, WORKFLOW_PATH_FILTER, "pull_request path order")
    require_order(text, PYTHON_STEP, COMPILE_STEP, "step order")
    require_order(text, COMPILE_STEP, HELPER_SELF_TEST_STEP, "step order")
    require_order(text, HELPER_SELF_TEST_STEP, SELFTEST_CHECKER_STEP, "step order")
    require_order(text, SELFTEST_CHECKER_STEP, CONTRACT_CHECKER_SELF_TEST_STEP, "step order")
    require_order(text, CONTRACT_CHECKER_SELF_TEST_STEP, CONTRACT_CHECKER_STEP, "step order")
    require_order(text, CONTRACT_CHECKER_STEP, WORKFLOW_CHECKER_SELF_TEST_STEP, "step order")
    require_order(text, WORKFLOW_CHECKER_SELF_TEST_STEP, WORKFLOW_CHECKER_STEP, "step order")


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

permissions:
  contents: read

jobs:
  split-helper:
    runs-on: ubuntu-latest
    steps:
      - name: Setup Python
        uses: actions/setup-python@v6.2.0
        with:
          python-version: '3.x'

      - name: Compile current split-helper packet scripts
        run: python3 -m py_compile scripts/zigux/split-pinned-zig-archive.py scripts/zigux/check-lane05-split-helper-selftest.py scripts/zigux/check-lane05-split-helper-workflow.py scripts/zigux/check-lane05-split-helper-archive-packet-contract.py

      - name: Self-test current split pinned Zig archive helper
        run: python3 scripts/zigux/split-pinned-zig-archive.py --self-test

      - name: Self-test current Lane 05 split helper selftest checker
        run: python3 scripts/zigux/check-lane05-split-helper-selftest.py --self-test

      - name: Self-test current Lane 05 split helper archive-packet contract checker
        run: python3 scripts/zigux/check-lane05-split-helper-archive-packet-contract.py --self-test

      - name: Check current Lane 05 split helper archive-packet contract
        run: python3 scripts/zigux/check-lane05-split-helper-archive-packet-contract.py

      - name: Self-test current Lane 05 split-helper workflow checker
        run: python3 scripts/zigux/check-lane05-split-helper-workflow.py --self-test

      - name: Check current Lane 05 split-helper workflow packet
        run: python3 scripts/zigux/check-lane05-split-helper-workflow.py
"""
    check_workflow(good_workflow)
    case_count = 1

    for broken_text, expected in (
        (
            good_workflow.replace(
                "scripts/zigux/check-lane05-split-helper-archive-packet-contract.py",
                "",
                1,
            ),
            "compile command",
        ),
        (
            good_workflow.replace(
                "      - name: Self-test current Lane 05 split helper archive-packet contract checker\n"
                "        run: python3 scripts/zigux/check-lane05-split-helper-archive-packet-contract.py --self-test\n\n",
                "",
                1,
            ),
            CONTRACT_CHECKER_SELF_TEST_STEP,
        ),
        (
            good_workflow.replace(
                "      - name: Check current Lane 05 split helper archive-packet contract\n"
                "        run: python3 scripts/zigux/check-lane05-split-helper-archive-packet-contract.py\n\n",
                "",
                1,
            ),
            CONTRACT_CHECKER_STEP,
        ),
    ):
        try:
            check_workflow(broken_text)
        except SystemExit as exc:
            assert expected in str(exc), str(exc)
            case_count += 1
        else:
            raise AssertionError(f"expected failure for {expected}")

    reordered_steps = good_workflow.replace(
        "      - name: Self-test current Lane 05 split helper archive-packet contract checker\n"
        "        run: python3 scripts/zigux/check-lane05-split-helper-archive-packet-contract.py --self-test\n\n"
        "      - name: Check current Lane 05 split helper archive-packet contract\n"
        "        run: python3 scripts/zigux/check-lane05-split-helper-archive-packet-contract.py\n",
        "      - name: Check current Lane 05 split helper archive-packet contract\n"
        "        run: python3 scripts/zigux/check-lane05-split-helper-archive-packet-contract.py\n\n"
        "      - name: Self-test current Lane 05 split helper archive-packet contract checker\n"
        "        run: python3 scripts/zigux/check-lane05-split-helper-archive-packet-contract.py --self-test\n",
        1,
    )
    try:
        check_workflow(reordered_steps)
    except SystemExit as exc:
        assert "step order" in str(exc), str(exc)
        case_count += 1
    else:
        raise AssertionError("expected reordered step failure")

    print("LANE05_SPLIT_HELPER_WORKFLOW_SELF_TEST=pass")
    print(f"LANE05_SPLIT_HELPER_WORKFLOW_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the Lane 05 split-helper workflow keeps its expected guard steps."
    )
    parser.add_argument("--self-test", action="store_true")
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
    return 0


if __name__ == "__main__":
    sys.exit(main())
