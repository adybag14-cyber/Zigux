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
    "PHASE1_BENCH_FIND_NEXT_BIT_ITERATIONS": 20000,
    "PHASE1_BENCH_FIND_BIT_EDGE_ITERATIONS": 20000,
    "PHASE1_BENCH_STRING_ITERATIONS": 40000,
    "PHASE1_BENCH_HWEIGHT_ITERATIONS": 100000,
    "PHASE1_BENCH_LIST_SORT_ITERATIONS": 1000,
    "PHASE1_BENCH_RBTREE_ITERATIONS": 4000,
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

REQUIRED_EXACT_CHECKSUMS = set(EXPECTED_CHECKSUMS)
REQUIRED_FIND_BIT_EXACT_CHECKSUMS = {
    "PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM",
    "PHASE1_BENCH_FIND_BIT_EDGE_CHECKSUM",
}

REQUIRED_BITMAP_SOURCE_MARKERS = [
    'fn bitmapBench() struct { checksum: u64 } {',
    "bitmap.setRange(&map, 5, 32);",
    "bitmap.setRange(&map, 256, 64);",
    "bitmap.setRange(&map, 2048, 17);",
    "checksum +%= @intCast(bitmap.weight(&map, 4096));",
    'fn bitmapWindowBench() struct { checksum: u64 } {',
    "const nbits = bitmap.bits_per_long + 5;",
    "if ((idx & 1) == 0) {",
    "lhs[1] |= @as(bitmap.Word, 1) << 2;",
    "rhs[1] &= ~(@as(bitmap.Word, 1) << 4);",
    "lhs[1] &= ~(@as(bitmap.Word, 1) << 2);",
    "rhs[1] |= @as(bitmap.Word, 1) << 4;",
    "checksum +%= @intCast(bitmap.weightedOr(&dst, &lhs, &rhs, nbits));",
    "checksum +%= @intCast(bitmap.__bitmap_weighted_or(&dst, &lhs, &rhs, nbits));",
    "checksum +%= @intCast(bitmap.weightAnd(&lhs, &rhs, nbits));",
    "checksum +%= @intCast(bitmap.bitmap_weight_and(&lhs, &rhs, nbits));",
    "checksum +%= @intCast(bitmap.__bitmap_weight_and(&lhs, &rhs, nbits));",
    "checksum +%= @intCast(bitmap.weightAndNot(&lhs, &rhs, nbits));",
    "checksum +%= @intCast(bitmap.bitmap_weight_andnot(&lhs, &rhs, nbits));",
    "checksum +%= @intCast(bitmap.__bitmap_weight_andnot(&lhs, &rhs, nbits));",
    "checksum +%= @intCast(bitmap.weightedXor(&dst, &lhs, &rhs, nbits));",
    "checksum +%= @intCast(bitmap.__bitmap_weighted_xor(&dst, &lhs, &rhs, nbits));",
    "bitmap.complement(&dst, &lhs, nbits);",
    "bitmap.__bitmap_complement(&dst, &rhs, nbits);",
    "bitmap.orBits(&dst, &lhs, &rhs, nbits);",
    "checksum +%= @as(u64, @intFromBool(bitmap.andBits(&dst, &lhs, &rhs, nbits)));",
    "checksum +%= @as(u64, @intFromBool(bitmap.andNotBits(&dst, &lhs, &rhs, nbits)));",
    "bitmap.xorBits(&dst, &lhs, &rhs, nbits);",
    "checksum +%= @as(u64, @intFromBool(bitmap.intersects(&lhs, &rhs, nbits)));",
    "checksum +%= @as(u64, @intFromBool(bitmap.subset(&rhs, &dst, nbits)));",
    "bitmap.__bitmap_or(&dst, &lhs, &rhs, nbits);",
    "checksum +%= @intCast(bitmap.__bitmap_weight(&dst, nbits));",
    "checksum +%= @as(u64, @intFromBool(bitmap.__bitmap_and(&dst, &lhs, &rhs, nbits)));",
    "checksum +%= @as(u64, @intFromBool(bitmap.__bitmap_andnot(&dst, &lhs, &rhs, nbits)));",
    "bitmap.__bitmap_xor(&dst, &lhs, &rhs, nbits);",
    "checksum +%= @as(u64, @intFromBool(bitmap.__bitmap_intersects(&lhs, &rhs, nbits)));",
    "checksum +%= @as(u64, @intFromBool(bitmap.__bitmap_subset(&rhs, &dst, nbits)));",
    "var cleared = [_]bitmap.Word{ 0, 0, copy_sentinel };",
    "bitmap.copyClearTail(cleared[0..2], partial_copy_src[0..2], copy_count);",
    "checksum +%= @intCast(bitmap.weight(cleared[0..2], copy_count));",
    "checksum +%= @as(u64, @intFromBool(cleared[1] == bitmap.lastWordMask(copy_count)));",
    "checksum +%= @as(u64, @intFromBool(cleared[2] == copy_sentinel));",
    "var extended = [_]bitmap.Word{ copy_sentinel, copy_sentinel, copy_sentinel, copy_sentinel };",
    "bitmap.copyAndExtend(extended[0..3], partial_copy_src[0..2], copy_count, copy_size);",
    "checksum +%= @intCast(bitmap.weight(extended[0..3], copy_size));",
    "checksum +%= @as(u64, @intFromBool(extended[1] == bitmap.lastWordMask(copy_count)));",
    "checksum +%= @as(u64, @intFromBool(extended[2] == 0));",
    "checksum +%= @as(u64, @intFromBool(extended[3] == copy_sentinel));",
    "var aligned_extended = [_]bitmap.Word{ copy_sentinel, copy_sentinel, copy_sentinel, copy_sentinel };",
    "bitmap.copyAndExtend(aligned_extended[0..3], aligned_copy_src[0..1], aligned_copy_count, copy_size);",
    "checksum +%= @intCast(bitmap.weight(aligned_extended[0..3], copy_size));",
    "checksum +%= @as(u64, @intFromBool(aligned_extended[0] == aligned_copy_src[0]));",
    "checksum +%= @as(u64, @intFromBool(aligned_extended[1] == 0));",
    "checksum +%= @as(u64, @intFromBool(aligned_extended[2] == 0));",
    "checksum +%= @as(u64, @intFromBool(aligned_extended[3] == copy_sentinel));",
]

