#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path


WORKFLOW_PATH = Path(".github/workflows/zigux-bootstrap.yml")

PREVIOUS_STEP = "- name: Check current Lane 05 stage helper selftest packet"
PREVIOUS_CMD = "python3 scripts/zigux/check-lane05-stage-helper-selftest.py"
CONTRACT_SELF_TEST_STEP = "- name: Self-test current Lane 05 split helper contract checker"
CONTRACT_SELF_TEST_CMD = "python3 scripts/zigux/check-lane05-split-helper-contract.py --self-test"
CONTRACT_CHECK_STEP = "- name: Check current Lane 05 split helper contract packet"
CONTRACT_CHECK_CMD = "python3 scripts/zigux/check-lane05-split-helper-contract.py"
SELF_TEST_STEP = "- name: Self-test current Lane 05 split helper selftest checker"
SELF_TEST_CMD = "python3 scripts/zigux/check-lane05-split-helper-selftest.py --self-test"
CHECK_STEP = "- name: Check current Lane 05 split helper selftest packet"
CHECK_CMD = "python3 scripts/zigux/check-lane05-split-helper-selftest.py"
NEXT_STEP = "- name: Self-test current Phase 2 fixdep gate checker"


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
        raise SystemExit(
            f"lane05 split-helper workflow checker missing ordered markers for {label}"
        )
    if earlier_index >= later_index:
        raise SystemExit(
            "lane05 split-helper workflow checker expected "
            f"{label} `{earlier}` before `{later}`"
        )


def check_workflow(text: str) -> int:
    for marker, label in (
        (PREVIOUS_STEP, "previous lane05 anchor step"),
        (PREVIOUS_CMD, "previous lane05 anchor command"),
        (CONTRACT_SELF_TEST_STEP, "split helper contract self-test step"),
        (CONTRACT_SELF_TEST_CMD, "split helper contract self-test command"),
        (CONTRACT_CHECK_STEP, "split helper contract check step"),
        (CONTRACT_CHECK_CMD, "split helper contract check command"),
        (SELF_TEST_STEP, "split helper selftest step"),
        (SELF_TEST_CMD, "split helper selftest command"),
        (CHECK_STEP, "split helper packet check step"),
        (CHECK_CMD, "split helper packet check command"),
        (NEXT_STEP, "next phase anchor"),
    ):
        require_marker(text, marker, label)

    for line, label in (
        (f"run: {PREVIOUS_CMD}", "previous lane05 anchor command"),
        (f"run: {CONTRACT_SELF_TEST_CMD}", "split helper contract self-test command"),
        (f"run: {CONTRACT_CHECK_CMD}", "split helper contract check command"),
        (f"run: {SELF_TEST_CMD}", "split helper selftest command"),
        (f"run: {CHECK_CMD}", "split helper packet check command"),
    ):
        require_exact_line(text, line, label)

    for step, label in (
        (PREVIOUS_STEP, "previous lane05 anchor step"),
        (CONTRACT_SELF_TEST_STEP, "split helper contract self-test step"),
        (CONTRACT_CHECK_STEP, "split helper contract check step"),
        (SELF_TEST_STEP, "split helper selftest step"),
        (CHECK_STEP, "split helper packet check step"),
    ):
        require_exact_line(text, step, label)

    require_order(text, PREVIOUS_STEP, CONTRACT_SELF_TEST_STEP, "lane05 step order")
    require_order(text, CONTRACT_SELF_TEST_STEP, CONTRACT_CHECK_STEP, "lane05 step order")
    require_order(text, CONTRACT_CHECK_STEP, SELF_TEST_STEP, "lane05 step order")
    require_order(text, SELF_TEST_STEP, CHECK_STEP, "lane05 step order")
    require_order(text, CHECK_STEP, NEXT_STEP, "lane05 step order")
    return 5


def write_sample_root(root: Path) -> None:
    workflow = root / WORKFLOW_PATH
    workflow.parent.mkdir(parents=True, exist_ok=True)
    workflow.write_text(
        """name: zigux-bootstrap
jobs:
  bootstrap:
    steps:
      - name: Check current Lane 05 stage helper selftest packet
        run: python3 scripts/zigux/check-lane05-stage-helper-selftest.py
      - name: Self-test current Lane 05 split helper contract checker
        run: python3 scripts/zigux/check-lane05-split-helper-contract.py --self-test
      - name: Check current Lane 05 split helper contract packet
        run: python3 scripts/zigux/check-lane05-split-helper-contract.py
      - name: Self-test current Lane 05 split helper selftest checker
        run: python3 scripts/zigux/check-lane05-split-helper-selftest.py --self-test
      - name: Check current Lane 05 split helper selftest packet
        run: python3 scripts/zigux/check-lane05-split-helper-selftest.py
      - name: Self-test current Phase 2 fixdep gate checker
        run: python3 scripts/zigux/check-phase2-fixdep-gate.py --self-test
""",
        encoding="utf-8",
    )


