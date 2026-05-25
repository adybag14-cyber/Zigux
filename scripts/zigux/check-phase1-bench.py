#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent
EXPECTATIONS_REL = Path("zigux/tests/fixtures/phase1_bench_expectations.json")
PHASE1_BENCH_REL = Path("zigux/tests/phase1_bench.zig")
BUILD_FILE_REL = Path("zigux/tests/build.zig")
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
FIND_BIT_REQUIRED_SOURCE_MARKERS = {
    "find_bit_bench_fn": "fn findBitBench() struct { checksum: u64 } {",
    "find_bit_edge_fn": "fn findBitEdgeBench() struct { checksum: u64 } {",
    "find_bit_bench_call": "const find_bit_result = findBitBench();",
    "find_bit_edge_call": "const find_bit_edge_result = findBitEdgeBench();",
    "find_next_iterations_print": 'try stdout_writer.interface.print("PHASE1_BENCH_FIND_NEXT_BIT_ITERATIONS={d}\\n", .{iterations_find_bit});',
    "find_next_checksum_print": 'try stdout_writer.interface.print("PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM={d}\\n", .{find_bit_result.checksum});',
    "find_edge_iterations_print": 'try stdout_writer.interface.print("PHASE1_BENCH_FIND_BIT_EDGE_ITERATIONS={d}\\n", .{iterations_find_bit_edge});',
    "find_edge_checksum_print": 'try stdout_writer.interface.print("PHASE1_BENCH_FIND_BIT_EDGE_CHECKSUM={d}\\n", .{find_bit_edge_result.checksum});',
    "boundary_next_bit": "checksum +%= @intCast(find_bit.findNextBit(&boundary_set, head_nbits, boundary));",
    "boundary_next_and_bit": "checksum +%= @intCast(find_bit.findNextAndBit(&boundary_set, &boundary_set, head_nbits, boundary));",
    "boundary_next_zero_bit": "checksum +%= @intCast(find_bit.findNextZeroBit(&boundary_zero, head_nbits, boundary));",
    "tail_first_bit": "checksum +%= @intCast(find_bit.findFirstBit(&tail_set, tail_nbits));",
    "tail_first_and_bit": "checksum +%= @intCast(find_bit.findFirstAndBit(&tail_set, &tail_set, tail_nbits));",
    "tail_last_bit": "checksum +%= @intCast(find_bit.findLastBit(&tail_set, tail_nbits));",
}
RBTREE_REQUIRED_SOURCE_MARKERS = {
    "rbtree_bench_fn": "fn rbtreeBench() struct { checksum: u64 } {",
    "rbtree_postorder_safe_fn": "fn rbtreePostorderSafeBench() struct { checksum: u64 } {",
    "rbtree_find_add_fn": "fn rbtreeFindAddBench() struct { checksum: u64 } {",
    "rbtree_duplicate_fn": "fn rbtreeDuplicateBench() struct { checksum: u64 } {",
    "rbtree_cached_fn": "fn rbtreeCachedBench() struct { checksum: u64 } {",
    "rbtree_bench_call": "const rbtree_result = rbtreeBench();",
    "rbtree_postorder_safe_call": "const rbtree_postorder_safe_result = rbtreePostorderSafeBench();",
    "rbtree_find_add_call": "const rbtree_find_add_result = rbtreeFindAddBench();",
    "rbtree_duplicate_call": "const rbtree_duplicate_result = rbtreeDuplicateBench();",
    "rbtree_cached_call": "const rbtree_cached_result = rbtreeCachedBench();",
    "rbtree_iterations_print": 'try stdout_writer.interface.print("PHASE1_BENCH_RBTREE_ITERATIONS={d}\\n", .{iterations_rbtree});',
    "rbtree_checksum_print": 'try stdout_writer.interface.print("PHASE1_BENCH_RBTREE_CHECKSUM={d}\\n", .{rbtree_result.checksum});',
    "rbtree_postorder_safe_print": 'try stdout_writer.interface.print("PHASE1_BENCH_RBTREE_POSTORDER_SAFE_CHECKSUM={d}\\n", .{rbtree_postorder_safe_result.checksum});',
    "rbtree_find_add_print": 'try stdout_writer.interface.print("PHASE1_BENCH_RBTREE_FIND_ADD_CHECKSUM={d}\\n", .{rbtree_find_add_result.checksum});',
    "rbtree_duplicate_print": 'try stdout_writer.interface.print("PHASE1_BENCH_RBTREE_DUPLICATE_CHECKSUM={d}\\n", .{rbtree_duplicate_result.checksum});',
    "rbtree_cached_print": 'try stdout_writer.interface.print("PHASE1_BENCH_RBTREE_CACHED_CHECKSUM={d}\\n", .{rbtree_cached_result.checksum});',
    "rbtree_insert": "rbtree.add(&entry.node, &root, less);",
    "rbtree_postorder": "var node = rbtree.firstPostorder(&root);",
    "rbtree_find_add": "const existing = rbtree.findAdd(&probe.node, &root, cmp);",
    "rbtree_duplicate_range": "var iter = rbtree.matchIterator(&duplicate_key, &root, key_cmp);",
    "rbtree_cached_leftmost": "const promoted_leftmost = rbtree.eraseCached(&entries[1].node, &cached_root);",
}


