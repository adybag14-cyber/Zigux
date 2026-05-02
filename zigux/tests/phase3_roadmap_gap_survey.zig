const std = @import("std");

const DeliveryEvidence = struct {
    kind: []const u8,
    path: []const u8,
};

const Gap = struct {
    id: []const u8,
    status: []const u8,
    kind: []const u8,
    path: []const u8,
    why_now: []const u8,
};

const Manifest = struct {
    lane_key: []const u8,
    roadmap_phase: []const u8,
    surveyed_commit: []const u8,
    roadmap_anchors: []const []const u8,
    current_boundary_surfaces: []const []const u8,
    current_interop_families: []const []const u8,
    rbtree_evidence: []const []const u8,
    current_interop_gap: []const u8,
    current_rbtree_status: []const u8,
    next_bounded_step: []const u8,
    adjacent_growth_marker: []const u8,
    delivery_evidence: []const DeliveryEvidence,
    gaps: []const Gap,
};

fn isLowerHexSha(value: []const u8) bool {
    if (value.len != 40) return false;
    for (value) |byte| {
        if (!std.ascii.isHex(byte) or std.ascii.isUpper(byte)) return false;
    }
    return true;
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

test "phase3 roadmap gap manifest records the narrowed rbtree gap" {
    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, @embedFile("phase3_roadmap_gap_manifest.json"), .{});
    defer parsed.deinit();

    const manifest = parsed.value;
    try std.testing.expectEqualStrings("P3-L02", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 3", manifest.roadmap_phase);
    try std.testing.expect(isLowerHexSha(manifest.surveyed_commit));
    try std.testing.expectEqual(@as(usize, 4), manifest.roadmap_anchors.len);
    try std.testing.expectEqual(@as(usize, 4), manifest.current_boundary_surfaces.len);
    try std.testing.expectEqual(@as(usize, 12), manifest.current_interop_families.len);
    try std.testing.expectEqual(@as(usize, 12), manifest.rbtree_evidence.len);
    try std.testing.expectEqual(@as(usize, 7), manifest.delivery_evidence.len);
    try std.testing.expectEqual(@as(usize, 3), manifest.gaps.len);

    try std.testing.expectEqualStrings("rbtree", manifest.current_interop_families[4]);
    try std.testing.expectEqualStrings("curated-rbtree-c-binding-surface-still-missing", manifest.current_interop_gap);
    try std.testing.expectEqualStrings("phase3-helper-packet-exists-but-curated-c-binding-surface-is-still-missing", manifest.current_rbtree_status);
    try std.testing.expectEqualStrings("curated-rbtree-boundary-header-and-parity-fixture-before-more-chrdev-growth", manifest.next_bounded_step);

    try std.testing.expectEqualStrings("Documentation/zigux/phase3-rbtree-slice.md", manifest.rbtree_evidence[1]);
    try std.testing.expectEqualStrings("zigux/helpers/rbtree_view.zig", manifest.rbtree_evidence[6]);
    try std.testing.expectEqualStrings("zigux/tests/phase3_rbtree_survey.zig", manifest.rbtree_evidence[7]);
    try std.testing.expectEqualStrings("zigux/tests/phase3_rbtree_manifest.json", manifest.rbtree_evidence[8]);

    try std.testing.expectEqualStrings("phase3-rbtree-boundary-record", manifest.gaps[0].id);
    try std.testing.expectEqualStrings("helper_landed_binding_followup_pending", manifest.gaps[0].status);
    try std.testing.expectEqualStrings("include/zigux/abi.h", manifest.gaps[0].path);
    try expectContains(manifest.gaps[0].why_now, "no curated ABI record");
}

test "phase3 roadmap gap survey note and rbtree helper packet stay aligned" {
    const roadmap_gap = @embedFile("../../Documentation/zigux/phase3-roadmap-gap-survey.md");
    const interop_note = @embedFile("../../Documentation/zigux/phase3-rbtree-interop-survey.md");
    const slice_note = @embedFile("../../Documentation/zigux/phase3-rbtree-slice.md");
    const helper = @embedFile("../helpers/rbtree_view.zig");
    const helper_manifest = @embedFile("phase3_rbtree_manifest.json");

    try expectContains(roadmap_gap, "PHASE3_CURRENT_RBTREE_STATUS=phase3-helper-packet-exists-but-curated-c-binding-surface-is-still-missing");
    try expectContains(roadmap_gap, "PHASE3_INTEROP_GAP=curated-rbtree-c-binding-surface-still-missing");
    try expectContains(roadmap_gap, "PHASE3_NEXT_BOUNDED_STEP=curated-rbtree-boundary-header-and-parity-fixture-before-more-chrdev-growth");

    try expectContains(interop_note, "PHASE3_RBTREE_PHASE3_HELPER=zigux/helpers/rbtree_view.zig");
    try expectContains(interop_note, "PHASE3_RBTREE_PHASE3_BOUNDARY=helper-landed-curated-c-binding-surface-still-missing");
    try expectContains(interop_note, "PHASE3_RBTREE_NEXT_BOUNDED_STEP=one-curated-phase3-rbtree-boundary-record");

    try expectContains(slice_note, "PHASE3_SLICE=rbtree-helper-interop");
    try expectContains(slice_note, "`zig test zigux/helpers/rbtree_view.zig`");
    try expectContains(slice_note, "`zig test zigux/tests/phase3_rbtree_survey.zig`");

    try expectContains(helper, "pub fn summarize");
    try expectContains(helper, "TRUNCATED_FLAG");
    try expectContains(helper_manifest, "\"helper_landed_binding_followup_pending\"");
}

test "phase3 roadmap gap survey gate points at the refreshed python validator" {
    const validator = @embedFile("../../scripts/zigux/validate-phase3-roadmap-gap-survey.py");
    try expectContains(validator, "PHASE3_CURRENT_RBTREE_STATUS=phase3-helper-packet-exists-but-curated-c-binding-surface-is-still-missing");
    try expectContains(validator, "PHASE3_INTEROP_GAP=curated-rbtree-c-binding-surface-still-missing");
    try expectContains(validator, "zigux/helpers/rbtree_view.zig");
    try expectContains(validator, "Documentation/zigux/phase3-rbtree-slice.md");
    try expectContains(validator, "zigux/tests/phase3_rbtree_survey.zig");
    try expectContains(validator, "zigux/tests/phase3_rbtree_manifest.json");
}
