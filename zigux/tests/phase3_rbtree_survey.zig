const std = @import("std");

const Manifest = struct {
    lane_key: []const u8,
    phase: []const u8,
    anchor: []const u8,
    status: []const u8,
    roadmap_destination: []const u8,
    remaining_gap: []const u8,
    file_count: usize,
    files: []const []const u8,
};

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

test "phase3 rbtree survey records the landed helper packet and narrowed remaining gap" {
    const allocator = std.testing.allocator;
    const manifest_json = @embedFile("phase3_rbtree_manifest.json");
    const slice_note = @embedFile("../../Documentation/zigux/phase3-rbtree-slice.md");
    const helper = @embedFile("../helpers/rbtree_view.zig");
    const roadmap_gap = @embedFile("../../Documentation/zigux/phase3-roadmap-gap-survey.md");

    const parsed = try std.json.parseFromSlice(Manifest, allocator, manifest_json, .{});
    defer parsed.deinit();

    const manifest = parsed.value;
    try std.testing.expectEqualStrings("P3-L02", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 3", manifest.phase);
    try std.testing.expectEqualStrings("lib/rbtree.c", manifest.anchor);
    try std.testing.expectEqualStrings("helper_landed_binding_followup_pending", manifest.status);
    try std.testing.expectEqualStrings("zigux/helpers/rbtree_view.zig", manifest.roadmap_destination);
    try std.testing.expectEqualStrings("curated-rbtree-c-binding-surface-still-missing", manifest.remaining_gap);
    try std.testing.expectEqual(@as(usize, 4), manifest.file_count);
    try std.testing.expectEqual(@as(usize, 4), manifest.files.len);

    try expectContains(helper, "pub fn summarize");
    try expectContains(helper, "pub fn countBounded");
    try expectContains(helper, "TRUNCATED_FLAG");
    try expectContains(helper, "ROOT_BLACK_FLAG");

    try expectContains(slice_note, "PHASE3_SLICE=rbtree-helper-interop");
    try expectContains(slice_note, "`zig test zigux/helpers/rbtree_view.zig`");
    try expectContains(slice_note, "`zig test zigux/tests/phase3_rbtree_survey.zig`");
    try expectContains(slice_note, "curated C header and binding surface");

    try expectContains(roadmap_gap, "PHASE3_CURRENT_RBTREE_STATUS=phase3-helper-packet-exists-but-curated-c-binding-surface-is-still-missing");
    try expectContains(roadmap_gap, "PHASE3_INTEROP_GAP=curated-rbtree-c-binding-surface-still-missing");
}