REQUIRED_FIND_BIT_SOURCE_MARKERS = [
    'fn findBitBench() struct { checksum: u64 } {',
    "var map = std.mem.zeroes([find_bit.bitsToWords(4096)]find_bit.Word);",
    "map[0] |= (@as(find_bit.Word, 1) << 3);",
    "map[7] |= (@as(find_bit.Word, 1) << 9);",
    "map[15] |= (@as(find_bit.Word, 1) << 17);",
    "map[31] |= (@as(find_bit.Word, 1) << 1);",
    "checksum +%= @intCast(find_bit.findNextBit(&map, 4096, idx % 1024));",
    'fn findBitEdgeBench() struct { checksum: u64 } {',
    "const boundary = find_bit.bits_per_long - 1;",
    "const tail_nbits = find_bit.bits_per_long + 5;",
    "const past_nbits = 7;",
    "checksum +%= @intCast(find_bit.findNextBit(&boundary_set, head_nbits, boundary));",
    "checksum +%= @intCast(find_bit._find_next_bit(&boundary_set, head_nbits, boundary));",
    "checksum +%= @intCast(find_bit.find_next_bit(&boundary_set, head_nbits, boundary));",
    "checksum +%= @intCast(find_bit.findFirstBit(&tail_set, tail_nbits));",
    "checksum +%= @intCast(find_bit._find_first_bit(&tail_set, tail_nbits));",
    "checksum +%= @intCast(find_bit.find_first_bit(&tail_set, tail_nbits));",
    "checksum +%= @intCast(find_bit.findFirstZeroBit(&tail_full, tail_nbits));",
    "checksum +%= @intCast(find_bit._find_first_zero_bit(&tail_full, tail_nbits));",
    "checksum +%= @intCast(find_bit.find_first_zero_bit(&tail_full, tail_nbits));",
    "checksum +%= @intCast(find_bit.findNextZeroBit(&tail_full, tail_nbits, find_bit.bits_per_long));",
    "checksum +%= @intCast(find_bit.find_next_zero_bit(&tail_full, tail_nbits, find_bit.bits_per_long));",
    "checksum +%= @intCast(find_bit.findFirstAndBit(&tail_set, &tail_set, tail_nbits));",
    "checksum +%= @intCast(find_bit._find_first_and_bit(&tail_set, &tail_set, tail_nbits));",
    "checksum +%= @intCast(find_bit.find_first_and_bit(&tail_set, &tail_set, tail_nbits));",
    "checksum +%= @intCast(find_bit.findNextAndBit(&tail_set, &tail_set, tail_nbits, find_bit.bits_per_long + 4));",
    "checksum +%= @intCast(find_bit.find_next_and_bit(&tail_set, &tail_set, tail_nbits, find_bit.bits_per_long + 4));",
    "checksum +%= @intCast(find_bit.findLastBit(&tail_set, tail_nbits));",
    "checksum +%= @intCast(find_bit._find_last_bit(&tail_set, tail_nbits));",
    "checksum +%= @intCast(find_bit.find_last_bit(&tail_set, tail_nbits));",
    "checksum +%= @intCast(find_bit.findNextBit(&empty, past_nbits, past_nbits));",
    "checksum +%= @intCast(find_bit.findNextBit(&empty, past_nbits, past_nbits + 4));",
    "checksum +%= @intCast(find_bit.findNextZeroBit(&empty, past_nbits, past_nbits));",
    "checksum +%= @intCast(find_bit.findNextZeroBit(&empty, past_nbits, past_nbits + 4));",
    "checksum +%= @intCast(find_bit.findNextAndBit(&empty, &empty, past_nbits, past_nbits));",
    "checksum +%= @intCast(find_bit.findNextAndBit(&empty, &empty, past_nbits, past_nbits + 4));",
    "checksum +%= @intCast(find_bit.find_next_bit(&empty, past_nbits, past_nbits));",
    "checksum +%= @intCast(find_bit.find_next_bit(&empty, past_nbits, past_nbits + 4));",
    "checksum +%= @intCast(find_bit.find_next_zero_bit(&empty, past_nbits, past_nbits));",
    "checksum +%= @intCast(find_bit.find_next_zero_bit(&empty, past_nbits, past_nbits + 4));",
    "checksum +%= @intCast(find_bit.find_next_and_bit(&empty, &empty, past_nbits, past_nbits));",
    "checksum +%= @intCast(find_bit.find_next_and_bit(&empty, &empty, past_nbits, past_nbits + 4));",
]

