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

fn readWorkspaceFile(
    io: anytype,
    allocator: std.mem.Allocator,
    path: []const u8,
    limit: usize,
) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(io, path, allocator, .limited(limit));
}

fn expectContainsAll(haystack: []const u8, needles: []const []const u8) !void {
    for (needles) |needle| {
        try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
    }
}

test "phase3 roadmap gap manifest keeps the current interop gap explicit" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const manifest_json = try readWorkspaceFile(
        io_instance.io(),
        std.testing.allocator,
        "zigux/tests/phase3_roadmap_gap_manifest.json",
        24 * 1024,
    );
    defer std.testing.allocator.free(manifest_json);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{
        .ignore_unknown_fields = true,
    });
    defer parsed.deinit();

    const manifest = parsed.value;
    try std.testing.expectEqualStrings("P3-L01", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 3", manifest.roadmap_phase);
    try std.testing.expect(isLowerHexSha(manifest.surveyed_commit));
    try std.testing.expectEqual(@as(usize, 4), manifest.roadmap_anchors.len);
    try std.testing.expectEqual(@as(usize, 4), manifest.current_boundary_surfaces.len);
    try std.testing.expectEqual(@as(usize, 11), manifest.current_interop_families.len);
    try std.testing.expectEqual(@as(usize, 8), manifest.rbtree_evidence.len);
    try std.testing.expectEqual(@as(usize, 5), manifest.delivery_evidence.len);
    try std.testing.expectEqual(@as(usize, 3), manifest.gaps.len);

    try std.testing.expectEqualStrings("rust/exports.c", manifest.roadmap_anchors[0]);
    try std.testing.expectEqualStrings("lib/rbtree.c", manifest.roadmap_anchors[2]);
    try std.testing.expectEqualStrings("zigux/kernel/export_shim.zig", manifest.current_boundary_surfaces[2]);
    try std.testing.expectEqualStrings("bitmap", manifest.current_interop_families[0]);
    try std.testing.expectEqualStrings("chrdev", manifest.current_interop_families[10]);
    try std.testing.expectEqualStrings("Documentation/zigux/phase3-rbtree-interop-survey.md", manifest.rbtree_evidence[0]);
    try std.testing.expectEqualStrings("zigux/tests/phase7_rbtree_manifest.json", manifest.rbtree_evidence[7]);
    try std.testing.expectEqualStrings("rbtree-interop-slice-still-missing", manifest.current_interop_gap);
    try std.testing.expectEqualStrings("phase3-survey-exists-but-phase3-interop-slice-is-missing", manifest.current_rbtree_status);
    try std.testing.expectEqualStrings("small-phase3-rbtree-interop-slice-before-more-chrdev-growth", manifest.next_bounded_step);
    try std.testing.expectEqualStrings("chrdev-plan-growth-exceeds-roadmap-anchors", manifest.adjacent_growth_marker);

    try std.testing.expectEqualStrings("documentation", manifest.delivery_evidence[0].kind);
    try std.testing.expectEqualStrings("Documentation/zigux/phase3-roadmap-gap-survey.md", manifest.delivery_evidence[0].path);
    try std.testing.expectEqualStrings("validation", manifest.delivery_evidence[2].kind);
    try std.testing.expectEqualStrings("scripts/zigux/validate-phase3-roadmap-gap-survey.py", manifest.delivery_evidence[2].path);
    try std.testing.expectEqualStrings("manifest", manifest.delivery_evidence[3].kind);
    try std.testing.expectEqualStrings("zigux/tests/phase3_roadmap_gap_manifest.json", manifest.delivery_evidence[3].path);
    try std.testing.expectEqualStrings("validation", manifest.delivery_evidence[4].kind);
    try std.testing.expectEqualStrings("zigux/tests/phase3_roadmap_gap_survey.zig", manifest.delivery_evidence[4].path);

    try std.testing.expectEqualStrings("phase3-rbtree-boundary-slice", manifest.gaps[0].id);
    try std.testing.expectEqualStrings("missing", manifest.gaps[0].status);
    try std.testing.expectEqualStrings("roadmap_anchor", manifest.gaps[0].kind);
    try std.testing.expectEqualStrings("lib/rbtree.c", manifest.gaps[0].path);
    try std.testing.expect(std.mem.indexOf(u8, manifest.gaps[0].why_now, "Phase 3 helper, dump, fixture, or slice note") != null);
    try std.testing.expectEqualStrings("phase3-uapi-breadth", manifest.gaps[1].id);
    try std.testing.expectEqualStrings("deferred", manifest.gaps[1].status);
    try std.testing.expectEqualStrings("boundary_scope", manifest.gaps[1].kind);
    try std.testing.expectEqualStrings("zigux/uapi/version.zig", manifest.gaps[1].path);
    try std.testing.expect(std.mem.indexOf(u8, manifest.gaps[1].why_now, "broader curated UAPI shim family") != null);
    try std.testing.expectEqualStrings("chrdev-growth-not-roadmap-closure", manifest.gaps[2].id);
    try std.testing.expectEqualStrings("adjacent_only", manifest.gaps[2].status);
    try std.testing.expectEqualStrings("review_boundary", manifest.gaps[2].kind);
    try std.testing.expectEqualStrings("zigux/helpers/chrdev_open_plan.zig", manifest.gaps[2].path);
    try std.testing.expect(std.mem.indexOf(u8, manifest.gaps[2].why_now, "adjacent exploratory growth") != null);
}

