#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path


WORKFLOW_PATH = Path(".github/workflows/zigux-bootstrap.yml")

SETUP_PYTHON_STEP = "- name: Setup Python"
ARCHIVE_PARTS_SELF_TEST_STEP = "- name: Self-test current Lane 05 archive parts packet checker"
ARCHIVE_PARTS_SELF_TEST_CMD = (
    "python3 scripts/zigux/check-lane05-archive-parts-packet.py --self-test"
)
ARCHIVE_PARTS_CHECK_STEP = "- name: Check current Lane 05 archive parts packet"
ARCHIVE_PARTS_CHECK_CMD = (
    "python3 scripts/zigux/check-lane05-archive-parts-packet.py --allow-missing"
)
WORKFLOW_SELF_TEST_STEP = (
    "- name: Self-test current Lane 05 archive-parts bootstrap workflow checker"
)
WORKFLOW_SELF_TEST_CMD = (
    "python3 scripts/zigux/check-lane05-archive-parts-bootstrap-workflow.py --self-test"
)
WORKFLOW_CHECK_STEP = "- name: Check current Lane 05 archive-parts bootstrap workflow packet"
WORKFLOW_CHECK_CMD = (
    "python3 scripts/zigux/check-lane05-archive-parts-bootstrap-workflow.py"
)
SETUP_TOOLCHAIN_STEP = "- name: Setup pinned Zig toolchain"
NEXT_STEP = "- name: Self-test current Zig toolchain checker"


def require_marker(text: str, marker: str, label: str) -> None:
    if marker not in text:
        raise SystemExit(f"lane05 archive-parts bootstrap checker missing {label}: {marker}")


def require_exact_line(text: str, line: str, label: str) -> None:
    count = sum(1 for current in text.splitlines() if current.strip() == line)
    if count != 1:
        raise SystemExit(
            "lane05 archive-parts bootstrap checker expected exactly "
            f"1 {label} line `{line}`, found {count}"
        )


def require_order(text: str, earlier: str, later: str, label: str) -> None:
    earlier_index = text.find(earlier)
    later_index = text.find(later)
    if earlier_index == -1 or later_index == -1:
        raise SystemExit(
            f"lane05 archive-parts bootstrap checker missing ordered markers for {label}"
        )
    if earlier_index >= later_index:
        raise SystemExit(
            "lane05 archive-parts bootstrap checker expected "
            f"{label} `{earlier}` before `{later}`"
        )


def check_workflow(text: str) -> None:
    for marker, label in (
        (SETUP_PYTHON_STEP, "setup-python step"),
        (ARCHIVE_PARTS_SELF_TEST_STEP, "archive-parts self-test step"),
        (ARCHIVE_PARTS_SELF_TEST_CMD, "archive-parts self-test command"),
        (ARCHIVE_PARTS_CHECK_STEP, "archive-parts check step"),
        (ARCHIVE_PARTS_CHECK_CMD, "archive-parts check command"),
        (WORKFLOW_SELF_TEST_STEP, "workflow self-test step"),
        (WORKFLOW_SELF_TEST_CMD, "workflow self-test command"),
        (WORKFLOW_CHECK_STEP, "workflow check step"),
        (WORKFLOW_CHECK_CMD, "workflow check command"),
        (SETUP_TOOLCHAIN_STEP, "toolchain setup step"),
        (NEXT_STEP, "next-step anchor"),
    ):
        require_marker(text, marker, label)

    for line, label in (
        (f"run: {ARCHIVE_PARTS_SELF_TEST_CMD}", "archive-parts self-test command"),
        (f"run: {ARCHIVE_PARTS_CHECK_CMD}", "archive-parts check command"),
        (f"run: {WORKFLOW_SELF_TEST_CMD}", "workflow self-test command"),
        (f"run: {WORKFLOW_CHECK_CMD}", "workflow check command"),
    ):
        require_exact_line(text, line, label)

    for step, label in (
        (ARCHIVE_PARTS_SELF_TEST_STEP, "archive-parts self-test step"),
        (ARCHIVE_PARTS_CHECK_STEP, "archive-parts check step"),
        (WORKFLOW_SELF_TEST_STEP, "workflow self-test step"),
        (WORKFLOW_CHECK_STEP, "workflow check step"),
    ):
        require_exact_line(text, step, label)

    require_order(text, SETUP_PYTHON_STEP, ARCHIVE_PARTS_SELF_TEST_STEP, "lane05 step order")
    require_order(
        text,
        ARCHIVE_PARTS_SELF_TEST_STEP,
        ARCHIVE_PARTS_CHECK_STEP,
        "lane05 step order",
    )
    require_order(
        text,
        ARCHIVE_PARTS_CHECK_STEP,
        WORKFLOW_SELF_TEST_STEP,
        "lane05 step order",
    )
    require_order(
        text,
        WORKFLOW_SELF_TEST_STEP,
        WORKFLOW_CHECK_STEP,
        "lane05 step order",
    )
    require_order(text, WORKFLOW_CHECK_STEP, SETUP_TOOLCHAIN_STEP, "lane05 step order")
    require_order(text, SETUP_TOOLCHAIN_STEP, NEXT_STEP, "lane05 step order")


