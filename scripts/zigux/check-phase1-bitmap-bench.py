#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXPECTATIONS = ROOT / "zigux" / "tests" / "fixtures" / "phase1_bench_expectations.json"
PHASE1_BENCH = ROOT / "zigux" / "tests" / "phase1_bench.zig"
EXPECTED_ITERATIONS = {
    "PHASE1_BENCH_BITMAP_WEIGHT_ITERATIONS": 20000,
    "PHASE1_BENCH_BITMAP_WINDOW_ITERATIONS": 20000,
}
EXPECTED_CHECKSUMS = [
    "PHASE1_BENCH_BITMAP_WEIGHT_CHECKSUM",
    "PHASE1_BENCH_BITMAP_WINDOW_CHECKSUM",
]
REQUIRED_BITMAP_SOURCE_MARKERS = [
    "fn bitmapWindowBench() struct { checksum: u64 } {",
    "const nbits = bitmap.bits_per_long + 5;",
    "bitmap.setRange(&lhs, bitmap.bits_per_long - 2, 6);",
    "lhs[1] |= @as(bitmap.Word, 1) << 2;",
    "rhs[1] &= ~(@as(bitmap.Word, 1) << 4);",
    "bitmap.orBits(&dst, &lhs, &rhs, nbits);",
    "bitmap.andBits(&dst, &lhs, &rhs, nbits)",
    "bitmap.andNotBits(&dst, &lhs, &rhs, nbits)",
    "bitmap.xorBits(&dst, &lhs, &rhs, nbits);",
    "bitmap.intersects(&lhs, &rhs, nbits)",
    "bitmap.subset(&rhs, &dst, nbits)",
]


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


def load_json_text(text: str) -> object:
    return json.loads(text, object_pairs_hook=DuplicateTrackingDict)


def load_expectations(path: Path) -> object:
    return load_json_text(path.read_text(encoding="utf-8"))


def validate_expectations(expectations: object) -> tuple[str, object]:
    if not isinstance(expectations, dict):
        return ("expectations_type", type(expectations).__name__)
    if isinstance(expectations, DuplicateTrackingDict) and expectations.duplicate_keys:
        return ("expectations_duplicate_keys", expectations.duplicate_keys)
    if expectations.get("status") != "pass":
        return ("expectations_status", expectations.get("status"))

    iterations = expectations.get("iterations")
    if not isinstance(iterations, dict):
        return ("expectations_iterations_type", type(iterations).__name__)
    if isinstance(iterations, DuplicateTrackingDict) and iterations.duplicate_keys:
        return ("expectations_duplicate_iteration_keys", iterations.duplicate_keys)
    for key, value in EXPECTED_ITERATIONS.items():
        actual = iterations.get(key)
        if not isinstance(actual, int):
            return ("expectations_iteration_value_type", (key, type(actual).__name__))
        if actual != value:
            return ("expectations_iteration_value", (key, value, actual))

    checksums = expectations.get("checksums")
    if not isinstance(checksums, list):
        return ("expectations_checksums_type", type(checksums).__name__)
    missing_checksums = [key for key in EXPECTED_CHECKSUMS if key not in checksums]
    if missing_checksums:
        return ("expectations_checksums", missing_checksums)

    exact_checksums = expectations.get("exact_checksums")
    if not isinstance(exact_checksums, dict):
        return ("expectations_exact_checksums_type", type(exact_checksums).__name__)
    if isinstance(exact_checksums, DuplicateTrackingDict) and exact_checksums.duplicate_keys:
        return ("expectations_duplicate_exact_checksum_keys", exact_checksums.duplicate_keys)
    for key in EXPECTED_CHECKSUMS:
        value = exact_checksums.get(key)
        if not isinstance(value, int):
            return ("expectations_exact_checksum_value_type", (key, type(value).__name__))
        if value <= 0:
            return ("expectations_exact_checksum_nonpositive", (key, value))

    return ("pass", expectations)


def validate_bench_source(source: str) -> tuple[str, object]:
    missing = [marker for marker in REQUIRED_BITMAP_SOURCE_MARKERS if marker not in source]
    if missing:
        return ("missing_bitmap_source_markers", missing)
    return ("pass", None)