test "phase3 roadmap gap survey note and dedicated rbtree note stay aligned" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const survey_note = try readWorkspaceFile(
        io_instance.io(),
        std.testing.allocator,
        "Documentation/zigux/phase3-roadmap-gap-survey.md",
        24 * 1024,
    );
    defer std.testing.allocator.free(survey_note);

    const rbtree_note = try readWorkspaceFile(
        io_instance.io(),
        std.testing.allocator,
        "Documentation/zigux/phase3-rbtree-interop-survey.md",
        16 * 1024,
    );
    defer std.testing.allocator.free(rbtree_note);

    try expectContainsAll(survey_note, &.{
        "PHASE3_CURRENT_RBTREE_STATUS=phase3-survey-exists-but-phase3-interop-slice-is-missing",
        "PHASE3_INTEROP_GAP=rbtree-interop-slice-still-missing",
        "PHASE3_NEXT_BOUNDED_STEP=small-phase3-rbtree-interop-slice-before-more-chrdev-growth",
        "PHASE3_SURVEY_MANIFEST=zigux/tests/phase3_roadmap_gap_manifest.json",
        "PHASE3_SURVEY_GATE=zig test zigux/tests/phase3_roadmap_gap_survey.zig",
        "The largest roadmap-backed interop gap is still `lib/rbtree.c`.",
        "zigux/tests/phase3_roadmap_gap_manifest.json",
        "zig test zigux/tests/phase3_roadmap_gap_survey.zig",
        "Documentation/zigux/phase3-rbtree-interop-survey.md",
        "scripts/zigux/validate-phase3-roadmap-gap-survey.py",
        "chrdev_* planning ladder",
    });
    try expectContainsAll(rbtree_note, &.{
        "PHASE3_RBTREE_PHASE3_BOUNDARY=missing-helper-dump-fixture-and-slice",
        "PHASE3_RBTREE_NEXT_BOUNDED_STEP=one-curated-phase3-rbtree-view-slice",
        "no `zigux/helpers/rbtree*.zig` boundary-facing helper family",
        "no `zigux/tests/phase3_rbtree*.zig` dump, fixture, or parity packet",
    });
}

test "phase3 roadmap gap survey gate stays aligned with the dedicated python validator" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const validator = try readWorkspaceFile(
        io_instance.io(),
        std.testing.allocator,
        "scripts/zigux/validate-phase3-roadmap-gap-survey.py",
        24 * 1024,
    );
    defer std.testing.allocator.free(validator);

    try expectContainsAll(validator, &.{
        'MANIFEST_REL = "zigux/tests/phase3_roadmap_gap_manifest.json"',
        'SURVEY_GATE_REL = "zigux/tests/phase3_roadmap_gap_survey.zig"',
        '"PHASE3_SURVEY_MANIFEST=zigux/tests/phase3_roadmap_gap_manifest.json"',
        '"PHASE3_SURVEY_GATE=zig test zigux/tests/phase3_roadmap_gap_survey.zig"',
        '"PHASE3_CURRENT_RBTREE_VALIDATOR=scripts/zigux/validate-phase3-rbtree-interop-survey.py"',
        '"missing_manifest_snippet:"',
        '"missing_survey_gate_snippet:"',
        '"phase3-rbtree-boundary-slice"',
        '"chrdev-growth-not-roadmap-closure"',
    });
}
