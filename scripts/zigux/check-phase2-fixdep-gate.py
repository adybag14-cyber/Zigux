#!/usr/bin/env python3
import argparse
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
WORKFLOW_PATH = ROOT / ".github" / "workflows" / "zigux-bootstrap.yml"

REQUIRED_WORKFLOW_RUNS = [
    "python3 scripts/zigux/check-phase2-fixdep-gate.py --self-test",
    "python3 scripts/zigux/check-phase2-fixdep-gate.py",
    "python3 scripts/zigux/check-fixdep-diff.py --self-test",
    "python3 scripts/zigux/check-fixdep-diff.py",
    "zig test scripts/zigux/fixdep.zig",
]


def workflow_run_lines(workflow_text: str) -> list[str]:
    return [line.strip() for line in workflow_text.splitlines()]


def count_workflow_marker(lines: list[str], marker: str) -> int:
    expected = f"run: {marker}"
    return sum(1 for line in lines if line == expected)


def validate_texts(workflow_text: str) -> list[str]:
    issues: list[str] = []

    workflow_lines = workflow_run_lines(workflow_text)
    for marker in REQUIRED_WORKFLOW_RUNS:
        count = count_workflow_marker(workflow_lines, marker)
        if count != 1:
            issues.append(f"workflow_exact_marker:{marker}:count={count}:expected=1")

    workflow_positions: list[int] = []
    workflow_order_ready = True
    for marker in REQUIRED_WORKFLOW_RUNS:
        expected = f"run: {marker}"
        try:
            workflow_positions.append(workflow_lines.index(expected))
        except ValueError:
            workflow_order_ready = False
            break
    if workflow_order_ready and workflow_positions != sorted(workflow_positions):
        issues.append("workflow_order:fixdep_gate_packet")

    return issues


def run_self_test() -> int:
    workflow_text = "\n".join(
        [
            "run: python3 scripts/zigux/check-phase2-fixdep-gate.py --self-test",
            "run: python3 scripts/zigux/check-phase2-fixdep-gate.py",
            "run: python3 scripts/zigux/check-fixdep-diff.py --self-test",
            "run: python3 scripts/zigux/check-fixdep-diff.py",
            "run: zig test scripts/zigux/fixdep.zig",
        ]
    ) + "\n"

    assert validate_texts(workflow_text) == []

    issues = validate_texts(
        workflow_text.replace(
            "run: python3 scripts/zigux/check-fixdep-diff.py --self-test\n",
            "",
            1,
        )
    )
    assert (
        "workflow_exact_marker:python3 scripts/zigux/check-fixdep-diff.py --self-test:count=0:expected=1"
        in issues
    )

    issues = validate_texts(
        workflow_text.replace(
            "run: python3 scripts/zigux/check-fixdep-diff.py\n",
            "run: python3 scripts/zigux/check-fixdep-diff.py\nrun: python3 scripts/zigux/check-fixdep-diff.py\n",
            1,
        )
    )
    assert "workflow_exact_marker:python3 scripts/zigux/check-fixdep-diff.py:count=2:expected=1" in issues

    issues = validate_texts(
        workflow_text.replace(
            "run: zig test scripts/zigux/fixdep.zig\n",
            "",
            1,
        )
    )
    assert "workflow_exact_marker:zig test scripts/zigux/fixdep.zig:count=0:expected=1" in issues

    issues = validate_texts(
        workflow_text.replace(
            "run: python3 scripts/zigux/check-phase2-fixdep-gate.py --self-test\n",
            "run: python3 scripts/zigux/check-phase2-fixdep-gate.py --self-test\nrun: python3 scripts/zigux/check-phase2-fixdep-gate.py --self-test\n",
            1,
        )
    )
    assert (
        "workflow_exact_marker:python3 scripts/zigux/check-phase2-fixdep-gate.py --self-test:count=2:expected=1"
        in issues
    )

    issues = validate_texts(
        workflow_text.replace(
            "run: python3 scripts/zigux/check-phase2-fixdep-gate.py --self-test\nrun: python3 scripts/zigux/check-phase2-fixdep-gate.py\n",
            "run: python3 scripts/zigux/check-phase2-fixdep-gate.py\nrun: python3 scripts/zigux/check-phase2-fixdep-gate.py --self-test\n",
            1,
        )
    )
    assert "workflow_order:fixdep_gate_packet" in issues

    print("PHASE2_FIXDEP_GATE_SELF_TEST=pass")
    print("PHASE2_FIXDEP_GATE_SELF_TEST_CASE_COUNT=5")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check the bounded Phase 2 fixdep workflow gating packet."
    )
    parser.add_argument("--self-test", action="store_true", help="Run checkout-free checker self-tests.")
    args = parser.parse_args()
    if args.self_test:
        return run_self_test()

    issues = validate_texts(WORKFLOW_PATH.read_text(encoding="utf-8"))
    if issues:
        print("PHASE2_FIXDEP_GATE=fail")
        print("PHASE2_FIXDEP_GATE_ISSUES_START")
        for issue in issues:
            print(issue)
        print("PHASE2_FIXDEP_GATE_ISSUES_END")
        return 1

    print("PHASE2_FIXDEP_GATE=pass")
    print(f"PHASE2_FIXDEP_GATE_WORKFLOW_MARKER_COUNT={len(REQUIRED_WORKFLOW_RUNS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