def validate_output(expectations: dict[str, object], stdout: str) -> tuple[str, object]:
    parsed, counts = parse_output(stdout)
    expected_keys = {"PHASE1_BENCH", *EXPECTED_ITERATIONS, *EXPECTED_CHECKSUMS}
    duplicate = sorted(key for key in expected_keys if counts.get(key, 0) > 1)
    if duplicate:
        return ("duplicate", duplicate)
    unexpected = sorted(key for key in parsed if key.startswith("PHASE1_BENCH") and key not in expected_keys)
    if unexpected:
        return ("unexpected", unexpected)
    if parsed.get("PHASE1_BENCH") != "pass":
        return ("status", parsed.get("PHASE1_BENCH"))

    for key, value in EXPECTED_ITERATIONS.items():
        actual = parsed.get(key)
        if actual is None:
            return ("missing", [key])
        try:
            actual_value = int(actual)
        except ValueError:
            return ("iteration_value_type", (key, actual))
        if actual_value != value:
            return ("iteration_mismatch", (key, value, actual_value))

    exact_checksums = expectations["exact_checksums"]
    assert isinstance(exact_checksums, dict)
    for key in EXPECTED_CHECKSUMS:
        actual = parsed.get(key)
        if actual is None:
            return ("missing", [key])
        try:
            actual_value = int(actual)
        except ValueError:
            return ("checksum_value_type", (key, actual))
        if actual_value <= 0:
            return ("nonpositive_checksum", (key, actual_value))
        expected_value = exact_checksums[key]
        assert isinstance(expected_value, int)
        if actual_value != expected_value:
            return ("exact_checksum_mismatch", (key, expected_value, actual_value))

    return ("pass", parsed)


def self_test_case_count() -> int:
    return 8


