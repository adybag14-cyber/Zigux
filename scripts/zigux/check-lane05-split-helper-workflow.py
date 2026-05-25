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
CONTRACT_SELFTEST_SELF_TEST_STEP = "- name: Self-test current Lane 05 split helper contract selftest checker"
CONTRACT_SELFTEST_SELF_TEST_CMD = "python3 scripts/zigux/check-lane05-split-helper-contract-selftest.py --self-test"
CONTRACT_SELFTEST_CHECK_STEP = "- name: Check current Lane 05 split helper contract selftest packet"
CONTRACT_SELFTEST_CHECK_CMD = "python3 scripts/zigux/check-lane05-split-helper-contract-selftest.py"
SELF_TEST_STEP = "- name: Self-test current Lane 05 split helper selftest checker"
SELF_TEST_CMD = "python3 scripts/zigux/check-lane05-split-helper-selftest.py --self-test"
CHECK_STEP = "- name: Check current Lane 05 split helper selftest packet"
CHECK_CMD = "python3 scripts/zigux/check-lane05-split-helper-selftest.py"
SELFTEST_SELF_TEST_STEP = "- name: Self-test current Lane 05 split helper selftest selftest checker"
SELFTEST_SELF_TEST_CMD = "python3 scripts/zigux/check-lane05-split-helper-selftest-selftest.py --self-test"
SELFTEST_CHECK_STEP = "- name: Check current Lane 05 split helper selftest selftest packet"
SELFTEST_CHECK_CMD = "python3 scripts/zigux/check-lane05-split-helper-selftest-selftest.py"
WORKFLOW_SELF_TEST_STEP = "- name: Self-test current Lane 05 split helper workflow checker"
WORKFLOW_SELF_TEST_CMD = "python3 scripts/zigux/check-lane05-split-helper-workflow.py --self-test"
WORKFLOW_CHECK_STEP = "- name: Check current Lane 05 split helper workflow packet"
WORKFLOW_CHECK_CMD = "python3 scripts/zigux/check-lane05-split-helper-workflow.py"
WORKFLOW_SELFTEST_SELF_TEST_STEP = "- name: Self-test current Lane 05 split helper workflow selftest checker"
WORKFLOW_SELFTEST_SELF_TEST_CMD = "python3 scripts/zigux/check-lane05-split-helper-workflow-selftest.py --self-test"
WORKFLOW_SELFTEST_CHECK_STEP = "- name: Check current Lane 05 split helper workflow selftest packet"
WORKFLOW_SELFTEST_CHECK_CMD = "python3 scripts/zigux/check-lane05-split-helper-workflow-selftest.py"
CLI_SELF_TEST_STEP = "- name: Self-test current Lane 05 split helper cli-contract checker"
CLI_SELF_TEST_CMD = "python3 scripts/zigux/check-lane05-split-helper-cli-contract.py --self-test"
CLI_CHECK_STEP = "- name: Check current Lane 05 split helper cli-contract packet"
CLI_CHECK_CMD = "python3 scripts/zigux/check-lane05-split-helper-cli-contract.py"
CLI_SELFTEST_SELF_TEST_STEP = "- name: Self-test current Lane 05 split helper cli-contract selftest checker"
CLI_SELFTEST_SELF_TEST_CMD = "python3 scripts/zigux/check-lane05-split-helper-cli-contract-selftest.py --self-test"
CLI_SELFTEST_CHECK_STEP = "- name: Check current Lane 05 split helper cli-contract selftest packet"
CLI_SELFTEST_CHECK_CMD = "python3 scripts/zigux/check-lane05-split-helper-cli-contract-selftest.py"
ALIGN_SELF_TEST_STEP = "- name: Self-test current Lane 05 split-stage alignment checker"
ALIGN_SELF_TEST_CMD = "python3 scripts/zigux/check-lane05-split-stage-helper-alignment.py --self-test"
ALIGN_CHECK_STEP = "- name: Check current Lane 05 split-stage alignment packet"
ALIGN_CHECK_CMD = "python3 scripts/zigux/check-lane05-split-stage-helper-alignment.py"
ALIGN_SELFTEST_SELF_TEST_STEP = "- name: Self-test current Lane 05 split-stage alignment selftest checker"
ALIGN_SELFTEST_SELF_TEST_CMD = "python3 scripts/zigux/check-lane05-split-stage-alignment-selftest.py --self-test"
ALIGN_SELFTEST_CHECK_STEP = "- name: Check current Lane 05 split-stage alignment selftest packet"
ALIGN_SELFTEST_CHECK_CMD = "python3 scripts/zigux/check-lane05-split-stage-alignment-selftest.py"
NEXT_STEP = "- name: Self-test current Phase 2 fixdep gate checker"

