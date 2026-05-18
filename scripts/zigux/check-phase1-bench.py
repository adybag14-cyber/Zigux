#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import subprocess
import tempfile


HERE = Path(__file__).resolve()
ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent
EXPECTATIONS = ROOT / "zigux" / "tests" / "fixtures" / "phase1_bench_expectations.json"
EXPECTED_ITERATIONS = {
    "PHASE1_BENCH_BITMAP_WEIGHT_ITERATIONS": 20000,
    "PHASE1_BENCH_BITMAP_WINDOW_ITERATIONS": 20000,
    "PHASE1_BENCH_FIND_NEXT_BIT_ITERATIONS": 20000,
    "PHASE1_BENCH_FIND_BIT_EDGE_ITERATIONS": 20000,
    "PHASE1_BENCH_STRING_ITERATIONS": 40000,
    "PHASE1_BENCH_HWEIGHT_ITERATIONS": 100000,
    "PHASE1_BENCH_LIST_SORT_ITERATIONS": 1000,
    "PHASE1_BENCH_RBTREE_ITERATIONS": 4000,
}
RBTREE_REQUIRED_ITERATIONS = {
    "PHASE1_BENCH_RBTREE_ITERATIONS",
}
EXPECTED_CHECKSUMS = [
    "PHASE1_BENCH_BITMAP_WEIGHT_CHECKSUM",
    "PHASE1_BENCH_BITMAP_WINDOW_CHECKSUM",
    "PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM",
    "PHASE1_BENCH_FIND_BIT_EDGE_CHECKSUM",
    "PHASE1_BENCH_STRING_CHECKSUM",
    "PHASE1_BENCH_HWEIGHT_CHECKSUM",
    "PHASE1_BENCH_LIST_SORT_CHECKSUM",
    "PHASE1_BENCH_RBTREE_CHECKSUM",
    "PHASE1_BENCH_RBTREE_POSTORDER_SAFE_CHECKSUM",
    "PHASE1_BENCH_RBTREE_FIND_ADD_CHECKSUM",
    "PHASE1_BENCH_RBTREE_DUPLICATE_CHECKSUM",
    "PHASE1_BENCH_RBTREE_CACHED_CHECKSUM",
]
REQUIRED_EXACT_CHECKSUMS = {
    "PHASE1_BENCH_BITMAP_WEIGHT_CHECKSUM",
    "PHASE1_BENCH_BITMAP_WINDOW_CHECKSUM",
    "PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM",
    "PHASE1_BENCH_FIND_BIT_EDGE_CHECKSUM",
    "PHASE1_BENCH_STRING_CHECKSUM",
    "PHASE1_BENCH_HWEIGHT_CHECKSUM",
    "PHASE1_BENCH_LIST_SORT_CHECKSUM",
    "PHASE1_BENCH_RBTREE_CHECKSUM",
    "PHASE1_BENCH_RBTREE_POSTORDER_SAFE_CHECKSUM",
    "PHASE1_BENCH_RBTREE_FIND_ADD_CHECKSUM",
    "PHASE1_BENCH_RBTREE_DUPLICATE_CHECKSUM",
    "PHASE1_BENCH_RBTREE_CACHED_CHECKSUM",
}
BITMAP_REQUIRED_EXACT_CHECKSUMS = {
    "PHASE1_BENCH_BITMAP_WEIGHT_CHECKSUM",
    "PHASE1_BENCH_BITMAP_WINDOW_CHECKSUM",
}
FIND_BIT_REQUIRED_EXACT_CHECKSUMS = {
    "PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM",
    "PHASE1_BENCH_FIND_BIT_EDGE_CHECKSUM",
}
STRING_REQUIRED_EXACT_CHECKSUMS = {
    "PHASE1_BENCH_STRING_CHECKSUM",
}
HWEIGHT_REQUIRED_EXACT_CHECKSUMS = {
    "PHASE1_BENCH_HWEIGHT_CHECKSUM",
}
LIST_SORT_REQUIRED_EXACT_CHECKSUMS = {
    "PHASE1_BENCH_LIST_SORT_CHECKSUM",
}
RBTREE_REQUIRED_EXACT_CHECKSUMS = {
    "PHASE1_BENCH_RBTREE_CHECKSUM",
    "PHASE1_BENCH_RBTREE_POSTORDER_SAFE_CHECKSUM",
    "PHASE1_BENCH_RBTREE_FIND_ADD_CHECKSUM",
    "PHASE1_BENCH_RBTREE_DUPLICATE_CHECKSUM",
    "PHASE1_BENCH_RBTREE_CACHED_CHECKSUM",
}


class DuplicateTrackingDict(dict[str, object]):
    def __init__(self, pairs: list[tuple[str, object]]) -> None:
        super().__init__()
        self.duplicate_keys: list[str] = []
        for key, value in pairs:
            if key in self and key not in self.duplicate_keys:
                self.duplicate_keys.append(key)
            self[key] = value


def find_zig(explicit: str | None) -> str:
    if explicit:
        return explicit
    zig = shutil.which("zig")
    if zig:
        return zig
    raise SystemExit("zig not found; pass --zig or add zig to PATH")


def parse_output(stdout: str) -> tuple[dict[str, str], dict[str, int]]:
    parsed: dict[str, str] = {}
    counts: dict[str, int] = {}
    for raw_line in stdout.splitlines():
        line = raw_line.strip()
        if not line or "=" not in line:
            continue
        key, value = line.split("=", 1)
        parsed[key] = value
        counts[key] = counts.get(key, 0) + 1
    return parsed, counts


def load_expectations_text(text: str) -> object:
    return json.loads(text, object_pairs_hook=DuplicateTrackingDict)


def load_expectations(path: Path) -> object:
    return load_expectations_text(path.read_text(encoding="utf-8"))


def load_runtime_expectations(path: Path) -> tuple[str, object]:
    try:
        expectations = load_expectations(path)
    except FileNotFoundError:
        return ("expectations_missing", path)
    except json.JSONDecodeError as exc:
        return ("expectations_json_error", exc)

    kind, payload = validate_expectations(expectations)
    if kind != "pass":
        return (kind, payload)
    return ("pass", expectations)


