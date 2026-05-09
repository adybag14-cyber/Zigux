#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import subprocess


ROOT = Path(__file__).resolve().parents[2]
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
]
REQUIRED_EXACT_CHECKSUMS = {
    "PHASE1_BENCH_BITMAP_WEIGHT_CHECKSUM",
    "PHASE1_BENCH_BITMAP_WINDOW_CHECKSUM",
    "PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM",
    "PHASE1_BENCH_FIND_BIT_EDGE_CHECKSUM",
    "PHASE1_BENCH_STRING_CHECKSUM",
    "PHASE1_BENCH_RBTREE_CHECKSUM",
    "PHASE1_BENCH_RBTREE_DUPLICATE_MUTATION_CHECKSUM",
    "PHASE1_BENCH_RBTREE_CACHED_CHECKSUM",
}
BITMAP_REQUIRED_EXACT_CHECKSUMS = {
    "PHASE1_BENCH_BITMAP_WEIGHT_CHECKSUM",
    "PHASE1_BENCH_BITMAP_WINDOW_CHECKSUM",
}
RBTREE_REQUIRED_EXACT_CHECKSUMS = {
    "PHASE1_BENCH_RBTREE_CHECKSUM",
    "PHASE1_BENCH_RBTREE_DUPLICATE_MUTATION_CHECKSUM",
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

    for key in sorted(RBTREE_REQUIRED_EXACT_CHECKSUMS):
        if key in checksum_keys and key not in exact_checksums:
            return ("expectations_checksums_rbtree_exact_required", key)

    exact_keys = set(exact_checksums)
    if exact_keys != REQUIRED_EXACT_CHECKSUMS:
        missing = sorted(REQUIRED_EXACT_CHECKSUMS - exact_keys)
        unexpected = sorted(exact_keys - REQUIRED_EXACT_CHECKSUMS)
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
            "PHASE1_BENCH_RBTREE_CHECKSUM": 6,
            "PHASE1_BENCH_RBTREE_DUPLICATE_MUTATION_CHECKSUM": 7,
            "PHASE1_BENCH_RBTREE_CACHED_CHECKSUM": 8,
        },
    }
    kind, payload = validate_expectations(expectations)
    assert kind == "pass", (kind, payload)

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
            "PHASE1_BENCH_HWEIGHT_CHECKSUM=9",
            "PHASE1_BENCH_LIST_SORT_CHECKSUM=10",
            "PHASE1_BENCH_RBTREE_CHECKSUM=6",
            "PHASE1_BENCH_RBTREE_DUPLICATE_MUTATION_CHECKSUM=7",
            "PHASE1_BENCH_RBTREE_CACHED_CHECKSUM=8",
        ]
    )
    kind, _ = validate_output(expectations, ok_output)
    assert kind == "pass"

    rbtree_iteration_mismatch_output = ok_output.replace(
        "PHASE1_BENCH_RBTREE_ITERATIONS=4000",
        "PHASE1_BENCH_RBTREE_ITERATIONS=4",
    )
    kind, payload = validate_output(expectations, rbtree_iteration_mismatch_output)
    assert kind == "rbtree_iteration_mismatch"
    assert payload == ("PHASE1_BENCH_RBTREE_ITERATIONS", 4000, "4")

    mismatch_output = ok_output.replace(
        "PHASE1_BENCH_RBTREE_CACHED_CHECKSUM=8",
        "PHASE1_BENCH_RBTREE_CACHED_CHECKSUM=80",
    )
    kind, payload = validate_output(expectations, mismatch_output)
    assert kind == "exact_checksum_mismatch"
    assert payload == ("PHASE1_BENCH_RBTREE_CACHED_CHECKSUM", 8, 80)

    duplicate_mutation_mismatch_output = ok_output.replace(
        "PHASE1_BENCH_RBTREE_DUPLICATE_MUTATION_CHECKSUM=7",
        "PHASE1_BENCH_RBTREE_DUPLICATE_MUTATION_CHECKSUM=70",
    )
    kind, payload = validate_output(expectations, duplicate_mutation_mismatch_output)
    assert kind == "exact_checksum_mismatch"
    assert payload == ("PHASE1_BENCH_RBTREE_DUPLICATE_MUTATION_CHECKSUM", 7, 70)

    duplicate_output = ok_output + "\nPHASE1_BENCH_RBTREE_CACHED_CHECKSUM=8"
    kind, payload = validate_output(expectations, duplicate_output)
    assert kind == "duplicate"
    assert payload == ["PHASE1_BENCH_RBTREE_CACHED_CHECKSUM"]

    downgraded_bitmap_weight_exact = {
        "status": "pass",
        "iterations": dict(EXPECTED_ITERATIONS),
        "checksums": list(EXPECTED_CHECKSUMS),
        "exact_checksums": {
            "PHASE1_BENCH_BITMAP_WINDOW_CHECKSUM": 2,
            "PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM": 3,
            "PHASE1_BENCH_FIND_BIT_EDGE_CHECKSUM": 4,
            "PHASE1_BENCH_STRING_CHECKSUM": 5,
            "PHASE1_BENCH_RBTREE_CHECKSUM": 6,
            "PHASE1_BENCH_RBTREE_DUPLICATE_MUTATION_CHECKSUM": 7,
            "PHASE1_BENCH_RBTREE_CACHED_CHECKSUM": 8,
        },
    }
    kind, payload = validate_expectations(downgraded_bitmap_weight_exact)
    assert kind == "expectations_checksums_bitmap_exact_required"
    assert payload == "PHASE1_BENCH_BITMAP_WEIGHT_CHECKSUM"

    downgraded_bitmap_window_exact = {
        "status": "pass",
        "iterations": dict(EXPECTED_ITERATIONS),
        "checksums": list(EXPECTED_CHECKSUMS),
        "exact_checksums": {
            "PHASE1_BENCH_BITMAP_WEIGHT_CHECKSUM": 1,
            "PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM": 3,
            "PHASE1_BENCH_FIND_BIT_EDGE_CHECKSUM": 4,
            "PHASE1_BENCH_STRING_CHECKSUM": 5,
            "PHASE1_BENCH_RBTREE_CHECKSUM": 6,
            "PHASE1_BENCH_RBTREE_DUPLICATE_MUTATION_CHECKSUM": 7,
            "PHASE1_BENCH_RBTREE_CACHED_CHECKSUM": 8,
        },
    }
    kind, payload = validate_expectations(downgraded_bitmap_window_exact)
    assert kind == "expectations_checksums_bitmap_exact_required"
    assert payload == "PHASE1_BENCH_BITMAP_WINDOW_CHECKSUM"

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
            "PHASE1_BENCH_RBTREE_CHECKSUM": 6,
            "PHASE1_BENCH_RBTREE_DUPLICATE_MUTATION_CHECKSUM": 7,
        },
    }
    kind, payload = validate_expectations(downgraded_rbtree_exact)
    assert kind == "expectations_missing_exact_checksums"
    assert payload == ["PHASE1_BENCH_RBTREE_CACHED_CHECKSUM"]

    missing_duplicate_mutation_exact = {
        "status": "pass",
        "iterations": dict(EXPECTED_ITERATIONS),
        "checksums": list(EXPECTED_CHECKSUMS),
        "exact_checksums": {
            "PHASE1_BENCH_BITMAP_WEIGHT_CHECKSUM": 1,
            "PHASE1_BENCH_BITMAP_WINDOW_CHECKSUM": 2,
            "PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM": 3,
            "PHASE1_BENCH_FIND_BIT_EDGE_CHECKSUM": 4,
            "PHASE1_BENCH_STRING_CHECKSUM": 5,
            "PHASE1_BENCH_RBTREE_CHECKSUM": 6,
            "PHASE1_BENCH_RBTREE_CACHED_CHECKSUM": 8,
        },
    }
    kind, payload = validate_expectations(missing_duplicate_mutation_exact)
    assert kind == "expectations_missing_exact_checksums"
    assert payload == ["PHASE1_BENCH_RBTREE_DUPLICATE_MUTATION_CHECKSUM"]

    missing_string_exact = {
        "status": "pass",
        "iterations": dict(EXPECTED_ITERATIONS),
        "checksums": list(EXPECTED_CHECKSUMS),
        "exact_checksums": {
            "PHASE1_BENCH_BITMAP_WEIGHT_CHECKSUM": 1,
            "PHASE1_BENCH_BITMAP_WINDOW_CHECKSUM": 2,
            "PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM": 3,
            "PHASE1_BENCH_FIND_BIT_EDGE_CHECKSUM": 4,
            "PHASE1_BENCH_RBTREE_CHECKSUM": 6,
            "PHASE1_BENCH_RBTREE_DUPLICATE_MUTATION_CHECKSUM": 7,
            "PHASE1_BENCH_RBTREE_CACHED_CHECKSUM": 8,
        },
    }
    kind, payload = validate_expectations(missing_string_exact)
    assert kind == "expectations_missing_exact_checksums"
    assert payload == ["PHASE1_BENCH_STRING_CHECKSUM"]

    missing_find_next_exact = {
        "status": "pass",
        "iterations": dict(EXPECTED_ITERATIONS),
        "checksums": list(EXPECTED_CHECKSUMS),
        "exact_checksums": {
            "PHASE1_BENCH_BITMAP_WEIGHT_CHECKSUM": 1,
            "PHASE1_BENCH_BITMAP_WINDOW_CHECKSUM": 2,
            "PHASE1_BENCH_FIND_BIT_EDGE_CHECKSUM": 4,
            "PHASE1_BENCH_STRING_CHECKSUM": 5,
            "PHASE1_BENCH_RBTREE_CHECKSUM": 6,
            "PHASE1_BENCH_RBTREE_DUPLICATE_MUTATION_CHECKSUM": 7,
            "PHASE1_BENCH_RBTREE_CACHED_CHECKSUM": 8,
        },
    }
    kind, payload = validate_expectations(missing_find_next_exact)
    assert kind == "expectations_missing_exact_checksums"
    assert payload == ["PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM"]

    missing_find_bit_edge_exact = {
        "status": "pass",
        "iterations": dict(EXPECTED_ITERATIONS),
        "checksums": list(EXPECTED_CHECKSUMS),
        "exact_checksums": {
            "PHASE1_BENCH_BITMAP_WEIGHT_CHECKSUM": 1,
            "PHASE1_BENCH_BITMAP_WINDOW_CHECKSUM": 2,
            "PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM": 3,
            "PHASE1_BENCH_STRING_CHECKSUM": 5,
            "PHASE1_BENCH_RBTREE_CHECKSUM": 6,
            "PHASE1_BENCH_RBTREE_DUPLICATE_MUTATION_CHECKSUM": 7,
            "PHASE1_BENCH_RBTREE_CACHED_CHECKSUM": 8,
        },
    }
    kind, payload = validate_expectations(missing_find_bit_edge_exact)
    assert kind == "expectations_missing_exact_checksums"
    assert payload == ["PHASE1_BENCH_FIND_BIT_EDGE_CHECKSUM"]

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
            "PHASE1_BENCH_RBTREE_CHECKSUM": 6,
            "PHASE1_BENCH_RBTREE_DUPLICATE_MUTATION_CHECKSUM": 7,
            "PHASE1_BENCH_RBTREE_CACHED_CHECKSUM": 8,
        },
    }
    kind, payload = validate_expectations(missing_rbtree_iterations)
    assert kind == "expectations_missing_rbtree_iterations"
    assert payload == ["PHASE1_BENCH_RBTREE_ITERATIONS"]

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
            "PHASE1_BENCH_RBTREE_CHECKSUM": 6,
            "PHASE1_BENCH_RBTREE_DUPLICATE_MUTATION_CHECKSUM": 7,
            "PHASE1_BENCH_RBTREE_CACHED_CHECKSUM": 8,
        },
    }
    kind, payload = validate_expectations(reordered_checksums)
    assert kind == "expectations_checksum_order"
    assert payload == reordered_checksums["checksums"]

    print("PHASE1_BENCH_CHECK_SELF_TEST=pass")
    print("PHASE1_BENCH_CHECK_SELF_TEST_CASE_COUNT=14")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run and validate the bounded Phase 1 benchmark smoke output.")
    parser.add_argument("--zig", help="Path to Zig executable")
    parser.add_argument("--self-test", action="store_true", help="Run checker self-test cases without invoking Zig.")
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return 0

    try:
        expectations = load_expectations(EXPECTATIONS)
    except json.JSONDecodeError as exc:
        print("PHASE1_BENCH_CHECK=fail")
        print(f"EXPECTATIONS_JSON_ERROR={exc.msg}")
        print(f"EXPECTATIONS_JSON_LINE={exc.lineno}")
        print(f"EXPECTATIONS_JSON_COLUMN={exc.colno}")
        return 1

    kind, payload = validate_expectations(expectations)
    if kind != "pass":
        print("PHASE1_BENCH_CHECK=fail")
        print(f"PHASE1_BENCH_CHECK_REASON={kind}")
        print(payload)
        return 1

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

    assert isinstance(expectations, dict)
    kind, payload = validate_output(expectations, result.stdout)
    if kind != "pass":
        print("PHASE1_BENCH_CHECK=fail")
        print(f"PHASE1_BENCH_CHECK_REASON={kind}")
        print(payload)
        return 1

    print("PHASE1_BENCH_CHECK=pass")
    print(f"PHASE1_BENCH_EXPECTATIONS={EXPECTATIONS}")
    print(f"PHASE1_BENCH_ZIG={zig}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
