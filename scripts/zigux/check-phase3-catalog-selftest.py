#!/usr/bin/env python3
from __future__ import annotations

import argparse

from phase3_catalog import PHASE3_CATALOG_SELF_TEST_CASE_COUNT, run_self_test


PHASE3_CATALOG_SELF_TEST_MARKER = "PHASE3_CATALOG_SELF_TEST=pass"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run the Phase 3 catalog self-test and emit a validator-owned pass marker."
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run the Phase 3 catalog self-test and print the explicit pass marker on success.",
    )
    args = parser.parse_args()

    if not args.self_test:
        raise SystemExit("expected --self-test")

    result = run_self_test()
    if result == 0:
        print(PHASE3_CATALOG_SELF_TEST_MARKER)
        print(f"PHASE3_CATALOG_SELF_TEST_CASE_COUNT={PHASE3_CATALOG_SELF_TEST_CASE_COUNT}")
    return result


if __name__ == "__main__":
    raise SystemExit(main())