ORDERED_STEPS = (
    (PREVIOUS_STEP, PREVIOUS_CMD),
    (CONTRACT_SELF_TEST_STEP, CONTRACT_SELF_TEST_CMD),
    (CONTRACT_CHECK_STEP, CONTRACT_CHECK_CMD),
    (CONTRACT_SELFTEST_SELF_TEST_STEP, CONTRACT_SELFTEST_SELF_TEST_CMD),
    (CONTRACT_SELFTEST_CHECK_STEP, CONTRACT_SELFTEST_CHECK_CMD),
    (SELF_TEST_STEP, SELF_TEST_CMD),
    (CHECK_STEP, CHECK_CMD),
    (SELFTEST_SELF_TEST_STEP, SELFTEST_SELF_TEST_CMD),
    (SELFTEST_CHECK_STEP, SELFTEST_CHECK_CMD),
    (WORKFLOW_SELF_TEST_STEP, WORKFLOW_SELF_TEST_CMD),
    (WORKFLOW_CHECK_STEP, WORKFLOW_CHECK_CMD),
    (WORKFLOW_SELFTEST_SELF_TEST_STEP, WORKFLOW_SELFTEST_SELF_TEST_CMD),
    (WORKFLOW_SELFTEST_CHECK_STEP, WORKFLOW_SELFTEST_CHECK_CMD),
    (CLI_SELF_TEST_STEP, CLI_SELF_TEST_CMD),
    (CLI_CHECK_STEP, CLI_CHECK_CMD),
    (CLI_SELFTEST_SELF_TEST_STEP, CLI_SELFTEST_SELF_TEST_CMD),
    (CLI_SELFTEST_CHECK_STEP, CLI_SELFTEST_CHECK_CMD),
    (ALIGN_SELF_TEST_STEP, ALIGN_SELF_TEST_CMD),
    (ALIGN_CHECK_STEP, ALIGN_CHECK_CMD),
    (ALIGN_SELFTEST_SELF_TEST_STEP, ALIGN_SELFTEST_SELF_TEST_CMD),
    (ALIGN_SELFTEST_CHECK_STEP, ALIGN_SELFTEST_CHECK_CMD),
)


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
    for step, command in ORDERED_STEPS:
        require_exact_line(text, step, "lane05 workflow step")
        require_exact_line(text, f"run: {command}", "lane05 workflow command")

    require_exact_line(text, NEXT_STEP, "next phase anchor step")
    for (earlier, _), (later, _) in zip(ORDERED_STEPS, ORDERED_STEPS[1:]):
        require_order(text, earlier, later, "lane05 step order")
    require_order(text, ORDERED_STEPS[-1][0], NEXT_STEP, "lane05 trailing anchor order")
    return len(ORDERED_STEPS)


def sample_workflow_text() -> str:
    lines = [
        "name: zigux-bootstrap",
        "jobs:",
        "  bootstrap:",
        "    steps:",
    ]
    for step, command in ORDERED_STEPS:
        lines.append(f"      {step}")
        lines.append(f"        run: {command}")
    lines.append(f"      {NEXT_STEP}")
    lines.append("        run: python3 scripts/zigux/check-phase2-fixdep-gate.py --self-test")
    return "\n".join(lines) + "\n"


def write_sample_root(root: Path) -> None:
    workflow = root / WORKFLOW_PATH
    workflow.parent.mkdir(parents=True, exist_ok=True)
    workflow.write_text(sample_workflow_text(), encoding="utf-8")


def run_self_test() -> int:
    good_workflow = sample_workflow_text()
    assert check_workflow(good_workflow) == len(ORDERED_STEPS)
    case_count = 1

    missing_cases = (
        (CONTRACT_SELFTEST_SELF_TEST_STEP, "contract selftest step"),
        (SELFTEST_SELF_TEST_STEP, "selftest selftest step"),
        (WORKFLOW_SELFTEST_CHECK_STEP, "workflow selftest check step"),
        (CLI_SELFTEST_CHECK_STEP, "cli selftest check step"),
    )
    for marker, expected in missing_cases:
        try:
            check_workflow(good_workflow.replace(f"      {marker}\n", "", 1))
        except SystemExit as exc:
            assert expected.split()[0] in str(exc) or marker in str(exc), str(exc)
            case_count += 1
        else:
            raise AssertionError(f"expected failure for {expected}")

    reordered_steps = good_workflow.replace(
        f"      {CLI_CHECK_STEP}\n"
        f"        run: {CLI_CHECK_CMD}\n"
        f"      {CLI_SELFTEST_SELF_TEST_STEP}\n"
        f"        run: {CLI_SELFTEST_SELF_TEST_CMD}\n",
        f"      {CLI_SELFTEST_SELF_TEST_STEP}\n"
        f"        run: {CLI_SELFTEST_SELF_TEST_CMD}\n"
        f"      {CLI_CHECK_STEP}\n"
        f"        run: {CLI_CHECK_CMD}\n",
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
