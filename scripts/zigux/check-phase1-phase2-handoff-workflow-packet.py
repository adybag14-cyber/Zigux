#!/usr/bin/env python3
"""Guard the live Phase 2 closure to Phase 1 entry workflow handoff."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent

WORKFLOW_REL = Path(".github/workflows/zigux-bootstrap.yml")
PHASE2_VALIDATE_REL = Path("scripts/zigux/validate-phase2.py")
PHASE2_CLOSURE_REL = Path("scripts/zigux/validate-phase2-closure.py")
PHASE1_DIRECT_OWNER_REL = Path("scripts/zigux/check-phase1-direct-owner-markers.py")
PHASE1_DIRECT_ANCHOR_REL = Path("scripts/zigux/check-phase1-direct-anchor-manifest-gate.py")
PHASE1_STRING_REVIEW_REL = Path("scripts/zigux/check-phase1-string-review-packet.py")

REQUIRED_FILES = (
    WORKFLOW_REL,
    PHASE2_VALIDATE_REL,
    PHASE2_CLOSURE_REL,
    PHASE1_DIRECT_OWNER_REL,
    PHASE1_DIRECT_ANCHOR_REL,
    PHASE1_STRING_REVIEW_REL,
)

REQUIRED_WORKFLOW_RUNS = (
    "python3 scripts/zigux/validate-phase2.py",
    "python3 scripts/zigux/validate-phase2-closure.py --self-test",
    "python3 scripts/zigux/validate-phase2-closure.py",
    "python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test",
    "python3 scripts/zigux/check-phase1-direct-owner-markers.py",
    "python3 scripts/zigux/check-phase1-direct-anchor-manifest-gate.py --self-test",
    "python3 scripts/zigux/check-phase1-direct-anchor-manifest-gate.py",
    "python3 scripts/zigux/check-phase1-string-review-packet.py --self-test",
    "python3 scripts/zigux/check-phase1-string-review-packet.py",
)

REQUIRED_STEP_NAMES = (
    "Validate current Phase 2 tool packet",
    "Self-test current Phase 2 closure validator",
    "Check current Phase 2 closure packet",
    "Self-test current Phase 1 direct-owner checker",
    "Check current Phase 1 direct-owner markers",
    "Self-test current Phase 1 direct-anchor manifest gate",
    "Check current Phase 1 direct-anchor manifest gate",
    "Self-test current Phase 1 string review checker",
    "Check current Phase 1 string review packet",
)

FILE_MARKERS = {
    PHASE2_VALIDATE_REL: (
        "TOOLCHAIN_POLICY = \"scripts/zigux/zig-toolchain-policy.json\"",
        "KCONFIG_BRIDGE_VALIDATOR_PATH = \"scripts/zigux/check-kconfig-bridge.py\"",
        "DEFAULT_REQUIRED_MAKE_ROUTES = (",
    ),
    PHASE2_CLOSURE_REL: (
        "VALIDATOR_COMMANDS = (",
        "\"python3 scripts/zigux/validate-phase2.py\"",
        "\"python3 scripts/zigux/validate-phase2-closure.py\"",
        "PHASE2_CLOSURE_REL = Path(\"Documentation/zigux/phase2-closure.md\")",
    ),
    PHASE1_DIRECT_OWNER_REL: (
        "Guard the Phase 1 direct-owner marker packet against lane-note and helper drift.",
        "EXPECTED_DIRECT_ANCHOR_FOLLOWUP_HELPERS = [",
        "\"tools/lib/string.zig\"",
    ),
    PHASE1_DIRECT_ANCHOR_REL: (
        "BITMAP_DIRECT_ANCHOR_CHECKER_REL = Path(\"scripts/zigux/check-phase1-bitmap-direct-anchors.py\")",
        "FIND_BIT_REVIEW_CHECKER_REL = Path(\"scripts/zigux/check-phase1-find-bit-review-packet.py\")",
        "STRING_REVIEW_CHECKER_REL = Path(\"scripts/zigux/check-phase1-string-review-packet.py\")",
    ),
    PHASE1_STRING_REVIEW_REL: (
        "tools/lib/string.zig",
        "strscpy",
        "memparse",
    ),
}


def read_text(root: Path, relative: Path) -> str:
    return (root / relative).read_text(encoding="utf-8")


def count_run_line(workflow: str, command: str) -> int:
    return sum(1 for line in workflow.splitlines() if line.strip() == f"run: {command}")


def count_step_name(workflow: str, name: str) -> int:
    return sum(1 for line in workflow.splitlines() if line.strip() == f"- name: {name}")


def marker_positions(workflow: str, markers: tuple[str, ...]) -> list[int]:
    positions: list[int] = []
    for marker in markers:
        position = workflow.find(marker)
        if position < 0:
            return []
        positions.append(position)
    return positions


def validate_root(root: Path) -> list[str]:
    issues: list[str] = []

    for relative in REQUIRED_FILES:
        if not (root / relative).is_file():
            issues.append(f"missing_required_file:{relative.as_posix()}")

    if issues:
        return issues

    workflow = read_text(root, WORKFLOW_REL)

    for command in REQUIRED_WORKFLOW_RUNS:
        count = count_run_line(workflow, command)
        if count != 1:
            issues.append(f"workflow_run_count:{command}:expected=1:actual={count}")

    for name in REQUIRED_STEP_NAMES:
        count = count_step_name(workflow, name)
        if count != 1:
            issues.append(f"workflow_step_name_count:{name}:expected=1:actual={count}")

    run_positions = marker_positions(workflow, REQUIRED_WORKFLOW_RUNS)
    if not run_positions:
        issues.append("workflow_required_run_sequence:missing")
    elif run_positions != sorted(run_positions):
        issues.append("workflow_required_run_sequence:out_of_order")

    step_positions = marker_positions(workflow, REQUIRED_STEP_NAMES)
    if not step_positions:
        issues.append("workflow_required_step_sequence:missing")
    elif step_positions != sorted(step_positions):
        issues.append("workflow_required_step_sequence:out_of_order")

    closure_position = workflow.find("python3 scripts/zigux/validate-phase2-closure.py")
    phase1_position = workflow.find("python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test")
    phase3_position = workflow.find("python3 scripts/zigux/validate_phase3_selftest.py")
    if closure_position >= 0 and phase1_position >= 0 and closure_position > phase1_position:
        issues.append("workflow_phase2_closure_after_phase1_entry")
    if phase1_position >= 0 and phase3_position >= 0 and phase3_position < phase1_position:
        issues.append("workflow_phase3_starts_before_phase1_entry")

    for relative, markers in FILE_MARKERS.items():
        content = read_text(root, relative)
        for marker in markers:
            if marker not in content:
                issues.append(f"file_marker_missing:{relative.as_posix()}:{marker}")

    return issues


def write_text(root: Path, relative: Path, content: str) -> None:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def sample_workflow() -> str:
    lines = ["name: zigux-bootstrap", "jobs:", "  bootstrap:", "    steps:"]
    for name, command in zip(REQUIRED_STEP_NAMES, REQUIRED_WORKFLOW_RUNS, strict=True):
        lines.extend([f"      - name: {name}", f"        run: {command}"])
    lines.extend(
        [
            "      - name: Self-test current Phase 3 interop packet",
            "        run: python3 scripts/zigux/validate_phase3_selftest.py",
        ]
    )
    return "\n".join(lines) + "\n"


def write_sample_root(root: Path) -> None:
    write_text(root, WORKFLOW_REL, sample_workflow())
    for relative, markers in FILE_MARKERS.items():
        write_text(root, relative, "\n".join(markers) + "\n")


def run_self_test() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        write_sample_root(root)
        assert validate_root(root) == []

        workflow = read_text(root, WORKFLOW_REL)
        duplicate = workflow.replace(
            "        run: python3 scripts/zigux/check-phase1-direct-owner-markers.py\n",
            "        run: python3 scripts/zigux/check-phase1-direct-owner-markers.py\n"
            "        run: python3 scripts/zigux/check-phase1-direct-owner-markers.py\n",
        )
        write_text(root, WORKFLOW_REL, duplicate)
        assert any(
            issue.startswith(
                "workflow_run_count:python3 scripts/zigux/check-phase1-direct-owner-markers.py:"
            )
            for issue in validate_root(root)
        )

        write_sample_root(root)
        reordered = read_text(root, WORKFLOW_REL).replace(
            "      - name: Self-test current Phase 2 closure validator\n"
            "        run: python3 scripts/zigux/validate-phase2-closure.py --self-test\n"
            "      - name: Check current Phase 2 closure packet\n"
            "        run: python3 scripts/zigux/validate-phase2-closure.py\n"
            "      - name: Self-test current Phase 1 direct-owner checker\n"
            "        run: python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test\n",
            "      - name: Self-test current Phase 1 direct-owner checker\n"
            "        run: python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test\n"
            "      - name: Self-test current Phase 2 closure validator\n"
            "        run: python3 scripts/zigux/validate-phase2-closure.py --self-test\n"
            "      - name: Check current Phase 2 closure packet\n"
            "        run: python3 scripts/zigux/validate-phase2-closure.py\n",
        )
        write_text(root, WORKFLOW_REL, reordered)
        assert "workflow_required_run_sequence:out_of_order" in validate_root(root)

        write_sample_root(root)
        write_text(root, PHASE1_DIRECT_ANCHOR_REL, "missing anchors\n")
        assert any(
            issue.startswith("file_marker_missing:scripts/zigux/check-phase1-direct-anchor-manifest-gate.py")
            for issue in validate_root(root)
        )

        write_sample_root(root)
        (root / PHASE2_CLOSURE_REL).unlink()
        assert f"missing_required_file:{PHASE2_CLOSURE_REL.as_posix()}" in validate_root(root)

    print("PHASE1_PHASE2_HANDOFF_WORKFLOW_PACKET_SELF_TEST=pass")
    print("PHASE1_PHASE2_HANDOFF_WORKFLOW_PACKET_SELF_TEST_CASE_COUNT=4")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check the Phase 2 closure to Phase 1 entry workflow handoff packet."
    )
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT, help="Zigux tree root to validate.")
    parser.add_argument("--self-test", action="store_true", help="Run built-in checker self-tests.")
    parser.add_argument("--write-sample-root", type=Path, help="Write a minimal passing sample tree.")
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return 0

    if args.write_sample_root:
        write_sample_root(args.write_sample_root)
        print(f"PHASE1_PHASE2_HANDOFF_WORKFLOW_PACKET_SAMPLE_ROOT={args.write_sample_root}")
        return 0

    issues = validate_root(args.root)
    if issues:
        print("PHASE1_PHASE2_HANDOFF_WORKFLOW_PACKET=fail")
        print("PHASE1_PHASE2_HANDOFF_WORKFLOW_PACKET_ISSUES_START")
        for issue in issues:
            print(issue)
        print("PHASE1_PHASE2_HANDOFF_WORKFLOW_PACKET_ISSUES_END")
        return 1

    print("PHASE1_PHASE2_HANDOFF_WORKFLOW_PACKET=pass")
    print(f"PHASE1_PHASE2_HANDOFF_WORKFLOW_PACKET_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(f"PHASE1_PHASE2_HANDOFF_WORKFLOW_PACKET_REQUIRED_STEP_COUNT={len(REQUIRED_WORKFLOW_RUNS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
