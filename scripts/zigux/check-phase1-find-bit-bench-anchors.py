#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import tempfile


HERE = Path(__file__).resolve()
ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent
FIND_BIT = ROOT / "tools" / "lib" / "find_bit.zig"

REQUIRED_TEST_MARKERS = {
    "andnot_gap_test": 'test "find first and next set bits across words, with andnot gaps explicit" {',
    "same_word_start_mask_test": 'test "single-word next scans honor start masks" {',
    "boundary_head_test": 'test "head-word boundary scans keep the last in-range bit reachable from an inclusive start" {',
    "boundary_tail_test": 'test "tail-word boundary scans keep the last in-range bit reachable from an inclusive start" {',
    "single_word_tail_test": 'test "single-word tail windows keep the last in-range next matches reachable from an inclusive start" {',
    "single_word_partial_window_test": 'test "single-word next scans clamp partial windows before returning nbits" {',
    "word_boundary_test": 'test "word-boundary next scans start fresh on the next word" {',
    "zero_sized_scan_test": 'test "zero-sized scans ignore populated backing words" {',
    "past_end_no_read_test": 'test "next scans past nbits return without reading bitmap words" {',
    "tail_mask_shared_test": 'test "tail mask ignores shared bits beyond nbits" {',
    "tail_word_set_skip_test": 'test "tail-word next set scans skip earlier in-range matches before clamping" {',
    "tail_word_zero_shared_skip_test": 'test "tail-word next zero and shared scans skip earlier in-range matches before clamping" {',
    "clump8_tail_reach_test": 'test "clump8 scans keep tail bytes reachable from partial final words" {',
    "clump8_tail_mask_test": 'test "clump8 scans mask tail bits beyond nbits" {',
    "clump8_untouched_test": 'test "clump8 zero-bit and past-end windows leave the caller byte untouched" {',
    "clump8_no_read_test": 'test "clump8 past-end scans return without reading bitmap words" {',
    "clump8_skip_forward_test": 'test "clump8 scans skip earlier aligned bytes once the offset moves forward" {',
    "clump8_word_boundary_test": 'test "clump8 keeps the last aligned byte of a word isolated from the next word" {',
    "get_value8_last_aligned_test": 'test "getValue8 reads the last aligned byte of a word without folding in the next word" {',
    "underscore_andnot_alias_test": 'test "low-level underscore aliases mirror the primary find helpers, including andnot" {',
    "linux_andnot_alias_test": 'test "Linux-style aliases mirror the primary find helpers, including andnot" {',
    "last_bit_exact_word_boundary_test": 'test "find last bit ignores storage beyond an exact word boundary" {',
    "last_bit_tail_test": 'test "find last bit clamps tail words to nbits" {',
    "last_bit_empty_test": 'test "find last bit returns nbits when no set bits remain" {',
}

REQUIRED_SOURCE_COUNT_MARKERS = {
    "find_next_boundary": ("findNextBit(&set_map, nbits, boundary)", 3),
    "find_next_and_boundary": ("findNextAndBit(&and_lhs, &and_rhs, nbits, boundary)", 1),
    "find_next_andnot_boundary": ("findNextAndNotBit(&andnot_lhs, &andnot_rhs, nbits, boundary)", 2),
    "find_next_or_boundary": ("findNextOrBit(&or_lhs, &or_rhs, nbits, boundary)", 2),
    "find_next_zero_boundary": ("findNextZeroBit(&zero_map, nbits, boundary)", 1),
    "find_last_nbits_bitmap": ('try std.testing.expectEqual(@as(usize, nbits), findLastBit(&bitmap, nbits));', 2),
    "find_first_clump8_tail_word": ('try std.testing.expectEqual(@as(usize, bits_per_long), findFirstClump8(&clump, &bitmap, nbits));', 2),
    "find_first_clump8_tail_value": ('try std.testing.expectEqual(@as(u8, 0b0000_1000), clump);', 2),
}

