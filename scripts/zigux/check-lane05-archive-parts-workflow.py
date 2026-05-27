#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path


WORKFLOW_PATH = Path(".github/workflows/zigux-bootstrap-archive-parts-packet.yml")

WORKFLOW_NAME = "name: zigux-bootstrap-archive-parts-packet"
PUSH_BRANCH = "branches: [ master ]"
CHECKER_PATH = "- 'scripts/zigux/check-lane05-archive-parts-packet.py'"
WORKFLOW_CHECKER_PATH = "- 'scripts/zigux/check-lane05-archive-parts-workflow.py'"
POLICY_PATH = "- 'scripts/zigux/zig-toolchain-policy.json'"
THIRD_PARTY_PATH = "- 'third_party/**'"
WORKFLOW_PATH_FILTER = "- '.github/workflows/zigux-bootstrap-archive-parts-packet.yml'"
CHECKOUT_STEP = "- name: Checkout"
PYTHON_STEP = "- name: Setup Python"
PACKET_CHECKER_SELF_TEST_STEP = "- name: Self-test current Lane 05 archive parts packet checker"
PACKET_CHECKER_SELF_TEST_CMD = (
    "python3 scripts/zigux/check-lane05-archive-parts-packet.py --self-test"
)
WORKFLOW_CHECKER_SELF_TEST_STEP = (
    "- name: Self-test current Lane 05 archive parts workflow checker"
)
WORKFLOW_CHECKER_SELF_TEST_CMD = (
    "python3 scripts/zigux/check-lane05-archive-parts-workflow.py --self-test"
)
WORKFLOW_CHECKER_STEP = "- name: Check current Lane 05 archive parts workflow packet"
WORKFLOW_CHECKER_CMD = "python3 scripts/zigux/check-lane05-archive-parts-workflow.py"
PACKET_CHECKER_STEP = "- name: Check current Lane 05 archive parts packet"
PACKET_CHECKER_CMD = (
    "python3 scripts/zigux/check-lane05-archive-parts-packet.py --allow-missing"
)


def require_marker(text: str, marker: str, label: str) -> None:
    if marker not in text:
        raise SystemExit(f"lane05 archive-parts workflow checker missing {label}: {marker}")


