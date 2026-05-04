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

test "phase3 rbtree survey records the landed dedicated boundary packet and narrowed shared gap" {
    const allocator = std.testing.allocator;
    const manifest_json = @embedFile("phase3_rbtree_manifest.json");
    const slice_note = @embedFile("../../Documentation/zigux/phase3-rbtree-slice.md");
    const interop_survey = @embedFile("../../Documentation/zigux/phase3-rbtree-interop-survey.md");
    const helper = @embedFile("../helpers/rbtree_view.zig");
    const root_view_helper = @embedFile("../helpers/rbtree_root_view.zig");
    const roadmap_gap = @embedFile("../../Documentation/zigux/phase3-roadmap-gap-survey.md");

    const parsed = try std.json.parseFromSlice(Manifest, allocator, manifest_json, .{});
    defer parsed.deinit();

    const manifest = parsed.value;
    try std.testing.expectEqualStrings("P3-Y01", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 3", manifest.phase);
    try std.testing.expectEqualStrings("lib/rbtree.c", manifest.anchor);
    try std.testing.expectEqualStrings("dedicated_boundary_landed_shared_abi_followup_pending", manifest.status);
    try std.testing.expectEqualStrings("zigux/helpers/rbtree_view.zig", manifest.roadmap_destination);
    try std.testing.expectEqualStrings("shared-phase3-abi-rbtree-root-view-lift-still-missing", manifest.remaining_gap);
    try std.testing.expectEqual(@as(usize, 13), manifest.file_count);
    try std.testing.expectEqual(@as(usize, 13), manifest.files.len);

    try expectContains(manifest_json, "include/zigux/rbtree.h");
    try expectContains(manifest_json, "zigux/bindings/rbtree.zig");
    try expectContains(manifest_json, "zigux/helpers/rbtree_root_view.zig");
    try expectContains(manifest_json, "Documentation/zigux/phase3-rbtree-interop-survey.md");
    try expectContains(manifest_json, "zigux/tests/phase3_rbtree_shared_contract.zig");
    try expectContains(manifest_json, "zigux/tests/fixtures/phase3_rbtree/expected.json");
    try expectContains(manifest_json, "zigux/tests/fixtures/phase3_rbtree/phase3_rbtree_c_harness.c");

    try expectContains(helper, "pub fn summarize");
    try expectContains(helper, "pub fn countBounded");
    try expectContains(helper, "TRUNCATED_FLAG");
    try expectContains(helper, "ROOT_BLACK_FLAG");

    try expectContains(root_view_helper, "pub const KNOWN_FLAG_MASK");
    try expectContains(root_view_helper, "pub fn canonicalize");
    try expectContains(root_view_helper, "pub fn cached");
    try expectContains(root_view_helper, "rbtree.ROOT_FLAG_LEFTMOST_VALID");

    try expectContains(slice_note, "PHASE3_SLICE=rbtree-helper-interop");
    try expectContains(slice_note, "`zig test zigux/helpers/rbtree_view.zig`");
    try expectContains(slice_note, "`zig test zigux/helpers/rbtree_root_view.zig`");
    try expectContains(slice_note, "`zig test zigux/tests/phase3_rbtree_survey.zig`");
    try expectContains(slice_note, "`zig test zigux/tests/phase3_rbtree_root_view_survey.zig`");
    try expectContains(slice_note, "PHASE3_VALIDATE_GATE=python3 scripts/zigux/validate-phase3.py");
    try expectContains(slice_note, "PHASE3_TEST_GATE=zig build phase3-test --build-file zigux/tests/build.zig");
    try expectContains(slice_note, "PHASE3_INTEROP_GATE=python3 scripts/zigux/run-phase3-checks.py --slug rbtree");
    try expectContains(slice_note, "dedicated `rbtree` boundary packet");
    try expectContains(slice_note, "reusable root-view helper around the dedicated Phase 3 binding packet");

    try expectContains(interop_survey, "the shared Phase 3 ABI manifest now explicitly catalogs the dedicated `rbtree` boundary header, binding, dump, survey, and parity fixture files");
    try expectContains(interop_survey, "include/zigux/rbtree.h");
    try expectContains(interop_survey, "zigux/bindings/rbtree.zig");
    try expectContains(interop_survey, "zigux/tests/phase3_rbtree_dump.zig");
    try expectContains(interop_survey, "zigux/tests/phase3_rbtree_shared_contract.zig");
    try expectContains(interop_survey, "zigux/tests/phase3_rbtree_manifest.json");

    try expectContains(roadmap_gap, "PHASE3_CURRENT_RBTREE_STATUS=phase3-dedicated-rbtree-boundary-exists-shared-abi-lift-still-missing");
    try expectContains(roadmap_gap, "PHASE3_INTEROP_GAP=shared-phase3-abi-rbtree-lift-still-missing");
}
