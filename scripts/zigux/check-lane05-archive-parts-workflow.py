#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
WORKFLOW_PATH = Path(".github/workflows/zigux-bootstrap-archive-parts-packet.yml")

WORKFLOW_NAME = "name: zigux-bootstrap-archive-parts-packet"
PUSH_BRANCHES = "branches: [ master ]"
SCRIPT_PATH = "- 'scripts/zigux/check-lane05-archive-parts-packet.py'"
POLICY_PATH = "- 'scripts/zigux/zig-toolchain-policy.json'"
THIRD_PARTY_PATH = "- 'third_party/**'"
WORKFLOW_PATH_LINE = "- '.github/workflows/zigux-bootstrap-archive-parts-packet.yml'"
JOB_NAME = "lane05-archive-parts-packet:"
CHECKOUT_STEP = "- name: Checkout"
CHECKOUT_ACTION = "uses: actions/checkout@v6.0.2"
PYTHON_STEP = "- name: Setup Python"
PYTHON_ACTION = "uses: actions/setup-python@v6.2.0"
PYTHON_VERSION = "python-version: '3.x'"
SELF_TEST_STEP = "- name: Self-test current Lane 05 archive parts workflow checker"
SELF_TEST_CMD = "python3 scripts/zigux/check-lane05-archive-parts-workflow.py --self-test"
CHECK_STEP = "- name: Check current Lane 05 archive parts workflow packet"
CHECK_CMD = "python3 scripts/zigux/check-lane05-archive-parts-workflow.py"
PARTS_SELF_TEST_STEP = "- name: Self-test current Lane 05 archive parts packet checker"
PARTS_SELF_TEST_CMD = "python3 scripts/zigux/check-lane05-archive-parts-packet.py --self-test"
PARTS_CHECK_STEP = "- name: Check current Lane 05 archive parts packet"
PARTS_CHECK_CMD = "python3 scripts/zigux/check-lane05-archive-parts-packet.py --allow-missing"


def require_marker(text: str, marker: str, label: str) -> None:
    if marker not in text:
        raise SystemExit(f"lane05 archive-parts workflow checker missing {label}: {marker}")


def require_exact_count(text: str, marker: str, expected: int, label: str) -> None:
    actual = text.count(marker)
    if actual != expected:
        raise SystemExit(
            "lane05 archive-parts workflow checker expected exactly "
            f"{expected} occurrences of {label} {marker}, found {actual}"
        )


def require_exact_line_count(text: str, marker: str, expected: int, label: str) -> None:
    actual = sum(1 for line in text.splitlines() if line.strip() == marker)
    if actual != expected:
        raise SystemExit(
            "lane05 archive-parts workflow checker expected exactly "
            f"{expected} occurrences of {label} {marker}, found {actual}"
        )


def require_order(text: str, earlier: str, later: str, label: str) -> None:
    earlier_index = text.find(earlier)
    later_index = text.find(later)
    if earlier_index == -1 or later_index == -1:
        raise SystemExit(
            f"lane05 archive-parts workflow checker missing ordered markers for {label}"
        )
    if earlier_index >= later_index:
        raise SystemExit(
            "lane05 archive-parts workflow checker expected "
            f"{label} `{earlier}` before `{later}`"
        )


def check_workflow(text: str) -> None:
    required_markers = (
        WORKFLOW_NAME,
        PUSH_BRANCHES,
        SCRIPT_PATH,
        POLICY_PATH,
        THIRD_PARTY_PATH,
        WORKFLOW_PATH_LINE,
        JOB_NAME,
        CHECKOUT_STEP,
        CHECKOUT_ACTION,
        PYTHON_STEP,
        PYTHON_ACTION,
        PYTHON_VERSION,
        SELF_TEST_STEP,
        SELF_TEST_CMD,
        CHECK_STEP,
        CHECK_CMD,
        PARTS_SELF_TEST_STEP,
        PARTS_SELF_TEST_CMD,
        PARTS_CHECK_STEP,
        PARTS_CHECK_CMD,
    )
    for marker in required_markers:
        require_marker(text, marker, "workflow marker")

    require_exact_count(text, SELF_TEST_STEP, 1, "workflow step name")
    require_exact_line_count(text, f"run: {SELF_TEST_CMD}", 1, "workflow run line")
    require_exact_count(text, CHECK_STEP, 1, "workflow step name")
    require_exact_line_count(text, f"run: {CHECK_CMD}", 1, "workflow run line")
    require_exact_count(text, PARTS_SELF_TEST_STEP, 1, "workflow step name")
    require_exact_line_count(text, f"run: {PARTS_SELF_TEST_CMD}", 1, "workflow run line")
    require_exact_count(text, PARTS_CHECK_STEP, 1, "workflow step name")
    require_exact_line_count(text, f"run: {PARTS_CHECK_CMD}", 1, "workflow run line")
    require_exact_line_count(text, SCRIPT_PATH, 1, "workflow path filter line")
    require_exact_line_count(text, POLICY_PATH, 1, "workflow path filter line")
    require_exact_line_count(text, THIRD_PARTY_PATH, 1, "workflow path filter line")
    require_exact_line_count(text, WORKFLOW_PATH_LINE, 1, "workflow path filter line")

    require_order(text, CHECKOUT_STEP, PYTHON_STEP, "workflow step order")
    require_order(text, PYTHON_STEP, SELF_TEST_STEP, "workflow step order")
    require_order(text, SELF_TEST_STEP, CHECK_STEP, "workflow step order")
    require_order(text, CHECK_STEP, PARTS_SELF_TEST_STEP, "workflow step order")
    require_order(text, PARTS_SELF_TEST_STEP, PARTS_CHECK_STEP, "workflow step order")
    require_order(text, SCRIPT_PATH, POLICY_PATH, "workflow pull_request path order")
    require_order(text, POLICY_PATH, THIRD_PARTY_PATH, "workflow pull_request path order")
    require_order(
        text,
        THIRD_PARTY_PATH,
        WORKFLOW_PATH_LINE,
        "workflow pull_request path order",
    )