class DuplicateTrackingDict(dict[str, object]):
    def __init__(self, pairs: list[tuple[str, object]]) -> None:
        super().__init__()
        self.duplicate_keys: list[str] = []
        for key, value in pairs:
            if key in self and key not in self.duplicate_keys:
                self.duplicate_keys.append(key)
            self[key] = value


def resolve_root(explicit: str | None) -> Path:
    if explicit:
        return Path(explicit).resolve()
    return DEFAULT_ROOT


def expectations_path(root: Path) -> Path:
    return root / EXPECTATIONS_REL


def phase1_bench_path(root: Path) -> Path:
    return root / PHASE1_BENCH_REL


def build_file_path(root: Path) -> Path:
    return root / BUILD_FILE_REL


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
        return ("missing_expectations_file", path)
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

    for label, required_keys in (
        ("bitmap", BITMAP_REQUIRED_EXACT_CHECKSUMS),
        ("find_bit", FIND_BIT_REQUIRED_EXACT_CHECKSUMS),
        ("string", STRING_REQUIRED_EXACT_CHECKSUMS),
        ("hweight", HWEIGHT_REQUIRED_EXACT_CHECKSUMS),
        ("list_sort", LIST_SORT_REQUIRED_EXACT_CHECKSUMS),
        ("rbtree", RBTREE_REQUIRED_EXACT_CHECKSUMS),
    ):
        for key in sorted(required_keys):
            if key in checksum_keys and key not in exact_checksums:
                return (f"expectations_checksums_{label}_exact_required", key)

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


def validate_bench_source(text: str) -> tuple[str, object]:
    missing = [
        label for label, marker in FIND_BIT_REQUIRED_SOURCE_MARKERS.items() if marker not in text
    ]
    missing.extend(
        label for label, marker in RBTREE_REQUIRED_SOURCE_MARKERS.items() if marker not in text
    )
    if missing:
        return ("bench_source_missing_markers", missing)
    return ("pass", text)


def load_runtime_bench_source(path: Path) -> tuple[str, object]:
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ("missing_bench_source_file", path)
    return validate_bench_source(text)


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

    for label, required_keys in (
        ("rbtree", RBTREE_REQUIRED_EXACT_CHECKSUMS),
        ("bitmap", BITMAP_REQUIRED_EXACT_CHECKSUMS),
        ("find_bit", FIND_BIT_REQUIRED_EXACT_CHECKSUMS),
        ("string", STRING_REQUIRED_EXACT_CHECKSUMS),
        ("hweight", HWEIGHT_REQUIRED_EXACT_CHECKSUMS),
        ("list_sort", LIST_SORT_REQUIRED_EXACT_CHECKSUMS),
    ):
        missing_exact = sorted(key for key in required_keys if parsed.get(key) is None)
        if missing_exact:
            return (f"missing_{label}_exact_checksums", missing_exact)

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


