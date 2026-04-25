#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from phase3_catalog import discover_phase3_slices
from phase3_check_lib import render_wrapper_stub


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate template-backed Phase 3 wrapper scripts.")
    parser.add_argument("--check", action="store_true", help="Fail if any wrapper does not match the generated stub.")
    args = parser.parse_args()

    expected = render_wrapper_stub()
    mismatches: list[str] = []

    for entry in discover_phase3_slices():
        path = entry.check_script
        if not path.exists():
            mismatches.append(path.as_posix())
            continue
        current = path.read_text(encoding="utf-8")
        if current != expected:
            mismatches.append(path.as_posix())
            if not args.check:
                path.write_text(expected, encoding="utf-8", newline="\n")

    if mismatches and args.check:
        print("PHASE3_WRAPPER_TEMPLATES=fail")
        for path in mismatches:
            print(path)
        return 1

    if args.check:
        print("PHASE3_WRAPPER_TEMPLATES=pass")
    else:
        print(f"PHASE3_WRAPPER_TEMPLATES=updated:{len(mismatches)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
