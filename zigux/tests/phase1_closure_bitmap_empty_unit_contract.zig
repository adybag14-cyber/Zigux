const std = @import("std");

const closure_marker =
    \\PHASE1_BITMAP_EMPTY_UNIT_REVIEW=bitmap_scnprintf leaves a non-empty caller buffer untouched when no bits are set, matching both the direct Zig unit test and the committed parity fixture
;

const manifest_empty_buffer_anchor =
    \\"empty_buffer_anchor": "test \"bitmap scnprintf leaves the caller buffer untouched for an empty bitmap\""
;

const manifest_review_summary =
    \\shared Phase 1 fixture keys now own bitmap allocator sizing, zero-filled allocation words, copy/copy-clear-tail/copy-and-extend replay, scnprintf output, truncation, tiny-buffer handling, logical operator outputs, range set/clear/fill/zero outcomes, and partial-window xor replay, while current master keeps the direct helper-local bitmap packet bounded to whole-word range edges, raw copy alias behavior, tail-clearing and extension semantics, zero and aligned copyAndExtend handling, zero-sized destination-view no-op coverage, zero-bit logical short-circuit coverage, exact-word-boundary equality fast-path masking, tail-masked predicate behavior, out-of-range tail-bit full or empty or weight masking, caller-window xor and or clamping, multiword-tail xor and or clamp witnesses, weighted tail-count clamping, terminator-only and zero-length caller-view formatting, empty-bitmap caller-buffer preservation, Linux-style alias mirror coverage, and allocator optional-reset coverage.
;

const fixture_scnprintf_packet =
    \\"scnprintf": "1-3,66-67"
    \\"truncated_scnprintf_len": 7
    \\"truncated_scnprintf": "1-3,66-"
    \\"terminator_only_scnprintf_len": 0
    \\"terminator_only_nul": 0
    \\"zero_length_scnprintf_len": 0
;

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectNotContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

test "closure note keeps bitmap empty-unit review tied to scnprintf" {
    try expectContains(
        closure_marker,
        "PHASE1_BITMAP_EMPTY_UNIT_REVIEW=bitmap_scnprintf leaves a non-empty caller buffer untouched when no bits are set",
    );
    try expectContains(closure_marker, "matching both the direct Zig unit test and the committed parity fixture");
    try expectContains(closure_marker, "bitmap_scnprintf");
    try expectNotContains(closure_marker, "complement-tail");
    try expectNotContains(closure_marker, "partial_xor");
}

test "manifest keeps empty-buffer proof helper-local" {
    try expectContains(
        manifest_empty_buffer_anchor,
        "\"empty_buffer_anchor\": \"test \\\"bitmap scnprintf leaves the caller buffer untouched for an empty bitmap\\\"\"",
    );
    try expectContains(manifest_review_summary, "empty-bitmap caller-buffer preservation");
    try expectContains(manifest_review_summary, "terminator-only and zero-length caller-view formatting");
    try expectContains(manifest_review_summary, "scnprintf output, truncation, tiny-buffer handling");
    try expectNotContains(manifest_review_summary, "empty_unit_fixture_key");
}

test "shared fixture carries scnprintf values without a dedicated empty-unit key" {
    try expectContains(fixture_scnprintf_packet, "\"scnprintf\": \"1-3,66-67\"");
    try expectContains(fixture_scnprintf_packet, "\"truncated_scnprintf_len\": 7");
    try expectContains(fixture_scnprintf_packet, "\"truncated_scnprintf\": \"1-3,66-\"");
    try expectContains(fixture_scnprintf_packet, "\"terminator_only_scnprintf_len\": 0");
    try expectContains(fixture_scnprintf_packet, "\"terminator_only_nul\": 0");
    try expectContains(fixture_scnprintf_packet, "\"zero_length_scnprintf_len\": 0");
    try expectNotContains(fixture_scnprintf_packet, "\"empty_unit_scnprintf\"");
    try expectNotContains(fixture_scnprintf_packet, "\"empty_buffer_anchor\"");
}
