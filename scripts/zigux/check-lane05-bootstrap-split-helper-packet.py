#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
WORKFLOW_PATH = Path(".github/workflows/zigux-bootstrap.yml")

STAGE_HELPER_SELF_TEST_STEP = "- name: Self-test current staged pinned Zig archive helper"
STAGE_HELPER_SELF_TEST_CMD = "python3 scripts/zigux/stage-pinned-zig-archive.py --self-test"
STAGE_HELPER_PACKET_STEP = "- name: Check current Lane 05 stage helper selftest packet"
STAGE_HELPER_PACKET_CMD = "python3 scripts/zigux/check-lane05-stage-helper-selftest.py"
SPLIT_HELPER_SELF_TEST_STEP = "- name: Self-test current split pinned Zig archive helper"
SPLIT_HELPER_SELF_TEST_CMD = "python3 scripts/zigux/split-pinned-zig-archive.py --self-test"
SPLIT_HELPER_CHECKER_SELF_TEST_STEP = "- name: Self-test current Lane 05 split helper selftest checker"
SPLIT_HELPER_CHECKER_SELF_TEST_CMD = "python3 scripts/zigux/check-lane05-split-helper-selftest.py --self-test"
SPLIT_HELPER_PACKET_STEP = "- name: Check current Lane 05 split helper selftest packet"
SPLIT_HELPER_PACKET_CMD = "python3 scripts/zigux/check-lane05-split-helper-selftest.py"
NEXT_STEP = "- name: Self-test current Phase 2 fixdep gate checker"


def require_marker(text: str, marker: str, label: str) -> None:
    if marker not in text:
        raise SystemExit(f"lane05 bootstrap split-helper packet missing {label}: {marker}")


def require_exact_line(text: str, line: str, label: str) -> None:
    count = sum(1 for current in text.splitlines() if current.strip() == line)
    if count != 1:
        raise SystemExit(
            "lane05 bootstrap split-helper packet expected exactly "
            f"1 {label} line `{line}`, found {count}"
        )


def require_order(text: str, earlier: str, later: str, label: str) -> None:
    earlier_index = text.find(earlier)
    later_index = text.find(later)
    if earlier_index == -1 or later_index == -1:
        raise SystemExit(
            f"lane05 bootstrap split-helper packet missing ordered markers for {label}"
        )
    if earlier_index >= later_index:
        raise SystemExit(
            "lane05 bootstrap split-helper packet expected "
            f"{label} `{earlier}` before `{later}`"
        )


def check_workflow(text: str) -> None:
    for marker, label in (
        (STAGE_HELPER_SELF_TEST_STEP, "stage helper self-test step"),
        (STAGE_HELPER_SELF_TEST_CMD, "stage helper self-test command"),
        (STAGE_HELPER_PACKET_STEP, "stage helper packet step"),
        (STAGE_HELPER_PACKET_CMD, "stage helper packet command"),
        (SPLIT_HELPER_SELF_TEST_STEP, "split helper self-test step"),
        (SPLIT_HELPER_SELF_TEST_CMD, "split helper self-test command"),
        (SPLIT_HELPER_CHECKER_SELF_TEST_STEP, "split helper checker self-test step"),
        (SPLIT_HELPER_CHECKER_SELF_TEST_CMD, "split helper checker self-test command"),
        (SPLIT_HELPER_PACKET_STEP, "split helper packet step"),
        (SPLIT_HELPER_PACKET_CMD, "split helper packet command"),
        (NEXT_STEP, "next phase anchor"),
    ):
        require_marker(text, marker, label)

    for line, label in (
        (f"run: {STAGE_HELPER_SELF_TEST_CMD}", "stage helper self-test command"),
        (f"run: {STAGE_HELPER_PACKET_CMD}", "stage helper packet command"),
        (f"run: {SPLIT_HELPER_SELF_TEST_CMD}", "split helper self-test command"),
        (
            f"run: {SPLIT_HELPER_CHECKER_SELF_TEST_CMD}",
            "split helper checker self-test command",
        ),
        (f"run: {SPLIT_HELPER_PACKET_CMD}", "split helper packet command"),
    ):
        require_exact_line(text, line, label)

    for step, label in (
        (STAGE_HELPER_SELF_TEST_STEP, "stage helper self-test step"),
        (STAGE_HELPER_PACKET_STEP, "stage helper packet step"),
        (SPLIT_HELPER_SELF_TEST_STEP, "split helper self-test step"),
        (SPLIT_HELPER_CHECKER_SELF_TEST_STEP, "split helper checker self-test step"),
        (SPLIT_HELPER_PACKET_STEP, "split helper packet step"),
    ):
        require_exact_line(text, step, label)

    require_order(
        text,
        STAGE_HELPER_SELF_TEST_STEP,
        STAGE_HELPER_PACKET_STEP,
        "lane05 anchor order",
    )
    require_order(
        text,
        STAGE_HELPER_PACKET_STEP,
        SPLIT_HELPER_SELF_TEST_STEP,
        "lane05 step order",
    )
    require_order(
        text,
        SPLIT_HELPER_SELF_TEST_STEP,
        SPLIT_HELPER_CHECKER_SELF_TEST_STEP,
        "lane05 step order",
    )
    require_order(
        text,
        SPLIT_HELPER_CHECKER_SELF_TEST_STEP,
        SPLIT_HELPER_PACKET_STEP,
        "lane05 step order",
    )
    require_order(text, SPLIT_HELPER_PACKET_STEP, NEXT_STEP, "lane05 step order")


