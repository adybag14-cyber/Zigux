const std = @import("std");
const devres = @import("devres");

const SurveySummary = struct {
    devres_c_lines: usize,
    preexisting_phase13_build_present: bool,
    preexisting_phase13_make_target_present: bool,
    preexisting_devres_zig_present: bool,
    preexisting_phase13_devres_test_present: bool,
    preexisting_phase13_devres_slice_present: bool,
    preexisting_phase13_devres_reviewability_present: bool,
    preexisting_phase13_devres_survey_present: bool,
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
        std.mem.eql(u8, status, "blocked_on_dma_state") or
        std.mem.eql(u8, status, "blocked_on_scatterlist_state") or
        std.mem.eql(u8, status, "blocked_on_device_tree_state") or
        std.mem.eql(u8, status, "blocked_on_arch_memtype_state");
}

test "phase13 devres reviewability packet records the helper-only DMA/scatterlist boundary" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const manifest_json = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase13_devres_manifest.json",
        std.testing.allocator,
        .limited(48 * 1024),
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

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{
        .ignore_unknown_fields = true,
    });
    defer parsed.deinit();

    const manifest = parsed.value;
    try std.testing.expectEqualStrings("P13-L11", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 13", manifest.phase);
    try std.testing.expectEqualStrings("7a4454d0474106972cad7e164b79293bd54a40c6", manifest.surveyed_commit);
    try std.testing.expectEqualStrings("lib/devres.c", manifest.anchor);
    try std.testing.expectEqual(@as(usize, 3), manifest.roadmap_destinations.len);
    try std.testing.expectEqual(@as(usize, 399), manifest.survey_summary.devres_c_lines);
    try std.testing.expect(manifest.survey_summary.preexisting_phase13_build_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase13_make_target_present);
    try std.testing.expect(manifest.survey_summary.preexisting_devres_zig_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase13_devres_test_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase13_devres_slice_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase13_devres_reviewability_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase13_devres_survey_present);
    try std.testing.expectEqual(@as(usize, 16), manifest.gaps.len);

    const descriptor = devres.DevresHelperLab.descriptor();
    try std.testing.expectEqualStrings("lib/devres.c", descriptor.anchor);
    try std.testing.expect(descriptor.provides_ioremap_lifetime_planning);
    try std.testing.expect(descriptor.provides_ioremap_wc_wrapper_planning);
    try std.testing.expect(descriptor.provides_release_pointer_match);
    try std.testing.expect(descriptor.provides_ioremap_resource_planning);
    try std.testing.expect(descriptor.provides_of_iomap_planning);
    try std.testing.expect(descriptor.provides_pretty_name_helper);
    try std.testing.expect(descriptor.provides_arch_io_wc_memtype_planning);
    try std.testing.expect(!descriptor.touches_live_device_lists);
    try std.testing.expect(!descriptor.touches_live_mmio);
    try std.testing.expect(!descriptor.touches_live_arch_memtype);

    try std.testing.expect(std.mem.indexOf(u8, slice_note, "devm_arch_io_reserve_memtype_wc()") != null);
    try std.testing.expect(std.mem.indexOf(u8, slice_note, "This slice does not claim live `devres_alloc_node()` ownership") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "devm_arch_phys_wc_add()") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "devm_arch_io_reserve_memtype_wc()") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "7a4454d0474106972cad7e164b79293bd54a40c6") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "devm_ioremap_wc()") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "dmam_alloc_*") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "dma_map_sgtable()") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "struct scatterlist") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "sg_table") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "sg_*") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "live scatter-gather ownership") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "live DMA-backed helpers") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "blocked `phase13-devres-live-mmio-side-effects`") != null);

    var starter_landed_count: usize = 0;
    var blocked_count: usize = 0;
    var saw_reviewability_gate = false;
    var saw_survey_note = false;
    var saw_arch_phys_wc = false;
    var saw_arch_io_memtype = false;
    var saw_mmio_block = false;
    var saw_dma_block = false;
    var saw_scatterlist_block = false;

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

        if (std.mem.eql(u8, gap.id, "phase13-devres-reviewability-gate")) {
            saw_reviewability_gate = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("zigux/tests/phase13_devres_reviewability.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "helper-only DMA/scatterlist boundary machine-checkable") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase13-devres-helper-starter")) {
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "devm_ioremap_wc()") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase13-devres-test-gate")) {
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "devm_ioremap_wc()") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase13-devres-survey-note")) {
            saw_survey_note = true;
            try std.testing.expectEqualStrings("Documentation/zigux/phase13-devres-survey.md", gap.zigux_destination);
        }
        if (std.mem.eql(u8, gap.id, "phase13-devres-arch-phys-wc-token-planner")) {
            saw_arch_phys_wc = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "arch_phys_wc_del()") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase13-devres-arch-io-memtype-planner")) {
            saw_arch_io_memtype = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "arch_io_free_memtype_wc()") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase13-devres-live-mmio-side-effects")) {
            saw_mmio_block = true;
            try std.testing.expectEqualStrings("blocked_on_live_mmio_state", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "real region mutation or address-space effects") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase13-devres-live-dma-backed-helpers")) {
            saw_dma_block = true;
            try std.testing.expectEqualStrings("blocked_on_dma_state", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "dmam_alloc_*") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "dma_map_sgtable()") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase13-devres-live-scatterlist-ownership")) {
            saw_scatterlist_block = true;
            try std.testing.expectEqualStrings("blocked_on_scatterlist_state", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "sg") != null);
        }

        for (manifest.gaps[i + 1 ..]) |other| {
            try std.testing.expect(!std.mem.eql(u8, gap.id, other.id));
        }
    }

    try std.testing.expectEqual(@as(usize, 11), starter_landed_count);
    try std.testing.expectEqual(@as(usize, 5), blocked_count);
    try std.testing.expect(saw_reviewability_gate);
    try std.testing.expect(saw_survey_note);
    try std.testing.expect(saw_arch_phys_wc);
    try std.testing.expect(saw_arch_io_memtype);
    try std.testing.expect(saw_mmio_block);
    try std.testing.expect(saw_dma_block);
    try std.testing.expect(saw_scatterlist_block);
}