REQUIRED_SOURCE_EXACT_MARKERS = {
    "find_first_andnot_low_level_alias": "try std.testing.expectEqual(findFirstAndNotBit(&andnot_lhs, &andnot_rhs, nbits), _find_first_andnot_bit(&andnot_lhs, &andnot_rhs, nbits));",
    "find_first_andnot_gap": "findFirstAndNotBit(&andnot_lhs, &andnot_rhs, bits_per_long * 3)",
    "find_same_word_set_first": "try std.testing.expectEqual(@as(usize, 7), findNextBit(&set_bits, nbits, 3));",
    "find_same_word_set_second": "try std.testing.expectEqual(@as(usize, 11), findNextBit(&set_bits, nbits, 8));",
    "find_same_word_zero_first": "try std.testing.expectEqual(@as(usize, 4), findNextZeroBit(&zero_bits, nbits, 1));",
    "find_same_word_zero_second": "try std.testing.expectEqual(@as(usize, 9), findNextZeroBit(&zero_bits, nbits, 5));",
    "find_same_word_and_first": "try std.testing.expectEqual(@as(usize, 9), findNextAndBit(&and_lhs, &and_rhs, nbits, 2));",
    "find_same_word_and_second": "try std.testing.expectEqual(@as(usize, 12), findNextAndBit(&and_lhs, &and_rhs, nbits, 10));",
    "find_last_exact_word_boundary_first": "try std.testing.expectEqual(@as(usize, boundary), findLastBit(&bitmap, nbits));",
    "find_last_exact_word_boundary_clear": "bitmap[0] = 0;",
    "find_last_tail_single_word": "try std.testing.expectEqual(@as(usize, 4), findLastBit(&single_word, single_word_nbits));",
    "find_last_zero_sized": "findLastBit(&populated, 0)",
    "find_last_empty_zero": "findLastBit(&empty, 0)",
    "find_next_past_end": "findNextBit(&empty, 7, 11)",
    "find_next_zero_past_end": "findNextZeroBit(&empty, 7, 11)",
    "find_next_and_past_end": "findNextAndBit(&empty, &empty, 7, 11)",
    "find_next_or_past_end": "findNextOrBit(&empty, &empty, 7, 11)",
    "find_next_andnot_past_end": "findNextAndNotBit(&empty, &empty, 7, 11)",
    "find_next_or_single_word_clamp": "findNextOrBit(&or_lhs, &or_rhs, nbits, 13)",
    "find_next_and_tail_mask": "findNextAndBit(&lhs, &rhs, nbits, bits_per_long + 4)",
    "find_next_tail_skip": "try std.testing.expectEqual(@as(usize, bits_per_long + 4), findNextBit(&tail_map, nbits, bits_per_long + 2));",
    "find_next_tail_skip_stop": "try std.testing.expectEqual(@as(usize, nbits), findNextBit(&tail_map, nbits, bits_per_long + 5));",
    "find_next_andnot_single_word_window": "try std.testing.expectEqual(@as(usize, 8), findNextAndNotBit(&andnot_lhs, &andnot_rhs, nbits, 3));",
    "find_next_andnot_single_word_stop": "try std.testing.expectEqual(@as(usize, nbits), findNextAndNotBit(&andnot_lhs, &andnot_rhs, nbits, 9));",
    "find_next_andnot_word_boundary_follow": "try std.testing.expectEqual(boundary + 5, findNextAndNotBit(&andnot_lhs, &andnot_rhs, nbits, boundary + 1));",
    "find_next_andnot_single_word_tail_stop": "try std.testing.expectEqual(@as(usize, nbits), findNextAndNotBit(&andnot_lhs, &andnot_rhs, nbits, boundary + 1));",
    "find_next_andnot_tail_skip": "try std.testing.expectEqual(@as(usize, bits_per_long + 4), findNextAndNotBit(&tail_andnot_lhs, &tail_andnot_rhs, nbits, bits_per_long + 2));",
    "find_next_andnot_tail_skip_stop": "try std.testing.expectEqual(@as(usize, nbits), findNextAndNotBit(&tail_andnot_lhs, &tail_andnot_rhs, nbits, bits_per_long + 5));",
    "find_next_zero_tail_skip": "try std.testing.expectEqual(@as(usize, bits_per_long + 4), findNextZeroBit(&tail_zero_map, nbits, bits_per_long + 2));",
    "find_next_zero_tail_skip_stop": "try std.testing.expectEqual(@as(usize, nbits), findNextZeroBit(&tail_zero_map, nbits, bits_per_long + 5));",
    "find_next_and_tail_skip": "try std.testing.expectEqual(@as(usize, bits_per_long + 4), findNextAndBit(&tail_and_lhs, &tail_and_rhs, nbits, bits_per_long + 2));",
    "find_next_and_tail_skip_stop": "try std.testing.expectEqual(@as(usize, nbits), findNextAndBit(&tail_and_lhs, &tail_and_rhs, nbits, bits_per_long + 5));",
    "find_next_or_tail_skip": "try std.testing.expectEqual(@as(usize, bits_per_long + 4), findNextOrBit(&tail_or_lhs, &tail_or_rhs, nbits, bits_per_long + 2));",
    "find_next_or_tail_skip_stop": "try std.testing.expectEqual(@as(usize, nbits), findNextOrBit(&tail_or_lhs, &tail_or_rhs, nbits, bits_per_long + 5));",
    "find_first_clump8_zero_sized": "findFirstClump8(&clump, &populated, 0)",
    "find_next_clump8_untouched": "findNextClump8(&clump, &populated, 8, 12)",
    "find_clump8_past_end": "findNextClump8(&clump, &empty, 8, 8)",
    "find_clump8_linux_alias_past_end": "find_next_clump8(&clump, &empty, 8, 12)",
    "find_clump8_low_level_alias_past_end": "_find_next_clump8(&clump, &empty, 8, 20)",
    "find_clump8_skip_first": "try std.testing.expectEqual(@as(usize, 8), findNextClump8(&clump, &bitmap, nbits, 0));",
    "find_clump8_skip_second": "try std.testing.expectEqual(@as(usize, 24), findNextClump8(&clump, &bitmap, nbits, 16));",
    "find_clump8_skip_same_byte": "try std.testing.expectEqual(@as(usize, 24), findNextClump8(&clump, &bitmap, nbits, 25));",
    "find_clump8_skip_stop": "try std.testing.expectEqual(@as(usize, nbits), findNextClump8(&clump, &bitmap, nbits, 30));",
    "find_clump8_last_word_byte": "try std.testing.expectEqual(@as(usize, last_aligned_byte), findFirstClump8(&clump, &bitmap, nbits));",
    "find_clump8_next_word_byte": "try std.testing.expectEqual(@as(usize, bits_per_long), findNextClump8(&clump, &bitmap, nbits, bits_per_long));",
    "find_clump8_last_word_value": "try std.testing.expectEqual(@as(u8, 0xa5), clump);",
    "find_clump8_next_word_value": "try std.testing.expectEqual(@as(u8, 0x11), clump);",
    "find_get_value8_last_aligned": "try std.testing.expectEqual(@as(u8, 0xa5), getValue8(&bitmap, last_aligned_byte));",
    "find_get_value8_next_word": "try std.testing.expectEqual(@as(u8, 0x11), getValue8(&bitmap, bits_per_long));",
    "find_next_andnot_low_level_alias": "try std.testing.expectEqual(findNextAndNotBit(&andnot_lhs, &andnot_rhs, nbits, bits_per_long), _find_next_andnot_bit(&andnot_lhs, &andnot_rhs, nbits, bits_per_long));",
    "find_first_andnot_linux_alias": "try std.testing.expectEqual(findFirstAndNotBit(&andnot_lhs, &andnot_rhs, nbits), find_first_andnot_bit(&andnot_lhs, &andnot_rhs, nbits));",
    "find_next_andnot_linux_alias": "try std.testing.expectEqual(findNextAndNotBit(&andnot_lhs, &andnot_rhs, nbits, bits_per_long), find_next_andnot_bit(&andnot_lhs, &andnot_rhs, nbits, bits_per_long));",
}


