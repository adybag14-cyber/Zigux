#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path


WORKFLOW_PATH = Path(".github/workflows/zigux-bootstrap.yml")

ARCHIVE_CHECK_STEP = "- name: Check current pinned Zig archive packet"
ARCHIVE_CHECK_CMD = "python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing"
INSTALL_SELF_TEST_STEP = "- name: Self-test current Zig installer helper"
INSTALL_SELF_TEST_CMD = "python3 scripts/zigux/install-zig.py --self-test"
STAGE_HELPER_SELF_TEST_STEP = "- name: Self-test current staged pinned Zig archive helper"
STAGE_HELPER_SELF_TEST_CMD = "python3 scripts/zigux/stage-pinned-zig-archive.py --self-test"
CONTRACT_SELF_TEST_STEP = "- name: Self-test current Lane 05 stage helper contract checker"
CONTRACT_SELF_TEST_CMD = "python3 scripts/zigux/check-lane05-stage-helper-contract.py --self-test"
CONTRACT_CHECK_STEP = "- name: Check current Lane 05 stage helper contract packet"
CONTRACT_CHECK_CMD = "python3 scripts/zigux/check-lane05-stage-helper-contract.py"
SELFTEST_CHECKER_STEP = "- name: Self-test current Lane 05 stage helper selftest checker"
SELFTEST_CHECKER_CMD = "python3 scripts/zigux/check-lane05-stage-helper-selftest.py --self-test"
SELFTEST_PACKET_STEP = "- name: Check current Lane 05 stage helper selftest packet"
SELFTEST_PACKET_CMD = "python3 scripts/zigux/check-lane05-stage-helper-selftest.py"
WORKFLOW_CHECKER_SELF_TEST_STEP = "- name: Self-test current Lane 05 stage-helper workflow checker"
WORKFLOW_CHECKER_SELF_TEST_CMD = (
    "python3 scripts/zigux/check-lane05-stage-helper-workflow.py --self-test"
)
WORKFLOW_CHECKER_STEP = "- name: Check current Lane 05 stage-helper workflow packet"
WORKFLOW_CHECKER_CMD = "python3 scripts/zigux/check-lane05-stage-helper-workflow.py"
NEXT_STEP = "- name: Self-test current Phase 2 fixdep gate checker"


def require_marker(text: str, marker: str, label: str) -> None:
    if marker not in text:
        raise SystemExit(f"lane05 stage-helper workflow checker missing {label}: {marker}")


def require_exact_line(text: str, line: str, label: str) -> None:
    count = sum(1 for current in text.splitlines() if current.strip() == line)
    if count != 1:
        raise SystemExit(
            "lane05 stage-helper workflow checker expected exactly "
            f"1 {label} line `{line}`, found {count}"
        )


def require_order(text: str, earlier: str, later: str, label: str) -> None:
    earlier_index = text.find(earlier)
    later_index = text.find(later)
    if earlier_index == -1 or later_index == -1:
        raise SystemExit(
            f"lane05 stage-helper workflow checker missing ordered markers for {label}"
        )
    if earlier_index >= later_index:
        raise SystemExit(
            "lane05 stage-helper workflow checker expected "
            f"{label} `{earlier}` before `{later}`"
        )


