#!/usr/bin/env python3
"""Guard the Phase 1 bitmap direct-anchor packet against helper-local drift."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent
BITMAP_REL = Path("tools/lib/bitmap.zig")

REQUIRED_TEST_MARKERS = {
    "set_clear_weight_full_empty": 'test "bitmap set clear weight and empty full helpers" {',
    "range_edges": 'test "bitmap range helpers preserve edges across whole-word spans" {',
    "copy_raw_alias": 'test "bitmap copy alias preserves raw source words without tail clearing" {',
    "copy_tail_extend_alias": 'test "bitmap copy aliases preserve tail clearing and extension semantics" {',
    "copy_zero_aligned": 'test "bitmap copy and extend handles zero and aligned counts" {',
    "copy_zero_sized_views": 'test "bitmap copy helpers keep zero-sized destination views untouched" {',
    "zero_bit_logical": 'test "bitmap zero-bit logical helpers stay explicit" {',
    "equal_fast_path": 'test "bitmap equal fast path ignores storage beyond an exact word boundary" {',
    "logical_baseline": 'test "bitmap and andnot equal intersects subset" {',
    "tail_mask_predicates": 'test "bitmap tail-masked helpers ignore out-of-range differences" {',
    "tail_mask_counts": 'test "bitmap full empty and weight ignore out-of-range tail bits" {',
    "xor_window": 'test "bitmap xor keeps caller-selected bit window" {',
    "xor_multiword_tail": 'test "bitmap xor across a multiword tail still lets callers clamp the last word" {',
    "or_window": 'test "bitmap or keeps caller-selected bit window" {',
    "or_multiword_tail": 'test "bitmap or across a multiword tail still lets callers clamp the last word" {',
    "weighted_or_xor_tail": 'test "bitmap weighted or and xor clamp counts to the declared tail window" {',
    "weighted_and_andnot_tail": 'test "bitmap weighted and andnot clamp counts to the declared tail window" {',
    "complement_tail": 'test "bitmap complement clamps partial tails and leaves zero-sized caller views untouched" {',
    "scnprintf_contiguous_ranges": 'test "bitmap scnprintf collapses contiguous ranges" {',
    "scnprintf_cross_word": 'test "bitmap scnprintf keeps contiguous ranges merged across word boundaries" {',
    "scnprintf_truncation": 'test "bitmap scnprintf truncates and keeps a terminator slot" {',
    "scnprintf_zero_views": 'test "bitmap scnprintf handles terminator-only and zero-length caller views" {',
    "scnprintf_empty_buffer": 'test "bitmap scnprintf leaves the caller buffer untouched for an empty bitmap" {',
    "linux_alias_copy_logic": 'test "bitmap Linux-style aliases mirror copy logical range and format helpers" {',
    "linux_alias_size_alloc": 'test "bitmap Linux-style aliases mirror size state and allocation helpers" {',
    "allocation_helpers": 'test "bitmap allocation helpers size zero fill and reset optionals" {',
}

REQUIRED_SOURCE_MARKERS = {
    "bitmap_size_alias": "pub fn bitmap_size(nbits: usize) usize {",
    "bitmap_zero_alias": "pub fn bitmap_zero(dst: []Word, nbits: usize) void {",
    "bitmap_fill_alias": "pub fn bitmap_fill(dst: []Word, nbits: usize) void {",
    "bitmap_copy_alias": "pub fn bitmap_copy(dst: []Word, src: []const Word, nbits: usize) void {",
    "bitmap_copy_clear_tail_alias": "pub fn bitmap_copy_clear_tail(dst: []Word, src: []const Word, nbits: usize) void {",
    "bitmap_copy_and_extend_alias": "pub fn bitmap_copy_and_extend(dst: []Word, src: []const Word, count: usize, size: usize) void {",
    "bitmap_empty_alias": "pub fn bitmap_empty(src: []const Word, nbits: usize) bool {",
    "bitmap_full_alias": "pub fn bitmap_full(src: []const Word, nbits: usize) bool {",
    "bitmap_weight_alias": "pub fn bitmap_weight(src: []const Word, nbits: usize) usize {",
    "bitmap_or_alias": "pub fn bitmap_or(dst: []Word, src1: []const Word, src2: []const Word, nbits: usize) void {",
    "bitmap_xor_alias": "pub fn bitmap_xor(dst: []Word, src1: []const Word, src2: []const Word, nbits: usize) void {",
    "bitmap_weighted_or_alias": "pub fn bitmap_weighted_or(dst: []Word, src1: []const Word, src2: []const Word, nbits: usize) usize {",
    "bitmap_weighted_xor_alias": "pub fn bitmap_weighted_xor(dst: []Word, src1: []const Word, src2: []const Word, nbits: usize) usize {",
    "bitmap_weight_and_alias": "pub fn bitmap_weight_and(src1: []const Word, src2: []const Word, nbits: usize) usize {",
    "bitmap_weight_andnot_alias": "pub fn bitmap_weight_andnot(src1: []const Word, src2: []const Word, nbits: usize) usize {",
    "bitmap_and_alias": "pub fn bitmap_and(dst: []Word, src1: []const Word, src2: []const Word, nbits: usize) bool {",
    "bitmap_andnot_alias": "pub fn bitmap_andnot(dst: []Word, src1: []const Word, src2: []const Word, nbits: usize) bool {",
    "bitmap_equal_alias": "pub fn bitmap_equal(src1: []const Word, src2: []const Word, nbits: usize) bool {",
    "bitmap_intersects_alias": "pub fn bitmap_intersects(src1: []const Word, src2: []const Word, nbits: usize) bool {",
    "bitmap_subset_alias": "pub fn bitmap_subset(src1: []const Word, src2: []const Word, nbits: usize) bool {",
    "bitmap_complement_alias": "pub fn bitmap_complement(dst: []Word, src: []const Word, nbits: usize) void {",
    "bitmap_set_alias": "pub fn bitmap_set(map: []Word, start: usize, len: usize) void {",
    "bitmap_clear_alias": "pub fn bitmap_clear(map: []Word, start: usize, len: usize) void {",
    "bitmap_scnprintf_alias": "pub fn bitmap_scnprintf(bitmap: []const Word, nbits: usize, buffer: []u8) usize {",
    "bitmap_alloc_alias": "pub fn bitmap_alloc(allocator: std.mem.Allocator, nbits: usize) ![]Word {",
    "bitmap_zalloc_alias": "pub fn bitmap_zalloc(allocator: std.mem.Allocator, nbits: usize) ![]Word {",
    "bitmap_free_alias": "pub fn bitmap_free(allocator: std.mem.Allocator, bitmap: *?[]Word) void {",
    "set_clear_weight_assert": "try std.testing.expectEqual(@as(usize, 5), weight(&map, bits_per_long * 2));",
    "clear_empty_assert": "try std.testing.expect(empty(&map, bits_per_long * 2));",
    "range_first_word_assert": "try std.testing.expectEqual(@as(Word, firstWordMask(start)), map[0]);",
    "range_last_partial_assert": "try std.testing.expectEqual(lastWordMask(start + len), map[3]);",
    "fill_tail_clamp_assert": "try std.testing.expect(full(&full_map, nbits));",
    "zero_bit_equal_identity_assert": "try std.testing.expect(equal(lhs[0..0], rhs[0..0], 0));",
    "zero_bit_subset_identity_assert": "try std.testing.expect(subset(lhs[0..0], rhs[0..0], 0));",
    "logical_and_assert": "try std.testing.expect(andBits(&dst, &lhs, &rhs, 8));",
    "logical_subset_assert": "try std.testing.expect(subset(&rhs, &lhs, 8));",
    "scnprintf_collapse_assert": 'try std.testing.expectEqualStrings("1-3,10-11", buffer[0..len]);',
    "empty_buffer_preserved_assert": "try std.testing.expectEqualSlices(u8, &[_]u8{ 0xaa, 0xaa, 0xaa, 0xaa }, &buffer);",
    "or_multiword_tail_assert": "try std.testing.expectEqualSlices(Word, &[_]Word{ 0b11_1101, 0b01_0111 }, &[_]Word{ dst[0], dst[1] & lastWordMask(nbits) });",
    "weighted_or_direct_count": "try std.testing.expectEqual(@as(usize, 2), direct_or_weight);",
    "weighted_xor_direct_count": "try std.testing.expectEqual(@as(usize, 2), direct_xor_weight);",
    "weighted_or_masked_count": "try std.testing.expectEqual(@as(usize, 2), weight(&direct_or, nbits));",
    "weighted_and_direct_count": "try std.testing.expectEqual(@as(usize, 1), direct_and_weight);",
    "weighted_andnot_direct_count": "try std.testing.expectEqual(@as(usize, 1), direct_andnot_weight);",
    "complement_tail_mask_assert": "try std.testing.expectEqual((~src[1]) & lastWordMask(nbits), direct[1]);",
    "bitmap_size_alias_assert": "try std.testing.expectEqual(bitmapSize(nbits), bitmap_size(nbits));",
    "bitmap_zero_alias_assert": "bitmap_zero(&alias, nbits);",
    "bitmap_empty_alias_assert": "try std.testing.expectEqual(empty(&direct, nbits), bitmap_empty(&alias, nbits));",
    "bitmap_fill_alias_assert": "bitmap_fill(&alias, nbits);",
    "bitmap_full_alias_assert": "try std.testing.expectEqual(full(&direct, nbits), bitmap_full(&alias, nbits));",
    "bitmap_weight_alias_assert": "try std.testing.expectEqual(weight(&direct, nbits), bitmap_weight(&alias, nbits));",
    "bitmap_copy_alias_assert": "bitmap_copy(&alias, &lhs, nbits);",
    "bitmap_copy_clear_tail_alias_assert": "bitmap_copy_clear_tail(&alias_tail, src[0..2], count);",
    "bitmap_copy_and_extend_alias_assert": "bitmap_copy_and_extend(&alias_extend, src[0..2], count, size);",
    "bitmap_or_alias_assert": "bitmap_or(&alias, &lhs, &rhs, nbits);",
    "bitmap_xor_alias_assert": "bitmap_xor(&alias, &lhs, &rhs, nbits);",
    "bitmap_weighted_or_alias_assert": "const alias_or_weight = bitmap_weighted_or(&alias_or, &or_lhs, &or_rhs, nbits);",
    "bitmap_weighted_xor_alias_assert": "const alias_xor_weight = bitmap_weighted_xor(&alias_xor, &xor_lhs, &xor_rhs, nbits);",
    "bitmap_weight_and_alias_assert": "const alias_and_weight = bitmap_weight_and(&and_lhs, &and_rhs, nbits);",
    "bitmap_weight_andnot_alias_assert": "const alias_andnot_weight = bitmap_weight_andnot(&and_lhs, &and_rhs, nbits);",
    "bitmap_complement_alias_assert": "bitmap_complement(&alias, &src, nbits);",
    "bitmap_and_alias_assert": "try std.testing.expectEqual(andBits(&direct, &lhs, &rhs, nbits), bitmap_and(&alias, &lhs, &rhs, nbits));",
    "bitmap_andnot_alias_assert": "try std.testing.expectEqual(andNotBits(&direct, &lhs, &rhs, nbits), bitmap_andnot(&alias, &lhs, &rhs, nbits));",
    "bitmap_equal_alias_assert": "try std.testing.expectEqual(equal(&lhs, &rhs, nbits), bitmap_equal(&lhs, &rhs, nbits));",
    "bitmap_intersects_alias_assert": "try std.testing.expectEqual(intersects(&lhs, &rhs, nbits), bitmap_intersects(&rhs, &lhs, nbits));",
    "bitmap_subset_alias_assert": "try std.testing.expectEqual(subset(&rhs, &lhs, nbits), bitmap_subset(&rhs, &lhs, nbits));",
    "bitmap_set_alias_assert": "bitmap_set(&alias_range, 1, 3);",
    "bitmap_clear_alias_assert": "bitmap_clear(&alias_range, 2, 1);",
    "bitmap_scnprintf_alias_assert": "const alias_len = bitmap_scnprintf(&alias_range, nbits, &alias_buffer);",
    "bitmap_alloc_alias_assert": "var plain_alias: ?[]Word = try bitmap_alloc(allocator, nbits);",
    "bitmap_zalloc_alias_assert": "var zeroed_alias: ?[]Word = try bitmap_zalloc(allocator, nbits);",
}


def repo_root(override: str | None) -> Path:
    return Path(override).resolve() if override else DEFAULT_ROOT.resolve()


def collect_marker_count_failures(text: str, markers: dict[str, str]) -> list[str]:
    failures: list[str] = []
    for label, marker in markers.items():
        count = text.count(marker)
        if count != 1:
            failures.append(f"{label}:expected=1:actual={count}")
    return failures


def validate_bitmap_source(text: str) -> tuple[str, object]:
    test_failures = collect_marker_count_failures(text, REQUIRED_TEST_MARKERS)
    if test_failures:
        return ("invalid_test_marker_counts", test_failures)

    source_failures = collect_marker_count_failures(text, REQUIRED_SOURCE_MARKERS)
    if source_failures:
        return ("invalid_source_marker_counts", source_failures)

    return ("pass", None)


def load_bitmap_source(root: Path) -> tuple[str, object]:
    path = root / BITMAP_REL
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ("missing_file", path)
    return validate_bitmap_source(text)


def build_sample_source(omit_label: str | None = None, duplicate_label: str | None = None) -> str:
    lines = list(REQUIRED_TEST_MARKERS.values()) + list(REQUIRED_SOURCE_MARKERS.values())

    if omit_label is not None:
        marker = REQUIRED_TEST_MARKERS.get(omit_label, REQUIRED_SOURCE_MARKERS.get(omit_label))
        assert marker is not None
        lines = [line for line in lines if line != marker]

    if duplicate_label is not None:
        marker = REQUIRED_TEST_MARKERS.get(duplicate_label, REQUIRED_SOURCE_MARKERS.get(duplicate_label))
        assert marker is not None
        for idx, line in enumerate(lines):
            if line == marker:
                lines.insert(idx + 1, line)
                break

    return "\n".join(lines) + "\n"


def run_self_test() -> None:
    case_count = 0

    kind, payload = validate_bitmap_source(build_sample_source())
    assert kind == "pass", (kind, payload)
    case_count += 1

    for label in REQUIRED_TEST_MARKERS:
        kind, payload = validate_bitmap_source(build_sample_source(omit_label=label))
        assert kind == "invalid_test_marker_counts", (label, kind, payload)
        assert payload == [f"{label}:expected=1:actual=0"], (label, payload)
        case_count += 1

    for label in REQUIRED_SOURCE_MARKERS:
        kind, payload = validate_bitmap_source(build_sample_source(omit_label=label))
        assert kind == "invalid_source_marker_counts", (label, kind, payload)
        assert payload == [f"{label}:expected=1:actual=0"], (label, payload)
        case_count += 1

    for label in REQUIRED_TEST_MARKERS:
        kind, payload = validate_bitmap_source(build_sample_source(duplicate_label=label))
        assert kind == "invalid_test_marker_counts", (label, kind, payload)
        assert payload == [f"{label}:expected=1:actual=2"], (label, payload)
        case_count += 1

    for label in REQUIRED_SOURCE_MARKERS:
        kind, payload = validate_bitmap_source(build_sample_source(duplicate_label=label))
        assert kind == "invalid_source_marker_counts", (label, kind, payload)
        assert payload == [f"{label}:expected=1:actual=2"], (label, payload)
        case_count += 1

    with tempfile.TemporaryDirectory(prefix="phase1-bitmap-direct-anchors-") as tmp:
        root = Path(tmp)
        kind, payload = load_bitmap_source(root)
        assert kind == "missing_file", (kind, payload)
        assert payload == root / BITMAP_REL
        case_count += 1

        path = root / BITMAP_REL
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(build_sample_source(), encoding="utf-8")
        kind, payload = load_bitmap_source(root)
        assert kind == "pass", (kind, payload)
        case_count += 1

    print("PHASE1_BITMAP_DIRECT_ANCHORS_SELF_TEST=pass")
    print(f"PHASE1_BITMAP_DIRECT_ANCHORS_SELF_TEST_CASE_COUNT={case_count}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="override the repository root for validation")
    parser.add_argument("--self-test", action="store_true", help="run self-test cases")
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return 0

    kind, payload = load_bitmap_source(repo_root(args.root))
    if kind != "pass":
        print("PHASE1_BITMAP_DIRECT_ANCHORS=fail")
        if isinstance(payload, list):
            print("PHASE1_BITMAP_DIRECT_ANCHORS_REASON=" + kind)
            for failure in payload:
                print(failure)
        else:
            print(f"PHASE1_BITMAP_DIRECT_ANCHORS_REASON={kind}")
            print(payload)
        return 1

    print("PHASE1_BITMAP_DIRECT_ANCHORS=pass")
    print(f"PHASE1_BITMAP_DIRECT_ANCHORS_HELPER={BITMAP_REL.as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
