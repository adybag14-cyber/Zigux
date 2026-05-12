#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import subprocess
import sys
import tempfile

from phase3_catalog import discover_phase3_slices
from phase3_check_lib import run_phase3_check

ROOT = Path(__file__).resolve().parents[2]


def command_plan_for_slug(slug: str) -> tuple[tuple[str, ...], ...]:
    if slug == "abi":
        return (
            (sys.executable, "scripts/zigux/check-phase3-abi.py"),
            ("zig", "build", "phase3-test", "--build-file", "zigux/tests/build.zig"),
            ("zig", "build", "phase3-dump", "--build-file", "zigux/tests/build.zig"),
        )
    return ()


def run_command_plan(
    commands: tuple[tuple[str, ...], ...],
    root: Path,
    runner=subprocess.run,
) -> int:
    for command in commands:
        result = runner(list(command), cwd=root, check=False)
        if result.returncode != 0:
            return result.returncode
    return 0


def run_slice_entry(entry, root: Path = ROOT) -> int:
    command_plan = command_plan_for_slug(entry.slug)
    if command_plan:
        return run_command_plan(command_plan, root)
    return run_phase3_check(entry.slug, description=entry.description)


def select_slices(entries: list[object], selected_slugs: list[str]) -> list[object]:
    slices = list(entries)
    selected = set(selected_slugs)
    if selected:
        slices = [entry for entry in slices if entry.slug in selected]
        missing = sorted(selected.difference({entry.slug for entry in slices}))
        if missing:
            raise SystemExit(f"unknown Phase 3 slugs: {', '.join(missing)}")
    return slices


def execute_slices(entries: list[object], fail_fast: bool, runner) -> list[str]:
    failures: list[str] = []
    for entry in entries:
        print(f"PHASE3_RUN={entry.slug}")
        rc = runner(entry)
        if rc != 0:
            failures.append(entry.slug)
            if fail_fast:
                break
    return failures


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_runner_selftest_") as tmp_dir_str:
        tmp_dir = Path(tmp_dir_str)
        alpha = tmp_dir / "check-phase3-alpha.py"
        alpha.write_text("# alpha\n", encoding="utf-8")
        entries = [
            type("Entry", (), {"slug": "alpha", "description": "alpha"})(),
            type("Entry", (), {"slug": "beta", "description": "beta"})(),
            type("Entry", (), {"slug": "gamma", "description": "gamma"})(),
        ]
        assert [entry.slug for entry in select_slices(entries, [])] == ["alpha", "beta", "gamma"]
        assert [entry.slug for entry in select_slices(entries, ["beta"])] == ["beta"]
        try:
            select_slices(entries, ["missing"])
        except SystemExit as exc:
            assert str(exc) == "unknown Phase 3 slugs: missing"
        else:
            raise AssertionError("expected missing slug failure")

        abi_plan = command_plan_for_slug("abi")
        assert abi_plan == (
            (sys.executable, "scripts/zigux/check-phase3-abi.py"),
            ("zig", "build", "phase3-test", "--build-file", "zigux/tests/build.zig"),
            ("zig", "build", "phase3-dump", "--build-file", "zigux/tests/build.zig"),
        )
        assert command_plan_for_slug("bitmap-cpumask") == ()

        observed_calls: list[tuple[tuple[str, ...], Path, bool]] = []

        def fake_runner_ok(command, cwd, check):
            observed_calls.append((tuple(command), cwd, check))
            return type("Result", (), {"returncode": 0})()

        assert run_command_plan(abi_plan, tmp_dir, runner=fake_runner_ok) == 0
        assert observed_calls == [
            ((sys.executable, "scripts/zigux/check-phase3-abi.py"), tmp_dir, False),
            (("zig", "build", "phase3-test", "--build-file", "zigux/tests/build.zig"), tmp_dir, False),
            (("zig", "build", "phase3-dump", "--build-file", "zigux/tests/build.zig"), tmp_dir, False),
        ]

        observed_calls.clear()

        def fake_runner_fail_second(command, cwd, check):
            observed_calls.append((tuple(command), cwd, check))
            returncode = 7 if len(observed_calls) == 2 else 0
            return type("Result", (), {"returncode": returncode})()

        assert run_command_plan(abi_plan, tmp_dir, runner=fake_runner_fail_second) == 7
        assert observed_calls == [
            ((sys.executable, "scripts/zigux/check-phase3-abi.py"), tmp_dir, False),
            (("zig", "build", "phase3-test", "--build-file", "zigux/tests/build.zig"), tmp_dir, False),
        ]

        calls: list[str] = []

        def fake_entry_runner(entry) -> int:
            calls.append(entry.slug)
            return 1 if entry.slug == "beta" else 0

        failures = execute_slices(entries, fail_fast=False, runner=fake_entry_runner)
        assert failures == ["beta"]
        assert calls == ["alpha", "beta", "gamma"]
        calls.clear()
        failures = execute_slices(entries, fail_fast=True, runner=fake_entry_runner)
        assert failures == ["beta"]
        assert calls == ["alpha", "beta"]
    print("PHASE3_RUNNER_SELF_TEST=pass")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Run focused Phase 3 parity checks.")
    parser.add_argument("--list", action="store_true")
    parser.add_argument("--slug", action="append", default=[])
    parser.add_argument("--fail-fast", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    slices = select_slices(discover_phase3_slices(), args.slug)
    if args.list:
        for entry in slices:
            print(entry.slug)
        return 0
    if not slices:
        raise SystemExit("no Phase 3 checks discovered")

    failures = execute_slices(
        slices,
        fail_fast=args.fail_fast,
        runner=lambda entry: run_slice_entry(entry),
    )
    if failures:
        print("PHASE3_RUN_STATUS=fail")
        print("PHASE3_FAILED_SLUGS=" + ",".join(failures))
        return 1
    print("PHASE3_RUN_STATUS=pass")
    print(f"PHASE3_RUN_COUNT={len(slices)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