def build_find_bit_bench_source(omit_label: str | None = None) -> str:
    lines = [
        "fn findBitBench() struct { checksum: u64 } {",
        "    checksum +%= @intCast(find_bit.findNextBit(&boundary_set, head_nbits, boundary));",
        "}",
        "fn findBitEdgeBench() struct { checksum: u64 } {",
        "    checksum +%= @intCast(find_bit.findNextBit(&boundary_set, head_nbits, boundary));",
        "    checksum +%= @intCast(find_bit.findNextAndBit(&boundary_set, &boundary_set, head_nbits, boundary));",
        "    checksum +%= @intCast(find_bit.findNextZeroBit(&boundary_zero, head_nbits, boundary));",
        "    checksum +%= @intCast(find_bit.findFirstBit(&tail_set, tail_nbits));",
        "    checksum +%= @intCast(find_bit.findFirstAndBit(&tail_set, &tail_set, tail_nbits));",
        "    checksum +%= @intCast(find_bit.findLastBit(&tail_set, tail_nbits));",
        "}",
        "const find_bit_result = findBitBench();",
        "const find_bit_edge_result = findBitEdgeBench();",
        'try stdout_writer.interface.print("PHASE1_BENCH_FIND_NEXT_BIT_ITERATIONS={d}\\n", .{iterations_find_bit});',
        'try stdout_writer.interface.print("PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM={d}\\n", .{find_bit_result.checksum});',
        'try stdout_writer.interface.print("PHASE1_BENCH_FIND_BIT_EDGE_ITERATIONS={d}\\n", .{iterations_find_bit_edge});',
        'try stdout_writer.interface.print("PHASE1_BENCH_FIND_BIT_EDGE_CHECKSUM={d}\\n", .{find_bit_edge_result.checksum});',
    ]
    if omit_label is not None:
        marker = FIND_BIT_REQUIRED_SOURCE_MARKERS[omit_label]
        lines = [line for line in lines if line != marker]
    return "\n".join(lines) + "\n"


def build_rbtree_bench_source(omit_label: str | None = None) -> str:
    lines = [
        "fn rbtreeBench() struct { checksum: u64 } {",
        "    rbtree.add(&entry.node, &root, less);",
        "}",
        "fn rbtreePostorderSafeBench() struct { checksum: u64 } {",
        "    var node = rbtree.firstPostorder(&root);",
        "}",
        "fn rbtreeFindAddBench() struct { checksum: u64 } {",
        "    const existing = rbtree.findAdd(&probe.node, &root, cmp);",
        "}",
        "fn rbtreeDuplicateBench() struct { checksum: u64 } {",
        "    var iter = rbtree.matchIterator(&duplicate_key, &root, key_cmp);",
        "}",
        "fn rbtreeCachedBench() struct { checksum: u64 } {",
        "    const promoted_leftmost = rbtree.eraseCached(&entries[1].node, &cached_root);",
        "}",
        "const rbtree_result = rbtreeBench();",
        "const rbtree_postorder_safe_result = rbtreePostorderSafeBench();",
        "const rbtree_find_add_result = rbtreeFindAddBench();",
        "const rbtree_duplicate_result = rbtreeDuplicateBench();",
        "const rbtree_cached_result = rbtreeCachedBench();",
        'try stdout_writer.interface.print("PHASE1_BENCH_RBTREE_ITERATIONS={d}\\n", .{iterations_rbtree});',
        'try stdout_writer.interface.print("PHASE1_BENCH_RBTREE_CHECKSUM={d}\\n", .{rbtree_result.checksum});',
        'try stdout_writer.interface.print("PHASE1_BENCH_RBTREE_POSTORDER_SAFE_CHECKSUM={d}\\n", .{rbtree_postorder_safe_result.checksum});',
        'try stdout_writer.interface.print("PHASE1_BENCH_RBTREE_FIND_ADD_CHECKSUM={d}\\n", .{rbtree_find_add_result.checksum});',
        'try stdout_writer.interface.print("PHASE1_BENCH_RBTREE_DUPLICATE_CHECKSUM={d}\\n", .{rbtree_duplicate_result.checksum});',
        'try stdout_writer.interface.print("PHASE1_BENCH_RBTREE_CACHED_CHECKSUM={d}\\n", .{rbtree_cached_result.checksum});',
    ]
    if omit_label is not None:
        marker = RBTREE_REQUIRED_SOURCE_MARKERS[omit_label]
        lines = [line for line in lines if line != marker]
    return "\n".join(lines) + "\n"


