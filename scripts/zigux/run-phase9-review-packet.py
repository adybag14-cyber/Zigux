#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import subprocess
import sys
import tempfile


SELF_PATH = Path(__file__).resolve()

PYTHON_CHECKERS = [
    "scripts/zigux/check-phase9-review-checklist-phase-boundaries.py",
    "scripts/zigux/check-phase9-freeze-map-study-boundaries.py",
    "scripts/zigux/check-phase9-trace-events-runtime-packet.py",
]

ZIG_TESTS = [
    "samples/zigux/runtime_trace_events.zig",
    "samples/zigux/runtime_trace_events_unregistered_gate.zig",
    "samples/zigux/runtime_trace_events_exit_rollback_guard.zig",
    "samples/zigux/runtime_trace_events_registration_reentry_gate.zig",
    "zigux/tests/runtime_trace_events_survey.zig",
]


def infer_repo_root() -> Path:
    for candidate in [SELF_PATH.parent, *SELF_PATH.parents]:
        if (candidate / "Documentation/zigux/review-checklist.md").exists():
            return candidate
    return SELF_PATH.parent


ROOT = infer_repo_root()


def build_command_plan(repo_root: Path, zig_bin: str, checks_only: bool) -> list[list[str]]:
    commands: list[list[str]] = []
    for rel_path in PYTHON_CHECKERS:
        commands.append([sys.executable, str(repo_root / rel_path)])
    if not checks_only:
        for rel_path in ZIG_TESTS:
            commands.append([zig_bin, "test", str(repo_root / rel_path)])
    return commands


def run_command_plan(commands: list[list[str]], repo_root: Path) -> int:
    for command in commands:
        printable = " ".join(command)
        print(f"PHASE9_REVIEW_PACKET_STEP={printable}")
        subprocess.run(command, cwd=repo_root, check=True)
    return 0


def run_self_test() -> int:
    repo_root = Path(tempfile.gettempdir()) / "zigux-phase9-review-packet-fixture"
    commands = build_command_plan(repo_root, "zig-custom", checks_only=False)
    expected = [
        [sys.executable, str(repo_root / PYTHON_CHECKERS[0])],
        [sys.executable, str(repo_root / PYTHON_CHECKERS[1])],
        [sys.executable, str(repo_root / PYTHON_CHECKERS[2])],
        ["zig-custom", "test", str(repo_root / ZIG_TESTS[0])],
        ["zig-custom", "test", str(repo_root / ZIG_TESTS[1])],
        ["zig-custom", "test", str(repo_root / ZIG_TESTS[2])],
        ["zig-custom", "test", str(repo_root / ZIG_TESTS[3])],
        ["zig-custom", "test", str(repo_root / ZIG_TESTS[4])],
    ]
    if commands != expected:
        raise SystemExit(f"unexpected full command plan: {commands!r}")

    checks_only_commands = build_command_plan(repo_root, "zig-custom", checks_only=True)
    expected_checks_only = expected[: len(PYTHON_CHECKERS)]
    if checks_only_commands != expected_checks_only:
        raise SystemExit(f"unexpected checks-only command plan: {checks_only_commands!r}")

    print("PHASE9_REVIEW_PACKET_SELF_TEST=pass")
    print(f"PHASE9_REVIEW_PACKET_CHECKER_COUNT={len(PYTHON_CHECKERS)}")
    print(f"PHASE9_REVIEW_PACKET_ZIG_TEST_COUNT={len(ZIG_TESTS)}")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Run the current Phase 9 review-first runtime packet checks. "
            "This keeps the narrow trace-events packet and freeze-boundary checks "
            "together without implying a dedicated phase9 Makefile route."
        )
    )
    parser.add_argument("--repo-root", type=Path, default=ROOT, help="repository root to inspect")
    parser.add_argument("--zig", default="zig", help="zig binary to use for the runtime sample tests")
    parser.add_argument(
        "--checks-only",
        action="store_true",
        help="run only the shipped Python review-packet guards and skip Zig sample replays",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="print the command plan instead of executing it",
    )
    parser.add_argument("--self-test", action="store_true", help="run the built-in plan self-test")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        return run_self_test()

    commands = build_command_plan(args.repo_root, args.zig, args.checks_only)
    if args.dry_run:
        for command in commands:
            print("PHASE9_REVIEW_PACKET_PLAN=" + " ".join(command))
        return 0

    return run_command_plan(commands, args.repo_root)


if __name__ == "__main__":
    raise SystemExit(main())
