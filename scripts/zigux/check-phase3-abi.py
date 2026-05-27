#!/usr/bin/env python3
"""Delegate to the live Phase 3 validator to avoid checker drift."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

VALIDATE_PHASE3_PATH = Path(__file__).with_name("validate-phase3.py")

SELF_TEST_REPLACEMENTS = (
    ("PHASE3_VALIDATION_SELF_TEST_CASE_COUNT=", "PHASE3_ABI_CHECK_SELF_TEST_CASE_COUNT="),
    ("PHASE3_VALIDATION_SELF_TEST=", "PHASE3_ABI_CHECK_SELF_TEST="),
)

RUN_REPLACEMENTS = (
    ("PHASE3_VALIDATION=", "PHASE3_ABI_CHECK="),
    ("PHASE3_SCOPE=", "PHASE3_ABI_SCOPE="),
)


def _emit_missing_validator(self_test: bool) -> int:
    if self_test:
        print("PHASE3_ABI_CHECK_SELF_TEST=fail")
    else:
        print("PHASE3_ABI_CHECK=fail")
    print(f"missing repo file: {VALIDATE_PHASE3_PATH.as_posix()}")
    return 1


def _rewrite(output: str, replacements: tuple[tuple[str, str], ...]) -> str:
    rewritten = output
    for old, new in replacements:
        rewritten = rewritten.replace(old, new)
    return rewritten


def _run_validator(args: list[str], self_test: bool) -> int:
    if not VALIDATE_PHASE3_PATH.is_file():
        return _emit_missing_validator(self_test)

    completed = subprocess.run(
        [sys.executable, str(VALIDATE_PHASE3_PATH), *args],
        check=False,
        capture_output=True,
        text=True,
    )
    replacements = SELF_TEST_REPLACEMENTS if self_test else RUN_REPLACEMENTS
    sys.stdout.write(_rewrite(completed.stdout, replacements))
    sys.stderr.write(completed.stderr)
    return completed.returncode


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the current bounded Phase 3 ABI, export/UAPI, and dump packet."
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path("."),
        help="repository root that contains the bounded Phase 3 ABI packet",
    )
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    passthrough: list[str] = []
    if args.self_test:
        passthrough.append("--self-test")
    else:
        passthrough.extend(("--repo-root", str(args.repo_root)))
    return _run_validator(passthrough, self_test=args.self_test)


if __name__ == "__main__":
    raise SystemExit(main())