def build_full_bench_source(
    omit_find_bit_label: str | None = None,
    omit_rbtree_label: str | None = None,
) -> str:
    return (
        build_find_bit_bench_source(omit_find_bit_label)
        + build_rbtree_bench_source(omit_rbtree_label)
    )


def make_expectations(*, missing_exact: str | None = None, reordered_checksums: bool = False) -> dict[str, object]:
    exact_checksums = {
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
    }
    if missing_exact is not None:
        del exact_checksums[missing_exact]
    checksums = list(EXPECTED_CHECKSUMS)
    if reordered_checksums:
        checksums = [
            "PHASE1_BENCH_BITMAP_WINDOW_CHECKSUM",
            "PHASE1_BENCH_BITMAP_WEIGHT_CHECKSUM",
            "PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM",
            "PHASE1_BENCH_FIND_BIT_EDGE_CHECKSUM",
            "PHASE1_BENCH_STRING_CHECKSUM",
            "PHASE1_BENCH_HWEIGHT_CHECKSUM",
            "PHASE1_BENCH_LIST_SORT_CHECKSUM",
            "PHASE1_BENCH_RBTREE_CHECKSUM",
        ]
    return {
        "status": "pass",
        "iterations": dict(EXPECTED_ITERATIONS),
        "checksums": checksums,
        "exact_checksums": exact_checksums,
    }


