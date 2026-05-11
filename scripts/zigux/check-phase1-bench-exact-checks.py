#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path


SELF_PATH = Path(__file__).resolve()
DEFAULT_ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) >= 3 else SELF_PATH.parent
EXPECTATIONS_RELATIVE_PATH = Path("zigux/tests/fixtures/phase1_bench_expectations.json")

EXPECTED_EXACT_CHECKSUMS = {
    "PHASE1_BENCH_BITMAP_WEIGHT_CHECKSUM": 2260000,
    "PHASE1_BENCH_BITMAP_WINDOW_CHECKSUM": 620000,
    "PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM": 15621472,
    "PHASE1_BENCH_FIND_BIT_EDGE_CHECKSUM": 23340000,
    "PHASE1_BENCH_STRING_CHECKSUM": 320000,
    "PHASE1_BENCH_RBTREE_CHECKSUM": 3380000,
}


class DuplicateTrackingDict(dict[str, object]):
    def __init__(self, pairs: list[tuple[str, object]]) -> None:
        super().__init__()
        self.duplicate_keys: list[str] = []
        for key, value in pairs:
            if key in self and key not in self.duplicate_keys:
                self.duplicate_keys.append(key)
            self[key] = value


def load_json_text(text: str) -> object:
    return json.loads(text, object_pairs_hook=DuplicateTrackingDict)


def load_json(path: Path) -> object:
    return load_json_text(path.read_text(encoding="utf-8"))


def expectations_path(root_arg: str | None) -> Path:
    root = DEFAULT_ROOT if root_arg is None else Path(root_arg).resolve()
    return root / EXPECTATIONS_RELATIVE_PATH


def validate_exact_checksums(expectations: object) -> list[str]:
    if not isinstance(expectations, dict):
        return [f"phase1_bench_expectations:type={type(expectations).__name__}"]

    issues: list[str] = []
    if isinstance(expectations, DuplicateTrackingDict) and expectations.duplicate_keys:
        for key in expectations.duplicate_keys:
            issues.append(f"phase1_bench_expectations:duplicate_root_key={key}")

    checksums = expectations.get("checksums")
    if not isinstance(checksums, list):
        return [*issues, f"phase1_bench_expectations:checksums_type={type(checksums).__name__}"]

    checksum_names: set[str] = set()
    duplicate_checksum_names: set[str] = set()
    for item in checksums:
        if not isinstance(item, str):
            issues.append(f"phase1_bench_expectations:checksum_type={type(item).__name__}")
            continue
        if item in checksum_names:
            duplicate_checksum_names.add(item)
        checksum_names.add(item)

    for key in sorted(duplicate_checksum_names):
        issues.append(f"phase1_bench_expectations:duplicate_checksum={key}")

    exact_checksums = expectations.get("exact_checksums")
    if not isinstance(exact_checksums, dict):
        return [*issues, f"phase1_bench_expectations:exact_checksums_type={type(exact_checksums).__name__}"]

    if isinstance(exact_checksums, DuplicateTrackingDict) and exact_checksums.duplicate_keys:
        for key in exact_checksums.duplicate_keys:
            issues.append(f"phase1_bench_expectations:duplicate_exact_checksum_key={key}")

    for key, expected in EXPECTED_EXACT_CHECKSUMS.items():
        if key not in checksum_names:
            issues.append(f"phase1_bench_expectations:checksum_not_listed={key}")
        actual = exact_checksums.get(key)
        if not isinstance(actual, int):
            issues.append(f"phase1_bench_expectations:exact_checksum_type={key}:{type(actual).__name__}")
            continue
        if actual != expected:
            issues.append(f"phase1_bench_expectations:exact_checksum_mismatch={key}:expected={expected}:actual={actual}")

    for key in exact_checksums:
        if key not in EXPECTED_EXACT_CHECKSUMS:
            issues.append(f"phase1_bench_expectations:unexpected_exact_checksum={key}")

    return issues


