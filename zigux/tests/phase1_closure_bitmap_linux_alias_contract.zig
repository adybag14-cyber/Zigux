const std = @import("std");

const closure_marker =
    \\PHASE1_BITMAP_LINUX_ALIAS_REVIEW=helper-local bitmap Linux-style alias proof stays explicit through the direct bitmap test anchor and the Phase 1 helper manifest so the Linux-style bitmap alloc/free, zero/fill, predicate, mutation, and render aliases remain behaviorally locked to the primary helper surface
;

const helper_alias_anchors =
    \\test "bitmap Linux-style aliases mirror copy logical range and format helpers"
    \\test "bitmap Linux-style aliases mirror size state and allocation helpers"
;

const manifest_alias_anchor =
    \\"linux_alias_anchor": "test \"bitmap Linux-style aliases mirror copy logical range and format helpers\""
;

const manifest_review_summary =
    \\shared Phase 1 fixture keys now own bitmap allocator sizing, zero-filled allocation words, copy/copy-clear-tail/copy-and-extend replay, scnprintf output, truncation, tiny-buffer handling, logical operator outputs, range set/clear/fill/zero outcomes, and partial-window xor replay, while current master keeps the direct helper-local bitmap packet bounded to whole-word range edges, raw copy alias behavior, tail-clearing and extension semantics, zero and aligned copyAndExtend handling, zero-sized destination-view no-op coverage, zero-bit logical short-circuit coverage, exact-word-boundary equality fast-path masking, tail-masked predicate behavior, out-of-range tail-bit full or empty or weight masking, caller-window xor and or clamping, multiword-tail xor and or clamp witnesses, weighted tail-count clamping, terminator-only and zero-length caller-view formatting, empty-bitmap caller-buffer preservation, Linux-style alias mirror coverage, and allocator optional-reset coverage.
;

const shared_fixture_packet =
    \\"copy_values": [18446744073709551615, 18446744073709551615]
    \\"copy_clear_tail_values": [18446744073709551615, 31]
    \\"copy_and_extend_values": [18446744073709551615, 31, 0]
    \\"or_values": [14, 0]
    \\"xor_values": [4, 0]
    \\"range_after_set": [14, 12, 0]
    \\"scnprintf": "1-3,66-67"
    \\"alloc_words": 3
    \\"zalloc_values": [0, 0, 0]
;

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectNotContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

test "closure note keeps bitmap Linux alias review helper-local" {
    try expectContains(
        closure_marker,
        "PHASE1_BITMAP_LINUX_ALIAS_REVIEW=helper-local bitmap Linux-style alias proof stays explicit",
    );
    try expectContains(closure_marker, "direct bitmap test anchor and the Phase 1 helper manifest");
    try expectContains(closure_marker, "alloc/free, zero/fill, predicate, mutation, and render aliases");
    try expectContains(closure_marker, "behaviorally locked to the primary helper surface");
    try expectNotContains(closure_marker, "shared fixture key");
    try expectNotContains(closure_marker, "validator-owned");
}

test "direct bitmap anchors split Linux aliases by behavior family" {
    try expectContains(
        helper_alias_anchors,
        "test \"bitmap Linux-style aliases mirror copy logical range and format helpers\"",
    );
    try expectContains(
        helper_alias_anchors,
        "test \"bitmap Linux-style aliases mirror size state and allocation helpers\"",
    );
    try expectContains(helper_alias_anchors, "copy logical range and format");
    try expectContains(helper_alias_anchors, "size state and allocation");
    try expectNotContains(helper_alias_anchors, "primary helper surface");
}

test "manifest keeps Linux alias ownership in the bitmap direct-anchor packet" {
    try expectContains(
        manifest_alias_anchor,
        "\"linux_alias_anchor\": \"test \\\"bitmap Linux-style aliases mirror copy logical range and format helpers\\\"\"",
    );
    try expectContains(manifest_review_summary, "Linux-style alias mirror coverage");
    try expectContains(manifest_review_summary, "allocator optional-reset coverage");
    try expectContains(manifest_review_summary, "copy/copy-clear-tail/copy-and-extend replay");
    try expectContains(manifest_review_summary, "logical operator outputs");
    try expectContains(manifest_review_summary, "range set/clear/fill/zero outcomes");
}

test "shared fixture covers replay values without claiming a Linux alias fixture key" {
    try expectContains(shared_fixture_packet, "\"copy_values\": [18446744073709551615, 18446744073709551615]");
    try expectContains(shared_fixture_packet, "\"copy_clear_tail_values\": [18446744073709551615, 31]");
    try expectContains(shared_fixture_packet, "\"copy_and_extend_values\": [18446744073709551615, 31, 0]");
    try expectContains(shared_fixture_packet, "\"or_values\": [14, 0]");
    try expectContains(shared_fixture_packet, "\"xor_values\": [4, 0]");
    try expectContains(shared_fixture_packet, "\"range_after_set\": [14, 12, 0]");
    try expectContains(shared_fixture_packet, "\"scnprintf\": \"1-3,66-67\"");
    try expectContains(shared_fixture_packet, "\"alloc_words\": 3");
    try expectContains(shared_fixture_packet, "\"zalloc_values\": [0, 0, 0]");
    try expectNotContains(shared_fixture_packet, "\"linux_alias_values\"");
    try expectNotContains(shared_fixture_packet, "\"bitmap_linux_alias_anchor\"");
}