def validate_expectations(expectations: object) -> tuple[str, object]:
    if not isinstance(expectations, dict):
        return ("expectations_type", type(expectations).__name__)
    if isinstance(expectations, DuplicateTrackingDict) and expectations.duplicate_keys:
        return ("expectations_duplicate_keys", expectations.duplicate_keys)
    if expectations.get("status") != "pass":
        return ("expectations_status", expectations.get("status"))

    iterations = expectations.get("iterations")
    checksums = expectations.get("checksums")
    exact_checksums = expectations.get("exact_checksums")

    if not isinstance(iterations, dict):
        return ("expectations_iterations_type", type(iterations).__name__)
    if isinstance(iterations, DuplicateTrackingDict) and iterations.duplicate_keys:
        return ("expectations_duplicate_iteration_keys", iterations.duplicate_keys)
    if not isinstance(checksums, list):
        return ("expectations_checksums_type", type(checksums).__name__)
    if not isinstance(exact_checksums, dict):
        return ("expectations_exact_checksums_type", type(exact_checksums).__name__)
    if isinstance(exact_checksums, DuplicateTrackingDict) and exact_checksums.duplicate_keys:
        return ("expectations_duplicate_exact_checksum_keys", exact_checksums.duplicate_keys)

    iteration_keys = set(iterations)
    missing_rbtree_iterations = sorted(RBTREE_REQUIRED_ITERATIONS - iteration_keys)
    if missing_rbtree_iterations:
        return ("expectations_missing_rbtree_iterations", missing_rbtree_iterations)
    if iteration_keys != set(EXPECTED_ITERATIONS):
        missing = sorted(set(EXPECTED_ITERATIONS) - iteration_keys)
        unexpected = sorted(iteration_keys - set(EXPECTED_ITERATIONS))
        if missing:
            return ("expectations_missing_iterations", missing)
        return ("expectations_unexpected_iteration", unexpected[0])
    for key, expected in EXPECTED_ITERATIONS.items():
        value = iterations.get(key)
        if not isinstance(value, int):
            return ("expectations_iteration_value_type", (key, type(value).__name__))
        if value != expected:
            if key in RBTREE_REQUIRED_ITERATIONS:
                return ("expectations_rbtree_iteration_value", (key, expected, value))
            return ("expectations_iteration_value", (key, expected, value))

    seen: set[str] = set()
    duplicates: list[str] = []
    for item in checksums:
        if not isinstance(item, str):
            return ("expectations_checksum_type", type(item).__name__)
        if item in seen and item not in duplicates:
            duplicates.append(item)
        seen.add(item)
    if duplicates:
        return ("expectations_duplicate_checksums", duplicates)
    if checksums != EXPECTED_CHECKSUMS:
        return ("expectations_checksum_order", checksums)
    checksum_keys = set(checksums)
    if checksum_keys != set(EXPECTED_CHECKSUMS):
        missing = sorted(set(EXPECTED_CHECKSUMS) - checksum_keys)
        unexpected = sorted(checksum_keys - set(EXPECTED_CHECKSUMS))
        if missing:
            return ("expectations_missing_checksums", missing)
        return ("expectations_unexpected_checksums", unexpected)

    for key in sorted(BITMAP_REQUIRED_EXACT_CHECKSUMS):
        if key in checksum_keys and key not in exact_checksums:
            return ("expectations_checksums_bitmap_exact_required", key)

    for key in sorted(FIND_BIT_REQUIRED_EXACT_CHECKSUMS):
        if key in checksum_keys and key not in exact_checksums:
            return ("expectations_checksums_find_bit_exact_required", key)

    for key in sorted(STRING_REQUIRED_EXACT_CHECKSUMS):
        if key in checksum_keys and key not in exact_checksums:
            return ("expectations_checksums_string_exact_required", key)

    for key in sorted(HWEIGHT_REQUIRED_EXACT_CHECKSUMS):
        if key in checksum_keys and key not in exact_checksums:
            return ("expectations_checksums_hweight_exact_required", key)

    for key in sorted(LIST_SORT_REQUIRED_EXACT_CHECKSUMS):
        if key in checksum_keys and key not in exact_checksums:
            return ("expectations_checksums_list_sort_exact_required", key)

    for key in sorted(RBTREE_REQUIRED_EXACT_CHECKSUMS):
        if key in checksum_keys and key not in exact_checksums:
            return ("expectations_checksums_rbtree_exact_required", key)

    exact_keys = set(exact_checksums)
    if exact_keys != set(REQUIRED_EXACT_CHECKSUMS):
        missing = sorted(set(REQUIRED_EXACT_CHECKSUMS) - exact_keys)
        unexpected = sorted(exact_keys - set(REQUIRED_EXACT_CHECKSUMS))
        if missing:
            return ("expectations_missing_exact_checksums", missing)
        return ("expectations_unexpected_exact_checksums", unexpected)
    for key, value in exact_checksums.items():
        if not isinstance(value, int):
            return ("expectations_exact_checksum_value_type", (key, type(value).__name__))
        if value <= 0:
            return ("expectations_exact_checksum_nonpositive", (key, value))

    return ("pass", expectations)


def validate_output(expectations: dict[str, object], stdout: str) -> tuple[str, object]:
    parsed, counts = parse_output(stdout)
    required_keys = {
        "PHASE1_BENCH",
        *expectations["iterations"],
        *expectations["checksums"],
        *expectations["exact_checksums"],
    }
    duplicate = sorted(key for key in required_keys if counts.get(key, 0) > 1)
    if duplicate:
        return ("duplicate", duplicate)

    unexpected = sorted(
        key for key in parsed if key.startswith("PHASE1_BENCH") and key not in required_keys
    )
    if unexpected:
        return ("unexpected", unexpected)

    if parsed.get("PHASE1_BENCH") != expectations["status"]:
        return ("status", (expectations["status"], parsed.get("PHASE1_BENCH")))

    missing: list[str] = []
    rbtree_iteration_keys = set(RBTREE_REQUIRED_ITERATIONS)
    for key, expected in expectations["iterations"].items():
        actual = parsed.get(key)
        if actual is None:
            if key in rbtree_iteration_keys:
                return ("missing_rbtree_iterations", [key])
            missing.append(key)
            continue
        try:
            value = int(actual)
        except ValueError:
            return ("iteration_value_type", (key, actual))
        if value != expected:
            if key in rbtree_iteration_keys:
                return ("rbtree_iteration_mismatch", (key, expected, actual))
            return ("iteration_mismatch", (key, expected, actual))

    missing_rbtree_exact = sorted(
        key for key in RBTREE_REQUIRED_EXACT_CHECKSUMS if parsed.get(key) is None
    )
    if missing_rbtree_exact:
        return ("missing_rbtree_exact_checksums", missing_rbtree_exact)

    missing_bitmap_exact = sorted(
        key for key in BITMAP_REQUIRED_EXACT_CHECKSUMS if parsed.get(key) is None
    )
    if missing_bitmap_exact:
        return ("missing_bitmap_exact_checksums", missing_bitmap_exact)

    missing_find_bit_exact = sorted(
        key for key in FIND_BIT_REQUIRED_EXACT_CHECKSUMS if parsed.get(key) is None
    )
    if missing_find_bit_exact:
        return ("missing_find_bit_exact_checksums", missing_find_bit_exact)

    missing_string_exact = sorted(
        key for key in STRING_REQUIRED_EXACT_CHECKSUMS if parsed.get(key) is None
    )
    if missing_string_exact:
        return ("missing_string_exact_checksums", missing_string_exact)

    missing_hweight_exact = sorted(
        key for key in HWEIGHT_REQUIRED_EXACT_CHECKSUMS if parsed.get(key) is None
    )
    if missing_hweight_exact:
        return ("missing_hweight_exact_checksums", missing_hweight_exact)

    missing_list_sort_exact = sorted(
        key for key in LIST_SORT_REQUIRED_EXACT_CHECKSUMS if parsed.get(key) is None
    )
    if missing_list_sort_exact:
        return ("missing_list_sort_exact_checksums", missing_list_sort_exact)

    for key in expectations["checksums"]:
        actual = parsed.get(key)
        if actual is None:
            missing.append(key)
            continue
        try:
            value = int(actual)
        except ValueError:
            return ("checksum_value_type", (key, actual))
        if value <= 0:
            return ("nonpositive_checksum", (key, actual))
        expected_exact = expectations["exact_checksums"].get(key)
        if expected_exact is not None and value != expected_exact:
            return ("exact_checksum_mismatch", (key, expected_exact, value))

    for key, expected_exact in expectations["exact_checksums"].items():
        if key in expectations["checksums"]:
            continue
        actual = parsed.get(key)
        if actual is None:
            missing.append(key)
            continue
        try:
            value = int(actual)
        except ValueError:
            return ("checksum_value_type", (key, actual))
        if value != expected_exact:
            return ("exact_checksum_mismatch", (key, expected_exact, value))

    if missing:
        return ("missing", missing)
    return ("pass", parsed)