def run_self_test() -> None:
    base = {
        "status": "pass",
        "iterations": {
            "PHASE1_BENCH_BITMAP_WEIGHT_ITERATIONS": 20000,
        },
        "checksums": list(EXPECTED_EXACT_CHECKSUMS.keys()) + [
            "PHASE1_BENCH_HWEIGHT_CHECKSUM",
            "PHASE1_BENCH_LIST_SORT_CHECKSUM",
        ],
        "exact_checksums": dict(EXPECTED_EXACT_CHECKSUMS),
    }

    assert validate_exact_checksums(base) == []

    missing_listed = dict(base)
    missing_listed["checksums"] = [
        item for item in base["checksums"] if item != "PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM"
    ]
    assert "phase1_bench_expectations:checksum_not_listed=PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM" in validate_exact_checksums(missing_listed)

    missing_exact = dict(base)
    missing_exact["exact_checksums"] = dict(base["exact_checksums"])
    del missing_exact["exact_checksums"]["PHASE1_BENCH_STRING_CHECKSUM"]
    assert "phase1_bench_expectations:exact_checksum_type=PHASE1_BENCH_STRING_CHECKSUM:NoneType" in validate_exact_checksums(missing_exact)

    wrong_exact = dict(base)
    wrong_exact["exact_checksums"] = dict(base["exact_checksums"])
    wrong_exact["exact_checksums"]["PHASE1_BENCH_BITMAP_WINDOW_CHECKSUM"] = 1
    assert (
        "phase1_bench_expectations:exact_checksum_mismatch=PHASE1_BENCH_BITMAP_WINDOW_CHECKSUM:expected=620000:actual=1"
        in validate_exact_checksums(wrong_exact)
    )

    duplicate_root = load_json_text(
        '{"checksums":["PHASE1_BENCH_BITMAP_WEIGHT_CHECKSUM","PHASE1_BENCH_BITMAP_WINDOW_CHECKSUM","PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM","PHASE1_BENCH_FIND_BIT_EDGE_CHECKSUM","PHASE1_BENCH_STRING_CHECKSUM","PHASE1_BENCH_RBTREE_CHECKSUM"],"checksums":[],"exact_checksums":{"PHASE1_BENCH_BITMAP_WEIGHT_CHECKSUM":2260000,"PHASE1_BENCH_BITMAP_WINDOW_CHECKSUM":620000,"PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM":15621472,"PHASE1_BENCH_FIND_BIT_EDGE_CHECKSUM":23340000,"PHASE1_BENCH_STRING_CHECKSUM":320000,"PHASE1_BENCH_RBTREE_CHECKSUM":3380000}}'
    )
    assert "phase1_bench_expectations:duplicate_root_key=checksums" in validate_exact_checksums(duplicate_root)

    duplicate_exact = load_json_text(
        '{"checksums":["PHASE1_BENCH_BITMAP_WEIGHT_CHECKSUM","PHASE1_BENCH_BITMAP_WINDOW_CHECKSUM","PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM","PHASE1_BENCH_FIND_BIT_EDGE_CHECKSUM","PHASE1_BENCH_STRING_CHECKSUM","PHASE1_BENCH_RBTREE_CHECKSUM"],"exact_checksums":{"PHASE1_BENCH_BITMAP_WEIGHT_CHECKSUM":2260000,"PHASE1_BENCH_BITMAP_WEIGHT_CHECKSUM":2260001,"PHASE1_BENCH_BITMAP_WINDOW_CHECKSUM":620000,"PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM":15621472,"PHASE1_BENCH_FIND_BIT_EDGE_CHECKSUM":23340000,"PHASE1_BENCH_STRING_CHECKSUM":320000,"PHASE1_BENCH_RBTREE_CHECKSUM":3380000}}'
    )
    assert "phase1_bench_expectations:duplicate_exact_checksum_key=PHASE1_BENCH_BITMAP_WEIGHT_CHECKSUM" in validate_exact_checksums(duplicate_exact)

    print("PHASE1_BENCH_EXACT_CHECK_SELF_TEST=pass")
    print("PHASE1_BENCH_EXACT_CHECK_SELF_TEST_CASE_COUNT=6")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the Phase 1 bench expectations keep the shipped exact-checksum packet explicit."
    )
    parser.add_argument("--root", help="Validate an alternate Zigux tree root.")
    parser.add_argument("--self-test", action="store_true", help="Run built-in checker self-tests.")
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return 0

    try:
        expectations = load_json(expectations_path(args.root))
    except FileNotFoundError:
        print("PHASE1_BENCH_EXACT_CHECK=fail")
        print(f"MISSING_EXPECTATIONS={EXPECTATIONS_RELATIVE_PATH}")
        return 1
    except json.JSONDecodeError as exc:
        print("PHASE1_BENCH_EXACT_CHECK=fail")
        print(f"EXPECTATIONS_JSON_ERROR={exc.msg}")
        print(f"EXPECTATIONS_JSON_LINE={exc.lineno}")
        print(f"EXPECTATIONS_JSON_COLUMN={exc.colno}")
        return 1

    issues = validate_exact_checksums(expectations)
    if issues:
        print("PHASE1_BENCH_EXACT_CHECK=fail")
        print("PHASE1_BENCH_EXACT_CHECK_ISSUES_START")
        for issue in issues:
            print(issue)
        print("PHASE1_BENCH_EXACT_CHECK_ISSUES_END")
        return 1

    print("PHASE1_BENCH_EXACT_CHECK=pass")
    print(f"PHASE1_BENCH_EXACT_CHECK_EXPECTATIONS={EXPECTATIONS_RELATIVE_PATH}")
    print(f"PHASE1_BENCH_EXACT_CHECK_REQUIRED_KEYS={len(EXPECTED_EXACT_CHECKSUMS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