def require_exact_line(text: str, line: str, label: str) -> None:
    count = sum(1 for current in text.splitlines() if current.strip() == line)
    if count != 1:
        raise SystemExit(
            "lane05 archive-parts workflow checker expected exactly "
            f"1 {label} line `{line}`, found {count}"
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
    for marker, label in (
        (WORKFLOW_NAME, "workflow name"),
        (PUSH_BRANCH, "master push trigger"),
        (CHECKER_PATH, "archive-parts checker path filter"),
        (WORKFLOW_CHECKER_PATH, "workflow-checker path filter"),
        (POLICY_PATH, "policy path filter"),
        (THIRD_PARTY_PATH, "third-party path filter"),
        (WORKFLOW_PATH_FILTER, "workflow path filter"),
        (CHECKOUT_STEP, "checkout step"),
        (PYTHON_STEP, "python setup step"),
        (PACKET_CHECKER_SELF_TEST_STEP, "packet checker self-test step"),
        (PACKET_CHECKER_SELF_TEST_CMD, "packet checker self-test command"),
        (WORKFLOW_CHECKER_SELF_TEST_STEP, "workflow checker self-test step"),
        (WORKFLOW_CHECKER_SELF_TEST_CMD, "workflow checker self-test command"),
        (WORKFLOW_CHECKER_STEP, "workflow checker step"),
        (WORKFLOW_CHECKER_CMD, "workflow checker command"),
        (PACKET_CHECKER_STEP, "packet checker step"),
        (PACKET_CHECKER_CMD, "packet checker command"),
    ):
        require_marker(text, marker, label)

    for line, label in (
        (PUSH_BRANCH, "master push trigger"),
        (CHECKER_PATH, "archive-parts checker path filter"),
        (WORKFLOW_CHECKER_PATH, "workflow-checker path filter"),
        (POLICY_PATH, "policy path filter"),
        (THIRD_PARTY_PATH, "third-party path filter"),
        (WORKFLOW_PATH_FILTER, "workflow path filter"),
        (f"run: {PACKET_CHECKER_SELF_TEST_CMD}", "packet checker self-test command"),
        (f"run: {WORKFLOW_CHECKER_SELF_TEST_CMD}", "workflow checker self-test command"),
        (f"run: {WORKFLOW_CHECKER_CMD}", "workflow checker command"),
        (f"run: {PACKET_CHECKER_CMD}", "packet checker command"),
    ):
        require_exact_line(text, line, label)

    for line, label in (
        (CHECKOUT_STEP, "checkout step"),
        (PYTHON_STEP, "python setup step"),
        (PACKET_CHECKER_SELF_TEST_STEP, "packet checker self-test step"),
        (WORKFLOW_CHECKER_SELF_TEST_STEP, "workflow checker self-test step"),
        (WORKFLOW_CHECKER_STEP, "workflow checker step"),
        (PACKET_CHECKER_STEP, "packet checker step"),
    ):
        require_exact_line(text, line, label)

    require_order(text, CHECKER_PATH, WORKFLOW_CHECKER_PATH, "pull_request path order")
    require_order(text, WORKFLOW_CHECKER_PATH, POLICY_PATH, "pull_request path order")
    require_order(text, POLICY_PATH, THIRD_PARTY_PATH, "pull_request path order")
    require_order(text, THIRD_PARTY_PATH, WORKFLOW_PATH_FILTER, "pull_request path order")
    require_order(text, CHECKOUT_STEP, PYTHON_STEP, "step order")
    require_order(text, PYTHON_STEP, PACKET_CHECKER_SELF_TEST_STEP, "step order")
    require_order(
        text,
        PACKET_CHECKER_SELF_TEST_STEP,
        WORKFLOW_CHECKER_SELF_TEST_STEP,
        "step order",
    )
    require_order(
        text,
        WORKFLOW_CHECKER_SELF_TEST_STEP,
        WORKFLOW_CHECKER_STEP,
        "step order",
    )
    require_order(text, WORKFLOW_CHECKER_STEP, PACKET_CHECKER_STEP, "step order")


def run_self_test() -> int:
    good_workflow = """name: zigux-bootstrap-archive-parts-packet

on:
  push:
    branches: [ master ]
  pull_request:
    paths:
      - 'scripts/zigux/check-lane05-archive-parts-packet.py'
      - 'scripts/zigux/check-lane05-archive-parts-workflow.py'
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
        with:
          fetch-depth: 1

      - name: Setup Python
        uses: actions/setup-python@v6.2.0
        with:
          python-version: '3.x'

      - name: Self-test current Lane 05 archive parts packet checker
        run: python3 scripts/zigux/check-lane05-archive-parts-packet.py --self-test

      - name: Self-test current Lane 05 archive parts workflow checker
        run: python3 scripts/zigux/check-lane05-archive-parts-workflow.py --self-test

      - name: Check current Lane 05 archive parts workflow packet
        run: python3 scripts/zigux/check-lane05-archive-parts-workflow.py

      - name: Check current Lane 05 archive parts packet
        run: python3 scripts/zigux/check-lane05-archive-parts-packet.py --allow-missing
"""
    check_workflow(good_workflow)
    case_count = 1

    for broken_text, expected in (
        (
            good_workflow.replace(
                "      - name: Self-test current Lane 05 archive parts workflow checker\n"
                "        run: python3 scripts/zigux/check-lane05-archive-parts-workflow.py --self-test\n",
                "",
                1,
            ),
            WORKFLOW_CHECKER_SELF_TEST_STEP,
        ),
        (
            good_workflow.replace(
                "      - name: Check current Lane 05 archive parts workflow packet\n"
                "        run: python3 scripts/zigux/check-lane05-archive-parts-workflow.py\n",
                "",
                1,
            ),
            WORKFLOW_CHECKER_STEP,
        ),
        (
            good_workflow.replace(
                "- 'scripts/zigux/check-lane05-archive-parts-workflow.py'\n",
                "",
                1,
            ),
            WORKFLOW_CHECKER_PATH,
        ),
        (
            good_workflow.replace(
                "run: python3 scripts/zigux/check-lane05-archive-parts-packet.py --allow-missing",
                "run: python3 scripts/zigux/check-lane05-archive-parts-packet.py",
                1,
            ),
            PACKET_CHECKER_CMD,
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
        "      - name: Check current Lane 05 archive parts workflow packet\n"
        "        run: python3 scripts/zigux/check-lane05-archive-parts-workflow.py\n\n"
        "      - name: Check current Lane 05 archive parts packet\n"
        "        run: python3 scripts/zigux/check-lane05-archive-parts-packet.py --allow-missing\n",
        "      - name: Check current Lane 05 archive parts packet\n"
        "        run: python3 scripts/zigux/check-lane05-archive-parts-packet.py --allow-missing\n\n"
        "      - name: Check current Lane 05 archive parts workflow packet\n"
        "        run: python3 scripts/zigux/check-lane05-archive-parts-workflow.py\n",
        1,
    )
    try:
        check_workflow(reordered_steps)
    except SystemExit as exc:
        assert "step order" in str(exc), str(exc)
        case_count += 1
    else:
        raise AssertionError("expected reordered step failure")

    duplicate_step = good_workflow.replace(
        "      - name: Check current Lane 05 archive parts workflow packet\n",
        "      - name: Check current Lane 05 archive parts workflow packet\n"
        "      - name: Check current Lane 05 archive parts workflow packet\n",
        1,
    )
    try:
        check_workflow(duplicate_step)
    except SystemExit as exc:
        assert WORKFLOW_CHECKER_STEP in str(exc), str(exc)
        case_count += 1
    else:
        raise AssertionError("expected duplicate workflow checker step failure")

    print("LANE05_ARCHIVE_PARTS_WORKFLOW_SELF_TEST=pass")
    print(f"LANE05_ARCHIVE_PARTS_WORKFLOW_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the Lane 05 archive-parts workflow keeps its expected guard steps."
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
