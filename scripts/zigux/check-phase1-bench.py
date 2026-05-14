#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXPECTATIONS = ROOT / 'zigux' / 'tests' / 'fixtures' / 'phase1_bench_expectations.json'
PHASE1_BENCH = ROOT / 'zigux' / 'tests' / 'phase1_bench.zig'
EXPECTED_ITERATIONS = {
    'PHASE1_BENCH_BITMAP_WEIGHT_ITERATIONS': 20000,
    'PHASE1_BENCH_BITMAP_WINDOW_ITERATIONS': 20000,
    'PHASE1_BENCH_FIND_NEXT_BIT_ITERATIONS': 20000,
    'PHASE1_BENCH_FIND_BIT_EDGE_ITERATIONS': 20000,
    'PHASE1_BENCH_STRING_ITERATIONS': 40000,
    'PHASE1_BENCH_HWEIGHT_ITERATIONS': 100000,
    'PHASE1_BENCH_LIST_SORT_ITERATIONS': 1000,
    'PHASE1_BENCH_RBTREE_ITERATIONS': 4000,
}
EXPECTED_CHECKSUMS = [
    'PHASE1_BENCH_BITMAP_WEIGHT_CHECKSUM',
    'PHASE1_BENCH_BITMAP_WINDOW_CHECKSUM',
    'PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM',
    'PHASE1_BENCH_FIND_BIT_EDGE_CHECKSUM',
    'PHASE1_BENCH_STRING_CHECKSUM',
    'PHASE1_BENCH_HWEIGHT_CHECKSUM',
    'PHASE1_BENCH_LIST_SORT_CHECKSUM',
    'PHASE1_BENCH_RBTREE_CHECKSUM',
    'PHASE1_BENCH_RBTREE_POSTORDER_SAFE_CHECKSUM',
    'PHASE1_BENCH_RBTREE_FIND_ADD_CHECKSUM',
    'PHASE1_BENCH_RBTREE_DUPLICATE_CHECKSUM',
    'PHASE1_BENCH_RBTREE_CACHED_CHECKSUM',
]
REQUIRED_EXACT_CHECKSUMS = {
    'PHASE1_BENCH_BITMAP_WEIGHT_CHECKSUM',
    'PHASE1_BENCH_BITMAP_WINDOW_CHECKSUM',
    'PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM',
    'PHASE1_BENCH_FIND_BIT_EDGE_CHECKSUM',
    'PHASE1_BENCH_STRING_CHECKSUM',
    'PHASE1_BENCH_RBTREE_CHECKSUM',
    'PHASE1_BENCH_RBTREE_POSTORDER_SAFE_CHECKSUM',
    'PHASE1_BENCH_RBTREE_FIND_ADD_CHECKSUM',
    'PHASE1_BENCH_RBTREE_DUPLICATE_CHECKSUM',
    'PHASE1_BENCH_RBTREE_CACHED_CHECKSUM',
}
REQUIRED_FIND_BIT_EXACT_CHECKSUMS = {
    'PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM',
    'PHASE1_BENCH_FIND_BIT_EDGE_CHECKSUM',
}
REQUIRED_BITMAP_SOURCE_MARKERS = [
    'fn bitmapBench() struct { checksum: u64 } {',
    'bitmap.setRange(&map, 5, 32);',
    'bitmap.setRange(&map, 256, 64);',
    'bitmap.setRange(&map, 2048, 17);',
    'checksum +%= @intCast(bitmap.weight(&map, 4096));',
    'fn bitmapWindowBench() struct { checksum: u64 } {',
    'const nbits = bitmap.bits_per_long + 5;',
    'if ((idx & 1) == 0) {',
    'lhs[1] |= @as(bitmap.Word, 1) << 2;',
    'rhs[1] &= ~(@as(bitmap.Word, 1) << 4);',
    'lhs[1] &= ~(@as(bitmap.Word, 1) << 2);',
    'rhs[1] |= @as(bitmap.Word, 1) << 4;',
    'bitmap.orBits(&dst, &lhs, &rhs, nbits);',
    'checksum +%= @as(u64, @intFromBool(bitmap.andBits(&dst, &lhs, &rhs, nbits)));',
    'checksum +%= @as(u64, @intFromBool(bitmap.andNotBits(&dst, &lhs, &rhs, nbits)));',
    'bitmap.xorBits(&dst, &lhs, &rhs, nbits);',
    'checksum +%= @as(u64, @intFromBool(bitmap.intersects(&lhs, &rhs, nbits)));',
    'checksum +%= @as(u64, @intFromBool(bitmap.subset(&rhs, &dst, nbits)));',
]
REQUIRED_FIND_BIT_SOURCE_MARKERS = [
    'fn findBitBench() struct { checksum: u64 } {',
    'var map = std.mem.zeroes([find_bit.bitsToWords(4096)]find_bit.Word);',
    'map[0] |= (@as(find_bit.Word, 1) << 3);',
    'map[7] |= (@as(find_bit.Word, 1) << 9);',
    'map[15] |= (@as(find_bit.Word, 1) << 17);',
    'map[31] |= (@as(find_bit.Word, 1) << 1);',
    'checksum +%= @intCast(find_bit.findNextBit(&map, 4096, idx % 1024));',
    'fn findBitEdgeBench() struct { checksum: u64 } {',
    'const boundary = find_bit.bits_per_long - 1;',
    'const tail_nbits = find_bit.bits_per_long + 5;',
    'const past_nbits = 7;',
    'checksum +%= @intCast(find_bit.findNextBit(&boundary_set, head_nbits, boundary));',
    'checksum +%= @intCast(find_bit._find_next_bit(&boundary_set, head_nbits, boundary));',
    'checksum +%= @intCast(find_bit.find_next_bit(&boundary_set, head_nbits, boundary));',
    'checksum +%= @intCast(find_bit.findFirstBit(&tail_set, tail_nbits));',
    'checksum +%= @intCast(find_bit._find_first_bit(&tail_set, tail_nbits));',
    'checksum +%= @intCast(find_bit.find_first_bit(&tail_set, tail_nbits));',
    'checksum +%= @intCast(find_bit.findFirstZeroBit(&tail_full, tail_nbits));',
    'checksum +%= @intCast(find_bit._find_first_zero_bit(&tail_full, tail_nbits));',
    'checksum +%= @intCast(find_bit.find_first_zero_bit(&tail_full, tail_nbits));',
    'checksum +%= @intCast(find_bit.findFirstAndBit(&tail_set, &tail_set, tail_nbits));',
    'checksum +%= @intCast(find_bit._find_first_and_bit(&tail_set, &tail_set, tail_nbits));',
    'checksum +%= @intCast(find_bit.find_first_and_bit(&tail_set, &tail_set, tail_nbits));',
    'checksum +%= @intCast(find_bit.findLastBit(&tail_set, tail_nbits));',
    'checksum +%= @intCast(find_bit._find_last_bit(&tail_set, tail_nbits));',
    'checksum +%= @intCast(find_bit.find_last_bit(&tail_set, tail_nbits));',
    'checksum +%= @intCast(find_bit.findNextBit(&empty, past_nbits, past_nbits));',
    'checksum +%= @intCast(find_bit.findNextBit(&empty, past_nbits, past_nbits + 4));',
    'checksum +%= @intCast(find_bit.findNextZeroBit(&empty, past_nbits, past_nbits));',
    'checksum +%= @intCast(find_bit.findNextZeroBit(&empty, past_nbits, past_nbits + 4));',
    'checksum +%= @intCast(find_bit.findNextAndBit(&empty, &empty, past_nbits, past_nbits));',
    'checksum +%= @intCast(find_bit.findNextAndBit(&empty, &empty, past_nbits, past_nbits + 4));',
    'checksum +%= @intCast(find_bit.find_next_bit(&empty, past_nbits, past_nbits));',
    'checksum +%= @intCast(find_bit.find_next_bit(&empty, past_nbits, past_nbits + 4));',
    'checksum +%= @intCast(find_bit.find_next_zero_bit(&empty, past_nbits, past_nbits));',
    'checksum +%= @intCast(find_bit.find_next_zero_bit(&empty, past_nbits, past_nbits + 4));',
    'checksum +%= @intCast(find_bit.find_next_and_bit(&empty, &empty, past_nbits, past_nbits));',
    'checksum +%= @intCast(find_bit.find_next_and_bit(&empty, &empty, past_nbits, past_nbits + 4));',
]
REQUIRED_STRING_SOURCE_MARKERS = [
    'fn stringBench() !struct { checksum: u64 } {',
    'const enabled = try string.strtobool(if (even) "on" else "0");',
    "var trim_buf = [_]u8{ ' ', '\t', 'h', 'i', ' ', '\n' };",
    'const trimmed = string.trimSpaces(&trim_buf);',
    'const parsed = string.memparse(if (even) "64K rest" else "-17 tail");',
    'const dirty = if (even)',
    "string.memchrInv(\"aaaaXaaa\", 'a')",
    "string.memchrInv(\"bbbb\", 'b');",
    'checksum +%= @as(u64, @intFromBool(enabled));',
    'checksum +%= @intCast(trimmed.len);',
    'checksum +%= @intCast(parsed.rest.len);',
    'checksum +%= @as(u64, @intFromBool(dirty != null));',
]
REQUIRED_RBTREE_SOURCE_MARKERS = [
    'rbtree.findAdd(&find_add_entries[3].node, &find_add_root, cmpNode)',
    'rbtree.find(&wanted, &duplicate_root, cmpKey)',
    'rbtree.findFirst(&wanted, &duplicate_root, cmpKey)',
    'rbtree.nextMatch(&wanted, cursor, cmpKey)',
    'rbtree.erase(&duplicate_mutation_entries[2].node, &duplicate_mutation_root);',
    'duplicate_checksum +%= entry.serial + 97;',
    'rbtree.replaceNode(&duplicate_mutation_entries[4].node, &replacement_duplicate.node, &duplicate_mutation_root);',
    'duplicate_checksum +%= entry.serial + 107;',
    'rbtree.addCached(&entry.node, &cached_root, less);',
    'const initial_leftmost_entry: *const RbEntry = @fieldParentPtr("node", rbtree.firstCached(&cached_root).?);',
    'cached_checksum +%= @intCast(initial_leftmost_entry.key);',
    'cached_checksum +%= @as(u64, @intFromBool(rbtree.eraseCached(&cached_entries[2].node, &cached_root) == null));',
    'const still_leftmost_entry: *const RbEntry = @fieldParentPtr("node", rbtree.firstCached(&cached_root).?);',
    'cached_checksum +%= @intCast(still_leftmost_entry.key);',
    'const promoted_leftmost = rbtree.eraseCached(&cached_entries[1].node, &cached_root) orelse unreachable;',
    'cached_checksum +%= @intCast(promoted_leftmost_entry.key);',
    'rbtree.replaceNodeCached(&cached_entries[0].node, &cached_replacement.node, &cached_root)',
    'const replacement_leftmost_entry: *const RbEntry = @fieldParentPtr("node", rbtree.firstCached(&cached_root).?);',
    'cached_checksum +%= @intCast(replacement_leftmost_entry.key);',
    'rbtree.addCached(&new_leftmost.node, &cached_root, less);',
    'cached_checksum +%= @intCast(new_leftmost_entry.key);',
    'rbtree.first(&cached_root.root) == rbtree.firstCached(&cached_root)',
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
    zig = shutil.which('zig')
    if zig:
        return zig
    raise SystemExit('zig not found; pass --zig or add zig to PATH')


def parse_output(stdout: str) -> tuple[dict[str, str], dict[str, int]]:
    parsed: dict[str, str] = {}
    counts: dict[str, int] = {}
    for raw_line in stdout.splitlines():
        line = raw_line.strip()
        if not line or '=' not in line:
            continue
        key, value = line.split('=', 1)
        parsed[key] = value
        counts[key] = counts.get(key, 0) + 1
    return parsed, counts


def load_expectations(path: Path) -> object:
    return load_expectations_text(path.read_text(encoding='utf-8'))


def load_expectations_text(text: str) -> object:
    return json.loads(text, object_pairs_hook=DuplicateTrackingDict)


def validate_expectations(expectations: object) -> tuple[str, object]:
    if not isinstance(expectations, dict):
        return ('expectations_type', type(expectations).__name__)
    if isinstance(expectations, DuplicateTrackingDict) and expectations.duplicate_keys:
        return ('expectations_duplicate_keys', expectations.duplicate_keys)
    if expectations.get('status') != 'pass':
        return ('expectations_status', expectations.get('status'))

    iterations = expectations.get('iterations')
    if not isinstance(iterations, dict):
        return ('expectations_iterations_type', type(iterations).__name__)
    if isinstance(iterations, DuplicateTrackingDict) and iterations.duplicate_keys:
        return ('expectations_duplicate_iteration_keys', iterations.duplicate_keys)

    actual_iteration_keys = set()
    for key, value in iterations.items():
        if not isinstance(key, str):
            return ('expectations_iteration_key_type', type(key).__name__)
        if not isinstance(value, int):
            return ('expectations_iteration_value_type', (key, type(value).__name__))
        actual_iteration_keys.add(key)
        expected_value = EXPECTED_ITERATIONS.get(key)
        if expected_value is None:
            return ('expectations_unexpected_iteration', key)
        if value != expected_value:
            return ('expectations_iteration_value', (key, expected_value, value))

    missing_iterations = sorted(set(EXPECTED_ITERATIONS) - actual_iteration_keys)
    if missing_iterations:
        return ('expectations_missing_iterations', missing_iterations)

    checksums = expectations.get('checksums')
    if not isinstance(checksums, list):
        return ('expectations_checksums_type', type(checksums).__name__)
    seen: set[str] = set()
    duplicates: list[str] = []
    actual_checksums: list[str] = []
    for item in checksums:
        if not isinstance(item, str):
            return ('expectations_checksum_type', type(item).__name__)
        actual_checksums.append(item)
        if item in seen and item not in duplicates:
            duplicates.append(item)
        seen.add(item)
    if duplicates:
        return ('expectations_duplicate_checksums', duplicates)

    actual_checksum_set = set(actual_checksums)
    missing_checksums = sorted(set(EXPECTED_CHECKSUMS) - actual_checksum_set)
    if missing_checksums:
        return ('expectations_missing_checksums', missing_checksums)
    unexpected_checksums = sorted(actual_checksum_set - set(EXPECTED_CHECKSUMS))
    if unexpected_checksums:
        return ('expectations_unexpected_checksums', unexpected_checksums)

    exact_checksums = expectations.get('exact_checksums')
    if not isinstance(exact_checksums, dict):
        return ('expectations_exact_checksums_type', type(exact_checksums).__name__)
    if isinstance(exact_checksums, DuplicateTrackingDict) and exact_checksums.duplicate_keys:
        return ('expectations_duplicate_exact_checksum_keys', exact_checksums.duplicate_keys)

    actual_exact_checksum_keys = set()
    for key, value in exact_checksums.items():
        if not isinstance(key, str):
            return ('expectations_exact_checksum_key_type', type(key).__name__)
        if not isinstance(value, int):
            return ('expectations_exact_checksum_value_type', (key, type(value).__name__))
        if value <= 0:
            return ('expectations_exact_checksum_nonpositive', (key, value))
        if key not in actual_checksum_set:
            return ('expectations_exact_checksum_not_listed', key)
        actual_exact_checksum_keys.add(key)

    missing_find_bit_exact_checksums = sorted(REQUIRED_FIND_BIT_EXACT_CHECKSUMS - actual_exact_checksum_keys)
    if missing_find_bit_exact_checksums:
        return ('expectations_missing_find_bit_exact_checksums', missing_find_bit_exact_checksums)
    missing_exact_checksums = sorted(REQUIRED_EXACT_CHECKSUMS - actual_exact_checksum_keys)
    if missing_exact_checksums:
        return ('expectations_missing_exact_checksums', missing_exact_checksums)
    unexpected_exact_checksums = sorted(actual_exact_checksum_keys - REQUIRED_EXACT_CHECKSUMS)
    if unexpected_exact_checksums:
        return ('expectations_unexpected_exact_checksums', unexpected_exact_checksums)
    return ('pass', expectations)


def validate_bench_source(source: str) -> tuple[str, object]:
    missing_bitmap = [marker for marker in REQUIRED_BITMAP_SOURCE_MARKERS if marker not in source]
    if missing_bitmap:
        return ('missing_bitmap_source_markers', missing_bitmap)
    missing_find_bit = [marker for marker in REQUIRED_FIND_BIT_SOURCE_MARKERS if marker not in source]
    if missing_find_bit:
        return ('missing_find_bit_source_markers', missing_find_bit)
    missing_string = [marker for marker in REQUIRED_STRING_SOURCE_MARKERS if marker not in source]
    if missing_string:
        return ('missing_string_source_markers', missing_string)
    missing_rbtree = [marker for marker in REQUIRED_RBTREE_SOURCE_MARKERS if marker not in source]
    if missing_rbtree:
        return ('missing_rbtree_source_markers', missing_rbtree)
    return ('pass', None)


def clone_expectations(expectations: dict[str, object]) -> dict[str, object]:
    iterations = expectations.get('iterations')
    checksums = expectations.get('checksums')
    exact_checksums = expectations.get('exact_checksums')
    assert isinstance(iterations, dict)
    assert isinstance(checksums, list)
    assert isinstance(exact_checksums, dict)
    return {
        'status': expectations['status'],
        'iterations': dict(iterations),
        'checksums': list(checksums),
        'exact_checksums': dict(exact_checksums),
    }


def load_full_expectations_for_self_test() -> dict[str, object]:
    expectations = load_expectations(EXPECTATIONS)
    kind, payload = validate_expectations(expectations)
    assert kind == 'pass', (kind, payload)
    assert isinstance(expectations, dict)
    return clone_expectations(expectations)


def validate_output(expectations: dict[str, object], stdout: str) -> tuple[str, object]:
    parsed, counts = parse_output(stdout)
    exact_checksums: dict[str, int] = expectations['exact_checksums']
    required_keys = {'PHASE1_BENCH', *expectations['iterations'].keys(), *expectations['checksums']}
    duplicate = sorted(key for key in required_keys if counts.get(key, 0) > 1)
    if duplicate:
        return ('duplicate', duplicate)
    unexpected = sorted(key for key in parsed if key.startswith('PHASE1_BENCH') and key not in required_keys)
    if unexpected:
        return ('unexpected', unexpected)
    actual_status = parsed.get('PHASE1_BENCH')
    if actual_status != expectations['status']:
        return ('status', (expectations['status'], actual_status))

    missing: list[str] = []
    for key, value in expectations['iterations'].items():
        actual = parsed.get(key)
        if actual is None:
            missing.append(key)
            continue
        try:
            actual_value = int(actual)
        except ValueError:
            return ('iteration_value_type', (key, actual))
        if actual_value != int(value):
            return ('iteration_mismatch', (key, value, actual))

    for key in expectations['checksums']:
        actual = parsed.get(key)
        if actual is None:
            missing.append(key)
            continue
        try:
            actual_value = int(actual)
        except ValueError:
            return ('checksum_value_type', (key, actual))
        if actual_value <= 0:
            return ('nonpositive_checksum', (key, actual))
        expected_exact_value = exact_checksums.get(key)
        if expected_exact_value is not None and actual_value != expected_exact_value:
            return ('exact_checksum_mismatch', (key, expected_exact_value, actual_value))

    missing_find_bit_exact_checksums = sorted(key for key in REQUIRED_FIND_BIT_EXACT_CHECKSUMS if key in missing)
    if missing_find_bit_exact_checksums:
        return ('missing_find_bit_exact_checksums', missing_find_bit_exact_checksums)
    missing_exact_checksums = sorted(key for key in exact_checksums if key in missing)
    if missing_exact_checksums:
        return ('missing_exact_checksums', missing_exact_checksums)
    if missing:
        return ('missing', missing)
    return ('pass', parsed)


def print_command_output(label: str, output: str | None) -> None:
    if not output:
        return
    print(f'{label}_START')
    text = output.rstrip('\n')
    if text:
        print(text)
    print(f'{label}_END')


def run_self_test() -> None:
    full_expectations = load_full_expectations_for_self_test()
    full_exact_checksums: dict[str, int] = full_expectations['exact_checksums']
    cases = 0
    ok_output = '\n'.join([
        'PHASE1_BENCH=pass',
        'PHASE1_BENCH_BITMAP_WEIGHT_ITERATIONS=20000',
        'PHASE1_BENCH_BITMAP_WINDOW_ITERATIONS=20000',
        'PHASE1_BENCH_FIND_NEXT_BIT_ITERATIONS=20000',
        'PHASE1_BENCH_FIND_BIT_EDGE_ITERATIONS=20000',
        'PHASE1_BENCH_STRING_ITERATIONS=40000',
        'PHASE1_BENCH_HWEIGHT_ITERATIONS=100000',
        'PHASE1_BENCH_LIST_SORT_ITERATIONS=1000',
        'PHASE1_BENCH_RBTREE_ITERATIONS=4000',
        f"PHASE1_BENCH_BITMAP_WEIGHT_CHECKSUM={full_exact_checksums['PHASE1_BENCH_BITMAP_WEIGHT_CHECKSUM']}",
        f"PHASE1_BENCH_BITMAP_WINDOW_CHECKSUM={full_exact_checksums['PHASE1_BENCH_BITMAP_WINDOW_CHECKSUM']}",
        f"PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM={full_exact_checksums['PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM']}",
        f"PHASE1_BENCH_FIND_BIT_EDGE_CHECKSUM={full_exact_checksums['PHASE1_BENCH_FIND_BIT_EDGE_CHECKSUM']}",
        f"PHASE1_BENCH_STRING_CHECKSUM={full_exact_checksums['PHASE1_BENCH_STRING_CHECKSUM']}",
        'PHASE1_BENCH_HWEIGHT_CHECKSUM=1600000',
        'PHASE1_BENCH_LIST_SORT_CHECKSUM=69300',
        f"PHASE1_BENCH_RBTREE_CHECKSUM={full_exact_checksums['PHASE1_BENCH_RBTREE_CHECKSUM']}",
        f"PHASE1_BENCH_RBTREE_POSTORDER_SAFE_CHECKSUM={full_exact_checksums['PHASE1_BENCH_RBTREE_POSTORDER_SAFE_CHECKSUM']}",
        f"PHASE1_BENCH_RBTREE_FIND_ADD_CHECKSUM={full_exact_checksums['PHASE1_BENCH_RBTREE_FIND_ADD_CHECKSUM']}",
        f"PHASE1_BENCH_RBTREE_DUPLICATE_CHECKSUM={full_exact_checksums['PHASE1_BENCH_RBTREE_DUPLICATE_CHECKSUM']}",
        f"PHASE1_BENCH_RBTREE_CACHED_CHECKSUM={full_exact_checksums['PHASE1_BENCH_RBTREE_CACHED_CHECKSUM']}",
    ])
    kind, _ = validate_output(full_expectations, ok_output)
    assert kind == 'pass'
    cases += 1

    kind, _ = validate_bench_source('\n'.join([
        *REQUIRED_BITMAP_SOURCE_MARKERS,
        *REQUIRED_FIND_BIT_SOURCE_MARKERS,
        *REQUIRED_STRING_SOURCE_MARKERS,
        *REQUIRED_RBTREE_SOURCE_MARKERS,
    ]))
    assert kind == 'pass'
    cases += 1

    kind, payload = validate_bench_source('\n'.join([
        *REQUIRED_BITMAP_SOURCE_MARKERS,
        *REQUIRED_RBTREE_SOURCE_MARKERS,
        *REQUIRED_STRING_SOURCE_MARKERS,
    ]))
    assert kind == 'missing_find_bit_source_markers'
    assert payload == REQUIRED_FIND_BIT_SOURCE_MARKERS
    cases += 1

    kind, payload = validate_bench_source('\n'.join([
        *REQUIRED_FIND_BIT_SOURCE_MARKERS,
        *REQUIRED_RBTREE_SOURCE_MARKERS,
        *REQUIRED_STRING_SOURCE_MARKERS,
    ]))
    assert kind == 'missing_bitmap_source_markers'
    assert payload == REQUIRED_BITMAP_SOURCE_MARKERS
    cases += 1

    kind, payload = validate_bench_source('\n'.join([
        *REQUIRED_BITMAP_SOURCE_MARKERS,
        *REQUIRED_FIND_BIT_SOURCE_MARKERS,
        *REQUIRED_RBTREE_SOURCE_MARKERS,
    ]))
    assert kind == 'missing_string_source_markers'
    assert payload == REQUIRED_STRING_SOURCE_MARKERS
    cases += 1

    kind, payload = validate_bench_source('\n'.join([
        *REQUIRED_BITMAP_SOURCE_MARKERS,
        *REQUIRED_FIND_BIT_SOURCE_MARKERS,
        *REQUIRED_STRING_SOURCE_MARKERS,
    ]))
    assert kind == 'missing_rbtree_source_markers'
    assert payload == REQUIRED_RBTREE_SOURCE_MARKERS
    cases += 1

    kind, payload = validate_bench_source('\n'.join([
        *REQUIRED_BITMAP_SOURCE_MARKERS,
        *REQUIRED_FIND_BIT_SOURCE_MARKERS,
        *REQUIRED_STRING_SOURCE_MARKERS,
        *[marker for marker in REQUIRED_RBTREE_SOURCE_MARKERS if marker != 'duplicate_checksum +%= entry.serial + 107;'],
    ]))
    assert kind == 'missing_rbtree_source_markers'
    assert payload == ['duplicate_checksum +%= entry.serial + 107;']
    cases += 1

    kind, payload = validate_bench_source('\n'.join([
        *REQUIRED_BITMAP_SOURCE_MARKERS,
        *REQUIRED_FIND_BIT_SOURCE_MARKERS,
        *REQUIRED_STRING_SOURCE_MARKERS,
        *[marker for marker in REQUIRED_RBTREE_SOURCE_MARKERS if marker != 'cached_checksum +%= @intCast(replacement_leftmost_entry.key);'],
    ]))
    assert kind == 'missing_rbtree_source_markers'
    assert payload == ['cached_checksum +%= @intCast(replacement_leftmost_entry.key);']
    cases += 1

    kind, payload = validate_output(full_expectations, ok_output + '\nPHASE1_BENCH_FAKE_CHECKSUM=1')
    assert kind == 'unexpected'
    assert payload == ['PHASE1_BENCH_FAKE_CHECKSUM']
    cases += 1

    mismatch_output = ok_output.replace(
        f"PHASE1_BENCH_RBTREE_CACHED_CHECKSUM={full_exact_checksums['PHASE1_BENCH_RBTREE_CACHED_CHECKSUM']}",
        f"PHASE1_BENCH_RBTREE_CACHED_CHECKSUM={full_exact_checksums['PHASE1_BENCH_RBTREE_CACHED_CHECKSUM'] + 1}",
    )
    kind, payload = validate_output(full_expectations, mismatch_output)
    assert kind == 'exact_checksum_mismatch'
    assert payload == (
        'PHASE1_BENCH_RBTREE_CACHED_CHECKSUM',
        full_exact_checksums['PHASE1_BENCH_RBTREE_CACHED_CHECKSUM'],
        full_exact_checksums['PHASE1_BENCH_RBTREE_CACHED_CHECKSUM'] + 1,
    )
    cases += 1

    missing_find_bit_exact_output = ok_output.replace(
        f"\nPHASE1_BENCH_FIND_BIT_EDGE_CHECKSUM={full_exact_checksums['PHASE1_BENCH_FIND_BIT_EDGE_CHECKSUM']}",
        '',
    )
    kind, payload = validate_output(full_expectations, missing_find_bit_exact_output)
    assert kind == 'missing_find_bit_exact_checksums'
    assert payload == ['PHASE1_BENCH_FIND_BIT_EDGE_CHECKSUM']
    cases += 1

    missing_nonexact_output = ok_output.replace('\nPHASE1_BENCH_HWEIGHT_CHECKSUM=1600000', '')
    kind, payload = validate_output(full_expectations, missing_nonexact_output)
    assert kind == 'missing'
    assert payload == ['PHASE1_BENCH_HWEIGHT_CHECKSUM']
    cases += 1

    kind, _ = validate_expectations(full_expectations)
    assert kind == 'pass'
    cases += 1

    missing_checksum_expectations = clone_expectations(full_expectations)
    missing_checksum_expectations['checksums'].remove('PHASE1_BENCH_RBTREE_CACHED_CHECKSUM')
    kind, payload = validate_expectations(missing_checksum_expectations)
    assert kind == 'expectations_missing_checksums'
    assert payload == ['PHASE1_BENCH_RBTREE_CACHED_CHECKSUM']
    cases += 1

    missing_find_bit_exact_expectations = clone_expectations(full_expectations)
    del missing_find_bit_exact_expectations['exact_checksums']['PHASE1_BENCH_FIND_BIT_EDGE_CHECKSUM']
    kind, payload = validate_expectations(missing_find_bit_exact_expectations)
    assert kind == 'expectations_missing_find_bit_exact_checksums'
    assert payload == ['PHASE1_BENCH_FIND_BIT_EDGE_CHECKSUM']
    cases += 1

    missing_exact_expectations = clone_expectations(full_expectations)
    del missing_exact_expectations['exact_checksums']['PHASE1_BENCH_RBTREE_CACHED_CHECKSUM']
    kind, payload = validate_expectations(missing_exact_expectations)
    assert kind == 'expectations_missing_exact_checksums'
    assert payload == ['PHASE1_BENCH_RBTREE_CACHED_CHECKSUM']
    cases += 1

    unexpected_exact_expectations = clone_expectations(full_expectations)
    unexpected_exact_expectations['exact_checksums']['PHASE1_BENCH_HWEIGHT_CHECKSUM'] = 1600000
    kind, payload = validate_expectations(unexpected_exact_expectations)
    assert kind == 'expectations_unexpected_exact_checksums'
    assert payload == ['PHASE1_BENCH_HWEIGHT_CHECKSUM']
    cases += 1

    duplicate_checksum_expectations = clone_expectations(full_expectations)
    duplicate_checksum_expectations['checksums'].append('PHASE1_BENCH_BITMAP_WEIGHT_CHECKSUM')
    kind, payload = validate_expectations(duplicate_checksum_expectations)
    assert kind == 'expectations_duplicate_checksums'
    assert payload == ['PHASE1_BENCH_BITMAP_WEIGHT_CHECKSUM']
    cases += 1

    duplicate_root_expectations = load_expectations_text('{"status":"pass","status":"fail","iterations":{"PHASE1_BENCH_BITMAP_WEIGHT_ITERATIONS":20000,"PHASE1_BENCH_BITMAP_WINDOW_ITERATIONS":20000,"PHASE1_BENCH_FIND_NEXT_BIT_ITERATIONS":20000,"PHASE1_BENCH_FIND_BIT_EDGE_ITERATIONS":20000,"PHASE1_BENCH_STRING_ITERATIONS":40000,"PHASE1_BENCH_HWEIGHT_ITERATIONS":100000,"PHASE1_BENCH_LIST_SORT_ITERATIONS":1000,"PHASE1_BENCH_RBTREE_ITERATIONS":4000},"checksums":["PHASE1_BENCH_BITMAP_WEIGHT_CHECKSUM"],"exact_checksums":{}}')
    kind, payload = validate_expectations(duplicate_root_expectations)
    assert kind == 'expectations_duplicate_keys'
    assert payload == ['status']
    cases += 1

    print('PHASE1_BENCH_CHECK_SELF_TEST=pass')
    print(f'PHASE1_BENCH_CHECK_SELF_TEST_CASE_COUNT={cases}')


def main() -> int:
    parser = argparse.ArgumentParser(description='Run and validate the bounded Phase 1 benchmark smoke output.')
    parser.add_argument('--zig', help='Path to Zig executable')
    parser.add_argument('--self-test', action='store_true', help='Run checker self-test cases without invoking Zig.')
    args = parser.parse_args()
    if args.self_test:
        run_self_test()
        return 0

    try:
        expectations = load_expectations(EXPECTATIONS)
    except json.JSONDecodeError as exc:
        print('PHASE1_BENCH_CHECK=fail')
        print(f'EXPECTATIONS_JSON_ERROR={exc.msg}')
        print(f'EXPECTATIONS_JSON_LINE={exc.lineno}')
        print(f'EXPECTATIONS_JSON_COLUMN={exc.colno}')
        return 1

    kind, payload = validate_expectations(expectations)
    if kind == 'expectations_type':
        print('PHASE1_BENCH_CHECK=fail')
        print(f'EXPECTATIONS_TYPE={payload}')
        return 1
    if kind == 'expectations_status':
        print('PHASE1_BENCH_CHECK=fail')
        print(f'EXPECTATIONS_STATUS={payload}')
        return 1
    if kind == 'expectations_duplicate_keys':
        print('PHASE1_BENCH_CHECK=fail')
        print('DUPLICATE_EXPECTATION_KEYS_START')
        for key in payload:
            print(key)
        print('DUPLICATE_EXPECTATION_KEYS_END')
        return 1
    if kind == 'expectations_iterations_type':
        print('PHASE1_BENCH_CHECK=fail')
        print(f'EXPECTATIONS_ITERATIONS_TYPE={payload}')
        return 1
    if kind == 'expectations_duplicate_iteration_keys':
        print('PHASE1_BENCH_CHECK=fail')
        print('DUPLICATE_EXPECTATION_ITERATION_KEYS_START')
        for key in payload:
            print(key)
        print('DUPLICATE_EXPECTATION_ITERATION_KEYS_END')
        return 1
    if kind == 'expectations_iteration_key_type':
        print('PHASE1_BENCH_CHECK=fail')
        print(f'EXPECTATIONS_ITERATION_KEY_TYPE={payload}')
        return 1
    if kind == 'expectations_iteration_value_type':
        key, value_type = payload
        print('PHASE1_BENCH_CHECK=fail')
        print(f'EXPECTATIONS_ITERATION_VALUE_KEY={key}')
        print(f'EXPECTATIONS_ITERATION_VALUE_TYPE={value_type}')
        return 1
    if kind == 'expectations_unexpected_iteration':
        print('PHASE1_BENCH_CHECK=fail')
        print(f'UNEXPECTED_EXPECTATION_ITERATION={payload}')
        return 1
    if kind == 'expectations_iteration_value':
        key, expected, actual = payload
        print('PHASE1_BENCH_CHECK=fail')
        print(f'EXPECTATIONS_ITERATION_VALUE_MISMATCH={key}')
        print(f'EXPECTED={expected}')
        print(f'ACTUAL={actual}')
        return 1
    if kind == 'expectations_missing_iterations':
        print('PHASE1_BENCH_CHECK=fail')
        print('MISSING_EXPECTATION_ITERATIONS_START')
        for key in payload:
            print(key)
        print('MISSING_EXPECTATION_ITERATIONS_END')
        return 1
    if kind == 'expectations_checksums_type':
        print('PHASE1_BENCH_CHECK=fail')
        print(f'EXPECTATIONS_CHECKSUMS_TYPE={payload}')
        return 1
    if kind == 'expectations_checksum_type':
        print('PHASE1_BENCH_CHECK=fail')
        print(f'EXPECTATIONS_CHECKSUM_TYPE={payload}')
        return 1
    if kind == 'expectations_duplicate_checksums':
        print('PHASE1_BENCH_CHECK=fail')
        print('DUPLICATE_EXPECTATION_CHECKSUMS_START')
        for key in payload:
            print(key)
        print('DUPLICATE_EXPECTATION_CHECKSUMS_END')
        return 1
    if kind == 'expectations_missing_checksums':
        print('PHASE1_BENCH_CHECK=fail')
        print('MISSING_EXPECTATION_CHECKSUMS_START')
        for key in payload:
            print(key)
        print('MISSING_EXPECTATION_CHECKSUMS_END')
        return 1
    if kind == 'expectations_unexpected_checksums':
        print('PHASE1_BENCH_CHECK=fail')
        print('UNEXPECTED_EXPECTATION_CHECKSUMS_START')
        for key in payload:
            print(key)
        print('UNEXPECTED_EXPECTATION_CHECKSUMS_END')
        return 1
    if kind == 'expectations_exact_checksums_type':
        print('PHASE1_BENCH_CHECK=fail')
        print(f'EXPECTATIONS_EXACT_CHECKSUMS_TYPE={payload}')
        return 1
    if kind == 'expectations_duplicate_exact_checksum_keys':
        print('PHASE1_BENCH_CHECK=fail')
        print('DUPLICATE_EXPECTATION_EXACT_CHECKSUM_KEYS_START')
        for key in payload:
            print(key)
        print('DUPLICATE_EXPECTATION_EXACT_CHECKSUM_KEYS_END')
        return 1
    if kind == 'expectations_exact_checksum_key_type':
        print('PHASE1_BENCH_CHECK=fail')
        print(f'EXPECTATIONS_EXACT_CHECKSUM_KEY_TYPE={payload}')
        return 1
    if kind == 'expectations_exact_checksum_value_type':
        key, value_type = payload
        print('PHASE1_BENCH_CHECK=fail')
        print(f'EXPECTATIONS_EXACT_CHECKSUM_VALUE_KEY={key}')
        print(f'EXPECTATIONS_EXACT_CHECKSUM_VALUE_TYPE={value_type}')
        return 1
    if kind == 'expectations_exact_checksum_nonpositive':
        key, value = payload
        print('PHASE1_BENCH_CHECK=fail')
        print(f'EXPECTATIONS_EXACT_CHECKSUM_NONPOSITIVE_KEY={key}')
        print(f'ACTUAL={value}')
        return 1
    if kind == 'expectations_exact_checksum_not_listed':
        print('PHASE1_BENCH_CHECK=fail')
        print(f'EXPECTATIONS_EXACT_CHECKSUM_NOT_LISTED={payload}')
        return 1
    if kind == 'expectations_missing_find_bit_exact_checksums':
        print('PHASE1_BENCH_CHECK=fail')
        print('MISSING_EXPECTATION_FIND_BIT_EXACT_CHECKSUMS_START')
        for key in payload:
            print(key)
        print('MISSING_EXPECTATION_FIND_BIT_EXACT_CHECKSUMS_END')
        return 1
    if kind == 'expectations_missing_exact_checksums':
        print('PHASE1_BENCH_CHECK=fail')
        print('MISSING_EXPECTATION_EXACT_CHECKSUMS_START')
        for key in payload:
            print(key)
        print('MISSING_EXPECTATION_EXACT_CHECKSUMS_END')
        return 1
    if kind == 'expectations_unexpected_exact_checksums':
        print('PHASE1_BENCH_CHECK=fail')
        print('UNEXPECTED_EXPECTATION_EXACT_CHECKSUMS_START')
        for key in payload:
            print(key)
        print('UNEXPECTED_EXPECTATION_EXACT_CHECKSUMS_END')
        return 1

    try:
        bench_source = PHASE1_BENCH.read_text(encoding='utf-8')
    except FileNotFoundError:
        print('PHASE1_BENCH_CHECK=fail')
        print(f'PHASE1_BENCH_SOURCE_MISSING={PHASE1_BENCH}')
        return 1

    kind, payload = validate_bench_source(bench_source)
    if kind in {
        'missing_bitmap_source_markers',
        'missing_find_bit_source_markers',
        'missing_string_source_markers',
        'missing_rbtree_source_markers',
    }:
        if kind == 'missing_bitmap_source_markers':
            group = 'bitmap'
        elif kind == 'missing_find_bit_source_markers':
            group = 'find_bit'
        elif kind == 'missing_string_source_markers':
            group = 'string'
        else:
            group = 'rbtree'
        print('PHASE1_BENCH_CHECK=fail')
        print(f'MISSING_PHASE1_BENCH_SOURCE_MARKER_GROUP={group}')
        print('MISSING_PHASE1_BENCH_SOURCE_MARKERS_START')
        for marker in payload:
            print(marker)
        print('MISSING_PHASE1_BENCH_SOURCE_MARKERS_END')
        return 1

    zig = find_zig(args.zig)
    result = subprocess.run([
        zig, 'build', 'bench', '--build-file', 'zigux/tests/build.zig', '-Doptimize=ReleaseSafe'
    ], cwd=str(ROOT), capture_output=True, text=True)
    if result.returncode != 0:
        print('PHASE1_BENCH_CHECK=fail')
        print(f'BENCH_COMMAND_EXIT={result.returncode}')
        print_command_output('PHASE1_BENCH_STDOUT', result.stdout)
        print_command_output('PHASE1_BENCH_STDERR', result.stderr)
        return 1

    kind, payload = validate_output(expectations, result.stdout)
    if kind == 'duplicate':
        print('PHASE1_BENCH_CHECK=fail')
        print('DUPLICATE_PHASE1_BENCH_KEYS_START')
        for key in payload:
            print(key)
        print('DUPLICATE_PHASE1_BENCH_KEYS_END')
        return 1
    if kind == 'unexpected':
        print('PHASE1_BENCH_CHECK=fail')
        print('UNEXPECTED_PHASE1_BENCH_KEYS_START')
        for key in payload:
            print(key)
        print('UNEXPECTED_PHASE1_BENCH_KEYS_END')
        return 1
    if kind == 'status':
        expected, actual = payload
        print('PHASE1_BENCH_CHECK=fail')
        print(f'EXPECTED_STATUS={expected}')
        print(f'ACTUAL_STATUS={actual}')
        return 1
    if kind == 'iteration_mismatch':
        key, expected, actual = payload
        print('PHASE1_BENCH_CHECK=fail')
        print(f'ITERATION_MISMATCH={key}')
        print(f'EXPECTED={expected}')
        print(f'ACTUAL={actual}')
        return 1
    if kind == 'iteration_value_type':
        key, actual = payload
        print('PHASE1_BENCH_CHECK=fail')
        print(f'ITERATION_VALUE_TYPE={key}')
        print(f'ACTUAL={actual}')
        return 1
    if kind == 'nonpositive_checksum':
        key, actual = payload
        print('PHASE1_BENCH_CHECK=fail')
        print(f'NONPOSITIVE_CHECKSUM={key}')
        print(f'ACTUAL={actual}')
        return 1
    if kind == 'checksum_value_type':
        key, actual = payload
        print('PHASE1_BENCH_CHECK=fail')
        print(f'CHECKSUM_VALUE_TYPE={key}')
        print(f'ACTUAL={actual}')
        return 1
    if kind == 'exact_checksum_mismatch':
        key, expected, actual = payload
        print('PHASE1_BENCH_CHECK=fail')
        print(f'EXACT_CHECKSUM_MISMATCH={key}')
        print(f'EXPECTED={expected}')
        print(f'ACTUAL={actual}')
        return 1
    if kind == 'missing_find_bit_exact_checksums':
        print('PHASE1_BENCH_CHECK=fail')
        print('MISSING_PHASE1_BENCH_FIND_BIT_EXACT_CHECKSUMS_START')
        for key in payload:
            print(key)
        print('MISSING_PHASE1_BENCH_FIND_BIT_EXACT_CHECKSUMS_END')
        return 1
    if kind == 'missing_exact_checksums':
        print('PHASE1_BENCH_CHECK=fail')
        print('MISSING_PHASE1_BENCH_EXACT_CHECKSUMS_START')
        for key in payload:
            print(key)
        print('MISSING_PHASE1_BENCH_EXACT_CHECKSUMS_END')
        return 1
    if kind == 'missing':
        print('PHASE1_BENCH_CHECK=fail')
        print('MISSING_PHASE1_BENCH_KEYS_START')
        for key in payload:
            print(key)
        print('MISSING_PHASE1_BENCH_KEYS_END')
        return 1

    print('PHASE1_BENCH_CHECK=pass')
    print(f'PHASE1_BENCH_EXPECTATIONS={EXPECTATIONS}')
    print(f'PHASE1_BENCH_SOURCE={PHASE1_BENCH}')
    print(f'PHASE1_BENCH_ZIG={zig}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())