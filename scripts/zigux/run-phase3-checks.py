#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import subprocess
import sys

from phase3_catalog import discover_phase3_slices


ROOT = Path(__file__).resolve().parents[2]


def run(cmd: list[str]) -> int:
    completed = subprocess.run(cmd, cwd=str(ROOT), check=False)
    return completed.returncode


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
    args = parser.parse_args()

    slices = [entry for entry in discover_phase3_slices() if entry.check_script.exists()]
    selected = set(args.slug)
    if selected:
        slices = [entry for entry in slices if entry.slug in selected]
        missing = sorted(selected.difference({entry.slug for entry in slices}))
        if missing:
            raise SystemExit(f"unknown Phase 3 slugs: {', '.join(missing)}")

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