def run_self_test() -> None:
    case_count = 0
    expectations = {
        "status": "pass",
        "iterations": dict(EXPECTED_ITERATIONS),
        "checksums": list(EXPECTED_CHECKSUMS),
        "exact_checksums": {
            "PHASE1_BENCH_BITMAP_WEIGHT_CHECKSUM": 1,
            "PHASE1_BENCH_BITMAP_WINDOW_CHECKSUM": 2,
            "PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM": 3,
            "PHASE1_BENCH_FIND_BIT_EDGE_CHECKSUM": 4,
            "PHASE1_BENCH_STRING_CHECKSUM": 5,
            "PHASE1_BENCH_HWEIGHT_CHECKSUM": 6,
            "PHASE1_BENCH_LIST_SORT_CHECKSUM": 7,
            "PHASE1_BENCH_RBTREE_CHECKSUM": 8,
            "PHASE1_BENCH_RBTREE_POSTORDER_SAFE_CHECKSUM": 9,
            "PHASE1_BENCH_RBTREE_FIND_ADD_CHECKSUM": 10,
            "PHASE1_BENCH_RBTREE_DUPLICATE_CHECKSUM": 11,
            "PHASE1_BENCH_RBTREE_CACHED_CHECKSUM": 12,
        },
    }
    kind, payload = validate_expectations(expectations)
    assert kind == "pass", (kind, payload)
    case_count += 1

    duplicate_top_level_text = """{
  "status": "pass",
  "status": "fail",
  "iterations": {
    "PHASE1_BENCH_BITMAP_WEIGHT_ITERATIONS": 20000,
    "PHASE1_BENCH_BITMAP_WINDOW_ITERATIONS": 20000,
    "PHASE1_BENCH_FIND_NEXT_BIT_ITERATIONS": 20000,
    "PHASE1_BENCH_FIND_BIT_EDGE_ITERATIONS": 20000,
    "PHASE1_BENCH_STRING_ITERATIONS": 40000,
    "PHASE1_BENCH_HWEIGHT_ITERATIONS": 100000,
    "PHASE1_BENCH_LIST_SORT_ITERATIONS": 1000,
    "PHASE1_BENCH_RBTREE_ITERATIONS": 4000
  },
  "checksums": [
    "PHASE1_BENCH_BITMAP_WEIGHT_CHECKSUM",
    "PHASE1_BENCH_BITMAP_WINDOW_CHECKSUM",
    "PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM",
    "PHASE1_BENCH_FIND_BIT_EDGE_CHECKSUM",
    "PHASE1_BENCH_STRING_CHECKSUM",
    "PHASE1_BENCH_HWEIGHT_CHECKSUM",
    "PHASE1_BENCH_LIST_SORT_CHECKSUM",
    "PHASE1_BENCH_RBTREE_CHECKSUM",
    "PHASE1_BENCH_RBTREE_POSTORDER_SAFE_CHECKSUM",
    "PHASE1_BENCH_RBTREE_FIND_ADD_CHECKSUM",
    "PHASE1_BENCH_RBTREE_DUPLICATE_CHECKSUM",
    "PHASE1_BENCH_RBTREE_CACHED_CHECKSUM"
  ],
  "exact_checksums": {
    "PHASE1_BENCH_BITMAP_WEIGHT_CHECKSUM": 1,
    "PHASE1_BENCH_BITMAP_WINDOW_CHECKSUM": 2,
    "PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM": 3,
    "PHASE1_BENCH_FIND_BIT_EDGE_CHECKSUM": 4,
    "PHASE1_BENCH_STRING_CHECKSUM": 5,
    "PHASE1_BENCH_HWEIGHT_CHECKSUM": 6,
    "PHASE1_BENCH_LIST_SORT_CHECKSUM": 7,
    "PHASE1_BENCH_RBTREE_CHECKSUM": 8,
    "PHASE1_BENCH_RBTREE_POSTORDER_SAFE_CHECKSUM": 9,
    "PHASE1_BENCH_RBTREE_FIND_ADD_CHECKSUM": 10,
    "PHASE1_BENCH_RBTREE_DUPLICATE_CHECKSUM": 11,
    "PHASE1_BENCH_RBTREE_CACHED_CHECKSUM": 12
  }
}"""
    kind, payload = validate_expectations(load_expectations_text(duplicate_top_level_text))
    assert kind == "expectations_duplicate_keys"
    assert payload == ["status"]
    case_count += 1

    duplicate_iteration_text = """{
  "status": "pass",
  "iterations": {
    "PHASE1_BENCH_BITMAP_WEIGHT_ITERATIONS": 20000,
    "PHASE1_BENCH_BITMAP_WINDOW_ITERATIONS": 20000,
    "PHASE1_BENCH_FIND_NEXT_BIT_ITERATIONS": 20000,
    "PHASE1_BENCH_FIND_BIT_EDGE_ITERATIONS": 20000,
    "PHASE1_BENCH_STRING_ITERATIONS": 40000,
    "PHASE1_BENCH_HWEIGHT_ITERATIONS": 100000,
    "PHASE1_BENCH_LIST_SORT_ITERATIONS": 1000,
    "PHASE1_BENCH_RBTREE_ITERATIONS": 4000,
    "PHASE1_BENCH_RBTREE_ITERATIONS": 4001
  },
  "checksums": [
    "PHASE1_BENCH_BITMAP_WEIGHT_CHECKSUM",
    "PHASE1_BENCH_BITMAP_WINDOW_CHECKSUM",
    "PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM",
    "PHASE1_BENCH_FIND_BIT_EDGE_CHECKSUM",
    "PHASE1_BENCH_STRING_CHECKSUM",
    "PHASE1_BENCH_HWEIGHT_CHECKSUM",
    "PHASE1_BENCH_LIST_SORT_CHECKSUM",
    "PHASE1_BENCH_RBTREE_CHECKSUM",
    "PHASE1_BENCH_RBTREE_POSTORDER_SAFE_CHECKSUM",
    "PHASE1_BENCH_FIND_ADD_CHECKSUM",
    "PHASE1_BENCH_RBTREE_DUPLICATE_CHECKSUM",
    "PHASE1_BENCH_RBTREE_CACHED_CHECKSUM"
  ],
  "exact_checksums": {
    "PHASE1_BENCH_BITMAP_WEIGHT_CHECKSUM": 1,
    "PHASE1_BENCH_BITMAP_WINDOW_CHECKSUM": 2,
    "PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM": 3,
    "PHASE1_BENCH_FIND_BIT_EDGE_CHECKSUM": 4,
    "PHASE1_BENCH_STRING_CHECKSUM": 5,
    "PHASE1_BENCH_HWEIGHT_CHECKSUM": 6,
    "PHASE1_BENCH_LIST_SORT_CHECKSUM": 7,
    "PHASE1_BENCH_RBTREE_CHECKSUM": 8,
    "PHASE1_BENCH_RBTREE_POSTORDER_SAFE_CHECKSUM": 9,
    "PHASE1_BENCH_FIND_ADD_CHECKSUM": 10,
    "PHASE1_BENCH_RBTREE_DUPLICATE_CHECKSUM": 11,
    "PHASE1_BENCH_RBTREE_CACHED_CHECKSUM": 12
  }
}"""
    kind, payload = validate_expectations(load_expectations_text(duplicate_iteration_text))
    assert kind == "expectations_duplicate_iteration_keys"
    assert payload == ["PHASE1_BENCH_RBTREE_ITERATIONS"]
    case_count += 1

    duplicate_exact_checksum_text = """{
  "status": "pass",
  "iterations": {
    "PHASE1_BENCH_BITMAP_WEIGHT_ITERATIONS": 20000,
    "PHASE1_BENCH_BITMAP_WINDOW_ITERATIONS": 20000,
    "PHASE1_BENCH_FIND_NEXT_BIT_ITERATIONS": 20000,
    "PHASE1_BENCH_FIND_BIT_EDGE_ITERATIONS": 20000,
    "PHASE1_BENCH_STRING_ITERATIONS": 40000,
    "PHASE1_BENCH_HWEIGHT_ITERATIONS": 100000,
    "PHASE1_BENCH_LIST_SORT_ITERATIONS": 1000,
    "PHASE1_BENCH_RBTREE_ITERATIONS": 4000
  },
  "checksums": [
    "PHASE1_BENCH_BITMAP_WEIGHT_CHECKSUM",
    "PHASE1_BENCH_BITMAP_WINDOW_CHECKSUM",
    "PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM",
    "PHASE1_BENCH_FIND_BIT_EDGE_CHECKSUM",
    "PHASE1_BENCH_STRING_CHECKSUM",
    "PHASE1_BENCH_HWEIGHT_CHECKSUM",
    "PHASE1_BENCH_LIST_SORT_CHECKSUM",
    "PHASE1_BENCH_RBTREE_CHECKSUM",
    "PHASE1_BENCH_RBTREE_POSTORDER_SAFE_CHECKSUM",
    "PHASE1_BENCH_FIND_ADD_CHECKSUM",
    "PHASE1_BENCH_RBTREE_DUPLICATE_CHECKSUM",
    "PHASE1_BENCH_RBTREE_CACHED_CHECKSUM"
  ],
  "exact_checksums": {
    "PHASE1_BENCH_BITMAP_WEIGHT_CHECKSUM": 1,
    "PHASE1_BENCH_BITMAP_WINDOW_CHECKSUM": 2,
    "PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM": 3,
    "PHASE1_BENCH_FIND_BIT_EDGE_CHECKSUM": 4,
    "PHASE1_BENCH_STRING_CHECKSUM": 5,
    "PHASE1_BENCH_HWEIGHT_CHECKSUM": 6,
    "PHASE1_BENCH_LIST_SORT_CHECKSUM": 7,
    "PHASE1_BENCH_RBTREE_CHECKSUM": 8,
    "PHASE1_BENCH_RBTREE_POSTORDER_SAFE_CHECKSUM": 9,
    "PHASE1_BENCH_FIND_ADD_CHECKSUM": 10,
    "PHASE1_BENCH_RBTREE_DUPLICATE_CHECKSUM": 11,
    "PHASE1_BENCH_RBTREE_CACHED_CHECKSUM": 12,
    "PHASE1_BENCH_RBTREE_CACHED_CHECKSUM": 13
  }
}"""
    kind, payload = validate_expectations(load_expectations_text(duplicate_exact_checksum_text))
    assert kind == "expectations_duplicate_exact_checksum_keys"
    assert payload == ["PHASE1_BENCH_RBTREE_CACHED_CHECKSUM"]
    case_count += 1

    duplicate_checksum_list = {
        "status": "pass",
        "iterations": dict(EXPECTED_ITERATIONS),
        "checksums": list(EXPECTED_CHECKSUMS) + ["PHASE1_BENCH_RBTREE_CACHED_CHECKSUM"],
        "exact_checksums": {
            "PHASE1_BENCH_BITMAP_WEIGHT_CHECKSUM": 1,
            "PHASE1_BENCH_BITMAP_WINDOW_CHECKSUM": 2,
            "PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM": 3,
            "PHASE1_BENCH_FIND_BIT_EDGE_CHECKSUM": 4,
            "PHASE1_BENCH_STRING_CHECKSUM": 5,
            "PHASE1_BENCH_HWEIGHT_CHECKSUM": 6,
            "PHASE1_BENCH_LIST_SORT_CHECKSUM": 7,
            "PHASE1_BENCH_RBTREE_CHECKSUM": 8,
            "PHASE1_BENCH_RBTREE_POSTORDER_SAFE_CHECKSUM": 9,
            "PHASE1_BENCH_RBTREE_FIND_ADD_CHECKSUM": 10,
            "PHASE1_BENCH_RBTREE_DUPLICATE_CHECKSUM": 11,
            "PHASE1_BENCH_RBTREE_CACHED_CHECKSUM": 12,
        },
    }
    kind, payload = validate_expectations(duplicate_checksum_list)
    assert kind == "expectations_duplicate_checksums"
    assert payload == ["PHASE1_BENCH_RBTREE_CACHED_CHECKSUM"]
    case_count += 1

    ok_output = "\n".join(
        [
            "PHASE1_BENCH=pass",
            "PHASE1_BENCH_BITMAP_WEIGHT_ITERATIONS=20000",
            "PHASE1_BENCH_BITMAP_WINDOW_ITERATIONS=20000",
            "PHASE1_BENCH_FIND_NEXT_BIT_ITERATIONS=20000",
            "PHASE1_BENCH_FIND_BIT_EDGE_ITERATIONS=20000",
            "PHASE1_BENCH_STRING_ITERATIONS=40000",
            "PHASE1_BENCH_HWEIGHT_ITERATIONS=100000",
            "PHASE1_BENCH_LIST_SORT_ITERATIONS=1000",
            "PHASE1_BENCH_RBTREE_ITERATIONS=4000",
            "PHASE1_BENCH_BITMAP_WEIGHT_CHECKSUM=1",
            "PHASE1_BENCH_BITMAP_WINDOW_CHECKSUM=2",
            "PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM=3",
            "PHASE1_BENCH_FIND_BIT_EDGE_CHECKSUM=4",
            "PHASE1_BENCH_STRING_CHECKSUM=5",
            "PHASE1_BENCH_HWEIGHT_CHECKSUM=6",
            "PHASE1_BENCH_LIST_SORT_CHECKSUM=7",
            "PHASE1_BENCH_RBTREE_CHECKSUM=8",
            "PHASE1_BENCH_RBTREE_POSTORDER_SAFE_CHECKSUM=9",
            "PHASE1_BENCH_RBTREE_FIND_ADD_CHECKSUM=10",
            "PHASE1_BENCH_RBTREE_DUPLICATE_CHECKSUM=11",
            "PHASE1_BENCH_RBTREE_CACHED_CHECKSUM=12",
        ]
    )
    kind, _ = validate_output(expectations, ok_output)
    assert kind == "pass"
    case_count += 1

    missing_expectations_path = Path(tempfile.gettempdir()) / "phase1-bench-self-test-missing.json"
    if missing_expectations_path.exists():
        missing_expectations_path.unlink()
    kind, payload = load_runtime_expectations(missing_expectations_path)
    assert kind == "expectations_missing"
    assert payload == missing_expectations_path
    case_count += 1

    with tempfile.TemporaryDirectory(prefix="phase1-bench-self-test-json-") as tmpdir:
        invalid_expectations_path = Path(tmpdir) / "phase1-bench-expectations.json"
        invalid_expectations_path.write_text("{", encoding="utf-8")
        kind, payload = load_runtime_expectations(invalid_expectations_path)
        assert kind == "expectations_json_error"
        assert isinstance(payload, json.JSONDecodeError)
        assert payload.lineno == 1
        assert payload.colno == 2
    case_count += 1

    status_mismatch_output = ok_output.replace(
        "PHASE1_BENCH=pass",
        "PHASE1_BENCH=fail",
        1,
    )
    kind, payload = validate_output(expectations, status_mismatch_output)
    assert kind == "status"
    assert payload == ("pass", "fail")
    case_count += 1

    missing_status_output = ok_output.replace("PHASE1_BENCH=pass\n", "", 1)
    kind, payload = validate_output(expectations, missing_status_output)
    assert kind == "status"
    assert payload == ("pass", None)
    case_count += 1

    unexpected_output = ok_output + "\nPHASE1_BENCH_SPURIOUS=13"
    kind, payload = validate_output(expectations, unexpected_output)
    assert kind == "unexpected"
    assert payload == ["PHASE1_BENCH_SPURIOUS"]
    case_count += 1

    duplicate_iteration_output = ok_output + "\nPHASE1_BENCH_FIND_NEXT_BIT_ITERATIONS=20000"
    kind, payload = validate_output(expectations, duplicate_iteration_output)
    assert kind == "duplicate"
    assert payload == ["PHASE1_BENCH_FIND_NEXT_BIT_ITERATIONS"]
    case_count += 1

    rbtree_iteration_mismatch_output = ok_output.replace(
        "PHASE1_BENCH_RBTREE_ITERATIONS=4000",
        "PHASE1_BENCH_RBTREE_ITERATIONS=4",
    )
    kind, payload = validate_output(expectations, rbtree_iteration_mismatch_output)
    assert kind == "rbtree_iteration_mismatch"
    assert payload == ("PHASE1_BENCH_RBTREE_ITERATIONS", 4000, "4")
    case_count += 1

    for key, value in (
        ("PHASE1_BENCH_RBTREE_CHECKSUM", "8"),
        ("PHASE1_BENCH_RBTREE_POSTORDER_SAFE_CHECKSUM", "9"),
        ("PHASE1_BENCH_RBTREE_FIND_ADD_CHECKSUM", "10"),
        ("PHASE1_BENCH_RBTREE_DUPLICATE_CHECKSUM", "11"),
        ("PHASE1_BENCH_RBTREE_CACHED_CHECKSUM", "12"),
    ):
        missing_output = ok_output.replace(f"\n{key}={value}", "")
        kind, payload = validate_output(expectations, missing_output)
        assert kind == "missing_rbtree_exact_checksums"
        assert payload == [key]
        case_count += 1

    for key, value in (
        ("PHASE1_BENCH_BITMAP_WEIGHT_CHECKSUM", "1"),
        ("PHASE1_BENCH_BITMAP_WINDOW_CHECKSUM", "2"),
    ):
        missing_output = ok_output.replace(f"\n{key}={value}", "")
        kind, payload = validate_output(expectations, missing_output)
        assert kind == "missing_bitmap_exact_checksums"
        assert payload == [key]
        case_count += 1

    for key, value in (
        ("PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM", "3"),
        ("PHASE1_BENCH_FIND_BIT_EDGE_CHECKSUM", "4"),
    ):
        missing_output = ok_output.replace(f"\n{key}={value}", "")
        kind, payload = validate_output(expectations, missing_output)
        assert kind == "missing_find_bit_exact_checksums"
        assert payload == [key]
        case_count += 1

    for key, value, expected_kind in (
        ("PHASE1_BENCH_STRING_CHECKSUM", "5", "missing_string_exact_checksums"),
        ("PHASE1_BENCH_HWEIGHT_CHECKSUM", "6", "missing_hweight_exact_checksums"),
        ("PHASE1_BENCH_LIST_SORT_CHECKSUM", "7", "missing_list_sort_exact_checksums"),
    ):
        missing_output = ok_output.replace(f"\n{key}={value}", "")
        kind, payload = validate_output(expectations, missing_output)
        assert kind == expected_kind
        assert payload == [key]
        case_count += 1

    mismatch_output = ok_output.replace(
        "PHASE1_BENCH_RBTREE_CACHED_CHECKSUM=12",
        "PHASE1_BENCH_RBTREE_CACHED_CHECKSUM=120",
    )
    kind, payload = validate_output(expectations, mismatch_output)
    assert kind == "exact_checksum_mismatch"
    assert payload == ("PHASE1_BENCH_RBTREE_CACHED_CHECKSUM", 12, 120)
    case_count += 1

    duplicate_mismatch_output = ok_output.replace(
        "PHASE1_BENCH_RBTREE_DUPLICATE_CHECKSUM=11",
        "PHASE1_BENCH_RBTREE_DUPLICATE_CHECKSUM=110",
    )
    kind, payload = validate_output(expectations, duplicate_mismatch_output)
    assert kind == "exact_checksum_mismatch"
    assert payload == ("PHASE1_BENCH_RBTREE_DUPLICATE_CHECKSUM", 11, 110)
    case_count += 1

    duplicate_output = ok_output + "\nPHASE1_BENCH_RBTREE_CACHED_CHECKSUM=12"
    kind, payload = validate_output(expectations, duplicate_output)
    assert kind == "duplicate"
    assert payload == ["PHASE1_BENCH_RBTREE_CACHED_CHECKSUM"]
    case_count += 1

    downgraded_bitmap_weight_exact = {
        "status": "pass",
        "iterations": dict(EXPECTED_ITERATIONS),
        "checksums": list(EXPECTED_CHECKSUMS),
        "exact_checksums": {
            "PHASE1_BENCH_BITMAP_WINDOW_CHECKSUM": 2,
            "PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM": 3,
            "PHASE1_BENCH_FIND_BIT_EDGE_CHECKSUM": 4,
            "PHASE1_BENCH_STRING_CHECKSUM": 5,
            "PHASE1_BENCH_HWEIGHT_CHECKSUM": 6,
            "PHASE1_BENCH_LIST_SORT_CHECKSUM": 7,
            "PHASE1_BENCH_RBTREE_CHECKSUM": 8,
            "PHASE1_BENCH_RBTREE_POSTORDER_SAFE_CHECKSUM": 9,
            "PHASE1_BENCH_RBTREE_FIND_ADD_CHECKSUM": 10,
            "PHASE1_BENCH_RBTREE_DUPLICATE_CHECKSUM": 11,
            "PHASE1_BENCH_RBTREE_CACHED_CHECKSUM": 12,
        },
    }
    kind, payload = validate_expectations(downgraded_bitmap_weight_exact)
    assert kind == "expectations_checksums_bitmap_exact_required"
    assert payload == "PHASE1_BENCH_BITMAP_WEIGHT_CHECKSUM"
    case_count += 1

    downgraded_bitmap_window_exact = {
        "status": "pass",
        "iterations": dict(EXPECTED_ITERATIONS),
        "checksums": list(EXPECTED_CHECKSUMS),
        "exact_checksums": {
            "PHASE1_BENCH_BITMAP_WEIGHT_CHECKSUM": 1,
            "PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM": 3,
            "PHASE1_BENCH_FIND_BIT_EDGE_CHECKSUM": 4,
            "PHASE1_BENCH_STRING_CHECKSUM": 5,
            "PHASE1_BENCH_HWEIGHT_CHECKSUM": 6,
            "PHASE1_BENCH_LIST_SORT_CHECKSUM": 7,
            "PHASE1_BENCH_RBTREE_CHECKSUM": 8,
            "PHASE1_BENCH_RBTREE_POSTORDER_SAFE_CHECKSUM": 9,
            "PHASE1_BENCH_RBTREE_FIND_ADD_CHECKSUM": 10,
            "PHASE1_BENCH_RBTREE_DUPLICATE_CHECKSUM": 11,
            "PHASE1_BENCH_RBTREE_CACHED_CHECKSUM": 12,
        },
    }
    kind, payload = validate_expectations(downgraded_bitmap_window_exact)
    assert kind == "expectations_checksums_bitmap_exact_required"
    assert payload == "PHASE1_BENCH_BITMAP_WINDOW_CHECKSUM"
    case_count += 1

    downgraded_rbtree_exact = {
        "status": "pass",
        "iterations": dict(EXPECTED_ITERATIONS),
        "checksums": list(EXPECTED_CHECKSUMS),
        "exact_checksums": {
            "PHASE1_BENCH_BITMAP_WEIGHT_CHECKSUM": 1,
            "PHASE1_BENCH_BITMAP_WINDOW_CHECKSUM": 2,
            "PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM": 3,
            "PHASE1_BENCH_FIND_BIT_EDGE_CHECKSUM": 4,
            "PHASE1_BENCH_STRING_CHECKSUM": 5,
            "PHASE1_BENCH_HWEIGHT_CHECKSUM": 6,
            "PHASE1_BENCH_LIST_SORT_CHECKSUM": 7,
            "PHASE1_BENCH_RBTREE_CHECKSUM": 8,
            "PHASE1_BENCH_RBTREE_POSTORDER_SAFE_CHECKSUM": 9,
            "PHASE1_BENCH_RBTREE_FIND_ADD_CHECKSUM": 10,
            "PHASE1_BENCH_RBTREE_DUPLICATE_CHECKSUM": 11,
        },
    }
    kind, payload = validate_expectations(downgraded_rbtree_exact)
    assert kind == "expectations_checksums_rbtree_exact_required"
    assert payload == "PHASE1_BENCH_RBTREE_CACHED_CHECKSUM"
    case_count += 1

    missing_duplicate_exact = {
        "status": "pass",
        "iterations": dict(EXPECTED_ITERATIONS),
        "checksums": list(EXPECTED_CHECKSUMS),
        "exact_checksums": {
            "PHASE1_BENCH_BITMAP_WEIGHT_CHECKSUM": 1,
            "PHASE1_BENCH_BITMAP_WINDOW_CHECKSUM": 2,
            "PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM": 3,
            "PHASE1_BENCH_FIND_BIT_EDGE_CHECKSUM": 4,
            "PHASE1_BENCH_STRING_CHECKSUM": 5,
            "PHASE1_BENCH_HWEIGHT_CHECKSUM": 6,
            "PHASE1_BENCH_LIST_SORT_CHECKSUM": 7,
            "PHASE1_BENCH_RBTREE_CHECKSUM": 8,
            "PHASE1_BENCH_RBTREE_POSTORDER_SAFE_CHECKSUM": 9,
            "PHASE1_BENCH_RBTREE_FIND_ADD_CHECKSUM": 10,
            "PHASE1_BENCH_RBTREE_CACHED_CHECKSUM": 12,
        },
    }
    kind, payload = validate_expectations(missing_duplicate_exact)
    assert kind == "expectations_checksums_rbtree_exact_required"
    assert payload == "PHASE1_BENCH_RBTREE_DUPLICATE_CHECKSUM"
    case_count += 1

    missing_string_exact = {
        "status": "pass",
        "iterations": dict(EXPECTED_ITERATIONS),
        "checksums": list(EXPECTED_CHECKSUMS),
        "exact_checksums": {
            "PHASE1_BENCH_BITMAP_WEIGHT_CHECKSUM": 1,
            "PHASE1_BENCH_BITMAP_WINDOW_CHECKSUM": 2,
            "PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM": 3,
            "PHASE1_BENCH_FIND_BIT_EDGE_CHECKSUM": 4,
            "PHASE1_BENCH_HWEIGHT_CHECKSUM": 6,
            "PHASE1_BENCH_LIST_SORT_CHECKSUM": 7,
            "PHASE1_BENCH_RBTREE_CHECKSUM": 8,
            "PHASE1_BENCH_RBTREE_POSTORDER_SAFE_CHECKSUM": 9,
            "PHASE1_BENCH_RBTREE_FIND_ADD_CHECKSUM": 10,
            "PHASE1_BENCH_RBTREE_DUPLICATE_CHECKSUM": 11,
            "PHASE1_BENCH_RBTREE_CACHED_CHECKSUM": 12,
        },
    }
    kind, payload = validate_expectations(missing_string_exact)
    assert kind == "expectations_checksums_string_exact_required"
    assert payload == "PHASE1_BENCH_STRING_CHECKSUM"
    case_count += 1

    missing_hweight_exact = {
        "status": "pass",
        "iterations": dict(EXPECTED_ITERATIONS),
        "checksums": list(EXPECTED_CHECKSUMS),
        "exact_checksums": {
            "PHASE1_BENCH_BITMAP_WEIGHT_CHECKSUM": 1,
            "PHASE1_BENCH_BITMAP_WINDOW_CHECKSUM": 2,
            "PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM": 3,
            "PHASE1_BENCH_FIND_BIT_EDGE_CHECKSUM": 4,
            "PHASE1_BENCH_STRING_CHECKSUM": 5,
            "PHASE1_BENCH_LIST_SORT_CHECKSUM": 7,
            "PHASE1_BENCH_RBTREE_CHECKSUM": 8,
            "PHASE1_BENCH_RBTREE_POSTORDER_SAFE_CHECKSUM": 9,
            "PHASE1_BENCH_RBTREE_FIND_ADD_CHECKSUM": 10,
            "PHASE1_BENCH_RBTREE_DUPLICATE_CHECKSUM": 11,
            "PHASE1_BENCH_RBTREE_CACHED_CHECKSUM": 12,
        },
    }
    kind, payload = validate_expectations(missing_hweight_exact)
    assert kind == "expectations_checksums_hweight_exact_required"
    assert payload == "PHASE1_BENCH_HWEIGHT_CHECKSUM"
    case_count += 1

    missing_list_sort_exact = {
        "status": "pass",
        "iterations": dict(EXPECTED_ITERATIONS),
        "checksums": list(EXPECTED_CHECKSUMS),
        "exact_checksums": {
            "PHASE1_BENCH_BITMAP_WEIGHT_CHECKSUM": 1,
            "PHASE1_BENCH_BITMAP_WINDOW_CHECKSUM": 2,
            "PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM": 3,
            "PHASE1_BENCH_FIND_BIT_EDGE_CHECKSUM": 4,
            "PHASE1_BENCH_STRING_CHECKSUM": 5,
            "PHASE1_BENCH_HWEIGHT_CHECKSUM": 6,
            "PHASE1_BENCH_RBTREE_CHECKSUM": 8,
            "PHASE1_BENCH_RBTREE_POSTORDER_SAFE_CHECKSUM": 9,
            "PHASE1_BENCH_RBTREE_FIND_ADD_CHECKSUM": 10,
            "PHASE1_BENCH_RBTREE_DUPLICATE_CHECKSUM": 11,
            "PHASE1_BENCH_RBTREE_CACHED_CHECKSUM": 12,
        },
    }
    kind, payload = validate_expectations(missing_list_sort_exact)
    assert kind == "expectations_checksums_list_sort_exact_required"
    assert payload == "PHASE1_BENCH_LIST_SORT_CHECKSUM"
    case_count += 1

    missing_find_next_exact = {
        "status": "pass",
        "iterations": dict(EXPECTED_ITERATIONS),
        "checksums": list(EXPECTED_CHECKSUMS),
        "exact_checksums": {
            "PHASE1_BENCH_BITMAP_WEIGHT_CHECKSUM": 1,
            "PHASE1_BENCH_BITMAP_WINDOW_CHECKSUM": 2,
            "PHASE1_BENCH_FIND_BIT_EDGE_CHECKSUM": 4,
            "PHASE1_BENCH_STRING_CHECKSUM": 5,
            "PHASE1_BENCH_HWEIGHT_CHECKSUM": 6,
            "PHASE1_BENCH_LIST_SORT_CHECKSUM": 7,
            "PHASE1_BENCH_RBTREE_CHECKSUM": 8,
            "PHASE1_BENCH_RBTREE_POSTORDER_SAFE_CHECKSUM": 9,
            "PHASE1_BENCH_RBTREE_FIND_ADD_CHECKSUM": 10,
            "PHASE1_BENCH_RBTREE_DUPLICATE_CHECKSUM": 11,
            "PHASE1_BENCH_RBTREE_CACHED_CHECKSUM": 12,
        },
    }
    kind, payload = validate_expectations(missing_find_next_exact)
    assert kind == "expectations_checksums_find_bit_exact_required"
    assert payload == "PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM"
    case_count += 1

    missing_find_bit_edge_exact = {
        "status": "pass",
        "iterations": dict(EXPECTED_ITERATIONS),
        "checksums": list(EXPECTED_CHECKSUMS),
        "exact_checksums": {
            "PHASE1_BENCH_BITMAP_WEIGHT_CHECKSUM": 1,
            "PHASE1_BENCH_BITMAP_WINDOW_CHECKSUM": 2,
            "PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM": 3,
            "PHASE1_BENCH_STRING_CHECKSUM": 5,
            "PHASE1_BENCH_HWEIGHT_CHECKSUM": 6,
            "PHASE1_BENCH_LIST_SORT_CHECKSUM": 7,
            "PHASE1_BENCH_RBTREE_CHECKSUM": 8,
            "PHASE1_BENCH_RBTREE_POSTORDER_SAFE_CHECKSUM": 9,
            "PHASE1_BENCH_RBTREE_FIND_ADD_CHECKSUM": 10,
            "PHASE1_BENCH_RBTREE_DUPLICATE_CHECKSUM": 11,
            "PHASE1_BENCH_RBTREE_CACHED_CHECKSUM": 12,
        },
    }
    kind, payload = validate_expectations(missing_find_bit_edge_exact)
    assert kind == "expectations_checksums_find_bit_exact_required"
    assert payload == "PHASE1_BENCH_FIND_BIT_EDGE_CHECKSUM"
    case_count += 1

    missing_rbtree_iterations = {
        "status": "pass",
        "iterations": {
            key: value
            for key, value in EXPECTED_ITERATIONS.items()
            if key != "PHASE1_BENCH_RBTREE_ITERATIONS"
        },
        "checksums": list(EXPECTED_CHECKSUMS),
        "exact_checksums": {
            "PHASE1_BENCH_BITMAP_WEIGHT_CHECKSUM": 1,
            "PHASE1_BENCH_BITMAP_WINDOW_CHECKSUM": 2,
            "PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM": 3,
            "PHASE1_BENCH_FIND_BIT_EDGE_CHECKSUM": 4,
            "PHASE1_BENCH_STRING_CHECKSUM": 5,
            "PHASE1_BENCH_HWEIGHT_CHECKSUM": 6,
            "PHASE1_BENCH_LIST_SORT_CHECKSUM": 7,
            "PHASE1_BENCH_RBTREE_CHECKSUM": 8,
            "PHASE1_BENCH_RBTREE_POSTORDER_SAFE_CHECKSUM": 9,
            "PHASE1_BENCH_RBTREE_FIND_ADD_CHECKSUM": 10,
            "PHASE1_BENCH_RBTREE_DUPLICATE_CHECKSUM": 11,
            "PHASE1_BENCH_RBTREE_CACHED_CHECKSUM": 12,
        },
    }
    kind, payload = validate_expectations(missing_rbtree_iterations)
    assert kind == "expectations_missing_rbtree_iterations"
    assert payload == ["PHASE1_BENCH_RBTREE_ITERATIONS"]
    case_count += 1

    reordered_checksums = {
        "status": "pass",
        "iterations": dict(EXPECTED_ITERATIONS),
        "checksums": [
            "PHASE1_BENCH_BITMAP_WINDOW_CHECKSUM",
            "PHASE1_BENCH_BITMAP_WEIGHT_CHECKSUM",
            "PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM",
            "PHASE1_BENCH_FIND_BIT_EDGE_CHECKSUM",
            "PHASE1_BENCH_STRING_CHECKSUM",
            "PHASE1_BENCH_HWEIGHT_CHECKSUM",
            "PHASE1_BENCH_LIST_SORT_CHECKSUM",
            "PHASE1_BENCH_RBTREE_CHECKSUM",
        ],
        "exact_checksums": {
            "PHASE1_BENCH_BITMAP_WEIGHT_CHECKSUM": 1,
            "PHASE1_BENCH_BITMAP_WINDOW_CHECKSUM": 2,
            "PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM": 3,
            "PHASE1_BENCH_FIND_BIT_EDGE_CHECKSUM": 4,
            "PHASE1_BENCH_STRING_CHECKSUM": 5,
            "PHASE1_BENCH_HWEIGHT_CHECKSUM": 6,
            "PHASE1_BENCH_LIST_SORT_CHECKSUM": 7,
            "PHASE1_BENCH_RBTREE_CHECKSUM": 8,
            "PHASE1_BENCH_RBTREE_POSTORDER_SAFE_CHECKSUM": 9,
            "PHASE1_BENCH_RBTREE_FIND_ADD_CHECKSUM": 10,
            "PHASE1_BENCH_RBTREE_DUPLICATE_CHECKSUM": 11,
            "PHASE1_BENCH_RBTREE_CACHED_CHECKSUM": 12,
        },
    }
    kind, payload = validate_expectations(reordered_checksums)
    assert kind == "expectations_checksum_order"
    assert payload == reordered_checksums["checksums"]
    case_count += 1

    print("PHASE1_BENCH_CHECK_SELF_TEST=pass")
    print(f"PHASE1_BENCH_CHECK_SELF_TEST_CASE_COUNT={case_count}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run and validate the bounded Phase 1 benchmark smoke output.")
    parser.add_argument("--zig", help="Path to Zig executable")
    parser.add_argument("--self-test", action="store_true", help="Run checker self-test cases without invoking Zig.")
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return 0

    kind, payload = load_runtime_expectations(EXPECTATIONS)
    if kind == "expectations_missing":
        print("PHASE1_BENCH_CHECK=fail")
        print("PHASE1_BENCH_CHECK_REASON=expectations_missing")
        print(f"PHASE1_BENCH_EXPECTATIONS={payload}")
        return 1
    if kind == "expectations_json_error":
        exc = payload
        assert isinstance(exc, json.JSONDecodeError)
        print("PHASE1_BENCH_CHECK=fail")
        print("PHASE1_BENCH_CHECK_REASON=expectations_json_error")
        print("EXPECTATIONS_JSON_ERROR={}".format(exc.msg))
        print("EXPECTATIONS_JSON_LINE={}".format(exc.lineno))
        print("EXPECTATIONS_JSON_COLUMN={}".format(exc.colno))
        return 1
    if kind != "pass":
        print("PHASE1_BENCH_CHECK=fail")
        print(f"PHASE1_BENCH_CHECK_REASON={kind}")
        print(payload)
        return 1

    expectations = payload
    assert isinstance(expectations, dict)

    zig = find_zig(args.zig)
    result = subprocess.run(
        [zig, "build", "bench", "--build-file", "zigux/tests/build.zig", "-Doptimize=ReleaseSafe"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print("PHASE1_BENCH_CHECK=fail")
        print(f"BENCH_COMMAND_EXIT={result.returncode}")
        if result.stdout:
            print(result.stdout.rstrip("\n"))
        if result.stderr:
            print(result.stderr.rstrip("\n"))
        return 1

    kind, payload = validate_output(expectations, result.stdout)
    if kind != "pass":
        print("PHASE1_BENCH_CHECK=fail")
        print(f"PHASE1_BENCH_CHECK_REASON={kind}")
        print(payload)
        return 1

    print("PHASE1_BENCH_CHECK=pass")
    print(f"PHASE1_BENCH_EXPECTATION_COUNT={len(expectations['checksums'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
