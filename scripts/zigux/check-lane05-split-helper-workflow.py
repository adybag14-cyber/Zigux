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
CLI_SELF_TEST_STEP = "- name: Self-test current Lane 05 split helper cli-contract checker"
CLI_SELF_TEST_CMD = "python3 scripts/zigux/check-lane05-split-helper-cli-contract.py --self-test"
CLI_CHECK_STEP = "- name: Check current Lane 05 split helper cli-contract packet"
CLI_CHECK_CMD = "python3 scripts/zigux/check-lane05-split-helper-cli-contract.py"
ALIGN_SELF_TEST_STEP = "- name: Self-test current Lane 05 split-stage alignment checker"
ALIGN_SELF_TEST_CMD = "python3 scripts/zigux/check-lane05-split-stage-helper-alignment.py --self-test"
ALIGN_CHECK_STEP = "- name: Check current Lane 05 split-stage alignment packet"
ALIGN_CHECK_CMD = "python3 scripts/zigux/check-lane05-split-stage-helper-alignment.py"
ALIGN_SELFTEST_SELF_TEST_STEP = (
    "- name: Self-test current Lane 05 split-stage alignment selftest checker"
)
ALIGN_SELFTEST_SELF_TEST_CMD = (
    "python3 scripts/zigux/check-lane05-split-stage-alignment-selftest.py --self-test"
)
ALIGN_SELFTEST_CHECK_STEP = "- name: Check current Lane 05 split-stage alignment selftest packet"
ALIGN_SELFTEST_CHECK_CMD = "python3 scripts/zigux/check-lane05-split-stage-alignment-selftest.py"
NEXT_STEP = "- name: Self-test current Phase 2 fixdep gate checker"

ORDERED_STEPS = (
    PREVIOUS_STEP,
    CONTRACT_SELF_TEST_STEP,
    CONTRACT_CHECK_STEP,
    SELF_TEST_STEP,
    CHECK_STEP,
    CLI_SELF_TEST_STEP,
    CLI_CHECK_STEP,
    ALIGN_SELF_TEST_STEP,
    ALIGN_CHECK_STEP,
    ALIGN_SELFTEST_SELF_TEST_STEP,
    ALIGN_SELFTEST_CHECK_STEP,
    NEXT_STEP,
)

REQUIRED_MARKERS = (
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
    (CLI_SELF_TEST_STEP, "split helper cli-contract self-test step"),
    (CLI_SELF_TEST_CMD, "split helper cli-contract self-test command"),
    (CLI_CHECK_STEP, "split helper cli-contract check step"),
    (CLI_CHECK_CMD, "split helper cli-contract check command"),
    (ALIGN_SELF_TEST_STEP, "split-stage alignment self-test step"),
    (ALIGN_SELF_TEST_CMD, "split-stage alignment self-test command"),
    (ALIGN_CHECK_STEP, "split-stage alignment check step"),
    (ALIGN_CHECK_CMD, "split-stage alignment check command"),
    (ALIGN_SELFTEST_SELF_TEST_STEP, "split-stage selftest self-test step"),
    (ALIGN_SELFTEST_SELF_TEST_CMD, "split-stage selftest self-test command"),
    (ALIGN_SELFTEST_CHECK_STEP, "split-stage selftest check step"),
    (ALIGN_SELFTEST_CHECK_CMD, "split-stage selftest check command"),
    (NEXT_STEP, "next phase anchor"),
)

EXACT_LINES = (
    (f"run: {PREVIOUS_CMD}", "previous lane05 anchor command"),
    (f"run: {CONTRACT_SELF_TEST_CMD}", "split helper contract self-test command"),
    (f"run: {CONTRACT_CHECK_CMD}", "split helper contract check command"),
    (f"run: {SELF_TEST_CMD}", "split helper selftest command"),
    (f"run: {CHECK_CMD}", "split helper packet check command"),
    (f"run: {CLI_SELF_TEST_CMD}", "split helper cli-contract self-test command"),
    (f"run: {CLI_CHECK_CMD}", "split helper cli-contract check command"),
    (f"run: {ALIGN_SELF_TEST_CMD}", "split-stage alignment self-test command"),
    (f"run: {ALIGN_CHECK_CMD}", "split-stage alignment check command"),
    (f"run: {ALIGN_SELFTEST_SELF_TEST_CMD}", "split-stage selftest self-test command"),
    (f"run: {ALIGN_SELFTEST_CHECK_CMD}", "split-stage selftest check command"),
)


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
    for marker, label in REQUIRED_MARKERS:
        require_marker(text, marker, label)

    for line, label in EXACT_LINES:
        require_exact_line(text, line, label)

    for step in ORDERED_STEPS[:-1]:
        require_exact_line(text, step, "lane05 workflow step")

    for earlier, later in zip(ORDERED_STEPS, ORDERED_STEPS[1:]):
        require_order(text, earlier, later, "lane05 step order")

    return len(ORDERED_STEPS) - 1