def collect_marker_count_failures(
    text: str,
    markers: dict[str, str],
) -> list[str]:
    failures: list[str] = []
    for label, marker in markers.items():
        count = text.count(marker)
        if count != 1:
            failures.append(f"{label}:expected=1:actual={count}")
    return failures


def collect_expected_count_failures(
    text: str,
    markers: dict[str, tuple[str, int]],
) -> list[str]:
    failures: list[str] = []
    for label, (marker, expected_count) in markers.items():
        count = text.count(marker)
        if count != expected_count:
            failures.append(f"{label}:expected={expected_count}:actual={count}")
    return failures


def validate_find_bit_source(text: str) -> tuple[str, object]:
    test_failures = collect_marker_count_failures(text, REQUIRED_TEST_MARKERS)
    if test_failures:
        return ("invalid_test_marker_counts", test_failures)

    source_count_failures = collect_expected_count_failures(text, REQUIRED_SOURCE_COUNT_MARKERS)
    if source_count_failures:
        return ("invalid_source_count_markers", source_count_failures)

    source_exact_failures = collect_marker_count_failures(text, REQUIRED_SOURCE_EXACT_MARKERS)
    if source_exact_failures:
        return ("invalid_source_marker_counts", source_exact_failures)

    return ("pass", None)


def load_find_bit_source(path: Path) -> tuple[str, object]:
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ("missing_file", path)
    return validate_find_bit_source(text)


