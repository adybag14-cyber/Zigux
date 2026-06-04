const std = @import("std");
const build_options = @import("build_options");

const checker = build_options.direct_anchor_manifest_gate_py;
const manifest = build_options.phase1_helper_manifest_json;

const direct_anchor_helpers = [_][]const u8{
    "tools/lib/bitmap.zig",
    "tools/lib/find_bit.zig",
    "tools/lib/rbtree.zig",
    "tools/lib/string.zig",
};

const delegated_checkers = [_][]const u8{
    "scripts/zigux/check-phase1-bitmap-direct-anchors.py",
    "scripts/zigux/check-phase1-find-bit-review-packet.py",
    "scripts/zigux/check-phase1-rbtree-direct-anchors.py",
    "scripts/zigux/check-phase1-rbtree-review-packet.py",
    "scripts/zigux/check-phase1-string-review-packet.py",
};

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectContainsAny(haystack: []const u8, needles: []const []const u8) !void {
    for (needles) |needle| {
        if (std.mem.indexOf(u8, haystack, needle) != null) return;
    }
    return error.MissingNeedle;
}

fn expectCount(haystack: []const u8, needle: []const u8, expected: usize) !void {
    var count: usize = 0;
    var index: usize = 0;
    while (std.mem.indexOfPos(u8, haystack, index, needle)) |found| {
        count += 1;
        index = found + needle.len;
    }
    try std.testing.expectEqual(expected, count);
}

fn expectInOrder(haystack: []const u8, needles: []const []const u8) !void {
    var index: usize = 0;
    for (needles) |needle| {
        const found = std.mem.indexOfPos(u8, haystack, index, needle) orelse return error.MissingNeedle;
        index = found + needle.len;
    }
}

test "direct-anchor manifest gate keeps the four-helper lane split explicit" {
    try expectContains(checker, "EXPECTED_HELPERS");
    try expectContains(checker, "zigux/tests/fixtures/phase1_helper_manifest.json");
    try expectContains(checker, "manifest:helper_count=13");
    try expectContains(manifest, "\"helper_count\": 13");
    try expectContains(manifest, "\"status\": \"closed\"");

    for (direct_anchor_helpers) |helper| {
        try expectContains(checker, helper);
        try expectContains(manifest, helper);
    }

    try expectInOrder(manifest, direct_anchor_helpers[0..]);
    try expectContainsAny(checker, &.{
        "PHASE1_DIRECT_ANCHOR_HELPER_COUNT={len(EXPECTED_DIRECT_ANCHOR_FOLLOWUP_HELPERS)}",
        "PHASE1_DIRECT_ANCHOR_HELPER_COUNT={len(EXPECTED_HELPERS)}",
    });
    try expectContains(checker, "PHASE1_DIRECT_ANCHOR_REVIEW_FIELD_COUNT=");
}

test "delegated checker roster is either explicit or still direct-helper scoped" {
    try std.testing.expectEqual(@as(usize, 5), delegated_checkers.len);

    try expectContainsAny(checker, &.{
        "DELEGATED_CHECKERS",
        "EXPECTED_REVIEW_ANCHORS",
    });
    try expectContainsAny(checker, &.{
        "PHASE1_DIRECT_ANCHOR_DELEGATED_CHECKER_COUNT={len(DELEGATED_CHECKERS)}",
        "PHASE1_DIRECT_ANCHOR_HELPER_COUNT={len(EXPECTED_HELPERS)}",
    });
    try expectContains(checker, "PHASE1_DIRECT_ANCHOR_MANIFEST_GATE=pass");
    try expectContains(checker, "PHASE1_DIRECT_ANCHOR_MANIFEST_GATE=fail");
}

test "manifest review fields pin bitmap find_bit rbtree and string anchors" {
    const required_fields = [_][]const u8{
        "helper_test_anchors",
        "parity_fixture_keys",
        "partial_xor_review_fields",
        "phase1_helper_replay_anchor",
        "review_packet_summary",
        "next_safe_step_note",
    };

    try expectContains(checker, "review_anchors");
    for (required_fields) |field| {
        try expectContains(manifest, field);
    }

    try expectContainsAny(manifest, &.{
        "copy_raw_alias_anchor",
        "cross_word_scnprintf_anchor",
    });
    try expectContainsAny(manifest, &.{
        "andnot_scan_entrypoints",
        "tail_clamp_fixture_keys",
    });
    try expectContainsAny(manifest, &.{
        "cached_root_transition_fixture_keys",
        "cached_leftmost_fixture_keys",
        "cached_root_followup_anchors",
    });
    try expectContains(checker, "manifest:review_anchor_value={helper}:{field}");
    try expectContainsAny(checker, &.{
        "manifest:missing_review_anchor={helper}",
        "manifest:missing_review_anchor_field={helper}:{field}",
    });
}

test "manifest failures and self-test output markers are preserved" {
    try expectContains(checker, "json.loads");
    try expectContains(checker, "PHASE1_DIRECT_ANCHOR_MANIFEST_GATE=fail");
    try expectContains(checker, "PHASE1_DIRECT_ANCHOR_MANIFEST_GATE_ISSUES_START");
    try expectContains(checker, "PHASE1_DIRECT_ANCHOR_MANIFEST_GATE_ISSUES_END");
    try expectContains(checker, "PHASE1_DIRECT_ANCHOR_MANIFEST_GATE=pass");
    try expectContains(checker, "PHASE1_DIRECT_ANCHOR_MANIFEST_GATE_SELF_TEST=pass");
    try expectContains(checker, "PHASE1_DIRECT_ANCHOR_MANIFEST_GATE_SELF_TEST_CASE_COUNT={case_count}");
    try expectCount(checker, "manifest:helper_count=13", 2);
}