def run_self_test() -> int:
    good_workflow = """name: zigux-bootstrap
jobs:
  bootstrap:
    steps:
      - name: Setup Python
        uses: actions/setup-python@v6.2.0
      - name: Self-test current Lane 05 archive parts packet checker
        run: python3 scripts/zigux/check-lane05-archive-parts-packet.py --self-test
      - name: Check current Lane 05 archive parts packet
        run: python3 scripts/zigux/check-lane05-archive-parts-packet.py --allow-missing
      - name: Self-test current Lane 05 archive-parts bootstrap workflow checker
        run: python3 scripts/zigux/check-lane05-archive-parts-bootstrap-workflow.py --self-test
      - name: Check current Lane 05 archive-parts bootstrap workflow packet
        run: python3 scripts/zigux/check-lane05-archive-parts-bootstrap-workflow.py
      - name: Setup pinned Zig toolchain
        run: echo setup
      - name: Self-test current Zig toolchain checker
        run: python3 scripts/zigux/check-zig-toolchain.py --self-test
"""
    check_workflow(good_workflow)
    case_count = 1

    for broken_text, expected in (
        (
            good_workflow.replace(
                "      - name: Self-test current Lane 05 archive parts packet checker\n"
                "        run: python3 scripts/zigux/check-lane05-archive-parts-packet.py --self-test\n",
                "",
                1,
            ),
            ARCHIVE_PARTS_SELF_TEST_STEP,
        ),
        (
            good_workflow.replace(
                "      - name: Check current Lane 05 archive parts packet\n"
                "        run: python3 scripts/zigux/check-lane05-archive-parts-packet.py --allow-missing\n",
                "",
                1,
            ),
            ARCHIVE_PARTS_CHECK_STEP,
        ),
        (
            good_workflow.replace(
                "      - name: Self-test current Lane 05 archive-parts bootstrap workflow checker\n"
                "        run: python3 scripts/zigux/check-lane05-archive-parts-bootstrap-workflow.py --self-test\n",
                "",
                1,
            ),
            WORKFLOW_SELF_TEST_STEP,
        ),
        (
            good_workflow.replace(
                "      - name: Check current Lane 05 archive-parts bootstrap workflow packet\n"
                "        run: python3 scripts/zigux/check-lane05-archive-parts-bootstrap-workflow.py\n",
                "",
                1,
            ),
            WORKFLOW_CHECK_STEP,
        ),
    ):
        try:
            check_workflow(broken_text)
        except SystemExit as exc:
            assert expected in str(exc), str(exc)
            case_count += 1
        else:
            raise AssertionError(f"expected failure for {expected}")

    duplicate_archive_parts_step = good_workflow.replace(
        "      - name: Self-test current Lane 05 archive parts packet checker\n",
        "      - name: Self-test current Lane 05 archive parts packet checker\n"
        "      - name: Self-test current Lane 05 archive parts packet checker\n",
        1,
    )
    try:
        check_workflow(duplicate_archive_parts_step)
    except SystemExit as exc:
        assert ARCHIVE_PARTS_SELF_TEST_STEP in str(exc), str(exc)
        case_count += 1
    else:
        raise AssertionError("expected duplicate archive-parts self-test failure")

    reordered_workflow_guard = good_workflow.replace(
        "      - name: Self-test current Lane 05 archive-parts bootstrap workflow checker\n"
        "        run: python3 scripts/zigux/check-lane05-archive-parts-bootstrap-workflow.py --self-test\n"
        "      - name: Check current Lane 05 archive-parts bootstrap workflow packet\n"
        "        run: python3 scripts/zigux/check-lane05-archive-parts-bootstrap-workflow.py\n",
        "      - name: Check current Lane 05 archive-parts bootstrap workflow packet\n"
        "        run: python3 scripts/zigux/check-lane05-archive-parts-bootstrap-workflow.py\n"
        "      - name: Self-test current Lane 05 archive-parts bootstrap workflow checker\n"
        "        run: python3 scripts/zigux/check-lane05-archive-parts-bootstrap-workflow.py --self-test\n",
        1,
    )
    try:
        check_workflow(reordered_workflow_guard)
    except SystemExit as exc:
        assert "lane05 step order" in str(exc), str(exc)
        case_count += 1
    else:
        raise AssertionError("expected reordered workflow-guard failure")

    reordered_toolchain = good_workflow.replace(
        "      - name: Check current Lane 05 archive-parts bootstrap workflow packet\n"
        "        run: python3 scripts/zigux/check-lane05-archive-parts-bootstrap-workflow.py\n"
        "      - name: Setup pinned Zig toolchain\n"
        "        run: echo setup\n",
        "      - name: Setup pinned Zig toolchain\n"
        "        run: echo setup\n"
        "      - name: Check current Lane 05 archive-parts bootstrap workflow packet\n"
        "        run: python3 scripts/zigux/check-lane05-archive-parts-bootstrap-workflow.py\n",
        1,
    )
    try:
        check_workflow(reordered_toolchain)
    except SystemExit as exc:
        assert "lane05 step order" in str(exc), str(exc)
        case_count += 1
    else:
        raise AssertionError("expected reordered toolchain failure")

    print("LANE05_ARCHIVE_PARTS_BOOTSTRAP_WORKFLOW_SELF_TEST=pass")
    print(f"LANE05_ARCHIVE_PARTS_BOOTSTRAP_WORKFLOW_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the main Lane 05 bootstrap workflow runs the archive-parts packet guard before toolchain setup."
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
    print("LANE05_ARCHIVE_PARTS_BOOTSTRAP_WORKFLOW=pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