def run_self_test() -> int:
    good_workflow = """name: zigux-bootstrap
jobs:
  bootstrap:
    steps:
      - name: Check current Lane 05 stage helper selftest packet
        run: python3 scripts/zigux/check-lane05-stage-helper-selftest.py
      - name: Self-test current Lane 05 split helper contract checker
        run: python3 scripts/zigux/check-lane05-split-helper-contract.py --self-test
      - name: Check current Lane 05 split helper contract packet
        run: python3 scripts/zigux/check-lane05-split-helper-contract.py
      - name: Self-test current Lane 05 split helper selftest checker
        run: python3 scripts/zigux/check-lane05-split-helper-selftest.py --self-test
      - name: Check current Lane 05 split helper selftest packet
        run: python3 scripts/zigux/check-lane05-split-helper-selftest.py
      - name: Self-test current Phase 2 fixdep gate checker
        run: python3 scripts/zigux/check-phase2-fixdep-gate.py --self-test
"""
    assert check_workflow(good_workflow) == 5
    case_count = 1

    for broken_text, expected in (
        (
            good_workflow.replace(
                "      - name: Self-test current Lane 05 split helper contract checker\n"
                "        run: python3 scripts/zigux/check-lane05-split-helper-contract.py --self-test\n",
                "",
                1,
            ),
            CONTRACT_SELF_TEST_STEP,
        ),
        (
            good_workflow.replace(
                "        run: python3 scripts/zigux/check-lane05-split-helper-contract.py\n",
                "",
                1,
            ),
            CONTRACT_CHECK_CMD,
        ),
        (
            good_workflow.replace(
                "      - name: Self-test current Lane 05 split helper selftest checker\n"
                "        run: python3 scripts/zigux/check-lane05-split-helper-selftest.py --self-test\n",
                "",
                1,
            ),
            SELF_TEST_STEP,
        ),
        (
            good_workflow.replace(
                "      - name: Check current Lane 05 split helper selftest packet\n"
                "        run: python3 scripts/zigux/check-lane05-split-helper-selftest.py\n",
                "",
                1,
            ),
            CHECK_STEP,
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
        "      - name: Self-test current Lane 05 split helper selftest checker\n",
        "      - name: Self-test current Lane 05 split helper selftest checker\n"
        "      - name: Self-test current Lane 05 split helper selftest checker\n",
        1,
    )
    try:
        check_workflow(duplicate_step)
    except SystemExit as exc:
        assert SELF_TEST_STEP in str(exc), str(exc)
        case_count += 1
    else:
        raise AssertionError("expected duplicate split helper selftest step failure")

    reordered_steps = good_workflow.replace(
        "      - name: Check current Lane 05 split helper contract packet\n"
        "        run: python3 scripts/zigux/check-lane05-split-helper-contract.py\n"
        "      - name: Self-test current Lane 05 split helper selftest checker\n"
        "        run: python3 scripts/zigux/check-lane05-split-helper-selftest.py --self-test\n",
        "      - name: Self-test current Lane 05 split helper selftest checker\n"
        "        run: python3 scripts/zigux/check-lane05-split-helper-selftest.py --self-test\n"
        "      - name: Check current Lane 05 split helper contract packet\n"
        "        run: python3 scripts/zigux/check-lane05-split-helper-contract.py\n",
        1,
    )
    try:
        check_workflow(reordered_steps)
    except SystemExit as exc:
        assert "lane05 step order" in str(exc), str(exc)
        case_count += 1
    else:
        raise AssertionError("expected reordered split helper steps failure")

    print("LANE05_SPLIT_HELPER_WORKFLOW_SELF_TEST=pass")
    print(f"LANE05_SPLIT_HELPER_WORKFLOW_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that Lane 05 bootstrap runs the split-helper checker packet."
    )
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument(
        "--workflow",
        type=Path,
        default=WORKFLOW_PATH,
        help="Path to .github/workflows/zigux-bootstrap.yml",
    )
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        help="Write a compact sample root that should satisfy this checker and exit",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        write_sample_root(args.write_sample_root.resolve())
        return 0

    text = args.workflow.read_text(encoding="utf-8")
    step_count = check_workflow(text)
    print("LANE05_SPLIT_HELPER_WORKFLOW=pass")
    print(f"LANE05_SPLIT_HELPER_WORKFLOW_STEP_COUNT={step_count}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
