const std = @import("std");
const devres = @import("devres");

const SurveySummary = struct {
    preexisting_phase13_build_present: bool,
    preexisting_phase13_make_target_present: bool,
    preexisting_devres_zig_present: bool,
    preexisting_phase13_devres_test_present: bool,
    preexisting_phase13_devres_slice_present: bool,
    preexisting_phase13_devres_reviewability_present: bool,
    preexisting_phase13_devres_survey_present: bool,
    preexisting_phase13_devres_dma_coherent_present: bool,
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
    gaps: []const Gap,
};

fn isAllowedStatus(status: []const u8) bool {
    return std.mem.eql(u8, status, "starter_landed") or
        std.mem.eql(u8, status, "blocked_on_missing_shared_build_surface") or
        std.mem.eql(u8, status, "blocked_on_missing_direct_devres_test_surface") or
        std.mem.eql(u8, status, "blocked_on_missing_reviewability_surface") or
        std.mem.eql(u8, status, "blocked_on_dma_state") or
        std.mem.eql(u8, status, "blocked_on_scatterlist_state");
}

test "phase13 devres reviewability packet stays aligned with the current narrow boundary packet" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const manifest_json = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase13_devres_manifest.json",
        std.testing.allocator,
        .limited(16 * 1024),
    );
    defer std.testing.allocator.free(manifest_json);

    const slice_note = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase13-devres-slice.md",
        std.testing.allocator,
        .limited(16 * 1024),
    );
    defer std.testing.allocator.free(slice_note);

    const survey_note = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase13-devres-survey.md",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(survey_note);

    const helper_source = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "lib/devres.zig",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(helper_source);

    const direct_replay = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase13_devres.zig",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(direct_replay);

    const dma_boundary_replay = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase13_devres_dma_coherent.zig",
        std.testing.allocator,
        .limited(16 * 1024),
    );
    defer std.testing.allocator.free(dma_boundary_replay);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{
        .ignore_unknown_fields = true,
    });
    defer parsed.deinit();

    const manifest = parsed.value;
    try std.testing.expectEqualStrings("P13-L08", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 13", manifest.phase);
    try std.testing.expectEqualStrings("master-readback-2026-05-11", manifest.surveyed_commit);
    try std.testing.expectEqualStrings("lib/devres.c", manifest.anchor);
    try std.testing.expectEqual(@as(usize, 3), manifest.roadmap_destinations.len);

    try std.testing.expect(!manifest.survey_summary.preexisting_phase13_build_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase13_make_target_present);
    try std.testing.expect(manifest.survey_summary.preexisting_devres_zig_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase13_devres_slice_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase13_devres_survey_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase13_devres_dma_coherent_present);

    const descriptor = devres.DevresHelperLab.descriptor();
    try std.testing.expectEqualStrings("lib/devres.c", descriptor.anchor);
    try std.testing.expect(descriptor.provides_ioremap_lifetime_planning);
    try std.testing.expect(descriptor.provides_ioremap_wc_wrapper_planning);
    try std.testing.expect(descriptor.provides_release_pointer_match);
    try std.testing.expect(descriptor.provides_iounmap_call_planning);
    try std.testing.expect(descriptor.provides_ioremap_resource_planning);
    try std.testing.expect(descriptor.provides_of_iomap_planning);
    try std.testing.expect(descriptor.provides_pretty_name_helper);
    try std.testing.expect(descriptor.provides_arch_io_wc_memtype_planning);
    try std.testing.expect(descriptor.provides_arch_phys_wc_token_planning);
    try std.testing.expect(!descriptor.touches_live_device_lists);
    try std.testing.expect(!descriptor.touches_live_mmio);
    try std.testing.expect(!descriptor.touches_live_arch_memtype);

    try std.testing.expect(std.mem.indexOf(u8, helper_source, "pub const ManagedIounmapPlan") != null);
    try std.testing.expect(std.mem.indexOf(u8, helper_source, "pub fn planManagedIounmap(") != null);
    try std.testing.expect(std.mem.indexOf(u8, helper_source, ".warns_on_release_miss = !release_matches") != null);
    try std.testing.expect(std.mem.indexOf(u8, slice_note, "devm_iounmap()") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "devm_iounmap()") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "helper-only DMA/scatterlist boundary") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "P13-L08") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "master-readback-2026-05-11") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "zigux/tests/phase13_devres_reviewability.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, direct_replay, "\"lane_key\": \"P13-L08\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, direct_replay, "\"surveyed_commit\": \"master-readback-2026-05-11\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, direct_replay, "\"id\": \"phase13-devres-reviewability-gate\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, dma_boundary_replay, "\"preexisting_phase13_build_present\": false") != null);
    try std.testing.expect(std.mem.indexOf(u8, dma_boundary_replay, "\"id\": \"phase13-devres-dma-coherent-replay\"") != null);

    var starter_landed_count: usize = 0;
    var blocked_count: usize = 0;
    var saw_build_gate = false;
    var saw_direct_test_gate = false;
    var saw_reviewability_gate = false;
    var saw_dma_boundary_gate = false;
    var saw_dma_boundary = false;
    var saw_scatterlist_boundary = false;

    for (manifest.gaps, 0..) |gap, i| {
        try std.testing.expect(gap.id.len > 0);
        try std.testing.expect(gap.kind.len > 0);
        try std.testing.expect(gap.why_now.len > 0);
        try std.testing.expect(isAllowedStatus(gap.status));

        if (std.mem.eql(u8, gap.status, "starter_landed")) {
            starter_landed_count += 1;
        } else {
            blocked_count += 1;
        }

        if (std.mem.eql(u8, gap.id, "phase13-build-gate")) {
            saw_build_gate = true;
            try std.testing.expectEqualStrings("blocked_on_missing_shared_build_surface", gap.status);
            try std.testing.expectEqualStrings("zigux/tests/phase13_build.zig", gap.zigux_destination);
        }
        if (std.mem.eql(u8, gap.id, "phase13-devres-test-gate")) {
            saw_direct_test_gate = true;
            try std.testing.expectEqualStrings("blocked_on_missing_direct_devres_test_surface", gap.status);
            try std.testing.expectEqualStrings("zigux/tests/phase13_devres.zig", gap.zigux_destination);
        }
        if (std.mem.eql(u8, gap.id, "phase13-devres-reviewability-gate")) {
            saw_reviewability_gate = true;
            try std.testing.expectEqualStrings("blocked_on_missing_reviewability_surface", gap.status);
            try std.testing.expectEqualStrings("zigux/tests/phase13_devres_reviewability.zig", gap.zigux_destination);
        }
        if (std.mem.eql(u8, gap.id, "phase13-devres-dma-coherent-replay")) {
            saw_dma_boundary_gate = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("zigux/tests/phase13_devres_dma_coherent.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "machine-checkable") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase13-devres-live-dma-backed-helpers")) {
            saw_dma_boundary = true;
            try std.testing.expectEqualStrings("blocked_on_dma_state", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "dmam_alloc_*") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "dma_map_sgtable()") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase13-devres-live-scatterlist-ownership")) {
            saw_scatterlist_boundary = true;
            try std.testing.expectEqualStrings("blocked_on_scatterlist_state", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "struct scatterlist") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "sg_table") != null);
        }

        for (manifest.gaps[i + 1 ..]) |other| {
            try std.testing.expect(!std.mem.eql(u8, gap.id, other.id));
        }
    }

    try std.testing.expectEqual(@as(usize, 1), starter_landed_count);
    try std.testing.expectEqual(@as(usize, 5), blocked_count);
    try std.testing.expect(saw_build_gate);
    try std.testing.expect(saw_direct_test_gate);
    try std.testing.expect(saw_reviewability_gate);
    try std.testing.expect(saw_dma_boundary_gate);
    try std.testing.expect(saw_dma_boundary);
    try std.testing.expect(saw_scatterlist_boundary);
}