def check_workflow(text: str) -> None:
    for marker, label in (
        (ARCHIVE_CHECK_STEP, "archive check step"),
        (ARCHIVE_CHECK_CMD, "archive check command"),
        (INSTALL_SELF_TEST_STEP, "installer self-test step"),
        (INSTALL_SELF_TEST_CMD, "installer self-test command"),
        (STAGE_HELPER_SELF_TEST_STEP, "stage helper self-test step"),
        (STAGE_HELPER_SELF_TEST_CMD, "stage helper self-test command"),
        (CONTRACT_SELF_TEST_STEP, "stage helper contract self-test step"),
        (CONTRACT_SELF_TEST_CMD, "stage helper contract self-test command"),
        (CONTRACT_CHECK_STEP, "stage helper contract check step"),
        (CONTRACT_CHECK_CMD, "stage helper contract check command"),
        (SELFTEST_CHECKER_STEP, "stage helper selftest checker step"),
        (SELFTEST_CHECKER_CMD, "stage helper selftest checker command"),
        (SELFTEST_PACKET_STEP, "stage helper selftest packet step"),
        (SELFTEST_PACKET_CMD, "stage helper selftest packet command"),
        (WORKFLOW_CHECKER_SELF_TEST_STEP, "workflow checker self-test step"),
        (WORKFLOW_CHECKER_SELF_TEST_CMD, "workflow checker self-test command"),
        (WORKFLOW_CHECKER_STEP, "workflow checker step"),
        (WORKFLOW_CHECKER_CMD, "workflow checker command"),
        (NEXT_STEP, "next phase anchor"),
    ):
        require_marker(text, marker, label)

    for line, label in (
        (f"run: {ARCHIVE_CHECK_CMD}", "archive check command"),
        (f"run: {INSTALL_SELF_TEST_CMD}", "installer self-test command"),
        (f"run: {STAGE_HELPER_SELF_TEST_CMD}", "stage helper self-test command"),
        (f"run: {CONTRACT_SELF_TEST_CMD}", "contract self-test command"),
        (f"run: {CONTRACT_CHECK_CMD}", "contract check command"),
        (f"run: {SELFTEST_CHECKER_CMD}", "stage helper selftest checker command"),
        (f"run: {SELFTEST_PACKET_CMD}", "stage helper selftest packet command"),
        (f"run: {WORKFLOW_CHECKER_SELF_TEST_CMD}", "workflow checker self-test command"),
        (f"run: {WORKFLOW_CHECKER_CMD}", "workflow checker command"),
    ):
        require_exact_line(text, line, label)

    for step, label in (
        (STAGE_HELPER_SELF_TEST_STEP, "stage helper self-test step"),
        (CONTRACT_SELF_TEST_STEP, "contract self-test step"),
        (CONTRACT_CHECK_STEP, "contract check step"),
        (SELFTEST_CHECKER_STEP, "stage helper selftest checker step"),
        (SELFTEST_PACKET_STEP, "stage helper selftest packet step"),
        (WORKFLOW_CHECKER_SELF_TEST_STEP, "workflow checker self-test step"),
        (WORKFLOW_CHECKER_STEP, "workflow checker step"),
    ):
        require_exact_line(text, step, label)

    require_order(text, ARCHIVE_CHECK_STEP, INSTALL_SELF_TEST_STEP, "lane05 anchor order")
    require_order(text, INSTALL_SELF_TEST_STEP, STAGE_HELPER_SELF_TEST_STEP, "lane05 step order")
    require_order(text, STAGE_HELPER_SELF_TEST_STEP, CONTRACT_SELF_TEST_STEP, "lane05 step order")
    require_order(text, CONTRACT_SELF_TEST_STEP, CONTRACT_CHECK_STEP, "lane05 step order")
    require_order(text, CONTRACT_CHECK_STEP, SELFTEST_CHECKER_STEP, "lane05 step order")
    require_order(text, SELFTEST_CHECKER_STEP, SELFTEST_PACKET_STEP, "lane05 step order")
    require_order(
        text,
        SELFTEST_PACKET_STEP,
        WORKFLOW_CHECKER_SELF_TEST_STEP,
        "lane05 step order",
    )
    require_order(
        text,
        WORKFLOW_CHECKER_SELF_TEST_STEP,
        WORKFLOW_CHECKER_STEP,
        "lane05 step order",
    )
    require_order(text, WORKFLOW_CHECKER_STEP, NEXT_STEP, "lane05 step order")