def ok_output_lines() -> list[str]:
    return [
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


def write_fake_zig(path: Path, output: str) -> None:
    path.write_text(
        "\n".join(
            (
                "#!/usr/bin/env python3",
                "import sys",
                f"sys.stdout.write({output!r})",
                "raise SystemExit(0)",
                "",
            )
        ),
        encoding="utf-8",
    )
    path.chmod(0o755)


def run_self_test() -> None:
    case_count = 0

    expectations = make_expectations()
    kind, payload = validate_expectations(expectations)
    assert kind == "pass", (kind, payload)
    case_count += 1

    kind, payload = validate_bench_source(build_full_bench_source())
    assert kind == "pass", (kind, payload)
    case_count += 1

    with tempfile.TemporaryDirectory(prefix="phase1-bench-source-") as tmp:
        missing_path = Path(tmp) / "phase1_bench.zig"
        kind, payload = load_runtime_bench_source(missing_path)
        assert kind == "missing_bench_source_file"
        assert payload == missing_path
        case_count += 1

        source_path = Path(tmp) / "phase1_bench.zig"
        source_path.write_text(build_full_bench_source(), encoding="utf-8")
        kind, payload = load_runtime_bench_source(source_path)
        assert kind == "pass", (kind, payload)
        case_count += 1

        source_path.write_text(
            build_full_bench_source(omit_find_bit_label="find_edge_checksum_print"),
            encoding="utf-8",
        )
        kind, payload = load_runtime_bench_source(source_path)
        assert kind == "bench_source_missing_markers"
        assert payload == ["find_edge_checksum_print"]
        case_count += 1

        source_path.write_text(
            build_full_bench_source(omit_rbtree_label="rbtree_cached_print"),
            encoding="utf-8",
        )
        kind, payload = load_runtime_bench_source(source_path)
        assert kind == "bench_source_missing_markers"
        assert payload == ["rbtree_cached_print"]
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

    duplicate_iteration_text = duplicate_top_level_text.replace(
        '"PHASE1_BENCH_RBTREE_ITERATIONS": 4000',
        '"PHASE1_BENCH_RBTREE_ITERATIONS": 4000,\n    "PHASE1_BENCH_RBTREE_ITERATIONS": 4001',
        1,
    ).replace('"status": "fail",\n', "", 1)
    kind, payload = validate_expectations(load_expectations_text(duplicate_iteration_text))
    assert kind == "expectations_duplicate_iteration_keys"
    assert payload == ["PHASE1_BENCH_RBTREE_ITERATIONS"]
    case_count += 1

    duplicate_exact_checksum_text = duplicate_top_level_text.replace(
        '"PHASE1_BENCH_RBTREE_CACHED_CHECKSUM": 12',
        '"PHASE1_BENCH_RBTREE_CACHED_CHECKSUM": 12,\n    "PHASE1_BENCH_RBTREE_CACHED_CHECKSUM": 13',
        1,
    ).replace('"status": "fail",\n', "", 1)
    kind, payload = validate_expectations(load_expectations_text(duplicate_exact_checksum_text))
    assert kind == "expectations_duplicate_exact_checksum_keys"
    assert payload == ["PHASE1_BENCH_RBTREE_CACHED_CHECKSUM"]
    case_count += 1

    duplicate_checksum_list = make_expectations()
    duplicate_checksum_list["checksums"] = list(EXPECTED_CHECKSUMS) + ["PHASE1_BENCH_RBTREE_CACHED_CHECKSUM"]
    kind, payload = validate_expectations(duplicate_checksum_list)
    assert kind == "expectations_duplicate_checksums"
    assert payload == ["PHASE1_BENCH_RBTREE_CACHED_CHECKSUM"]
    case_count += 1

    ok_output = "\n".join(ok_output_lines())
    kind, payload = validate_output(expectations, ok_output)
    assert kind == "pass", (kind, payload)
    case_count += 1

    expectations_cases = [
        ("expectations_checksums_bitmap_exact_required", "PHASE1_BENCH_BITMAP_WEIGHT_CHECKSUM"),
        ("expectations_checksums_bitmap_exact_required", "PHASE1_BENCH_BITMAP_WINDOW_CHECKSUM"),
        ("expectations_checksums_rbtree_exact_required", "PHASE1_BENCH_RBTREE_CACHED_CHECKSUM"),
        ("expectations_checksums_rbtree_exact_required", "PHASE1_BENCH_RBTREE_DUPLICATE_CHECKSUM"),
        ("expectations_checksums_string_exact_required", "PHASE1_BENCH_STRING_CHECKSUM"),
        ("expectations_checksums_hweight_exact_required", "PHASE1_BENCH_HWEIGHT_CHECKSUM"),
        ("expectations_checksums_list_sort_exact_required", "PHASE1_BENCH_LIST_SORT_CHECKSUM"),
        ("expectations_checksums_find_bit_exact_required", "PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM"),
        ("expectations_checksums_find_bit_exact_required", "PHASE1_BENCH_FIND_BIT_EDGE_CHECKSUM"),
    ]
    for expected_kind, missing_key in expectations_cases:
        kind, payload = validate_expectations(make_expectations(missing_exact=missing_key))
        assert kind == expected_kind
        assert payload == missing_key
        case_count += 1

    missing_rbtree_iterations = make_expectations()
    del missing_rbtree_iterations["iterations"]["PHASE1_BENCH_RBTREE_ITERATIONS"]
    kind, payload = validate_expectations(missing_rbtree_iterations)
    assert kind == "expectations_missing_rbtree_iterations"
    assert payload == ["PHASE1_BENCH_RBTREE_ITERATIONS"]
    case_count += 1

    kind, payload = validate_expectations(make_expectations(reordered_checksums=True))
    assert kind == "expectations_checksum_order"
    case_count += 1

    output_cases = [
        ("status", ok_output.replace("PHASE1_BENCH=pass", "PHASE1_BENCH=fail", 1)),
        ("status", ok_output.replace("PHASE1_BENCH=pass\n", "", 1)),
        ("unexpected", ok_output + "\nPHASE1_BENCH_SPURIOUS=13"),
        ("duplicate", ok_output + "\nPHASE1_BENCH_FIND_NEXT_BIT_ITERATIONS=20000"),
        ("missing_rbtree_iterations", ok_output.replace("\nPHASE1_BENCH_RBTREE_ITERATIONS=4000", "")),
        ("rbtree_iteration_mismatch", ok_output.replace("PHASE1_BENCH_RBTREE_ITERATIONS=4000", "PHASE1_BENCH_RBTREE_ITERATIONS=4")),
        ("exact_checksum_mismatch", ok_output.replace("PHASE1_BENCH_RBTREE_CACHED_CHECKSUM=12", "PHASE1_BENCH_RBTREE_CACHED_CHECKSUM=120")),
        ("exact_checksum_mismatch", ok_output.replace("PHASE1_BENCH_RBTREE_DUPLICATE_CHECKSUM=11", "PHASE1_BENCH_RBTREE_DUPLICATE_CHECKSUM=110")),
        ("duplicate", ok_output + "\nPHASE1_BENCH_RBTREE_CACHED_CHECKSUM=12"),
    ]
    for expected_kind, text in output_cases:
        kind, payload = validate_output(expectations, text)
        assert kind == expected_kind, (kind, payload)
        case_count += 1

    for label, key, value in (
        ("missing_rbtree_exact_checksums", "PHASE1_BENCH_RBTREE_CHECKSUM", "8"),
        ("missing_rbtree_exact_checksums", "PHASE1_BENCH_RBTREE_POSTORDER_SAFE_CHECKSUM", "9"),
        ("missing_rbtree_exact_checksums", "PHASE1_BENCH_RBTREE_FIND_ADD_CHECKSUM", "10"),
        ("missing_rbtree_exact_checksums", "PHASE1_BENCH_RBTREE_DUPLICATE_CHECKSUM", "11"),
        ("missing_rbtree_exact_checksums", "PHASE1_BENCH_RBTREE_CACHED_CHECKSUM", "12"),
        ("missing_bitmap_exact_checksums", "PHASE1_BENCH_BITMAP_WEIGHT_CHECKSUM", "1"),
        ("missing_bitmap_exact_checksums", "PHASE1_BENCH_BITMAP_WINDOW_CHECKSUM", "2"),
        ("missing_find_bit_exact_checksums", "PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM", "3"),
        ("missing_find_bit_exact_checksums", "PHASE1_BENCH_FIND_BIT_EDGE_CHECKSUM", "4"),
        ("missing_string_exact_checksums", "PHASE1_BENCH_STRING_CHECKSUM", "5"),
        ("missing_hweight_exact_checksums", "PHASE1_BENCH_HWEIGHT_CHECKSUM", "6"),
        ("missing_list_sort_exact_checksums", "PHASE1_BENCH_LIST_SORT_CHECKSUM", "7"),
    ):
        kind, payload = validate_output(expectations, ok_output.replace(f"\n{key}={value}", ""))
        assert kind == label
        assert payload == [key]
        case_count += 1

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_root = Path(temp_dir)
        result = subprocess.run(
            [sys.executable, str(HERE), "--root", temp_dir],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 1
        expected_path = expectations_path(temp_root)
        assert "PHASE1_BENCH_CHECK=fail" in result.stdout
        assert "PHASE1_BENCH_CHECK_REASON=expectations_missing" in result.stdout
        assert f"PHASE1_BENCH_EXPECTATIONS={expected_path}" in result.stdout
        case_count += 1

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_root = Path(temp_dir)
        expected_path = expectations_path(temp_root)
        expected_path.parent.mkdir(parents=True, exist_ok=True)
        expected_path.write_text("{\n", encoding="utf-8")
        result = subprocess.run(
            [sys.executable, str(HERE), "--root", temp_dir],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 1
        assert "PHASE1_BENCH_CHECK=fail" in result.stdout
        assert "PHASE1_BENCH_CHECK_REASON=expectations_json_error" in result.stdout
        assert f"PHASE1_BENCH_EXPECTATIONS={expected_path}" in result.stdout
        assert "EXPECTATIONS_JSON_ERROR=" in result.stdout
        assert "EXPECTATIONS_JSON_LINE=" in result.stdout
        assert "EXPECTATIONS_JSON_COLUMN=" in result.stdout
        case_count += 1

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_root = Path(temp_dir)
        expected_path = expectations_path(temp_root)
        expected_path.parent.mkdir(parents=True, exist_ok=True)
        expected_path.write_text(duplicate_top_level_text, encoding="utf-8")
        result = subprocess.run(
            [sys.executable, str(HERE), "--root", temp_dir],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 1
        assert "PHASE1_BENCH_CHECK=fail" in result.stdout
        assert "PHASE1_BENCH_CHECK_REASON=expectations_duplicate_keys" in result.stdout
        assert f"PHASE1_BENCH_EXPECTATIONS={expected_path}" in result.stdout
        case_count += 1

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_root = Path(temp_dir)
        expected_path = expectations_path(temp_root)
        expected_path.parent.mkdir(parents=True, exist_ok=True)
        expected_path.write_text(json.dumps(expectations, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        result = subprocess.run(
            [sys.executable, str(HERE), "--root", temp_dir],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 1
        assert "PHASE1_BENCH_CHECK=fail" in result.stdout
        assert "PHASE1_BENCH_CHECK_REASON=missing_bench_source_file" in result.stdout
        assert f"PHASE1_BENCH_SOURCE={phase1_bench_path(temp_root)}" in result.stdout
        case_count += 1

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_root = Path(temp_dir)
        expected_path = expectations_path(temp_root)
        expected_path.parent.mkdir(parents=True, exist_ok=True)
        expected_path.write_text(json.dumps(expectations, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        source_path = phase1_bench_path(temp_root)
        source_path.parent.mkdir(parents=True, exist_ok=True)
        source_path.write_text(build_full_bench_source(omit_find_bit_label="find_edge_checksum_print"), encoding="utf-8")
        result = subprocess.run(
            [sys.executable, str(HERE), "--root", temp_dir],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 1
        assert "PHASE1_BENCH_CHECK=fail" in result.stdout
        assert "PHASE1_BENCH_CHECK_REASON=bench_source_missing_markers" in result.stdout
        assert f"PHASE1_BENCH_SOURCE={source_path}" in result.stdout
        case_count += 1

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_root = Path(temp_dir)
        expected_path = expectations_path(temp_root)
        expected_path.parent.mkdir(parents=True, exist_ok=True)
        expected_path.write_text(json.dumps(expectations, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        source_path = phase1_bench_path(temp_root)
        source_path.parent.mkdir(parents=True, exist_ok=True)
        source_path.write_text(build_full_bench_source(), encoding="utf-8")
        build_file = build_file_path(temp_root)
        build_file.parent.mkdir(parents=True, exist_ok=True)
        build_file.write_text("// bench build file is not executed by /bin/sh\n", encoding="utf-8")
        result = subprocess.run(
            [sys.executable, str(HERE), "--root", temp_dir, "--zig", "/bin/sh"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 1
        assert "PHASE1_BENCH_CHECK=fail" in result.stdout
        assert "PHASE1_BENCH_CHECK_REASON=bench_command_exit" in result.stdout
        assert f"PHASE1_BENCH_EXPECTATIONS={expected_path}" in result.stdout
        assert f"PHASE1_BENCH_SOURCE={source_path}" in result.stdout
        assert "BENCH_COMMAND_EXIT=" in result.stdout
        case_count += 1

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_root = Path(temp_dir)
        expected_path = expectations_path(temp_root)
        expected_path.parent.mkdir(parents=True, exist_ok=True)
        expected_path.write_text(json.dumps(expectations, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        source_path = phase1_bench_path(temp_root)
        source_path.parent.mkdir(parents=True, exist_ok=True)
        source_path.write_text(build_full_bench_source(), encoding="utf-8")
        build_file = build_file_path(temp_root)
        build_file.parent.mkdir(parents=True, exist_ok=True)
        build_file.write_text("// fake zig ignores this file\n", encoding="utf-8")
        fake_zig = temp_root / "fake-zig.py"
        fake_output = "\n".join(
            line
            for line in ok_output_lines()
            if not line.startswith("PHASE1_BENCH_BITMAP_WEIGHT_CHECKSUM=")
        ) + "\n"
        write_fake_zig(fake_zig, fake_output)
        result = subprocess.run(
            [sys.executable, str(HERE), "--root", temp_dir, "--zig", str(fake_zig)],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 1
        assert "PHASE1_BENCH_CHECK=fail" in result.stdout
        assert "PHASE1_BENCH_CHECK_REASON=missing_bitmap_exact_checksums" in result.stdout
        assert f"PHASE1_BENCH_EXPECTATIONS={expected_path}" in result.stdout
        assert f"PHASE1_BENCH_SOURCE={source_path}" in result.stdout
        case_count += 1

    print("PHASE1_BENCH_CHECK_SELF_TEST=pass")
    print(f"PHASE1_BENCH_CHECK_SELF_TEST_CASE_COUNT={case_count}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run and validate the bounded Phase 1 benchmark smoke output."
    )
    parser.add_argument("--root", help="Repository root to validate")
    parser.add_argument("--zig", help="Path to Zig executable")
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run checker self-test cases without invoking Zig.",
    )
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return 0

    root = resolve_root(args.root)
    expected_path = expectations_path(root)
    bench_source_path = phase1_bench_path(root)

    kind, payload = load_runtime_expectations(expected_path)
    if kind == "missing_expectations_file":
        print("PHASE1_BENCH_CHECK=fail")
        print("PHASE1_BENCH_CHECK_REASON=expectations_missing")
        print(f"PHASE1_BENCH_EXPECTATIONS={payload}")
        return 1
    if kind == "expectations_json_error":
        exc = payload
        assert isinstance(exc, json.JSONDecodeError)
        print("PHASE1_BENCH_CHECK=fail")
        print("PHASE1_BENCH_CHECK_REASON=expectations_json_error")
        print(f"PHASE1_BENCH_EXPECTATIONS={expected_path}")
        print("EXPECTATIONS_JSON_ERROR={}".format(exc.msg))
        print("EXPECTATIONS_JSON_LINE={}".format(exc.lineno))
        print("EXPECTATIONS_JSON_COLUMN={}".format(exc.colno))
        return 1
    if kind != "pass":
        print("PHASE1_BENCH_CHECK=fail")
        print(f"PHASE1_BENCH_CHECK_REASON={kind}")
        print(f"PHASE1_BENCH_EXPECTATIONS={expected_path}")
        print(payload)
        return 1

    expectations = payload
    assert isinstance(expectations, dict)

    kind, payload = load_runtime_bench_source(bench_source_path)
    if kind != "pass":
        print("PHASE1_BENCH_CHECK=fail")
        print(f"PHASE1_BENCH_CHECK_REASON={kind}")
        print(f"PHASE1_BENCH_SOURCE={bench_source_path}")
        print(payload)
        return 1

    zig = find_zig(args.zig)
    result = subprocess.run(
        [zig, "build", "bench", "--build-file", str(BUILD_FILE_REL), "-Doptimize=ReleaseSafe"],
        cwd=str(root),
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print("PHASE1_BENCH_CHECK=fail")
        print("PHASE1_BENCH_CHECK_REASON=bench_command_exit")
        print(f"PHASE1_BENCH_EXPECTATIONS={expected_path}")
        print(f"PHASE1_BENCH_SOURCE={bench_source_path}")
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
        print(f"PHASE1_BENCH_EXPECTATIONS={expected_path}")
        print(f"PHASE1_BENCH_SOURCE={bench_source_path}")
        print(payload)
        return 1

    print("PHASE1_BENCH_CHECK=pass")
    print(f"PHASE1_BENCH_EXPECTATIONS={expected_path}")
    print(f"PHASE1_BENCH_SOURCE={bench_source_path}")
    print(f"PHASE1_BENCH_ZIG={zig}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
