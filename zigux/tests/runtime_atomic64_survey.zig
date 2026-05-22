const std = @import("std");

const SurveySummary = struct {
    atomic64_test_c_lines: usize,
    preexisting_runtime_test_files: usize,
    preexisting_samples_zigux_present: bool,
    preexisting_phase9_build_present: bool,
    preexisting_phase9_doc_present: bool,
};

const RoadmapGapSummary = struct {
    roadmap_phase_goal: []const u8,
    landed_pilot_state: []const u8,
    missing_capability: []const u8,
    blocked_deliverable: []const u8,
    next_gate: []const u8,
};

const DeliveryEvidence = struct {
    id: []const u8,
    kind: []const u8,
    path: []const u8,
    why_now: []const u8,
};

const OwnershipEntry = struct {
    surface: []const u8,
    role: []const u8,
    owner: []const u8,
    boundary: []const u8,
};

const Gap = struct {
    id: []const u8,
    status: []const u8,
    kind: []const u8,
    zigux_destination: []const u8,
    why_now: []const u8,
};

const Manifest = struct {
    lane_key: []const u8,
    phase: []const u8,
    surveyed_commit: []const u8,
    anchor: []const u8,
    roadmap_destinations: []const []const u8,
    survey_summary: SurveySummary,
    roadmap_gap_summary: RoadmapGapSummary,
    delivery_evidence_catalog: []const DeliveryEvidence,
    ownership_map: []const OwnershipEntry,
    gaps: []const Gap,
};

fn isAllowedStatus(status: []const u8) bool {
    return std.mem.eql(u8, status, "starter_landed") or
        std.mem.eql(u8, status, "ready_next") or
        std.mem.eql(u8, status, "blocked_on_runtime_substrate") or
        std.mem.eql(u8, status, "visible_review_only_packet");
}

fn findGap(gaps: []const Gap, id: []const u8) ?Gap {
    for (gaps) |gap| {
        if (std.mem.eql(u8, gap.id, id)) return gap;
    }
    return null;
}

fn hasEvidence(entries: []const DeliveryEvidence, id: []const u8, path: []const u8) bool {
    for (entries) |entry| {
        if (std.mem.eql(u8, entry.id, id) and std.mem.eql(u8, entry.path, path)) return true;
    }
    return false;
}

fn hasOwnership(entries: []const OwnershipEntry, surface: []const u8, owner: []const u8) bool {
    for (entries) |entry| {
        if (std.mem.eql(u8, entry.surface, surface) and std.mem.eql(u8, entry.owner, owner)) {
            return true;
        }
    }
    return false;
}

test "phase 9 runtime atomic64 survey manifest records the visible shared-loader reminder packet" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const manifest_json = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/runtime_atomic64_manifest.json",
        std.testing.allocator,
        .limited(64 * 1024),
    );
    defer std.testing.allocator.free(manifest_json);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();

    const manifest = parsed.value;
    try std.testing.expectEqualStrings("P9-L04", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 9", manifest.phase);
    try std.testing.expectEqualStrings("lib/atomic64_test.c", manifest.anchor);
    try std.testing.expectEqual(@as(usize, 2), manifest.roadmap_destinations.len);
    try std.testing.expect(manifest.survey_summary.atomic64_test_c_lines >= 200);
    try std.testing.expectEqual(@as(usize, 3), manifest.survey_summary.preexisting_runtime_test_files);
    try std.testing.expect(manifest.survey_summary.preexisting_samples_zigux_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase9_build_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase9_doc_present);

    try std.testing.expectEqualStrings(
        "starter_landed_with_visible_shared_loader_packet",
        manifest.roadmap_gap_summary.landed_pilot_state,
    );
    try std.testing.expect(std.mem.indexOf(u8, manifest.roadmap_gap_summary.missing_capability, "runtime substrate") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest.roadmap_gap_summary.next_gate, "review-only evidence") != null);

    try std.testing.expect(manifest.delivery_evidence_catalog.len >= 8);
    try std.testing.expect(hasEvidence(
        manifest.delivery_evidence_catalog,
        "runtime-atomic64-sample",
        "samples/zigux/runtime_atomic64.zig",
    ));
    try std.testing.expect(hasEvidence(
        manifest.delivery_evidence_catalog,
        "runtime-atomic64-phase9-build",
        "zigux/tests/phase9_build.zig",
    ));
    try std.testing.expect(hasEvidence(
        manifest.delivery_evidence_catalog,
        "runtime-atomic64-survey-note",
        "Documentation/zigux/phase9-runtime-atomic64-survey.md",
    ));
    try std.testing.expect(hasEvidence(
        manifest.delivery_evidence_catalog,
        "runtime-atomic64-module-slice-note",
        "Documentation/zigux/phase9-runtime-atomic64-module-slice.md",
    ));

    try std.testing.expect(manifest.ownership_map.len >= 4);
    try std.testing.expect(hasOwnership(
        manifest.ownership_map,
        "zigux/tests/runtime_atomic64_manifest.json",
        "P9-L04",
    ));
    try std.testing.expect(hasOwnership(
        manifest.ownership_map,
        "zigux/tests/phase9_build.zig",
        "P9-L11",
    ));

    for (manifest.gaps, 0..) |gap, i| {
        try std.testing.expect(gap.id.len > 0);
        try std.testing.expect(gap.kind.len > 0);
        try std.testing.expect(gap.why_now.len > 0);
        try std.testing.expect(isAllowedStatus(gap.status));

        for (manifest.gaps[i + 1 ..]) |other| {
            try std.testing.expect(!std.mem.eql(u8, gap.id, other.id));
        }
    }

    const build_gap = findGap(manifest.gaps, "phase9-build-gate") orelse return error.MissingBuildGap;
    try std.testing.expectEqualStrings("visible_review_only_packet", build_gap.status);
    try std.testing.expectEqualStrings("zigux/tests/phase9_build.zig", build_gap.zigux_destination);

    const survey_gap = findGap(manifest.gaps, "runtime-atomic64-survey-gate") orelse return error.MissingSurveyGap;
    try std.testing.expectEqualStrings("starter_landed", survey_gap.status);

    const blocked_gap = findGap(manifest.gaps, "runtime-atomic64-live-loader-binding") orelse return error.MissingBlockedGap;
    try std.testing.expectEqualStrings("blocked_on_runtime_substrate", blocked_gap.status);
    try std.testing.expectEqualStrings("zigux/kernel/runtime_loader.zig", blocked_gap.zigux_destination);
}
