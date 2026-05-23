#!/usr/bin/env python3
"""Guard the current Phase 1 workflow preflight packet in zigux-bootstrap."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent
WORKFLOW_REL = Path(".github/workflows/zigux-bootstrap.yml")

PRE_TOOLCHAIN_STEP_NAMES = (
    "Setup Python",
    "Self-test current Phase 1 workflow preflight checker",
    "Preflight current Phase 1 workflow viability",
    "Setup pinned Zig toolchain",
)

PHASE1_PACKET_STEP_NAMES = (
    "Self-test current Phase 1 direct-owner checker",
    "Check current Phase 1 direct-owner markers",
    "Self-test current Phase 1 string review checker",
    "Check current Phase 1 string review packet",
    "Self-test current Phase 1 route summary checker",
    "Check current Phase 1 route summary packet",
    "Self-test current Phase 1 bench checker",
    "Self-test current Phase 1 shared reminder checker",
    "Check current Phase 1 shared reminder packet",
    "Self-test current Phase 1 closure validator",
    "Check current Phase 1 closure packet",
)

PHASE1_PACKET_BOUNDARY_STEP_NAMES = (
    "Validate current Phase 2 tool packet",
    *PHASE1_PACKET_STEP_NAMES,
    "Self-test current Phase 3 interop packet",
)

POST_PHASE1_PACKET_STEP_NAMES = (
    "Check current Phase 1 closure packet",
    "Self-test current Phase 3 interop packet",
    "Check current Phase 3 interop packet",
    "Run current Phase 1 shared tests-root smoke",
    "Self-test current Phase 4 repo-reality warning checker",
)

EXACT_ONCE_LINES = (
    "- name: Setup Python",
    "- name: Self-test current Phase 1 workflow preflight checker",
    "run: python3 scripts/zigux/check-phase1-workflow-preflight.py --self-test",
    "- name: Preflight current Phase 1 workflow viability",
    "run: python3 scripts/zigux/check-phase1-workflow-preflight.py",
    "- name: Setup pinned Zig toolchain",
    "- name: Self-test current Phase 1 direct-owner checker",
    "run: python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test",
    "- name: Check current Phase 1 direct-owner markers",
    "run: python3 scripts/zigux/check-phase1-direct-owner-markers.py",
    "- name: Self-test current Phase 1 string review checker",
    "run: python3 scripts/zigux/check-phase1-string-review-packet.py --self-test",
    "- name: Check current Phase 1 string review packet",
    "run: python3 scripts/zigux/check-phase1-string-review-packet.py",
    "- name: Self-test current Phase 1 route summary checker",
    "run: python3 scripts/zigux/check-phase1-route-summary-counts.py --self-test",
    "- name: Check current Phase 1 route summary packet",
    "run: python3 scripts/zigux/check-phase1-route-summary-counts.py",
    "- name: Self-test current Phase 1 bench checker",
    "run: python3 scripts/zigux/check-phase1-bench.py --self-test",
    "- name: Self-test current Phase 1 shared reminder checker",
    "run: python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test",
    "- name: Check current Phase 1 shared reminder packet",
    "run: python3 scripts/zigux/check-phase1-shared-reminder-packet.py",
    "- name: Self-test current Phase 1 closure validator",
    "run: python3 scripts/zigux/validate-phase1-closure.py --self-test",
    "- name: Check current Phase 1 closure packet",
    "run: python3 scripts/zigux/validate-phase1-closure.py",
    "- name: Self-test current Phase 3 interop packet",
    "- name: Check current Phase 3 interop packet",
    "- name: Run current Phase 1 shared tests-root smoke",
    "run: zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig",
    "- name: Self-test current Phase 4 repo-reality warning checker",
)

ORDERED_LINES = (
    "- name: Setup Python",
    "- name: Self-test current Phase 1 workflow preflight checker",
    "run: python3 scripts/zigux/check-phase1-workflow-preflight.py --self-test",
    "- name: Preflight current Phase 1 workflow viability",
    "run: python3 scripts/zigux/check-phase1-workflow-preflight.py",
    "- name: Setup pinned Zig toolchain",
    "- name: Validate current Phase 2 tool packet",
    "- name: Self-test current Phase 1 direct-owner checker",
    "- name: Check current Phase 1 direct-owner markers",
    "- name: Self-test current Phase 1 string review checker",
    "- name: Check current Phase 1 string review packet",
    "- name: Self-test current Phase 1 route summary checker",
    "- name: Check current Phase 1 route summary packet",
    "- name: Self-test current Phase 1 bench checker",
    "- name: Self-test current Phase 1 shared reminder checker",
    "- name: Check current Phase 1 shared reminder packet",
    "- name: Self-test current Phase 1 closure validator",
    "- name: Check current Phase 1 closure packet",
    "- name: Self-test current Phase 3 interop packet",
    "- name: Check current Phase 3 interop packet",
    "- name: Run current Phase 1 shared tests-root smoke",
    "- name: Self-test current Phase 4 repo-reality warning checker",
)

FORBIDDEN_LINES = (
    "run: python3 scripts/zigux/check-phase1-parity.py --self-test",
    "run: python3 scripts/zigux/check-phase1-parity.py",
    "run: python3 scripts/zigux/validate-phase1.py --self-test",
    "run: python3 scripts/zigux/validate-phase1.py",
    "run: zig build phase1-bench --build-file zigux/tests/build.zig",
    "run: make -C zigux phase1-validate",
    "run: make -C zigux phase1-test",
    "run: make -C zigux phase1-bench",
    "run: make -C zigux phase1",
)


def repo_root(root: str | None) -> Path:
    return Path(root).resolve() if root else DEFAULT_ROOT.resolve()


def count_stripped_lines(text: str, marker: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip() == marker.strip())


def step_indices(step_name_lines: list[str], step_names: tuple[str, ...]) -> list[int]:
    indices: list[int] = []
    for step_name in step_names:
        marker = f"- name: {step_name}"
        try:
            indices.append(step_name_lines.index(marker))
        except ValueError as exc:
            raise ValueError(marker) from exc
    return indices


def ensure_contiguous(indices: list[int], failure_label: str, failures: list[str]) -> None:
    if any(right - left != 1 for left, right in zip(indices, indices[1:])):
        failures.append(failure_label)


def collect_failures(root: Path) -> list[str]:
    workflow = root / WORKFLOW_REL
    if not workflow.is_file():
        return [f"missing_file:{WORKFLOW_REL.as_posix()}"]

    text = workflow.read_text(encoding="utf-8")
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

    stripped_lines = [line.strip() for line in text.splitlines()]
    step_name_lines = [line for line in stripped_lines if line.startswith("- name: ")]

    positions: list[int] = []
    for marker in ORDERED_LINES:
        positions.append(stripped_lines.index(marker.strip()))
    if positions != sorted(positions):
        failures.append("phase1_preflight_order:drifted")

    try:
        pre_toolchain_indices = step_indices(step_name_lines, PRE_TOOLCHAIN_STEP_NAMES)
        ensure_contiguous(
            pre_toolchain_indices,
            "phase1_preflight_insertion_window:drifted",
            failures,
        )

        packet_boundary_indices = step_indices(
            step_name_lines,
            PHASE1_PACKET_BOUNDARY_STEP_NAMES,
        )
        ensure_contiguous(
            packet_boundary_indices,
            "phase1_named_packet_window:drifted",
            failures,
        )

        post_phase1_indices = step_indices(step_name_lines, POST_PHASE1_PACKET_STEP_NAMES)
        ensure_contiguous(
            post_phase1_indices,
            "phase1_post_packet_window:drifted",
            failures,
        )
    except ValueError as exc:
        failures.append(f"missing_or_duplicate:{exc.args[0]}:count=0")

    return failures


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_sample_root(root: Path) -> None:
    write_text(
        root / WORKFLOW_REL,
        "\n".join(
            (
                "name: zigux-bootstrap",
                "jobs:",
                "  bootstrap:",
                "    steps:",
                "      - name: Checkout",
                "        uses: actions/checkout@v6.0.2",
                "      - name: Setup Python",
                "        uses: actions/setup-python@v6.2.0",
                "      - name: Self-test current Phase 1 workflow preflight checker",
                "        run: python3 scripts/zigux/check-phase1-workflow-preflight.py --self-test",
                "      - name: Preflight current Phase 1 workflow viability",
                "        run: python3 scripts/zigux/check-phase1-workflow-preflight.py",
                "      - name: Setup pinned Zig toolchain",
                "        run: ./setup-zig.sh",
                "      - name: Validate current Phase 2 tool packet",
                "        run: python3 scripts/zigux/validate-phase2.py",
                "      - name: Self-test current Phase 1 direct-owner checker",
                "        run: python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test",
                "      - name: Check current Phase 1 direct-owner markers",
                "        run: python3 scripts/zigux/check-phase1-direct-owner-markers.py",
                "      - name: Self-test current Phase 1 string review checker",
                "        run: python3 scripts/zigux/check-phase1-string-review-packet.py --self-test",
                "      - name: Check current Phase 1 string review packet",
                "        run: python3 scripts/zigux/check-phase1-string-review-packet.py",
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
                "      - name: Self-test current Phase 3 interop packet",
                "        run: python3 scripts/zigux/validate_phase3_selftest.py",
                "      - name: Check current Phase 3 interop packet",
                "        run: python3 scripts/zigux/run-phase3-checks.py",
                "      - name: Run current Phase 1 shared tests-root smoke",
                "        run: zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig",
                "      - name: Self-test current Phase 4 repo-reality warning checker",
                "        run: python3 scripts/zigux/check-phase4-repo-reality-warning.py --self-test",
            )
        )
        + "\n",
    )


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


def swap_preflight_and_zig_setup(root: Path) -> None:
    workflow = root / WORKFLOW_REL
    lines = workflow.read_text(encoding="utf-8").splitlines()
    preflight_idx = next(
        idx for idx, line in enumerate(lines) if line.strip() == "- name: Preflight current Phase 1 workflow viability"
    )
    setup_idx = next(idx for idx, line in enumerate(lines) if line.strip() == "- name: Setup pinned Zig toolchain")
    lines[preflight_idx], lines[setup_idx] = lines[setup_idx], lines[preflight_idx]
    workflow.write_text("\n".join(lines) + "\n", encoding="utf-8")


def append_forbidden(root: Path, marker: str) -> None:
    workflow = root / WORKFLOW_REL
    workflow.write_text(workflow.read_text(encoding="utf-8") + f"      - name: Forbidden\n        {marker}\n", encoding="utf-8")


def rename_step(root: Path, old_name: str, new_name: str) -> None:
    workflow = root / WORKFLOW_REL
    text = workflow.read_text(encoding="utf-8")
    old_marker = f"- name: {old_name}"
    new_marker = f"- name: {new_name}"
    if old_marker not in text:
        raise ValueError(old_marker)
    workflow.write_text(text.replace(old_marker, new_marker, 1), encoding="utf-8")


def insert_named_step_between(root: Path, before_step: str, inserted_step: str) -> None:
    workflow = root / WORKFLOW_REL
    lines = workflow.read_text(encoding="utf-8").splitlines()
    marker = f"- name: {before_step}"
    for idx, line in enumerate(lines):
        if line.strip() == marker:
            lines[idx:idx] = [f"      - name: {inserted_step}", "        run: echo drift"]
            workflow.write_text("\n".join(lines) + "\n", encoding="utf-8")
            return
    raise ValueError(marker)


def run_self_test() -> int:
    cases: list[tuple[str, object | None]] = [
        ("baseline", None),
        ("missing_workflow", lambda root: (root / WORKFLOW_REL).unlink()),
        ("missing_preflight_selftest", lambda root: remove_line(root, "run: python3 scripts/zigux/check-phase1-workflow-preflight.py --self-test")),
        ("duplicate_preflight_live", lambda root: duplicate_line(root, "run: python3 scripts/zigux/check-phase1-workflow-preflight.py")),
        ("missing_smoke", lambda root: remove_line(root, "run: zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig")),
        ("bad_order", swap_preflight_and_zig_setup),
        ("forbidden_validate_phase1", lambda root: append_forbidden(root, "run: python3 scripts/zigux/validate-phase1.py")),
        ("forbidden_bench_live", lambda root: append_forbidden(root, "run: zig build phase1-bench --build-file zigux/tests/build.zig")),
        ("renamed_phase1_packet_step", lambda root: rename_step(root, "Check current Phase 1 direct-owner markers", "Check current Phase 1 direct-owner packet")),
        ("split_phase1_named_window", lambda root: insert_named_step_between(root, "Self-test current Phase 1 closure validator", "Unexpected current Phase 1 detour")),
    ]

    for name, mutate in cases:
        with tempfile.TemporaryDirectory(prefix="phase1-workflow-preflight-") as tmpdir:
            root = Path(tmpdir)
            build_sample_root(root)
            if mutate is not None:
                mutate(root)
            failures = collect_failures(root)
            if name == "baseline":
                if failures:
                    print(f"phase1-workflow-preflight:{name}:unexpected={failures}")
                    return 1
            elif not failures:
                print(f"phase1-workflow-preflight:{name}:expected_failure")
                return 1

    print("PHASE1_WORKFLOW_PREFLIGHT_SELF_TEST=pass")
    print(f"PHASE1_WORKFLOW_PREFLIGHT_SELF_TEST_CASE_COUNT={len(cases)}")
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

    print("PHASE1_WORKFLOW_PREFLIGHT_READY=pass")
    print("PHASE1_WORKFLOW_PREFLIGHT_INSERTION_POINT=Setup Python,Self-test current Phase 1 workflow preflight checker,Preflight current Phase 1 workflow viability,Setup pinned Zig toolchain")
    print(f"PHASE1_WORKFLOW_PREFLIGHT_REQUIRED_LINE_COUNT={len(EXACT_ONCE_LINES)}")
    print("PHASE1_WORKFLOW_PHASE1_PACKET_WINDOW=Validate current Phase 2 tool packet,Self-test current Phase 1 direct-owner checker,Check current Phase 1 direct-owner markers,Self-test current Phase 1 string review checker,Check current Phase 1 string review packet,Self-test current Phase 1 route summary checker,Check current Phase 1 route summary packet,Self-test current Phase 1 bench checker,Self-test current Phase 1 shared reminder checker,Check current Phase 1 shared reminder packet,Self-test current Phase 1 closure validator,Check current Phase 1 closure packet,Self-test current Phase 3 interop packet")
    print("PHASE1_WORKFLOW_PHASE1_POST_PACKET=Check current Phase 1 closure packet,Self-test current Phase 3 interop packet,Check current Phase 3 interop packet,Run current Phase 1 shared tests-root smoke,Self-test current Phase 4 repo-reality warning checker")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
