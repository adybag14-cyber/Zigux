const std = @import("std");

const closure_marker =
    \\PHASE1_BITMAP_FINAL_PARTIAL_WORD_REVIEW=helper-local bitmap final partial-word proof stays explicit through the direct bitmap test anchor so setRange and clearRange clamp trailing partial-word masks to the requested tail window instead of spilling work beyond it
;

const manifest_anchor =
    \\"final_partial_word_anchor": "test \"bitmap range helpers preserve edges across whole-word spans\""
;

const manifest_review_summary =
    \\current master still ships direct fill-tail clamp, raw copy alias, cross-word scnprintf, exact-word-boundary equality fast-path masking, caller-window xor and or clamp, weighted tail-count clamp, empty-buffer, allocator-reset, zero-bit logical short-circuit, and Linux-style alias mirror anchors here
;

const fixture_range_packet =
    \\"range_after_set": [14, 12, 0],
    \\"range_after_clear": [0, 0, 0],
    \\"full_after_fill": true,
    \\"empty_after_zero": true
;

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectNotContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

test "closure note keeps bitmap final partial-word review parked helper-local" {
    try expectContains(
        closure_marker,
        "PHASE1_BITMAP_FINAL_PARTIAL_WORD_REVIEW=helper-local bitmap final partial-word proof stays explicit through the direct bitmap test anchor",
    );
    try expectContains(
        closure_marker,
        "setRange and clearRange clamp trailing partial-word masks to the requested tail window instead of spilling work beyond it",
    );
    try expectNotContains(closure_marker, "partial_xor_masked_values");
    try expectNotContains(closure_marker, "complement_tail");
}

test "manifest maps final partial-word review to the direct bitmap range anchor" {
    try expectContains(
        manifest_anchor,
        "\"final_partial_word_anchor\": \"test \\\"bitmap range helpers preserve edges across whole-word spans\\\"\"",
    );
    try expectContains(
        manifest_anchor,
        "bitmap range helpers preserve edges across whole-word spans",
    );
    try expectContains(
        manifest_review_summary,
        "current master still ships direct fill-tail clamp, raw copy alias, cross-word scnprintf, exact-word-boundary equality fast-path masking",
    );
    try expectContains(manifest_review_summary, "caller-window xor and or clamp");
    try expectContains(manifest_review_summary, "Linux-style alias mirror anchors");
}

test "shared fixture records range outcomes without inventing final partial-word keys" {
    try expectContains(fixture_range_packet, "\"range_after_set\": [14, 12, 0]");
    try expectContains(fixture_range_packet, "\"range_after_clear\": [0, 0, 0]");
    try expectContains(fixture_range_packet, "\"full_after_fill\": true");
    try expectContains(fixture_range_packet, "\"empty_after_zero\": true");
    try expectNotContains(fixture_range_packet, "\"final_partial_word_values\"");
    try expectNotContains(fixture_range_packet, "\"final_partial_word_mask\"");
}