def run_self_test() -> None:
    expectations = {
        "status": "pass",
        "iterations": dict(EXPECTED_ITERATIONS),
        "checksums": list(EXPECTED_CHECKSUMS),
        "exact_checksums": {
            "PHASE1_BENCH_BITMAP_WEIGHT_CHECKSUM": 2260000,
            "PHASE1_BENCH_BITMAP_WINDOW_CHECKSUM": 620000,
        },
    }

    kind, _ = validate_expectations(expectations)
    assert kind == "pass"

    source = "\n".join(REQUIRED_BITMAP_SOURCE_MARKERS)
    kind, _ = validate_bench_source(source)
    assert kind == "pass"

    missing_source = source.replace("bitmap.subset(&rhs, &dst, nbits)", "bitmap.subset(&lhs, &dst, nbits)", 1)
    kind, payload = validate_bench_source(missing_source)
    assert kind == "missing_bitmap_source_markers"
    assert payload == ["bitmap.subset(&rhs, &dst, nbits)"]

    ok_output = "\n".join(
        [
            "PHASE1_BENCH=pass",
            "PHASE1_BENCH_BITMAP_WEIGHT_ITERATIONS=20000",
            "PHASE1_BENCH_BITMAP_WINDOW_ITERATIONS=20000",
            "PHASE1_BENCH_BITMAP_WEIGHT_CHECKSUM=2260000",
            "PHASE1_BENCH_BITMAP_WINDOW_CHECKSUM=620000",
        ]
    )
    kind, _ = validate_output(expectations, ok_output)
    assert kind == "pass"

    duplicate_output = ok_output + "\nPHASE1_BENCH_BITMAP_WEIGHT_CHECKSUM=2260000"
    kind, payload = validate_output(expectations, duplicate_output)
    assert kind == "duplicate"
    assert payload == ["PHASE1_BENCH_BITMAP_WEIGHT_CHECKSUM"]

    mismatch_output = ok_output.replace("PHASE1_BENCH_BITMAP_WINDOW_CHECKSUM=620000", "PHASE1_BENCH_BITMAP_WINDOW_CHECKSUM=620001")
    kind, payload = validate_output(expectations, mismatch_output)
    assert kind == "exact_checksum_mismatch"
    assert payload == ("PHASE1_BENCH_BITMAP_WINDOW_CHECKSUM", 620000, 620001)

    bad_expectations = load_json_text(
        '{"status":"pass","iterations":{"PHASE1_BENCH_BITMAP_WEIGHT_ITERATIONS":20000,"PHASE1_BENCH_BITMAP_WINDOW_ITERATIONS":20000},'
        '"checksums":["PHASE1_BENCH_BITMAP_WEIGHT_CHECKSUM"],'
        '"exact_checksums":{"PHASE1_BENCH_BITMAP_WEIGHT_CHECKSUM":2260000,"PHASE1_BENCH_BITMAP_WINDOW_CHECKSUM":620000}}'
    )
    kind, payload = validate_expectations(bad_expectations)
    assert kind == "expectations_checksums"
    assert payload == ["PHASE1_BENCH_BITMAP_WINDOW_CHECKSUM"]

    missing_output = "\n".join(
        [
            "PHASE1_BENCH=pass",
            "PHASE1_BENCH_BITMAP_WEIGHT_ITERATIONS=20000",
            "PHASE1_BENCH_BITMAP_WINDOW_ITERATIONS=20000",
            "PHASE1_BENCH_BITMAP_WEIGHT_CHECKSUM=2260000",
        ]
    )
    kind, payload = validate_output(expectations, missing_output)
    assert kind == "missing"
    assert payload == ["PHASE1_BENCH_BITMAP_WINDOW_CHECKSUM"]

    print("PHASE1_BITMAP_BENCH_CHECK_SELF_TEST=pass")
    print(f"PHASE1_BITMAP_BENCH_CHECK_SELF_TEST_CASE_COUNT={self_test_case_count()}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Fail closed on the existing Phase 1 bitmap benchmark window source and exact checksum contract."
    )
    parser.add_argument("--zig", help="Path to Zig executable")
    parser.add_argument("--self-test", action="store_true", help="Run checker self-tests without invoking Zig")
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return 0

    expectations = load_expectations(EXPECTATIONS)
    kind, payload = validate_expectations(expectations)
    if kind != "pass":
        print("PHASE1_BITMAP_BENCH_CHECK=fail")
        print(f"EXPECTATIONS_FAILURE={kind}")
        print(f"EXPECTATIONS_DETAIL={payload}")
        return 1

    try:
        bench_source = PHASE1_BENCH.read_text(encoding="utf-8")
    except FileNotFoundError:
        print("PHASE1_BITMAP_BENCH_CHECK=fail")
        print(f"PHASE1_BENCH_SOURCE_MISSING={PHASE1_BENCH}")
        return 1

    kind, payload = validate_bench_source(bench_source)
    if kind != "pass":
        print("PHASE1_BITMAP_BENCH_CHECK=fail")
        print("MISSING_PHASE1_BITMAP_SOURCE_MARKERS_START")
        for marker in payload:
            print(marker)
        print("MISSING_PHASE1_BITMAP_SOURCE_MARKERS_END")
        return 1

    zig = find_zig(args.zig)
    result = subprocess.run(
        [zig, "build", "bench", "--build-file", "zigux/tests/build.zig", "-Doptimize=ReleaseSafe"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print("PHASE1_BITMAP_BENCH_CHECK=fail")
        print(f"BENCH_COMMAND_EXIT={result.returncode}")
        stdout = result.stdout.rstrip("\n")
        stderr = result.stderr.rstrip("\n")
        if stdout:
            print("PHASE1_BITMAP_BENCH_STDOUT_START")
            print(stdout)
            print("PHASE1_BITMAP_BENCH_STDOUT_END")
        if stderr:
            print("PHASE1_BITMAP_BENCH_STDERR_START")
            print(stderr)
            print("PHASE1_BITMAP_BENCH_STDERR_END")
        return 1

    kind, payload = validate_output(expectations, result.stdout)
    if kind != "pass":
        print("PHASE1_BITMAP_BENCH_CHECK=fail")
        print(f"OUTPUT_FAILURE={kind}")
        print(f"OUTPUT_DETAIL={payload}")
        return 1

    print("PHASE1_BITMAP_BENCH_CHECK=pass")
    print(f"PHASE1_BITMAP_BENCH_EXPECTATIONS={EXPECTATIONS}")
    print(f"PHASE1_BITMAP_BENCH_SOURCE={PHASE1_BENCH}")
    print(f"PHASE1_BITMAP_BENCH_ZIG={zig}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
