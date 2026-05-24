#!/usr/bin/env python3
"""Guard the current Phase 1 workflow preflight packet in zigux-bootstrap."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent
WORKFLOW_REL = Path(".github/workflows/zigux-bootstrap.yml")

PREFLIGHT_STEP_BLOCK = (
    "- name: Setup Python",
    "- name: Self-test current Phase 1 workflow preflight checker",
    "- name: Preflight current Phase 1 workflow viability",
    "- name: Setup pinned Zig toolchain",
)

EXACT_ONCE_LINES = (
    "- name: Setup Python",
    "- name: Self-test current Phase 1 workflow preflight checker",
    "run: python3 scripts/zigux/check-phase1-workflow-preflight.py --self-test",
    "- name: Preflight current Phase 1 workflow viability",
    "run: python3 scripts/zigux/check-phase1-workflow-preflight.py",
    "- name: Setup pinned Zig toolchain",
    "run: python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test",
    "run: python3 scripts/zigux/check-phase1-direct-owner-markers.py",
    "run: python3 scripts/zigux/check-phase1-string-review-packet.py --self-test",
    "run: python3 scripts/zigux/check-phase1-string-review-packet.py",
    "run: python3 scripts/zigux/check-phase1-route-summary-counts.py --self-test",
    "run: python3 scripts/zigux/check-phase1-route-summary-counts.py",
    "run: python3 scripts/zigux/check-phase1-bench.py --self-test",
    "run: python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test",
    "run: python3 scripts/zigux/check-phase1-shared-reminder-packet.py",
    "run: python3 scripts/zigux/validate-phase1-closure.py --self-test",
    "run: python3 scripts/zigux/validate-phase1-closure.py",
    "run: zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig",
)

ORDERED_LINES = (
    "- name: Setup Python",
    "- name: Self-test current Phase 1 workflow preflight checker",
    "run: python3 scripts/zigux/check-phase1-workflow-preflight.py --self-test",
    "- name: Preflight current Phase 1 workflow viability",
    "run: python3 scripts/zigux/check-phase1-workflow-preflight.py",
    "- name: Setup pinned Zig toolchain",
    "run: python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test",
    "run: python3 scripts/zigux/check-phase1-direct-owner-markers.py",
    "run: python3 scripts/zigux/check-phase1-string-review-packet.py --self-test",
    "run: python3 scripts/zigux/check-phase1-string-review-packet.py",
    "run: python3 scripts/zigux/check-phase1-route-summary-counts.py --self-test",
    "run: python3 scripts/zigux/check-phase1-route-summary-counts.py",
    "run: python3 scripts/zigux/check-phase1-bench.py --self-test",
    "run: python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test",
    "run: python3 scripts/zigux/check-phase1-shared-reminder-packet.py",
    "run: python3 scripts/zigux/validate-phase1-closure.py --self-test",
    "run: python3 scripts/zigux/validate-phase1-closure.py",
    "run: zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig",
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
    positions: list[int] = []
    for marker in ORDERED_LINES:
        positions.append(stripped_lines.index(marker.strip()))
    if positions != sorted(positions):
        failures.append("phase1_preflight_order:drifted")

    step_names = [line for line in stripped_lines if line.startswith("- name: ")]
    preflight_block_start = step_names.index(PREFLIGHT_STEP_BLOCK[0])
    if tuple(step_names[preflight_block_start : preflight_block_start + len(PREFLIGHT_STEP_BLOCK)]) != PREFLIGHT_STEP_BLOCK:
        failures.append("phase1_preflight_step_block:drifted")

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
                "      - name: Run current Phase 1 shared tests-root smoke",
                "        run: zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig",
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


def duplicate_line(root: Path, marker: str) -> None:
    workflow = root / WORKFLOW_REL
    lines = workflow.read_text(encoding="utf-8").splitlines()
    for idx, line in enumerate(lines):
        if line.strip() == marker.strip():
            lines.insert(idx + 1, line)
            workflow.write_text("\n".join(lines) + "\n", encoding="utf-8")
            return
    raise ValueError(marker)


def insert_step_after(root: Path, after_step_name: str, step_name: str, run_line: str) -> None:
    workflow = root / WORKFLOW_REL
    lines = workflow.read_text(encoding="utf-8").splitlines()
    for idx, line in enumerate(lines):
        if line.strip() == after_step_name.strip():
            lines.insert(idx + 1, "      - name: " + step_name)
            lines.insert(idx + 2, "        " + run_line.strip())
            workflow.write_text("\n".join(lines) + "\n", encoding="utf-8")
            return
    raise ValueError(after_step_name)


def swap_preflight_and_zig_setup(root: Path) -> None:
    workflow = root / WORKFLOW_REL
    lines = workflow.read_text(encoding="utf-8").splitlines()
    preflight_idx = next(
        idx for idx, line in enumerate(lines) if line.strip() == "run: python3 scripts/zigux/check-phase1-workflow-preflight.py"
    )
    setup_idx = next(idx for idx, line in enumerate(lines) if line.strip() == "- name: Setup pinned Zig toolchain")
    lines[preflight_idx], lines[setup_idx] = lines[setup_idx], lines[preflight_idx]
    workflow.write_text("\n".join(lines) + "\n", encoding="utf-8")


def append_forbidden(root: Path, marker: str) -> None:
    workflow = root / WORKFLOW_REL
    workflow.write_text(workflow.read_text(encoding="utf-8") + f"      - name: Forbidden\n        {marker}\n", encoding="utf-8")


def run_self_test() -> int:
    cases: list[tuple[str, object | None]] = [
        ("baseline", None),
        ("missing_workflow", lambda root: (root / WORKFLOW_REL).unlink()),
        (
            "missing_preflight_selftest_step_name",
            lambda root: remove_line(root, "- name: Self-test current Phase 1 workflow preflight checker"),
        ),
        (
            "renamed_preflight_live_step_name",
            lambda root: replace_line(
                root,
                "- name: Preflight current Phase 1 workflow viability",
                "- name: Preflight current Phase 1 workflow check",
            ),
        ),
        ("missing_preflight_selftest", lambda root: remove_line(root, "run: python3 scripts/zigux/check-phase1-workflow-preflight.py --self-test")),
        ("duplicate_preflight_live", lambda root: duplicate_line(root, "run: python3 scripts/zigux/check-phase1-workflow-preflight.py")),
        (
            "inserted_step_before_preflight_selftest",
            lambda root: insert_step_after(
                root,
                "- name: Setup Python",
                "Inserted helper",
                "run: python3 scripts/zigux/check-zig-toolchain.py --self-test",
            ),
        ),
        (
            "inserted_step_before_zig_setup",
            lambda root: insert_step_after(
                root,
                "- name: Preflight current Phase 1 workflow viability",
                "Inserted helper",
                "run: python3 scripts/zigux/check-zig-toolchain.py --policy-only",
            ),
        ),
        ("missing_smoke", lambda root: remove_line(root, "run: zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig")),
        ("bad_order", swap_preflight_and_zig_setup),
        ("forbidden_validate_phase1", lambda root: append_forbidden(root, "run: python3 scripts/zigux/validate-phase1.py")),
        ("forbidden_bench_live", lambda root: append_forbidden(root, "run: zig build phase1-bench --build-file zigux/tests/build.zig")),
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
    print(
        "PHASE1_WORKFLOW_PREFLIGHT_INSERTION_POINT="
        "Setup Python,Self-test current Phase 1 workflow preflight checker,"
        "Preflight current Phase 1 workflow viability,Setup pinned Zig toolchain"
    )
    print("PHASE1_WORKFLOW_PREFLIGHT_STEP_BLOCK=contiguous")
    print(f"PHASE1_WORKFLOW_PREFLIGHT_REQUIRED_LINE_COUNT={len(EXACT_ONCE_LINES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())