REQUIRED_STRING_SOURCE_MARKERS = [
    'fn stringBench() !struct { checksum: u64 } {',
    'const enabled = try string.strtobool(if (even) "on" else "0");',
    "var trim_buf = [_]u8{ ' ', '\t', 'h', 'i', ' ', '\n' };",
    "const trimmed = string.trimSpaces(&trim_buf);",
    'const parsed = string.memparse(if (even) "64K rest" else "-17 tail");',
    "const dirty = if (even)",
    "string.memchrInv(\"aaaaXaaa\", 'a')",
    "string.memchrInv(\"bbbb\", 'b');",
    "checksum +%= @as(u64, @intFromBool(enabled));",
    "checksum +%= @intCast(trimmed.len);",
    "checksum +%= @intCast(parsed.rest.len);",
    "checksum +%= @as(u64, @intFromBool(dirty != null));",
]

REQUIRED_RBTREE_SOURCE_MARKERS = [
    "rbtree.findAdd(&find_add_entries[3].node, &find_add_root, cmpNode)",
    "rbtree.find(&wanted, &duplicate_root, cmpKey)",
    "duplicate_checksum +%= @as(u64, @intFromBool(rbtree.find(&missing, &duplicate_root, cmpKey) == null));",
    "rbtree.findFirst(&wanted, &duplicate_root, cmpKey)",
    "rbtree.nextMatch(&wanted, cursor, cmpKey)",
    "rbtree.erase(&duplicate_mutation_entries[2].node, &duplicate_mutation_root);",
    "duplicate_checksum +%= entry.serial + 97;",
    "rbtree.replaceNode(&duplicate_mutation_entries[4].node, &replacement_duplicate.node, &duplicate_mutation_root);",
    "duplicate_checksum +%= entry.serial + 107;",
    "rbtree.addCached(&entry.node, &cached_root, less);",
    'const initial_leftmost_entry: *const RbEntry = @fieldParentPtr("node", rbtree.firstCached(&cached_root).?);',
    "cached_checksum +%= @intCast(initial_leftmost_entry.key);",
    "cached_checksum +%= @as(u64, @intFromBool(rbtree.eraseCached(&cached_entries[2].node, &cached_root) == null));",
    'const still_leftmost_entry: *const RbEntry = @fieldParentPtr("node", rbtree.firstCached(&cached_root).?);',
    "cached_checksum +%= @intCast(still_leftmost_entry.key);",
    "const promoted_leftmost = rbtree.eraseCached(&cached_entries[1].node, &cached_root) orelse unreachable;",
    "cached_checksum +%= @intCast(promoted_leftmost_entry.key);",
    "rbtree.replaceNodeCached(&cached_entries[0].node, &cached_replacement.node, &cached_root)",
    'const replacement_leftmost_entry: *const RbEntry = @fieldParentPtr("node", rbtree.firstCached(&cached_root).?);',
    "cached_checksum +%= @intCast(replacement_leftmost_entry.key);",
    "rbtree.addCached(&new_leftmost.node, &cached_root, less);",
    "cached_checksum +%= @intCast(new_leftmost_entry.key);",
    "rbtree.first(&cached_root.root) == rbtree.firstCached(&cached_root)",
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


def load_expectations(path: Path) -> object:
    return load_expectations_text(path.read_text(encoding="utf-8"))


def load_expectations_text(text: str) -> object:
    return json.loads(text, object_pairs_hook=DuplicateTrackingDict)


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
    actual_iteration_keys = set()
    for key, value in iterations.items():
        if not isinstance(key, str):
            return ("expectations_iteration_key_type", type(key).__name__)
        if not isinstance(value, int):
            return ("expectations_iteration_value_type", (key, type(value).__name__))
        actual_iteration_keys.add(key)
        expected_value = EXPECTED_ITERATIONS.get(key)
        if expected_value is None:
            return ("expectations_unexpected_iteration", key)
        if value != expected_value:
            return ("expectations_iteration_value", (key, expected_value, value))
    missing_iterations = sorted(set(EXPECTED_ITERATIONS) - actual_iteration_keys)
    if missing_iterations:
        return ("expectations_missing_iterations", missing_iterations)

    checksums = expectations.get("checksums")
    if not isinstance(checksums, list):
        return ("expectations_checksums_type", type(checksums).__name__)
    seen: set[str] = set()
    duplicates: list[str] = []
    actual_checksums: list[str] = []
    for item in checksums:
        if not isinstance(item, str):
            return ("expectations_checksum_type", type(item).__name__)
        actual_checksums.append(item)
        if item in seen and item not in duplicates:
            duplicates.append(item)
        seen.add(item)
    if duplicates:
        return ("expectations_duplicate_checksums", duplicates)
    actual_checksum_set = set(actual_checksums)
    missing_checksums = sorted(set(EXPECTED_CHECKSUMS) - actual_checksum_set)
    if missing_checksums:
        return ("expectations_missing_checksums", missing_checksums)
    unexpected_checksums = sorted(actual_checksum_set - set(EXPECTED_CHECKSUMS))
    if unexpected_checksums:
        return ("expectations_unexpected_checksums", unexpected_checksums)

    exact_checksums = expectations.get("exact_checksums")
    if not isinstance(exact_checksums, dict):
        return ("expectations_exact_checksums_type", type(exact_checksums).__name__)
    actual_exact_checksum_keys = set()
    for key, value in exact_checksums.items():
        if not isinstance(key, str):
            return ("expectations_exact_checksum_key_type", type(key).__name__)
        if not isinstance(value, int):
            return ("expectations_exact_checksum_value_type", (key, type(value).__name__))
        if value <= 0:
            return ("expectations_exact_checksum_nonpositive", (key, value))
        if key not in actual_checksum_set:
            return ("expectations_exact_checksum_not_listed", key)
        actual_exact_checksum_keys.add(key)
    missing_find_bit_exact = sorted(REQUIRED_FIND_BIT_EXACT_CHECKSUMS - actual_exact_checksum_keys)
    if missing_find_bit_exact:
        return ("expectations_missing_find_bit_exact_checksums", missing_find_bit_exact)
    missing_exact = sorted(REQUIRED_EXACT_CHECKSUMS - actual_exact_checksum_keys)
    if missing_exact:
        return ("expectations_missing_exact_checksums", missing_exact)
    unexpected_exact = sorted(actual_exact_checksum_keys - REQUIRED_EXACT_CHECKSUMS)
    if unexpected_exact:
        return ("expectations_unexpected_exact_checksums", unexpected_exact)
    return ("pass", expectations)


def validate_bench_source(source: str) -> tuple[str, object]:
    for name, markers in [
        ("bitmap", REQUIRED_BITMAP_SOURCE_MARKERS),
        ("find_bit", REQUIRED_FIND_BIT_SOURCE_MARKERS),
        ("string", REQUIRED_STRING_SOURCE_MARKERS),
        ("rbtree", REQUIRED_RBTREE_SOURCE_MARKERS),
    ]:
        missing = [marker for marker in markers if marker not in source]
        if missing:
            return (f"missing_{name}_source_markers", missing)
    return ("pass", None)


def clone_expectations(expectations: dict[str, object]) -> dict[str, object]:
    iterations = expectations.get("iterations")
    checksums = expectations.get("checksums")
    exact_checksums = expectations.get("exact_checksums")
    assert isinstance(iterations, dict)
    assert isinstance(checksums, list)
    assert isinstance(exact_checksums, dict)
    return {
        "status": expectations["status"],
        "iterations": dict(iterations),
        "checksums": list(checksums),
        "exact_checksums": dict(exact_checksums),
    }


def load_full_expectations_for_self_test() -> dict[str, object]:
    expectations = load_expectations(EXPECTATIONS)
    kind, payload = validate_expectations(expectations)
    assert kind == "pass", (kind, payload)
    assert isinstance(expectations, dict)
    return clone_expectations(expectations)


def validate_output(expectations: dict[str, object], stdout: str) -> tuple[str, object]:
    parsed, counts = parse_output(stdout)
    exact_checksums: dict[str, int] = expectations["exact_checksums"]
    required_keys = {"PHASE1_BENCH", *expectations["iterations"].keys(), *expectations["checksums"]}
    duplicate = sorted(key for key in required_keys if counts.get(key, 0) > 1)
    if duplicate:
        return ("duplicate", duplicate)
    unexpected = sorted(key for key in parsed if key.startswith("PHASE1_BENCH") and key not in required_keys)
    if unexpected:
        return ("unexpected", unexpected)
    actual_status = parsed.get("PHASE1_BENCH")
    if actual_status != expectations["status"]:
        return ("status", (expectations["status"], actual_status))

    missing: list[str] = []
    for key, value in expectations["iterations"].items():
        actual = parsed.get(key)
        if actual is None:
            missing.append(key)
            continue
        try:
            actual_value = int(actual)
        except ValueError:
            return ("iteration_value_type", (key, actual))
        if actual_value != int(value):
            return ("iteration_mismatch", (key, value, actual))

    for key in expectations["checksums"]:
        actual = parsed.get(key)
        if actual is None:
            missing.append(key)
            continue
        try:
            actual_value = int(actual)
        except ValueError:
            return ("checksum_value_type", (key, actual))
        if actual_value <= 0:
            return ("nonpositive_checksum", (key, actual))
        expected_exact_value = exact_checksums.get(key)
        if expected_exact_value is not None and actual_value != expected_exact_value:
            return ("exact_checksum_mismatch", (key, expected_exact_value, actual_value))

    missing_find_bit_exact = sorted(key for key in REQUIRED_FIND_BIT_EXACT_CHECKSUMS if key in missing)
    if missing_find_bit_exact:
        return ("missing_find_bit_exact_checksums", missing_find_bit_exact)
    missing_exact = sorted(key for key in exact_checksums if key in missing)
    if missing_exact:
        return ("missing_exact_checksums", missing_exact)
    if missing:
        return ("missing", missing)
    return ("pass", parsed)


def run_self_test() -> None:
    full_expectations = load_full_expectations_for_self_test()
    exact = full_expectations["exact_checksums"]
    cases = 0
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
            f"PHASE1_BENCH_BITMAP_WEIGHT_CHECKSUM={exact['PHASE1_BENCH_BITMAP_WEIGHT_CHECKSUM']}",
            f"PHASE1_BENCH_BITMAP_WINDOW_CHECKSUM={exact['PHASE1_BENCH_BITMAP_WINDOW_CHECKSUM']}",
            f"PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM={exact['PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM']}",
            f"PHASE1_BENCH_FIND_BIT_EDGE_CHECKSUM={exact['PHASE1_BENCH_FIND_BIT_EDGE_CHECKSUM']}",
            f"PHASE1_BENCH_STRING_CHECKSUM={exact['PHASE1_BENCH_STRING_CHECKSUM']}",
            f"PHASE1_BENCH_HWEIGHT_CHECKSUM={exact['PHASE1_BENCH_HWEIGHT_CHECKSUM']}",
            f"PHASE1_BENCH_LIST_SORT_CHECKSUM={exact['PHASE1_BENCH_LIST_SORT_CHECKSUM']}",
            f"PHASE1_BENCH_RBTREE_CHECKSUM={exact['PHASE1_BENCH_RBTREE_CHECKSUM']}",
            f"PHASE1_BENCH_RBTREE_POSTORDER_SAFE_CHECKSUM={exact['PHASE1_BENCH_RBTREE_POSTORDER_SAFE_CHECKSUM']}",
            f"PHASE1_BENCH_RBTREE_FIND_ADD_CHECKSUM={exact['PHASE1_BENCH_RBTREE_FIND_ADD_CHECKSUM']}",
            f"PHASE1_BENCH_RBTREE_DUPLICATE_CHECKSUM={exact['PHASE1_BENCH_RBTREE_DUPLICATE_CHECKSUM']}",
            f"PHASE1_BENCH_RBTREE_CACHED_CHECKSUM={exact['PHASE1_BENCH_RBTREE_CACHED_CHECKSUM']}",
        ]
    )
    kind, _ = validate_output(full_expectations, ok_output)
    assert kind == "pass"
    cases += 1

    kind, _ = validate_bench_source(
        "\n".join(
            [
                *REQUIRED_BITMAP_SOURCE_MARKERS,
                *REQUIRED_FIND_BIT_SOURCE_MARKERS,
                *REQUIRED_STRING_SOURCE_MARKERS,
                *REQUIRED_RBTREE_SOURCE_MARKERS,
            ]
        )
    )
    assert kind == "pass"
    cases += 1

    missing_bitmap_marker = "checksum +%= @intCast(bitmap.weightedOr(&dst, &lhs, &rhs, nbits));"
    kind, payload = validate_bench_source(
        "\n".join(
            [
                *[marker for marker in REQUIRED_BITMAP_SOURCE_MARKERS if marker != missing_bitmap_marker],
                *REQUIRED_FIND_BIT_SOURCE_MARKERS,
                *REQUIRED_STRING_SOURCE_MARKERS,
                *REQUIRED_RBTREE_SOURCE_MARKERS,
            ]
        )
    )
    assert kind == "missing_bitmap_source_markers"
    assert payload == [missing_bitmap_marker]
    cases += 1

    kind, payload = validate_bench_source(
        "\n".join(
            [
                *REQUIRED_BITMAP_SOURCE_MARKERS,
                *REQUIRED_FIND_BIT_SOURCE_MARKERS,
                *REQUIRED_RBTREE_SOURCE_MARKERS,
            ]
        )
    )
    assert kind == "missing_string_source_markers"
    assert payload == REQUIRED_STRING_SOURCE_MARKERS
    cases += 1

    mismatch_output = ok_output.replace(
        f"PHASE1_BENCH_BITMAP_WINDOW_CHECKSUM={exact['PHASE1_BENCH_BITMAP_WINDOW_CHECKSUM']}",
        f"PHASE1_BENCH_BITMAP_WINDOW_CHECKSUM={exact['PHASE1_BENCH_BITMAP_WINDOW_CHECKSUM'] + 1}",
    )
    kind, payload = validate_output(full_expectations, mismatch_output)
    assert kind == "exact_checksum_mismatch"
    assert payload == (
        "PHASE1_BENCH_BITMAP_WINDOW_CHECKSUM",
        exact["PHASE1_BENCH_BITMAP_WINDOW_CHECKSUM"],
        exact["PHASE1_BENCH_BITMAP_WINDOW_CHECKSUM"] + 1,
    )
    cases += 1

    string_mismatch_output = ok_output.replace(
        f"PHASE1_BENCH_STRING_CHECKSUM={exact['PHASE1_BENCH_STRING_CHECKSUM']}",
        f"PHASE1_BENCH_STRING_CHECKSUM={exact['PHASE1_BENCH_STRING_CHECKSUM'] + 1}",
    )
    kind, payload = validate_output(full_expectations, string_mismatch_output)
    assert kind == "exact_checksum_mismatch"
    assert payload == (
        "PHASE1_BENCH_STRING_CHECKSUM",
        exact["PHASE1_BENCH_STRING_CHECKSUM"],
        exact["PHASE1_BENCH_STRING_CHECKSUM"] + 1,
    )
    cases += 1

    missing_output = ok_output.replace(
        f"\nPHASE1_BENCH_FIND_BIT_EDGE_CHECKSUM={exact['PHASE1_BENCH_FIND_BIT_EDGE_CHECKSUM']}",
        "",
    )
    kind, payload = validate_output(full_expectations, missing_output)
    assert kind == "missing_find_bit_exact_checksums"
    assert payload == ["PHASE1_BENCH_FIND_BIT_EDGE_CHECKSUM"]
    cases += 1

    missing_cached_output = ok_output.replace(
        f"\nPHASE1_BENCH_RBTREE_CACHED_CHECKSUM={exact['PHASE1_BENCH_RBTREE_CACHED_CHECKSUM']}",
        "",
    )
    kind, payload = validate_output(full_expectations, missing_cached_output)
    assert kind == "missing_exact_checksums"
    assert payload == ["PHASE1_BENCH_RBTREE_CACHED_CHECKSUM"]
    cases += 1

    print("PHASE1_BENCH_CHECK_SELF_TEST=pass")
    print(f"PHASE1_BENCH_CHECK_SELF_TEST_CASE_COUNT={cases}")


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
        if kind == "expectations_type":
            print(f"EXPECTATIONS_TYPE={payload}")
        elif kind == "expectations_status":
            print(f"EXPECTATIONS_STATUS={payload}")
        else:
            print(f"EXPECTATIONS_VALIDATION_KIND={kind}")
            if isinstance(payload, list):
                print("EXPECTATIONS_VALIDATION_PAYLOAD_START")
                for item in payload:
                    print(item)
                print("EXPECTATIONS_VALIDATION_PAYLOAD_END")
            else:
                print(f"EXPECTATIONS_VALIDATION_PAYLOAD={payload}")
        return 1

    try:
        bench_source = PHASE1_BENCH.read_text(encoding="utf-8")
    except FileNotFoundError:
        print("PHASE1_BENCH_CHECK=fail")
        print(f"PHASE1_BENCH_SOURCE_MISSING={PHASE1_BENCH}")
        return 1

    kind, payload = validate_bench_source(bench_source)
    if kind != "pass":
        print("PHASE1_BENCH_CHECK=fail")
        print(f"MISSING_PHASE1_BENCH_SOURCE_MARKER_GROUP={kind.removeprefix('missing_').removesuffix('_source_markers')}")
        print("MISSING_PHASE1_BENCH_SOURCE_MARKERS_START")
        for marker in payload:
            print(marker)
        print("MISSING_PHASE1_BENCH_SOURCE_MARKERS_END")
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
            print("PHASE1_BENCH_STDOUT_START")
            print(result.stdout.rstrip("\n"))
            print("PHASE1_BENCH_STDOUT_END")
        if result.stderr:
            print("PHASE1_BENCH_STDERR_START")
            print(result.stderr.rstrip("\n"))
            print("PHASE1_BENCH_STDERR_END")
        return 1

    kind, payload = validate_output(expectations, result.stdout)
    if kind != "pass":
        print("PHASE1_BENCH_CHECK=fail")
        if kind == "status":
            expected, actual = payload
            print(f"EXPECTED_STATUS={expected}")
            print(f"ACTUAL_STATUS={actual}")
        elif kind in {"iteration_mismatch", "exact_checksum_mismatch"}:
            key, expected, actual = payload
            print(f"{kind.upper()}={key}")
            print(f"EXPECTED={expected}")
            print(f"ACTUAL={actual}")
        elif kind in {"iteration_value_type", "checksum_value_type", "nonpositive_checksum"}:
            key, actual = payload
            print(f"{kind.upper()}={key}")
            print(f"ACTUAL={actual}")
        elif kind in {"duplicate", "unexpected", "missing_find_bit_exact_checksums", "missing_exact_checksums", "missing"}:
            print(f"{kind.upper()}_START")
            for item in payload:
                print(item)
            print(f"{kind.upper()}_END")
        return 1

    print("PHASE1_BENCH_CHECK=pass")
    print(f"PHASE1_BENCH_EXPECTATIONS={EXPECTATIONS}")
    print(f"PHASE1_BENCH_SOURCE={PHASE1_BENCH}")
    print(f"PHASE1_BENCH_ZIG={zig}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
