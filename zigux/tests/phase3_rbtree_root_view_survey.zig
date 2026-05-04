const std = @import("std");
const root_view = @import("rbtree_root_view");
const rbtree = @import("rbtree_bindings");

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

test "phase3 rbtree root view helper stays wired into the bounded survey packet" {
    const manifest_json = @embedFile("phase3_rbtree_manifest.json");
    const slice_note = @embedFile("../../Documentation/zigux/phase3-rbtree-slice.md");
    const interop_survey = @embedFile("../../Documentation/zigux/phase3-rbtree-interop-survey.md");
    const helper_text = @embedFile("../helpers/rbtree_root_view.zig");

    try expectContains(manifest_json, "zigux/helpers/rbtree_root_view.zig");
    try expectContains(manifest_json, "zigux/tests/phase3_rbtree_root_view_survey.zig");

    try expectContains(slice_note, "`zig test zigux/helpers/rbtree_root_view.zig`");
    try expectContains(slice_note, "`zig test zigux/tests/phase3_rbtree_root_view_survey.zig`");
    try expectContains(slice_note, "reusable root-view helper around the dedicated Phase 3 binding packet");

    try expectContains(interop_survey, "zigux/helpers/rbtree_root_view.zig");
    try expectContains(interop_survey, "zigux/tests/phase3_rbtree_root_view_survey.zig");

    try expectContains(helper_text, "pub const KNOWN_FLAG_MASK");
    try expectContains(helper_text, "pub fn empty()");
    try expectContains(helper_text, "pub fn uncached");
    try expectContains(helper_text, "pub fn cached");
    try expectContains(helper_text, "pub fn canonicalize");
    try expectContains(helper_text, "pub fn isCanonical");
}

test "phase3 rbtree root view helper keeps dedicated binding semantics explicit" {
    const empty_view = root_view.empty();
    try std.testing.expect(root_view.isCanonical(empty_view));
    try std.testing.expect(rbtree.isEmpty(empty_view));

    const uncached_view = root_view.uncached(0x2200);
    try std.testing.expect(root_view.isCanonical(uncached_view));
    try std.testing.expect(!rbtree.isCached(uncached_view));
    try std.testing.expect(!rbtree.hasLeftmost(uncached_view));

    const cached_view = root_view.cached(0x4400, 0x3300);
    try std.testing.expect(root_view.isCanonical(cached_view));
    try std.testing.expect(rbtree.isCached(cached_view));
    try std.testing.expect(rbtree.hasLeftmost(cached_view));

    const unknown_bits: rbtree.RootView = .{
        .root_addr = 0x4400,
        .leftmost_addr = 0,
        .flags = rbtree.ROOT_FLAG_CACHED | 8,
        .reserved = 0,
    };
    try std.testing.expectEqual(@as(?rbtree.RootView, null), root_view.canonicalize(unknown_bits));

    const cached_without_root: rbtree.RootView = .{
        .root_addr = 0,
        .leftmost_addr = 0x3300,
        .flags = rbtree.ROOT_FLAG_CACHED | rbtree.ROOT_FLAG_LEFTMOST_VALID,
        .reserved = 0,
    };
    try std.testing.expectEqual(@as(?rbtree.RootView, null), root_view.canonicalize(cached_without_root));

    const cached_without_leftmost: rbtree.RootView = .{
        .root_addr = 0x4400,
        .leftmost_addr = 0,
        .flags = rbtree.ROOT_FLAG_CACHED | rbtree.ROOT_FLAG_LEFTMOST_VALID,
        .reserved = 0,
    };
    try std.testing.expectEqual(@as(?rbtree.RootView, null), root_view.canonicalize(cached_without_leftmost));

    const rootless_uncached: rbtree.RootView = .{
        .root_addr = 0,
        .leftmost_addr = 0,
        .flags = 0,
        .reserved = 0,
    };
    try std.testing.expectEqual(@as(?rbtree.RootView, null), root_view.canonicalize(rootless_uncached));
}