def marker_for_label(label: str) -> str:
    if label in REQUIRED_TEST_MARKERS:
        return REQUIRED_TEST_MARKERS[label]
    if label in REQUIRED_SOURCE_COUNT_MARKERS:
        return REQUIRED_SOURCE_COUNT_MARKERS[label][0]
    marker = REQUIRED_SOURCE_EXACT_MARKERS.get(label)
    assert marker is not None
    return marker


def build_sample_source(
    omit_label: str | None = None,
    duplicate_label: str | None = None,
) -> str:
    lines = [
        'test "find first and next set bits across words, with andnot gaps explicit" {',
        "    _ = findFirstAndNotBit(&andnot_lhs, &andnot_rhs, bits_per_long * 3);",
        "}",
        'test "single-word next scans honor start masks" {',
        "    try std.testing.expectEqual(@as(usize, 7), findNextBit(&set_bits, nbits, 3));",
        "    try std.testing.expectEqual(@as(usize, 11), findNextBit(&set_bits, nbits, 8));",
        "    try std.testing.expectEqual(@as(usize, 4), findNextZeroBit(&zero_bits, nbits, 1));",
        "    try std.testing.expectEqual(@as(usize, 9), findNextZeroBit(&zero_bits, nbits, 5));",
        "    try std.testing.expectEqual(@as(usize, 9), findNextAndBit(&and_lhs, &and_rhs, nbits, 2));",
        "    try std.testing.expectEqual(@as(usize, 12), findNextAndBit(&and_lhs, &and_rhs, nbits, 10));",
        "}",
        'test "head-word boundary scans keep the last in-range bit reachable from an inclusive start" {',
        "    _ = findNextBit(&set_map, nbits, boundary);",
        "    _ = findNextAndBit(&and_lhs, &and_rhs, nbits, boundary);",
        "    _ = findNextAndNotBit(&andnot_lhs, &andnot_rhs, nbits, boundary);",
        "    _ = findNextOrBit(&or_lhs, &or_rhs, nbits, boundary);",
        "    _ = findNextZeroBit(&zero_map, nbits, boundary);",
        "}",
        'test "tail-word boundary scans keep the last in-range bit reachable from an inclusive start" {',
        "    _ = findNextBit(&set_map, nbits, boundary);",
        "    _ = findNextAndNotBit(&andnot_lhs, &andnot_rhs, nbits, boundary);",
        "}",
        'test "single-word tail windows keep the last in-range next matches reachable from an inclusive start" {',
        "    _ = findNextBit(&set_map, nbits, boundary);",
        "    try std.testing.expectEqual(@as(usize, nbits), findNextAndNotBit(&andnot_lhs, &andnot_rhs, nbits, boundary + 1));",
        "}",
        'test "single-word next scans clamp partial windows before returning nbits" {',
        "    _ = findNextOrBit(&or_lhs, &or_rhs, nbits, 13);",
        "    try std.testing.expectEqual(@as(usize, 8), findNextAndNotBit(&andnot_lhs, &andnot_rhs, nbits, 3));",
        "    try std.testing.expectEqual(@as(usize, nbits), findNextAndNotBit(&andnot_lhs, &andnot_rhs, nbits, 9));",
        "}",
        'test "word-boundary next scans start fresh on the next word" {',
        "    _ = findNextOrBit(&or_lhs, &or_rhs, nbits, boundary);",
        "    try std.testing.expectEqual(boundary + 5, findNextAndNotBit(&andnot_lhs, &andnot_rhs, nbits, boundary + 1));",
        "}",
        'test "zero-sized scans ignore populated backing words" {',
        "    _ = findLastBit(&populated, 0);",
        "}",
        'test "next scans past nbits return without reading bitmap words" {',
        "    _ = findNextBit(&empty, 7, 11);",
        "    _ = findNextZeroBit(&empty, 7, 11);",
        "    _ = findNextAndBit(&empty, &empty, 7, 11);",
        "    _ = findNextOrBit(&empty, &empty, 7, 11);",
        "    _ = findNextAndNotBit(&empty, &empty, 7, 11);",
        "}",
        'test "tail mask ignores shared bits beyond nbits" {',
        "    _ = findNextAndBit(&lhs, &rhs, nbits, bits_per_long + 4);",
        "}",
        'test "tail-word next zero and shared scans skip earlier in-range matches before clamping" {',
        "    try std.testing.expectEqual(@as(usize, bits_per_long + 4), findNextZeroBit(&tail_zero_map, nbits, bits_per_long + 2));",
        "    try std.testing.expectEqual(@as(usize, nbits), findNextZeroBit(&tail_zero_map, nbits, bits_per_long + 5));",
        "    try std.testing.expectEqual(@as(usize, bits_per_long + 4), findNextAndBit(&tail_and_lhs, &tail_and_rhs, nbits, bits_per_long + 2));",
        "    try std.testing.expectEqual(@as(usize, nbits), findNextAndBit(&tail_and_lhs, &tail_and_rhs, nbits, bits_per_long + 5));",
        "    try std.testing.expectEqual(@as(usize, bits_per_long + 4), findNextOrBit(&tail_or_lhs, &tail_or_rhs, nbits, bits_per_long + 2));",
        "    try std.testing.expectEqual(@as(usize, nbits), findNextOrBit(&tail_or_lhs, &tail_or_rhs, nbits, bits_per_long + 5));",
        "}",
        'test "tail-word next set scans skip earlier in-range matches before clamping" {',
        "    try std.testing.expectEqual(@as(usize, bits_per_long + 4), findNextBit(&tail_map, nbits, bits_per_long + 2));",
        "    try std.testing.expectEqual(@as(usize, nbits), findNextBit(&tail_map, nbits, bits_per_long + 5));",
        "    try std.testing.expectEqual(@as(usize, bits_per_long + 4), findNextAndNotBit(&tail_andnot_lhs, &tail_andnot_rhs, nbits, bits_per_long + 2));",
        "    try std.testing.expectEqual(@as(usize, nbits), findNextAndNotBit(&tail_andnot_lhs, &tail_andnot_rhs, nbits, bits_per_long + 5));",
        "}",
        'test "clump8 scans keep tail bytes reachable from partial final words" {',
        "    try std.testing.expectEqual(@as(usize, bits_per_long), findFirstClump8(&clump, &bitmap, nbits));",
        "    try std.testing.expectEqual(@as(u8, 0b0000_1000), clump);",
        "}",
        'test "clump8 scans mask tail bits beyond nbits" {',
        "    try std.testing.expectEqual(@as(usize, bits_per_long), findFirstClump8(&clump, &bitmap, nbits));",
        "    try std.testing.expectEqual(@as(u8, 0b0000_1000), clump);",
        "}",
        'test "clump8 zero-bit and past-end windows leave the caller byte untouched" {',
        "    _ = findFirstClump8(&clump, &populated, 0);",
        "    _ = findNextClump8(&clump, &populated, 8, 12);",
        "}",
        'test "clump8 past-end scans return without reading bitmap words" {',
        "    _ = findNextClump8(&clump, &empty, 8, 8);",
        "    _ = find_next_clump8(&clump, &empty, 8, 12);",
        "    _ = _find_next_clump8(&clump, &empty, 8, 20);",
        "}",
        'test "clump8 scans skip earlier aligned bytes once the offset moves forward" {',
        "    try std.testing.expectEqual(@as(usize, 8), findNextClump8(&clump, &bitmap, nbits, 0));",
        "    try std.testing.expectEqual(@as(usize, 24), findNextClump8(&clump, &bitmap, nbits, 16));",
        "    try std.testing.expectEqual(@as(usize, 24), findNextClump8(&clump, &bitmap, nbits, 25));",
        "    try std.testing.expectEqual(@as(usize, nbits), findNextClump8(&clump, &bitmap, nbits, 30));",
        "}",
        'test "clump8 keeps the last aligned byte of a word isolated from the next word" {',
        "    try std.testing.expectEqual(@as(usize, last_aligned_byte), findFirstClump8(&clump, &bitmap, nbits));",
        "    try std.testing.expectEqual(@as(u8, 0xa5), clump);",
        "    try std.testing.expectEqual(@as(usize, bits_per_long), findNextClump8(&clump, &bitmap, nbits, bits_per_long));",
        "    try std.testing.expectEqual(@as(u8, 0x11), clump);",
        "}",
        'test "getValue8 reads the last aligned byte of a word without folding in the next word" {',
        "    try std.testing.expectEqual(@as(u8, 0xa5), getValue8(&bitmap, last_aligned_byte));",
        "    try std.testing.expectEqual(@as(u8, 0x11), getValue8(&bitmap, bits_per_long));",
        "}",
        'test "low-level underscore aliases mirror the primary find helpers, including andnot" {',
        "    try std.testing.expectEqual(findFirstAndNotBit(&andnot_lhs, &andnot_rhs, nbits), _find_first_andnot_bit(&andnot_lhs, &andnot_rhs, nbits));",
        "    try std.testing.expectEqual(findNextAndNotBit(&andnot_lhs, &andnot_rhs, nbits, bits_per_long), _find_next_andnot_bit(&andnot_lhs, &andnot_rhs, nbits, bits_per_long));",
        "}",
        'test "Linux-style aliases mirror the primary find helpers, including andnot" {',
        "    try std.testing.expectEqual(findFirstAndNotBit(&andnot_lhs, &andnot_rhs, nbits), find_first_andnot_bit(&andnot_lhs, &andnot_rhs, nbits));",
        "    try std.testing.expectEqual(findNextAndNotBit(&andnot_lhs, &andnot_rhs, nbits, bits_per_long), find_next_andnot_bit(&andnot_lhs, &andnot_rhs, nbits, bits_per_long));",
        "}",
        'test "find last bit ignores storage beyond an exact word boundary" {',
        "    try std.testing.expectEqual(@as(usize, boundary), findLastBit(&bitmap, nbits));",
        "    bitmap[0] = 0;",
        "    try std.testing.expectEqual(@as(usize, nbits), findLastBit(&bitmap, nbits));",
        "}",
        'test "find last bit clamps tail words to nbits" {',
        "    try std.testing.expectEqual(@as(usize, 4), findLastBit(&single_word, single_word_nbits));",
        "}",
        'test "find last bit returns nbits when no set bits remain" {',
        "    try std.testing.expectEqual(@as(usize, nbits), findLastBit(&bitmap, nbits));",
        "    _ = findLastBit(&empty, 0);",
        "}",
    ]

    if omit_label is not None:
        marker = marker_for_label(omit_label)
        assert marker is not None
        lines = [line for line in lines if marker not in line]

    if duplicate_label is not None:
        marker = marker_for_label(duplicate_label)
        assert marker is not None
        for idx, line in enumerate(lines):
            if marker in line:
                lines.insert(idx + 1, line)
                break

    return "\n".join(lines) + "\n"


