#!/usr/bin/env python3
from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path
import tempfile

from phase3_catalog import discover_phase3_slices
from phase3_check_lib import run_phase3_check


ROOT = Path(__file__).resolve().parents[2]


def validate_entries(entries: list[object]) -> None:
    duplicate_slugs = sorted(slug for slug, count in Counter(entry.slug for entry in entries).items() if count > 1)
    if duplicate_slugs:
        raise SystemExit(f"duplicate Phase 3 slugs: {', '.join(duplicate_slugs)}")

    duplicate_build_steps = sorted(
        build_step for build_step, count in Counter(entry.build_step for entry in entries).items() if count > 1
    )
    if duplicate_build_steps:
        raise SystemExit(f"duplicate Phase 3 build steps: {', '.join(duplicate_build_steps)}")


def select_slices(entries: list[object], selected_slugs: list[str]) -> list[object]:
    slices = list(entries)
    selected = set(selected_slugs)
    if selected:
        slices = [entry for entry in slices if entry.slug in selected]
        missing = sorted(selected.difference({entry.slug for entry in slices}))
        if missing:
            raise SystemExit(f"unknown Phase 3 slugs: {', '.join(missing)}")
    return slices


def describe_slices(entries: list[object]) -> list[str]:
    return [f"{entry.slug}\t{entry.build_step}\t{entry.description}" for entry in entries]


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
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_runner_selftest_") as tmp_dir_str:
        tmp_dir = Path(tmp_dir_str)
        alpha = tmp_dir / "check-phase3-alpha.py"
        alpha.write_text("# alpha\n", encoding="utf-8")

        entries = [
            type("Entry", (), {"slug": "alpha", "build_step": "phase3-alpha-dump", "description": "alpha", "check_script": alpha})(),
            type("Entry", (), {"slug": "beta", "build_step": "phase3-beta-dump", "description": "beta", "check_script": tmp_dir / "check-phase3-beta.py"})(),
            type("Entry", (), {"slug": "gamma", "build_step": "phase3-gamma-dump", "description": "gamma", "check_script": tmp_dir / "check-phase3-gamma.py"})(),
        ]

        validate_entries(entries)
        case_count += 1
        assert describe_slices(entries) == [
            "alpha\tphase3-alpha-dump\talpha",
            "beta\tphase3-beta-dump\tbeta",
            "gamma\tphase3-gamma-dump\tgamma",
        ]
        case_count += 1
        assert [entry.slug for entry in select_slices(entries, [])] == ["alpha", "beta", "gamma"]
        case_count += 1
        assert [entry.slug for entry in select_slices(entries, ["beta"])] == ["beta"]
        case_count += 1
        try:
            select_slices(entries, ["missing"])
        except SystemExit as exc:
            assert str(exc) == "unknown Phase 3 slugs: missing"
        else:
            raise AssertionError("expected missing slug to fail")
        case_count += 1

        try:
            validate_entries(
                entries
                + [type("Entry", (), {"slug": "alpha", "build_step": "phase3-delta-dump", "description": "delta", "check_script": tmp_dir / "check-phase3-delta.py"})()]
            )
        except SystemExit as exc:
            assert str(exc) == "duplicate Phase 3 slugs: alpha"
        else:
            raise AssertionError("expected duplicate slug to fail")
        case_count += 1

        try:
            validate_entries(
                entries
                + [type("Entry", (), {"slug": "delta", "build_step": "phase3-beta-dump", "description": "delta", "check_script": tmp_dir / "check-phase3-delta.py"})()]
            )
        except SystemExit as exc:
            assert str(exc) == "duplicate Phase 3 build steps: phase3-beta-dump"
        else:
            raise AssertionError("expected duplicate build step to fail")
        case_count += 1

        calls: list[tuple[str, str, str]] = []

        def fake_runner(entry) -> int:
            calls.append((entry.slug, entry.description, entry.build_step))
            return 1 if entry.slug == "beta" else 0

        failures = execute_slices(select_slices(entries, []), fail_fast=False, runner=fake_runner)
        assert failures == ["beta"]
        assert calls == [
            ("alpha", "alpha", "phase3-alpha-dump"),
            ("beta", "beta", "phase3-beta-dump"),
            ("gamma", "gamma", "phase3-gamma-dump"),
        ]
        case_count += 1

        calls.clear()
        failures = execute_slices(select_slices(entries, []), fail_fast=True, runner=fake_runner)
        assert failures == ["beta"]
        assert calls == [
            ("alpha", "alpha", "phase3-alpha-dump"),
            ("beta", "beta", "phase3-beta-dump"),
        ]
        case_count += 1

    print("PHASE3_RUNNER_SELF_TEST=pass")
    print(f"PHASE3_RUNNER_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="List or execute discovered Phase 3 parity checks.")
    parser.add_argument("--list", action="store_true", help="List discovered Phase 3 check slugs.")
    parser.add_argument("--describe", action="store_true", help="List discovered Phase 3 slugs with build steps and descriptions.")
    parser.add_argument(
        "--slug",
        action="append",
        default=[],
        help="Only run the named Phase 3 slug. Repeat to run more than one.",
    )
    parser.add_argument("--zig", help="Forward an explicit zig executable path to each check.")
    parser.add_argument("--cc", help="Forward an explicit C compiler path to each check.")
    parser.add_argument("--fail-fast", action="store_true", help="Stop after the first failing check.")
    parser.add_argument("--self-test", action="store_true", help="Run isolated slug-selection checks without executing Phase 3 builds.")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    slices = discover_phase3_slices()
    validate_entries(slices)
    slices = select_slices(slices, args.slug)

    if args.list:
        for entry in slices:
            print(entry.slug)
        return 0

    if args.describe:
        for line in describe_slices(slices):
            print(line)
        return 0

    if not slices:
        raise SystemExit("no Phase 3 checks discovered")

    def runner(entry) -> int:
        argv: list[str] = []
        if args.zig:
            argv.extend(["--zig", args.zig])
        if args.cc:
            argv.extend(["--cc", args.cc])
        return run_phase3_check(entry.slug, description=entry.description, build_step=entry.build_step, argv=argv)

    failures = execute_slices(slices, fail_fast=args.fail_fast, runner=runner)

    if failures:
        print("PHASE3_RUN_STATUS=fail")
        print("PHASE3_FAILED_SLUGS=" + ",".join(failures))
        return 1

    print("PHASE3_RUN_STATUS=pass")
    print(f"PHASE3_RUN_COUNT={len(slices)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
