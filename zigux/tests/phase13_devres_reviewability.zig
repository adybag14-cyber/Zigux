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
        std.mem.eql(u8, status, "blocked_on_live_mmio_state") or
        std.mem.eql(u8, status, "blocked_on_live_device_tree_state") or
        std.mem.eql(u8, status, "blocked_on_live_arch_memtype_state");
}

fn expectGap(
    manifest: Manifest,
    id: []const u8,
    status: []const u8,
    destination: []const u8,
    why_marker: []const u8,
) !void {
    for (manifest.gaps) |gap| {
        if (!std.mem.eql(u8, gap.id, id)) continue;
        try std.testing.expectEqualStrings(status, gap.status);
        try std.testing.expectEqualStrings(destination, gap.zigux_destination);
        try std.testing.expect(std.mem.indexOf(u8, gap.why_now, why_marker) != null);
        return;
    }
    return error.MissingGap;
}

test "phase13 devres reviewability packet matches the current helper-local mmio survey packet" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const manifest_json = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase13_devres_manifest.json",
        std.testing.allocator,
        .limited(64 * 1024),
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

    const devres_source = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "lib/devres.zig",
        std.testing.allocator,
        .limited(40 * 1024),
    );
    defer std.testing.allocator.free(devres_source);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{
        .ignore_unknown_fields = true,
    });
    defer parsed.deinit();

    const manifest = parsed.value;
    try std.testing.expectEqualStrings("P13-L01", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 13", manifest.phase);
    try std.testing.expectEqualStrings("master-readback-2026-05-13", manifest.surveyed_commit);
    try std.testing.expectEqualStrings("lib/devres.c", manifest.anchor);
    try std.testing.expectEqual(@as(usize, 3), manifest.roadmap_destinations.len);
    try std.testing.expectEqualStrings("lib/devres.zig", manifest.roadmap_destinations[0]);
    try std.testing.expectEqualStrings("zigux/tests/", manifest.roadmap_destinations[1]);
    try std.testing.expectEqualStrings("Documentation/zigux/", manifest.roadmap_destinations[2]);
    try std.testing.expect(!manifest.survey_summary.preexisting_phase13_build_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase13_make_target_present);
    try std.testing.expect(manifest.survey_summary.preexisting_devres_zig_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase13_devres_test_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase13_devres_slice_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase13_devres_reviewability_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase13_devres_survey_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase13_devres_dma_coherent_present);
    try std.testing.expectEqual(@as(usize, 12), manifest.gaps.len);

    const descriptor = devres.DevresHelperLab.descriptor();
    try std.testing.expectEqualStrings("lib/devres.c", descriptor.anchor);
    try std.testing.expect(descriptor.provides_ioremap_lifetime_planning);
    try std.testing.expect(descriptor.provides_ioremap_uc_wrapper_planning);
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

    try std.testing.expect(std.mem.indexOf(u8, devres_source, ".provides_iounmap_call_planning = true") != null);
    try std.testing.expect(std.mem.indexOf(u8, devres_source, "pub const ManagedIounmapPlan") != null);
    try std.testing.expect(std.mem.indexOf(u8, devres_source, "pub fn planManagedIounmap(") != null);
    try std.testing.expect(std.mem.indexOf(u8, devres_source, ".warns_on_release_miss = !release_matches") != null);
    try std.testing.expect(std.mem.indexOf(u8, devres_source, "pub fn planManagedIoremapAcquireUc(") != null);
    try std.testing.expect(std.mem.indexOf(u8, devres_source, "pub fn planManagedIoremapAcquireWc(") != null);
    try std.testing.expect(std.mem.indexOf(u8, devres_source, "pub fn planArchPhysWcAdd(") != null);
    try std.testing.expect(std.mem.indexOf(u8, slice_note, "devm_iounmap()") != null);
    try std.testing.expect(std.mem.indexOf(u8, slice_note, "devm_arch_phys_wc_add()") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "master-readback-2026-05-13") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "`P13-L01`") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "devm_iounmap()") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "devm_ioremap_uc()") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "devm_ioremap_wc()") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "devm_arch_phys_wc_add()") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "zigux/tests/phase13_devres_dma_coherent.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "older `scripts/zigux/check-phase13-devres-packet.py` wording should be treated as stale packet drift") != null);

    var starter_landed_count: usize = 0;
    var blocked_count: usize = 0;
    for (manifest.gaps) |gap| {
        try std.testing.expect(gap.id.len > 0);
        try std.testing.expect(gap.kind.len > 0);
        try std.testing.expect(gap.why_now.len > 0);
        try std.testing.expect(isAllowedStatus(gap.status));
        if (std.mem.eql(u8, gap.status, "starter_landed")) {
            starter_landed_count += 1;
        } else {
            blocked_count += 1;
        }
    }

    try expectGap(
        manifest,
        "phase13-make-target",
        "starter_landed",
        "zigux/Makefile",
        "stable shared Phase 13 replay handle",
    );
    try expectGap(
        manifest,
        "phase13-devres-helper-starter",
        "starter_landed",
        "lib/devres.zig",
        "helper-first managed ioremap lifetime",
    );
    try expectGap(
        manifest,
        "phase13-devres-slice-note",
        "starter_landed",
        "Documentation/zigux/phase13-devres-slice.md",
        "devm_arch_phys_wc_add()",
    );
    try expectGap(
        manifest,
        "phase13-devres-survey-note",
        "starter_landed",
        "Documentation/zigux/phase13-devres-survey.md",
        "`P13-L01` terms",
    );
    try expectGap(
        manifest,
        "phase13-devres-test-gate",
        "starter_landed",
        "zigux/tests/phase13_devres.zig",
        "token-style phys-WC helper",
    );
    try expectGap(
        manifest,
        "phase13-devres-reviewability-gate",
        "starter_landed",
        "zigux/tests/phase13_devres_reviewability.zig",
        "blocked live-state boundaries",
    );
    try expectGap(
        manifest,
        "phase13-devres-iounmap-planner",
        "starter_landed",
        "lib/devres.zig",
        "release-miss warning shaping",
    );
    try expectGap(
        manifest,
        "phase13-devres-of-iomap-planner",
        "starter_landed",
        "lib/devres.zig",
        "translated resources by index",
    );
    try expectGap(
        manifest,
        "phase13-devres-arch-phys-wc-token-planner",
        "starter_landed",
        "lib/devres.zig",
        "negative token results",
    );
    try expectGap(
        manifest,
        "phase13-devres-live-mmio-mappings",
        "blocked_on_live_mmio_state",
        "lib/devres.zig",
        "real mappings or unmaps",
    );
    try expectGap(
        manifest,
        "phase13-devres-live-device-tree-walk",
        "blocked_on_live_device_tree_state",
        "lib/devres.zig",
        "OF node traversal",
    );
    try expectGap(
        manifest,
        "phase13-devres-live-arch-memtype-state",
        "blocked_on_live_arch_memtype_state",
        "lib/devres.zig",
        "mutating real memtype state",
    );

    try std.testing.expectEqual(@as(usize, 9), starter_landed_count);
    try std.testing.expectEqual(@as(usize, 3), blocked_count);
}
