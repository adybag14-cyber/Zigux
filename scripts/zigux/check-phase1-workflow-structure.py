#!/usr/bin/env python3
"""Guard the current Phase 1 workflow structure in zigux-bootstrap."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent
WORKFLOW_REL = Path(".github/workflows/zigux-bootstrap.yml")

PHASE1_BLOCK_LINES = (
    "run: python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test",
    "run: python3 scripts/zigux/check-phase1-direct-owner-markers.py",
    "run: python3 scripts/zigux/check-phase1-direct-anchor-manifest-gate.py --self-test",
    "run: python3 scripts/zigux/check-phase1-direct-anchor-manifest-gate.py",
    "run: python3 scripts/zigux/check-phase1-string-review-packet.py --self-test",
    "run: python3 scripts/zigux/check-phase1-string-review-packet.py",
    "run: python3 scripts/zigux/check-phase1-find-bit-review-packet.py --self-test",
    "run: python3 scripts/zigux/check-phase1-find-bit-review-packet.py",
    "run: python3 scripts/zigux/check-phase1-route-summary-counts.py --self-test",
    "run: python3 scripts/zigux/check-phase1-route-summary-counts.py",
    "run: python3 scripts/zigux/check-phase1-bench.py --self-test",
    "run: python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test",
    "run: python3 scripts/zigux/check-phase1-shared-reminder-packet.py",
    "run: python3 scripts/zigux/validate-phase1-closure.py --self-test",
    "run: python3 scripts/zigux/validate-phase1-closure.py",
    "run: python3 scripts/zigux/check-phase1-workflow-structure.py --self-test",
    "run: python3 scripts/zigux/check-phase1-workflow-structure.py",
)

PHASE3_SELFTEST_LINE = "run: python3 scripts/zigux/validate_phase3_selftest.py"
PHASE3_DUMP_LINE = "run: zig build phase3-dump --build-file zigux/tests/build.zig"
PHASE1_SMOKE_LINE = "run: zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig"
PHASE4_START_LINE = "run: python3 scripts/zigux/check-phase4-repo-reality-warning.py --self-test"

EXACT_ONCE_LINES = (
    "- name: Setup pinned Zig toolchain",
    "run: python3 scripts/zigux/validate-phase2.py",
    *PHASE1_BLOCK_LINES,
    PHASE3_SELFTEST_LINE,
    PHASE3_DUMP_LINE,
    PHASE1_SMOKE_LINE,
    PHASE4_START_LINE,
)

FORBIDDEN_LINES = (
    "run: python3 scripts/zigux/check-phase1-bench.py",
    "run: python3 scripts/zigux/check-phase1-parity.py --self-test",
    "run: python3 scripts/zigux/check-phase1-parity.py",
    "run: python3 scripts/zigux/validate-phase1.py --self-test",
    "run: python3 scripts/zigux/validate-phase1.py",
    "run: make -C zigux phase1-validate",
    "run: make -C zigux phase1-test",
    "run: make -C zigux phase1-bench",
    "run: make -C zigux phase1",
)

OPTIONAL_PREFLIGHT_BLOCK = (
    "- name: Self-test current Phase 1 workflow preflight checker",
    "- name: Preflight current Phase 1 workflow viability",
)


def repo_root(root: str | None) -> Path:
    return Path(root).resolve() if root else DEFAULT_ROOT.resolve()


def count_stripped_lines(text: str, marker: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip() == marker.strip())


def step_names(text: str) -> list[str]:
    return [line.strip() for line in text.splitlines() if line.strip().startswith("- name: ")]


def find_line_index(lines: list[str], marker: str) -> int:
    for idx, line in enumerate(lines):
        if line == marker.strip():
            return idx
    raise ValueError(marker)


def collect_failures(root: Path) -> list[str]:
    workflow = root / WORKFLOW_REL
    if not workflow.is_file():
        return [f"missing_file:{WORKFLOW_REL.as_posix()}"]

    text = workflow.read_text(encoding="utf-8")
    stripped_lines = [line.strip() for line in text.splitlines()]
    run_lines = [line for line in stripped_lines if line.startswith("run: ")]
    failures: list[str] = []

    for marker in EXACT_ONCE_LINES:
        count = count_stripped_lines(text, marker)
        if count != 1:
            failures.append(f"missing_or_duplicate:{marker}:count={count}")

    for marker in FORBIDDEN_LINES:
        count = count_stripped_lines(text, marker)
        if count != 0:
            failures.append(f"forbidden_present:{marker}:count={count}")

    if failures:
        return failures

    setup_idx = find_line_index(stripped_lines, "- name: Setup pinned Zig toolchain")
    phase2_validate_step_idx = find_line_index(stripped_lines, "run: python3 scripts/zigux/validate-phase2.py")
    phase3_selftest_step_idx = find_line_index(stripped_lines, PHASE3_SELFTEST_LINE)
    phase2_validate_idx = find_line_index(run_lines, "run: python3 scripts/zigux/validate-phase2.py")
    phase3_selftest_idx = find_line_index(run_lines, PHASE3_SELFTEST_LINE)
    phase3_dump_idx = find_line_index(run_lines, PHASE3_DUMP_LINE)
    phase1_smoke_idx = find_line_index(run_lines, PHASE1_SMOKE_LINE)
    phase4_start_idx = find_line_index(run_lines, PHASE4_START_LINE)

    if not (setup_idx < phase2_validate_step_idx < phase3_selftest_step_idx):
        failures.append("workflow_boundaries:phase2_or_phase3_drifted")

    phase1_positions = [find_line_index(run_lines, marker) for marker in PHASE1_BLOCK_LINES]
    if phase1_positions != sorted(phase1_positions):
        failures.append("phase1_block_order:drifted")
    if not (phase2_validate_idx < phase1_positions[0]):
        failures.append("phase1_block_boundary:must_follow_phase2_validate")
    if not (phase1_positions[-1] < phase3_selftest_idx):
        failures.append("phase1_block_boundary:must_precede_phase3_selftest")
    if phase1_positions != list(range(phase1_positions[0], phase1_positions[0] + len(PHASE1_BLOCK_LINES))):
        failures.append("phase1_block_contiguity:drifted")

    if not (phase3_selftest_idx < phase3_dump_idx < phase1_smoke_idx < phase4_start_idx):
        failures.append("phase1_smoke_boundary:must_follow_phase3_dump_and_precede_phase4")

    names = step_names(text)
    if OPTIONAL_PREFLIGHT_BLOCK[0] in names or OPTIONAL_PREFLIGHT_BLOCK[1] in names:
        try:
            preflight_start = names.index(OPTIONAL_PREFLIGHT_BLOCK[0])
        except ValueError:
            failures.append("preflight_block:missing_selftest_step_name")
        else:
            if tuple(names[preflight_start : preflight_start + len(OPTIONAL_PREFLIGHT_BLOCK)]) != OPTIONAL_PREFLIGHT_BLOCK:
                failures.append("preflight_block:step_order_drifted")
            try:
                setup_python_idx = names.index("- name: Setup Python")
                setup_toolchain_idx = names.index("- name: Setup pinned Zig toolchain")
            except ValueError as exc:
                failures.append(f"preflight_block:missing_step_name:{exc}")
            else:
                if not (setup_python_idx < preflight_start < setup_toolchain_idx):
                    failures.append("preflight_block:must_stay_between_setup_python_and_toolchain")
                if preflight_start + len(OPTIONAL_PREFLIGHT_BLOCK) != setup_toolchain_idx:
                    failures.append("preflight_block:must_stay_adjacent_to_toolchain")

    return failures


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def sample_workflow(include_preflight: bool = False) -> str:
    lines = [
        "name: zigux-bootstrap",
        "jobs:",
        "  bootstrap:",
        "    steps:",
        "      - name: Setup Python",
        "        run: python3 -V",
    ]
    if include_preflight:
        lines.extend(
            [
                "      - name: Self-test current Phase 1 workflow preflight checker",
                "        run: python3 scripts/zigux/check-phase1-workflow-preflight.py --self-test",
                "      - name: Preflight current Phase 1 workflow viability",
                "        run: python3 scripts/zigux/check-phase1-workflow-preflight.py",
            ]
        )
    lines.extend(
        [
            "      - name: Setup pinned Zig toolchain",
            "        run: ./setup-zig.sh",
            "      - name: Validate current Phase 2 tool packet",
            "        run: python3 scripts/zigux/validate-phase2.py",
            "      - name: Self-test current Phase 1 direct-owner checker",
            "        run: python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test",
            "      - name: Check current Phase 1 direct-owner markers",
            "        run: python3 scripts/zigux/check-phase1-direct-owner-markers.py",
            "      - name: Self-test current Phase 1 direct-anchor manifest gate",
            "        run: python3 scripts/zigux/check-phase1-direct-anchor-manifest-gate.py --self-test",
            "      - name: Check current Phase 1 direct-anchor manifest gate",
            "        run: python3 scripts/zigux/check-phase1-direct-anchor-manifest-gate.py",
            "      - name: Self-test current Phase 1 string review checker",
            "        run: python3 scripts/zigux/check-phase1-string-review-packet.py --self-test",
            "      - name: Check current Phase 1 string review packet",
            "        run: python3 scripts/zigux/check-phase1-string-review-packet.py",
            "      - name: Self-test current Phase 1 find-bit review checker",
            "        run: python3 scripts/zigux/check-phase1-find-bit-review-packet.py --self-test",
            "      - name: Check current Phase 1 find-bit review packet",
            "        run: python3 scripts/zigux/check-phase1-find-bit-review-packet.py",
            "      - name: Self-test current Phase 1 route summary checker",
            "        run: python3 scripts/zigux/check-phase1-route-summary-counts.py --self-test",
            "      - name: Check current Phase 1 route summary packet",
            "        run: python3 scripts/zigux/check-phase1-route-summary-counts.py",
            "      - name: Self-test current Phase 1 bench checker",
            "        run: python3 scripts/zigux/check-phase1-bench.py --self-test",
            "      - name: Self-test current Phase 1 shared reminder checker",
            "        run: python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test",
            "      - name: Check current Phase 1 shared reminder packet",
            "        run: python3 scripts/zigux/check-phase1-shared-reminder-packet.py",
            "      - name: Self-test current Phase 1 closure validator",
            "        run: python3 scripts/zigux/validate-phase1-closure.py --self-test",
            "      - name: Check current Phase 1 closure packet",
            "        run: python3 scripts/zigux/validate-phase1-closure.py",
            "      - name: Self-test current Phase 1 workflow structure checker",
            "        run: python3 scripts/zigux/check-phase1-workflow-structure.py --self-test",
            "      - name: Check current Phase 1 workflow structure packet",
            "        run: python3 scripts/zigux/check-phase1-workflow-structure.py",
            "      - name: Self-test current Phase 3 interop packet",
            "        run: python3 scripts/zigux/validate_phase3_selftest.py",
            "      - name: Run current Phase 3 ABI dump replay",
            "        run: zig build phase3-dump --build-file zigux/tests/build.zig",
            "      - name: Run current Phase 1 shared tests-root smoke",
            "        run: zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig",
            "      - name: Self-test current Phase 4 repo-reality warning checker",
            "        run: python3 scripts/zigux/check-phase4-repo-reality-warning.py --self-test",
        ]
    )
    return "\n".join(lines) + "\n"


def build_sample_root(root: Path, include_preflight: bool = False) -> None:
    write_text(root / WORKFLOW_REL, sample_workflow(include_preflight=include_preflight))


def remove_line(root: Path, marker: str) -> None:
    workflow = root / WORKFLOW_REL
    lines = workflow.read_text(encoding="utf-8").splitlines()
    for idx, line in enumerate(lines):
        if line.strip() == marker.strip():
            del lines[idx]
            workflow.write_text("\n".join(lines) + "\n", encoding="utf-8")
            return
    raise ValueError(marker)


def duplicate_line(root: Path, marker: str) -> None:
    workflow = root / WORKFLOW_REL
    lines = workflow.read_text(encoding="utf-8").splitlines()
    for idx, line in enumerate(lines):
        if line.strip() == marker.strip():
            lines.insert(idx + 1, line)
            workflow.write_text("\n".join(lines) + "\n", encoding="utf-8")
            return
    raise ValueError(marker)


def insert_step_after(root: Path, after_marker: str, step_name: str, run_marker: str) -> None:
    workflow = root / WORKFLOW_REL
    lines = workflow.read_text(encoding="utf-8").splitlines()
    for idx, line in enumerate(lines):
        if line.strip() == after_marker.strip():
            lines[idx + 1 : idx + 1] = [
                f"      - name: {step_name}",
                f"        {run_marker.strip()}",
            ]
            workflow.write_text("\n".join(lines) + "\n", encoding="utf-8")
            return
    raise ValueError(after_marker)


def replace_line(root: Path, old: str, new: str) -> None:
    workflow = root / WORKFLOW_REL
    lines = workflow.read_text(encoding="utf-8").splitlines()
    for idx, line in enumerate(lines):
        if line.strip() == old.strip():
            indent = line[: len(line) - len(line.lstrip())]
            lines[idx] = f"{indent}{new.strip()}"
            workflow.write_text("\n".join(lines) + "\n", encoding="utf-8")
            return
    raise ValueError(old)


def append_forbidden(root: Path, marker: str) -> None:
    workflow = root / WORKFLOW_REL
    workflow.write_text(
        workflow.read_text(encoding="utf-8")
        + f"      - name: Forbidden\n        {marker.strip()}\n",
        encoding="utf-8",
    )


def run_self_test() -> int:
    cases: list[tuple[str, bool, object | None]] = [
        ("baseline_current", False, None),
        ("baseline_with_preflight", True, None),
        ("missing_workflow", False, lambda root: (root / WORKFLOW_REL).unlink()),
        ("missing_phase2_validate", False, lambda root: remove_line(root, "run: python3 scripts/zigux/validate-phase2.py")),
        ("missing_phase3_selftest", False, lambda root: remove_line(root, PHASE3_SELFTEST_LINE)),
        ("missing_phase1_smoke", False, lambda root: remove_line(root, PHASE1_SMOKE_LINE)),
        ("duplicate_phase1_smoke", False, lambda root: duplicate_line(root, PHASE1_SMOKE_LINE)),
        ("missing_live_string_review", False, lambda root: remove_line(root, "run: python3 scripts/zigux/check-phase1-string-review-packet.py")),
        ("live_bench_enabled", False, lambda root: append_forbidden(root, "run: python3 scripts/zigux/check-phase1-bench.py")),
        ("old_phase1_validate_route", False, lambda root: append_forbidden(root, "run: make -C zigux phase1-validate")),
        (
            "phase1_block_not_contiguous",
            False,
            lambda root: insert_step_after(
                root,
                "run: python3 scripts/zigux/check-phase1-route-summary-counts.py",
                "Inserted helper",
                "run: python3 scripts/zigux/check-zig-toolchain.py --policy-only",
            ),
        ),
        (
            "phase1_block_before_phase2_validate",
            False,
            lambda root: replace_line(
                root,
                "run: python3 scripts/zigux/validate-phase2.py",
                PHASE3_SELFTEST_LINE,
            ),
        ),
        (
            "phase1_smoke_before_phase3_dump",
            False,
            lambda root: insert_step_after(
                root,
                "run: python3 scripts/zigux/validate-phase1-closure.py",
                "Moved smoke too early",
                PHASE1_SMOKE_LINE,
            ),
        ),
        (
            "bad_preflight_order",
            True,
            lambda root: insert_step_after(
                root,
                "- name: Preflight current Phase 1 workflow viability",
                "Inserted helper",
                "run: python3 scripts/zigux/check-zig-toolchain.py --self-test",
            ),
        ),
    ]

    for name, include_preflight, mutate in cases:
        with tempfile.TemporaryDirectory(prefix="phase1-workflow-structure-") as tmpdir:
            root = Path(tmpdir)
            build_sample_root(root, include_preflight=include_preflight)
            if mutate is not None:
                mutate(root)
            failures = collect_failures(root)
            if name.startswith("baseline"):
                if failures:
                    print(f"phase1-workflow-structure:{name}:unexpected={failures}")
                    return 1
            elif not failures:
                print(f"phase1-workflow-structure:{name}:expected_failure")
                return 1

    print("PHASE1_WORKFLOW_STRUCTURE_SELF_TEST=pass")
    print(f"PHASE1_WORKFLOW_STRUCTURE_SELF_TEST_CASE_COUNT={len(cases)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="override repository root")
    parser.add_argument("--self-test", action="store_true", help="run built-in self-tests")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = collect_failures(repo_root(args.root))
    if failures:
        for failure in failures:
            print(failure)
        return 1

    print("PHASE1_WORKFLOW_STRUCTURE=pass")
    print("PHASE1_WORKFLOW_STRUCTURE_BLOCK=current_phase2_validate_to_phase3_selftest")
    print("PHASE1_WORKFLOW_STRUCTURE_SMOKE_PLACEMENT=post_phase3_dump_pre_phase4")
    print(f"PHASE1_WORKFLOW_STRUCTURE_REQUIRED_LINE_COUNT={len(EXACT_ONCE_LINES)}")
    print(f"PHASE1_WORKFLOW_STRUCTURE_PHASE1_STEP_COUNT={len(PHASE1_BLOCK_LINES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
