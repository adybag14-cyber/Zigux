#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

from phase3_catalog import discover_phase3_slices
from phase3_check_lib import run_phase3_check


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

        calls: list[str] = []
        def fake_runner(entry) -> int:
            calls.append(entry.slug)
            return 1 if entry.slug == "beta" else 0

        failures = execute_slices(entries, fail_fast=False, runner=fake_runner)
        assert failures == ["beta"]
        assert calls == ["alpha", "beta", "gamma"]
        calls.clear()
        failures = execute_slices(entries, fail_fast=True, runner=fake_runner)
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
        runner=lambda entry: run_phase3_check(entry.slug, description=entry.description),
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