def run_self_test() -> int:
    good_workflow = """name: zigux-bootstrap
jobs:
  bootstrap:
    steps:
      - name: Check current pinned Zig archive packet
        run: python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing
      - name: Self-test current Zig installer helper
        run: python3 scripts/zigux/install-zig.py --self-test
      - name: Self-test current staged pinned Zig archive helper
        run: python3 scripts/zigux/stage-pinned-zig-archive.py --self-test
      - name: Self-test current Lane 05 stage helper contract checker
        run: python3 scripts/zigux/check-lane05-stage-helper-contract.py --self-test
      - name: Check current Lane 05 stage helper contract packet
        run: python3 scripts/zigux/check-lane05-stage-helper-contract.py
      - name: Self-test current Lane 05 stage helper selftest checker
        run: python3 scripts/zigux/check-lane05-stage-helper-selftest.py --self-test
      - name: Check current Lane 05 stage helper selftest packet
        run: python3 scripts/zigux/check-lane05-stage-helper-selftest.py
      - name: Self-test current Lane 05 stage-helper workflow checker
        run: python3 scripts/zigux/check-lane05-stage-helper-workflow.py --self-test
      - name: Check current Lane 05 stage-helper workflow packet
        run: python3 scripts/zigux/check-lane05-stage-helper-workflow.py
      - name: Self-test current Phase 2 fixdep gate checker
        run: python3 scripts/zigux/check-phase2-fixdep-gate.py --self-test
"""
    check_workflow(good_workflow)
    case_count = 1

    for broken_text, expected in (
        (
            good_workflow.replace(
                "      - name: Self-test current Lane 05 stage-helper workflow checker\n"
                "        run: python3 scripts/zigux/check-lane05-stage-helper-workflow.py --self-test\n",
                "",
                1,
            ),
            WORKFLOW_CHECKER_SELF_TEST_STEP,
        ),
        (
            good_workflow.replace(
                "      - name: Check current Lane 05 stage-helper workflow packet\n"
                "        run: python3 scripts/zigux/check-lane05-stage-helper-workflow.py\n",
                "",
                1,
            ),
            WORKFLOW_CHECKER_STEP,
        ),
        (
            good_workflow.replace(
                "      - name: Self-test current staged pinned Zig archive helper\n"
                "        run: python3 scripts/zigux/stage-pinned-zig-archive.py --self-test\n",
                "",
                1,
            ),
            STAGE_HELPER_SELF_TEST_STEP,
        ),
        (
            good_workflow.replace(
                "      - name: Check current Lane 05 stage helper selftest packet\n"
                "        run: python3 scripts/zigux/check-lane05-stage-helper-selftest.py\n",
                "",
                1,
            ),
            SELFTEST_PACKET_STEP,
        ),
    ):
        try:
            check_workflow(broken_text)
        except SystemExit as exc:
            assert expected in str(exc), str(exc)
            case_count += 1
        else:
            raise AssertionError(f"expected failure for {expected}")

    duplicate_step = good_workflow.replace(
        "      - name: Check current Lane 05 stage-helper workflow packet\n",
        "      - name: Check current Lane 05 stage-helper workflow packet\n"
        "      - name: Check current Lane 05 stage-helper workflow packet\n",
        1,
    )
    try:
        check_workflow(duplicate_step)
    except SystemExit as exc:
        assert WORKFLOW_CHECKER_STEP in str(exc), str(exc)
        case_count += 1
    else:
        raise AssertionError("expected duplicate workflow checker step failure")

    reordered_steps = good_workflow.replace(
        "      - name: Self-test current Lane 05 stage-helper workflow checker\n"
        "        run: python3 scripts/zigux/check-lane05-stage-helper-workflow.py --self-test\n"
        "      - name: Check current Lane 05 stage-helper workflow packet\n"
        "        run: python3 scripts/zigux/check-lane05-stage-helper-workflow.py\n",
        "      - name: Check current Lane 05 stage-helper workflow packet\n"
        "        run: python3 scripts/zigux/check-lane05-stage-helper-workflow.py\n"
        "      - name: Self-test current Lane 05 stage-helper workflow checker\n"
        "        run: python3 scripts/zigux/check-lane05-stage-helper-workflow.py --self-test\n",
        1,
    )
    try:
        check_workflow(reordered_steps)
    except SystemExit as exc:
        assert "lane05 step order" in str(exc), str(exc)
        case_count += 1
    else:
        raise AssertionError("expected reordered workflow-checker step failure")

    print("LANE05_STAGE_HELPER_WORKFLOW_SELF_TEST=pass")
    print(f"LANE05_STAGE_HELPER_WORKFLOW_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that Lane 05 bootstrap keeps the staged-archive workflow packet explicit."
    )
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument(
        "--workflow",
        type=Path,
        default=WORKFLOW_PATH,
        help="Path to .github/workflows/zigux-bootstrap.yml",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    check_workflow(args.workflow.read_text(encoding="utf-8"))
    print("LANE05_STAGE_HELPER_WORKFLOW=pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
