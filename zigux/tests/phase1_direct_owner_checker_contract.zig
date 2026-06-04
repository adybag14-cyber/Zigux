const std = @import("std");
const options = @import("phase1_direct_owner_checker_contract_options");

const checker = options.checker;
const manifest = @embedFile("fixtures/phase1_helper_manifest.json");
const lane_note = options.lane_note;

const shared_replay_helpers = [_][]const u8{
    "tools/lib/argv_split.zig",
    "tools/lib/cmdline.zig",
    "tools/lib/ctype.zig",
    "tools/lib/hweight.zig",
    "tools/lib/list_sort.zig",
    "tools/lib/slab.zig",
    "tools/lib/str_error_r.zig",
    "tools/lib/vsprintf.zig",
    "tools/lib/zalloc.zig",
};

const direct_anchor_helpers = [_][]const u8{
    "tools/lib/bitmap.zig",
    "tools/lib/find_bit.zig",
    "tools/lib/rbtree.zig",
    "tools/lib/string.zig",
};

const direct_owner_prefixes = [_][]const u8{
    "PHASE1_BITMAP_DIRECT_OWNER=bitmap",
    "PHASE1_FIND_BIT_DIRECT_OWNER=find_bit",
    "PHASE1_RBTREE_DIRECT_OWNER=rbtree",
    "PHASE1_STRING_DIRECT_OWNER=string",
};

const next_safe_step_prefixes = [_][]const u8{
    "PHASE1_BITMAP_NEXT_SAFE_STEP=bitmap",
    "PHASE1_FIND_BIT_NEXT_SAFE_STEP=find_bit",
    "PHASE1_RBTREE_NEXT_SAFE_STEP=rbtree",
    "PHASE1_STRING_NEXT_SAFE_STEP=string",
};

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectContainsOnce(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expectEqual(@as(usize, 1), std.mem.count(u8, haystack, needle));
}

test "direct-owner checker keeps the Phase 1 helper lane split explicit" {
    try expectContains(checker, "check-phase1-direct-owner-markers.py");
    try expectContains(checker, "zigux/tests/fixtures/phase1_helper_manifest.json");
    try expectContains(checker, "Documentation/zigux/phase1-host-helper-lane-sequencing.md");

    try expectContains(manifest, "\"helper_count\": 13");
    try expectContains(manifest, "\"shared_replay_parked_helpers\"");
    try expectContains(manifest, "\"direct_anchor_followup_helpers\"");
    try expectContains(manifest, "Phase 1 helper follow-up stays parked on shared replay for the nine helpers above");
    try expectContains(manifest, "Do not reopen Phase 1 by batching helpers across those two sets in one lane");

    for (shared_replay_helpers) |helper| {
        try expectContains(manifest, helper);
        try expectContains(lane_note, helper);
    }
    for (direct_anchor_helpers) |helper| {
        try expectContains(manifest, helper);
        try expectContains(lane_note, helper);
    }
}

test "direct-owner checker and lane note retain one marker per direct helper" {
    try expectContains(lane_note, "These four helper-specific owner markers are now exact-checked");
    try expectContains(lane_note, "scripts/zigux/check-phase1-direct-owner-markers.py");

    for (direct_owner_prefixes) |prefix| {
        try expectContainsOnce(checker, prefix);
        try expectContainsOnce(lane_note, prefix);
    }
}

test "helper-specific next-step markers remain the owner-map tie breakers" {
    try expectContains(lane_note, "Start from `zigux/tests/fixtures/phase1_helper_manifest.json` and pick one helper family only.");
    try expectContains(lane_note, "If the helper sits in the shared-replay parked set");
    try expectContains(lane_note, "If the helper sits in the direct-anchor set");

    for (next_safe_step_prefixes) |prefix| {
        try expectContainsOnce(checker, prefix);
        try expectContainsOnce(lane_note, prefix);
    }
}

test "direct-anchor helper families keep distinct review vocabulary" {
    try expectContains(manifest, "copy_raw_alias_anchor");
    try expectContains(manifest, "same_word_start_masks");
    try expectContains(manifest, "cached_root");
    try expectContains(manifest, "sysfsStreq");

    try expectContains(checker, "bitmap");
    try expectContains(checker, "find_bit");
    try expectContains(checker, "rbtree");
    try expectContains(checker, "string");
}