def write_sample_root(root: Path) -> None:
    workflow = root / WORKFLOW_PATH
    workflow.parent.mkdir(parents=True, exist_ok=True)
    workflow.write_text(
        "\n".join(
            (
                "name: zigux-bootstrap",
                "jobs:",
                "  bootstrap:",
                "    steps:",
                "      - name: Self-test current staged pinned Zig archive helper",
                "        run: python3 scripts/zigux/stage-pinned-zig-archive.py --self-test",
                "      - name: Check current Lane 05 stage helper selftest packet",
                "        run: python3 scripts/zigux/check-lane05-stage-helper-selftest.py",
                "      - name: Self-test current split pinned Zig archive helper",
                "        run: python3 scripts/zigux/split-pinned-zig-archive.py --self-test",
                "      - name: Self-test current Lane 05 split helper selftest checker",
                "        run: python3 scripts/zigux/check-lane05-split-helper-selftest.py --self-test",
                "      - name: Check current Lane 05 split helper selftest packet",
                "        run: python3 scripts/zigux/check-lane05-split-helper-selftest.py",
                "      - name: Self-test current Phase 2 fixdep gate checker",
                "        run: python3 scripts/zigux/check-phase2-fixdep-gate.py --self-test",
            )
        )
        + "\n",
        encoding="utf-8",
    )


def run_self_test() -> int:
    good_workflow = """name: zigux-bootstrap
jobs:
  bootstrap:
    steps:
      - name: Self-test current staged pinned Zig archive helper
        run: python3 scripts/zigux/stage-pinned-zig-archive.py --self-test
      - name: Check current Lane 05 stage helper selftest packet
        run: python3 scripts/zigux/check-lane05-stage-helper-selftest.py
      - name: Self-test current split pinned Zig archive helper
        run: python3 scripts/zigux/split-pinned-zig-archive.py --self-test
      - name: Self-test current Lane 05 split helper selftest checker
        run: python3 scripts/zigux/check-lane05-split-helper-selftest.py --self-test
      - name: Check current Lane 05 split helper selftest packet
        run: python3 scripts/zigux/check-lane05-split-helper-selftest.py
      - name: Self-test current Phase 2 fixdep gate checker
        run: python3 scripts/zigux/check-phase2-fixdep-gate.py --self-test
"""
    check_workflow(good_workflow)
    case_count = 1

    for broken_text, expected in (
        (
            good_workflow.replace(
                "      - name: Self-test current split pinned Zig archive helper\n"
                "        run: python3 scripts/zigux/split-pinned-zig-archive.py --self-test\n",
                "",
                1,
            ),
            SPLIT_HELPER_SELF_TEST_STEP,
        ),
        (
            good_workflow.replace(
                "        run: python3 scripts/zigux/check-lane05-split-helper-selftest.py --self-test\n",
                "",
                1,
            ),
            SPLIT_HELPER_CHECKER_SELF_TEST_CMD,
        ),
        (
            good_workflow.replace(
                "      - name: Check current Lane 05 split helper selftest packet\n"
                "        run: python3 scripts/zigux/check-lane05-split-helper-selftest.py\n",
                "",
                1,
            ),
            SPLIT_HELPER_PACKET_STEP,
        ),
        (
            good_workflow.replace(
                "      - name: Check current Lane 05 stage helper selftest packet\n"
                "        run: python3 scripts/zigux/check-lane05-stage-helper-selftest.py\n",
                "",
                1,
            ),
            STAGE_HELPER_PACKET_STEP,
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
        "      - name: Self-test current split pinned Zig archive helper\n",
        "      - name: Self-test current split pinned Zig archive helper\n"
        "      - name: Self-test current split pinned Zig archive helper\n",
        1,
    )
    try:
        check_workflow(duplicate_step)
    except SystemExit as exc:
        assert SPLIT_HELPER_SELF_TEST_STEP in str(exc), str(exc)
        case_count += 1
    else:
        raise AssertionError("expected duplicate split helper step failure")

    reordered_steps = good_workflow.replace(
        "      - name: Self-test current split pinned Zig archive helper\n"
        "        run: python3 scripts/zigux/split-pinned-zig-archive.py --self-test\n"
        "      - name: Self-test current Lane 05 split helper selftest checker\n"
        "        run: python3 scripts/zigux/check-lane05-split-helper-selftest.py --self-test\n",
        "      - name: Self-test current Lane 05 split helper selftest checker\n"
        "        run: python3 scripts/zigux/check-lane05-split-helper-selftest.py --self-test\n"
        "      - name: Self-test current split pinned Zig archive helper\n"
        "        run: python3 scripts/zigux/split-pinned-zig-archive.py --self-test\n",
        1,
    )
    try:
        check_workflow(reordered_steps)
    except SystemExit as exc:
        assert "lane05 step order" in str(exc), str(exc)
        case_count += 1
    else:
        raise AssertionError("expected reordered split-helper steps failure")

    with tempfile.TemporaryDirectory(prefix="lane05_bootstrap_split_helper_packet_") as tmp_dir:
        sample_root = Path(tmp_dir)
        write_sample_root(sample_root)
        check_workflow((sample_root / WORKFLOW_PATH).read_text(encoding="utf-8"))
        case_count += 1

    print("LANE05_BOOTSTRAP_SPLIT_HELPER_PACKET_SELF_TEST=pass")
    print(f"LANE05_BOOTSTRAP_SPLIT_HELPER_PACKET_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the main bootstrap workflow keeps the Lane 05 split-helper packet explicit."
    )
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument(
        "--root",
        type=Path,
        default=ROOT,
        help="Repository root containing .github/workflows/zigux-bootstrap.yml",
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

    workflow_path = args.root.resolve() / WORKFLOW_PATH
    check_workflow(workflow_path.read_text(encoding="utf-8"))
    print("LANE05_BOOTSTRAP_SPLIT_HELPER_PACKET=pass")
    print(f"LANE05_BOOTSTRAP_SPLIT_HELPER_PACKET_WORKFLOW={workflow_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
