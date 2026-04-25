#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import subprocess
import sys
import tempfile

from phase3_catalog import discover_phase3_slices


ROOT = Path(__file__).resolve().parents[2]


def run(cmd: list[str]) -> int:
    completed = subprocess.run(cmd, cwd=str(ROOT), check=False)
    return completed.returncode


def select_slices(entries: list[object], selected_slugs: list[str], require_existing_check_script: bool = True) -> list[object]:
    slices = list(entries)
    if require_existing_check_script:
        slices = [entry for entry in slices if entry.check_script.exists()]

    selected = set(selected_slugs)
    if selected:
        slices = [entry for entry in slices if entry.slug in selected]
        missing = sorted(selected.difference({entry.slug for entry in slices}))
        if missing:
            raise SystemExit(f"unknown Phase 3 slugs: {', '.join(missing)}")

    return slices


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_runner_selftest_") as tmp_dir_str:
        tmp_dir = Path(tmp_dir_str)
        alpha = tmp_dir / "check-phase3-alpha.py"
        beta = tmp_dir / "check-phase3-beta.py"
        alpha.write_text("#!/usr/bin/env python3\n", encoding="utf-8")

        entries = [
            type("Entry", (), {"slug": "alpha", "check_script": alpha})(),
            type("Entry", (), {"slug": "beta", "check_script": beta})(),
        ]

        assert [entry.slug for entry in select_slices(entries, [], require_existing_check_script=True)] == ["alpha"]
        assert [entry.slug for entry in select_slices(entries, ["alpha"], require_existing_check_script=True)] == ["alpha"]
        assert [entry.slug for entry in select_slices(entries, ["beta"], require_existing_check_script=False)] == ["beta"]
        try:
            select_slices(entries, ["missing"], require_existing_check_script=False)
        except SystemExit as exc:
            assert str(exc) == "unknown Phase 3 slugs: missing"
        else:
            raise AssertionError("expected missing slug to fail")

    print("PHASE3_RUNNER_SELF_TEST=pass")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="List or execute discovered Phase 3 parity checks.")
    parser.add_argument("--list", action="store_true", help="List discovered Phase 3 check slugs.")
    parser.add_argument(
        "--slug",
        action="append",
        default=[],
        help="Only run the named Phase 3 slug. Repeat to run more than one.",
    )
    parser.add_argument("--zig", help="Forward an explicit zig executable path to each check.")
    parser.add_argument("--cc", help="Forward an explicit C compiler path to each check.")
    parser.add_argument("--fail-fast", action="store_true", help="Stop after the first failing check.")
    parser.add_argument("--self-test", action="store_true", help="Run isolated slug-selection checks without executing parity wrappers.")
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

    failures: list[str] = []
    for entry in slices:
        cmd = [sys.executable, str(entry.check_script)]
        if args.zig:
            cmd.extend(["--zig", args.zig])
        if args.cc:
            cmd.extend(["--cc", args.cc])
        print(f"PHASE3_RUN={entry.slug}")
        rc = run(cmd)
        if rc != 0:
            failures.append(entry.slug)
            if args.fail_fast:
                break

    if failures:
        print("PHASE3_RUN_STATUS=fail")
        print("PHASE3_FAILED_SLUGS=" + ",".join(failures))
        return 1

    print("PHASE3_RUN_STATUS=pass")
    print(f"PHASE3_RUN_COUNT={len(slices)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())