def run_self_test() -> None:
    case_count = 0

    kind, payload = validate_find_bit_source(build_sample_source())
    assert kind == "pass", (kind, payload)
    case_count += 1

    for label in REQUIRED_TEST_MARKERS:
        kind, payload = validate_find_bit_source(build_sample_source(omit_label=label))
        assert kind == "invalid_test_marker_counts", (label, kind, payload)
        assert payload == [f"{label}:expected=1:actual=0"], (label, payload)
        case_count += 1

    for label in REQUIRED_SOURCE_COUNT_MARKERS:
        kind, payload = validate_find_bit_source(build_sample_source(omit_label=label))
        assert kind == "invalid_source_count_markers", (label, kind, payload)
        marker, expected_count = REQUIRED_SOURCE_COUNT_MARKERS[label]
        assert payload == [f"{label}:expected={expected_count}:actual=0"], (label, payload)
        case_count += 1

    for label in REQUIRED_SOURCE_EXACT_MARKERS:
        kind, payload = validate_find_bit_source(build_sample_source(omit_label=label))
        assert kind == "invalid_source_marker_counts", (label, kind, payload)
        assert payload == [f"{label}:expected=1:actual=0"], (label, payload)
        case_count += 1

    for label in REQUIRED_TEST_MARKERS:
        kind, payload = validate_find_bit_source(build_sample_source(duplicate_label=label))
        assert kind == "invalid_test_marker_counts", (label, kind, payload)
        assert payload == [f"{label}:expected=1:actual=2"], (label, payload)
        case_count += 1

    for label in REQUIRED_SOURCE_COUNT_MARKERS:
        kind, payload = validate_find_bit_source(build_sample_source(duplicate_label=label))
        assert kind == "invalid_source_count_markers", (label, kind, payload)
        marker, expected_count = REQUIRED_SOURCE_COUNT_MARKERS[label]
        assert payload == [f"{label}:expected={expected_count}:actual={expected_count + 1}"], (label, payload)
        case_count += 1

    for label in REQUIRED_SOURCE_EXACT_MARKERS:
        kind, payload = validate_find_bit_source(build_sample_source(duplicate_label=label))
        assert kind == "invalid_source_marker_counts", (label, kind, payload)
        assert payload == [f"{label}:expected=1:actual=2"], (label, payload)
        case_count += 1

    with tempfile.TemporaryDirectory(prefix="phase1-find-bit-bench-anchors-") as tmp:
        source_path = Path(tmp) / "find_bit.zig"
        kind, payload = load_find_bit_source(source_path)
        assert kind == "missing_file", (kind, payload)
        assert payload == source_path
        case_count += 1

        source_path.write_text(build_sample_source(), encoding="utf-8")
        kind, payload = load_find_bit_source(source_path)
        assert kind == "pass", (kind, payload)
        case_count += 1

    print("PHASE1_FIND_BIT_BENCH_ANCHORS_SELF_TEST=pass")
    print(f"PHASE1_FIND_BIT_BENCH_ANCHORS_SELF_TEST_CASE_COUNT={case_count}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate that the live find_bit helper still carries the current bench-adjacent same-word start-mask, inclusive-boundary, tail-clamp, and byte-clump anchors directly in tools/lib/find_bit.zig."
    )
    parser.add_argument("--self-test", action="store_true", help="Run self-test cases only.")
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return 0

    kind, payload = load_find_bit_source(FIND_BIT)
    if kind != "pass":
        print("PHASE1_FIND_BIT_BENCH_ANCHORS=fail")
        print(f"PHASE1_FIND_BIT_BENCH_ANCHORS_REASON={kind}")
        print(payload)
        return 1

    print("PHASE1_FIND_BIT_BENCH_ANCHORS=pass")
    print(f"PHASE1_FIND_BIT_BENCH_ANCHORS_SOURCE={FIND_BIT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())