def sample_workflow_text() -> str:
    return """name: zigux-bootstrap
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
      - name: Self-test current Lane 05 split helper cli-contract checker
        run: python3 scripts/zigux/check-lane05-split-helper-cli-contract.py --self-test
      - name: Check current Lane 05 split helper cli-contract packet
        run: python3 scripts/zigux/check-lane05-split-helper-cli-contract.py
      - name: Self-test current Lane 05 split-stage alignment checker
        run: python3 scripts/zigux/check-lane05-split-stage-helper-alignment.py --self-test
      - name: Check current Lane 05 split-stage alignment packet
        run: python3 scripts/zigux/check-lane05-split-stage-helper-alignment.py
      - name: Self-test current Lane 05 split-stage alignment selftest checker
        run: python3 scripts/zigux/check-lane05-split-stage-alignment-selftest.py --self-test
      - name: Check current Lane 05 split-stage alignment selftest packet
        run: python3 scripts/zigux/check-lane05-split-stage-alignment-selftest.py
      - name: Self-test current Phase 2 fixdep gate checker
        run: python3 scripts/zigux/check-phase2-fixdep-gate.py --self-test
"""


def write_sample_root(root: Path) -> None:
    workflow = root / WORKFLOW_PATH
    workflow.parent.mkdir(parents=True, exist_ok=True)
    workflow.write_text(sample_workflow_text(), encoding="utf-8")


def run_self_test() -> int:
    good_workflow = sample_workflow_text()
    assert check_workflow(good_workflow) == len(ORDERED_STEPS) - 1
    case_count = 1

    failure_cases = (
        (
            "      - name: Self-test current Lane 05 split helper cli-contract checker\n"
            "        run: python3 scripts/zigux/check-lane05-split-helper-cli-contract.py --self-test\n",
            "",
            CLI_SELF_TEST_STEP,
        ),
        (
            "        run: python3 scripts/zigux/check-lane05-split-stage-helper-alignment.py\n",
            "",
            ALIGN_CHECK_CMD,
        ),
        (
            "      - name: Self-test current Lane 05 split-stage alignment selftest checker\n"
            "        run: python3 scripts/zigux/check-lane05-split-stage-alignment-selftest.py --self-test\n",
            "",
            ALIGN_SELFTEST_SELF_TEST_STEP,
        ),
    )
    for before, after, expected in failure_cases:
        try:
            check_workflow(good_workflow.replace(before, after, 1))
        except SystemExit as exc:
            assert expected in str(exc), str(exc)
            case_count += 1
        else:
            raise AssertionError(f"expected failure for {expected}")

    duplicate_step = good_workflow.replace(
        "      - name: Self-test current Lane 05 split-stage alignment checker\n",
        "      - name: Self-test current Lane 05 split-stage alignment checker\n"
        "      - name: Self-test current Lane 05 split-stage alignment checker\n",
        1,
    )
    try:
        check_workflow(duplicate_step)
    except SystemExit as exc:
        assert ALIGN_SELF_TEST_STEP in str(exc), str(exc)
        case_count += 1
    else:
        raise AssertionError("expected duplicate split-stage alignment step failure")

    reordered_steps = good_workflow.replace(
        "      - name: Check current Lane 05 split helper cli-contract packet\n"
        "        run: python3 scripts/zigux/check-lane05-split-helper-cli-contract.py\n"
        "      - name: Self-test current Lane 05 split-stage alignment checker\n"
        "        run: python3 scripts/zigux/check-lane05-split-stage-helper-alignment.py --self-test\n",
        "      - name: Self-test current Lane 05 split-stage alignment checker\n"
        "        run: python3 scripts/zigux/check-lane05-split-stage-helper-alignment.py --self-test\n"
        "      - name: Check current Lane 05 split helper cli-contract packet\n"
        "        run: python3 scripts/zigux/check-lane05-split-helper-cli-contract.py\n",
        1,
    )
    try:
        check_workflow(reordered_steps)
    except SystemExit as exc:
        assert "lane05 step order" in str(exc), str(exc)
        case_count += 1
    else:
        raise AssertionError("expected reordered lane05 workflow steps failure")

    print("LANE05_SPLIT_HELPER_WORKFLOW_SELF_TEST=pass")
    print(f"LANE05_SPLIT_HELPER_WORKFLOW_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that Lane 05 bootstrap runs the full split-helper checker packet."
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