def run_self_test() -> int:
    good_workflow = """name: zigux-bootstrap-archive-parts-packet

on:
  push:
    branches: [ master ]
  pull_request:
    paths:
      - 'scripts/zigux/check-lane05-archive-parts-packet.py'
      - 'scripts/zigux/zig-toolchain-policy.json'
      - 'third_party/**'
      - '.github/workflows/zigux-bootstrap-archive-parts-packet.yml'
  workflow_dispatch:

jobs:
  lane05-archive-parts-packet:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v6.0.2
      - name: Setup Python
        uses: actions/setup-python@v6.2.0
        with:
          python-version: '3.x'
      - name: Self-test current Lane 05 archive parts workflow checker
        run: python3 scripts/zigux/check-lane05-archive-parts-workflow.py --self-test
      - name: Check current Lane 05 archive parts workflow packet
        run: python3 scripts/zigux/check-lane05-archive-parts-workflow.py
      - name: Self-test current Lane 05 archive parts packet checker
        run: python3 scripts/zigux/check-lane05-archive-parts-packet.py --self-test
      - name: Check current Lane 05 archive parts packet
        run: python3 scripts/zigux/check-lane05-archive-parts-packet.py --allow-missing
"""
    check_workflow(good_workflow)
    case_count = 1

    missing_self_test_step = good_workflow.replace(
        f"      {SELF_TEST_STEP}\n        run: {SELF_TEST_CMD}\n",
        "",
        1,
    )
    try:
        check_workflow(missing_self_test_step)
    except SystemExit as exc:
        assert SELF_TEST_STEP in str(exc) or SELF_TEST_CMD in str(exc)
        case_count += 1
    else:
        raise AssertionError("expected missing workflow self-test step failure")

    missing_check_step = good_workflow.replace(
        f"      {CHECK_STEP}\n        run: {CHECK_CMD}\n",
        "",
        1,
    )
    try:
        check_workflow(missing_check_step)
    except SystemExit as exc:
        assert CHECK_STEP in str(exc) or CHECK_CMD in str(exc)
        case_count += 1
    else:
        raise AssertionError("expected missing workflow check step failure")

    missing_parts_check_cmd = good_workflow.replace(
        PARTS_CHECK_CMD,
        "python3 scripts/zigux/check-lane05-archive-parts-packet.py",
        1,
    )
    try:
        check_workflow(missing_parts_check_cmd)
    except SystemExit as exc:
        assert PARTS_CHECK_CMD in str(exc)
        case_count += 1
    else:
        raise AssertionError("expected missing allow-missing packet command failure")

    duplicate_third_party_path = good_workflow.replace(
        f"      {THIRD_PARTY_PATH}\n",
        f"      {THIRD_PARTY_PATH}\n      {THIRD_PARTY_PATH}\n",
        1,
    )
    try:
        check_workflow(duplicate_third_party_path)
    except SystemExit as exc:
        assert THIRD_PARTY_PATH in str(exc)
        case_count += 1
    else:
        raise AssertionError("expected duplicate path filter failure")

    reordered_steps = good_workflow.replace(
        f"      {SELF_TEST_STEP}\n        run: {SELF_TEST_CMD}\n"
        f"      {CHECK_STEP}\n        run: {CHECK_CMD}\n"
        f"      {PARTS_SELF_TEST_STEP}\n        run: {PARTS_SELF_TEST_CMD}\n",
        f"      {PARTS_SELF_TEST_STEP}\n        run: {PARTS_SELF_TEST_CMD}\n"
        f"      {SELF_TEST_STEP}\n        run: {SELF_TEST_CMD}\n"
        f"      {CHECK_STEP}\n        run: {CHECK_CMD}\n",
        1,
    )
    try:
        check_workflow(reordered_steps)
    except SystemExit as exc:
        assert "workflow step order" in str(exc)
        case_count += 1
    else:
        raise AssertionError("expected reordered step failure")

    print("LANE05_ARCHIVE_PARTS_WORKFLOW_SELF_TEST=pass")
    print(f"LANE05_ARCHIVE_PARTS_WORKFLOW_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the dedicated Lane 05 archive-parts workflow keeps its packet explicit."
    )
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument(
        "--workflow",
        type=Path,
        default=WORKFLOW_PATH,
        help="Path to .github/workflows/zigux-bootstrap-archive-parts-packet.yml",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    check_workflow(args.workflow.read_text(encoding="utf-8"))
    print("LANE05_ARCHIVE_PARTS_WORKFLOW=pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
