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

test "phase13 devres manifest records the landed helper-first MMIO safety surface and explicit blockers" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const manifest_json = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase13_devres_manifest.json",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(manifest_json);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();

    const manifest = parsed.value;
    try std.testing.expectEqualStrings("P13-L10", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 13", manifest.phase);
    try std.testing.expectEqualStrings("lib/devres.c", manifest.anchor);
    try std.testing.expectEqualStrings("7f50505d85ecd5e25afa9d833310cc24002de8ae", manifest.surveyed_commit);
    try std.testing.expectEqual(@as(usize, 3), manifest.roadmap_destinations.len);
    try std.testing.expect(manifest.survey_summary.devres_c_lines >= 390);
    try std.testing.expect(manifest.survey_summary.preexisting_phase13_build_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase13_make_target_present);
    try std.testing.expect(manifest.survey_summary.preexisting_devres_zig_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase13_devres_test_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase13_devres_slice_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase13_devres_reviewability_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase13_devres_survey_present);
    try std.testing.expectEqual(@as(usize, 18), manifest.gaps.len);

    const descriptor = devres.DevresHelperLab.descriptor();
    try std.testing.expectEqualStrings("lib/devres.c", descriptor.anchor);
    try std.testing.expect(descriptor.provides_ioremap_lifetime_planning);
    try std.testing.expect(descriptor.provides_ioremap_uc_wrapper_planning);
    try std.testing.expect(descriptor.provides_release_pointer_match);
    try std.testing.expect(descriptor.provides_ioport_lifetime_planning);
    try std.testing.expect(descriptor.provides_ioremap_resource_planning);
    try std.testing.expect(descriptor.provides_ioremap_resource_uc_planning);
    try std.testing.expect(descriptor.provides_ioremap_resource_wc_planning);
    try std.testing.expect(descriptor.provides_of_iomap_planning);
    try std.testing.expect(descriptor.provides_pretty_name_helper);
    try std.testing.expect(descriptor.provides_arch_phys_wc_token_planning);
    try std.testing.expect(descriptor.provides_arch_io_wc_memtype_planning);
    try std.testing.expect(!descriptor.touches_live_device_lists);
    try std.testing.expect(!descriptor.touches_live_mmio);
    try std.testing.expect(!descriptor.touches_live_arch_memtype);

    var starter_landed_count: usize = 0;
    var blocked_live_mmio_count: usize = 0;
    var blocked_dma_count: usize = 0;
    var blocked_scatterlist_count: usize = 0;
    var blocked_device_tree_count: usize = 0;
    var blocked_arch_memtype_count: usize = 0;
    var saw_build_gate = false;
    var saw_make_target = false;
    var saw_starter = false;
    var saw_tests = false;
    var saw_slice_note = false;
    var saw_reviewability_gate = false;
    var saw_survey_note = false;
    var saw_ioremap_lifetime = false;
    var saw_ioremap_resource = false;
    var saw_of_iomap = false;
    var saw_ioport = false;
    var saw_arch_phys_wc = false;
    var saw_arch_io_memtype = false;
    var saw_live_mmio_blocker = false;
    var saw_dma_blocker = false;
    var saw_scatterlist_blocker = false;
    var saw_device_tree_blocker = false;
    var saw_arch_memtype_blocker = false;

    for (manifest.gaps, 0..) |gap, i| {
        try std.testing.expect(gap.id.len > 0);
        try std.testing.expect(gap.kind.len > 0);
        try std.testing.expect(gap.why_now.len > 0);
        try std.testing.expect(isAllowedStatus(gap.status));

        if (std.mem.eql(u8, gap.status, "starter_landed")) {
            starter_landed_count += 1;
        } else if (std.mem.eql(u8, gap.status, "blocked_on_live_mmio_state")) {
            blocked_live_mmio_count += 1;
        } else if (std.mem.eql(u8, gap.status, "blocked_on_dma_state")) {
            blocked_dma_count += 1;
        } else if (std.mem.eql(u8, gap.status, "blocked_on_scatterlist_state")) {
            blocked_scatterlist_count += 1;
        } else if (std.mem.eql(u8, gap.status, "blocked_on_device_tree_state")) {
            blocked_device_tree_count += 1;
        } else if (std.mem.eql(u8, gap.status, "blocked_on_arch_memtype_state")) {
            blocked_arch_memtype_count += 1;
        }

        if (std.mem.eql(u8, gap.id, "phase13-build-gate")) {
            saw_build_gate = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("zigux/tests/phase13_build.zig", gap.zigux_destination);
        }
        if (std.mem.eql(u8, gap.id, "phase13-make-target")) {
            saw_make_target = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("zigux/Makefile", gap.zigux_destination);
        }
        if (std.mem.eql(u8, gap.id, "phase13-devres-starter")) {
            saw_starter = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("lib/devres.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "__devm_ioremap") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "__devm_ioremap_resource") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase13-devres-tests")) {
            saw_tests = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("zigux/tests/phase13_devres.zig", gap.zigux_destination);
        }
        if (std.mem.eql(u8, gap.id, "phase13-devres-slice-note")) {
            saw_slice_note = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("Documentation/zigux/phase13-devres-slice.md", gap.zigux_destination);
        }
        if (std.mem.eql(u8, gap.id, "phase13-devres-reviewability-gate")) {
            saw_reviewability_gate = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("zigux/tests/phase13_devres_reviewability.zig", gap.zigux_destination);
        }
        if (std.mem.eql(u8, gap.id, "phase13-devres-survey-note")) {
            saw_survey_note = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("Documentation/zigux/phase13-devres-survey.md", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "helper-first") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase13-devres-managed-ioremap-lifetime")) {
            saw_ioremap_lifetime = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("lib/devres.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "devm_ioremap_uc") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "devm_iounmap") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase13-devres-managed-resource-planner")) {
            saw_ioremap_resource = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("lib/devres.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "devm_ioremap_resource") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "devm_ioremap_resource_wc") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase13-devres-devicetree-iomap-planner")) {
            saw_of_iomap = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("lib/devres.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "devm_of_iomap") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "of_address_to_resource") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase13-devres-ioport-lifetime-planner")) {
            saw_ioport = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("lib/devres.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "devm_ioport_map") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "devm_ioport_unmap") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase13-devres-arch-phys-wc-token-planner")) {
            saw_arch_phys_wc = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("lib/devres.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "devm_arch_phys_wc_add") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "arch_phys_wc_del") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase13-devres-arch-io-memtype-planner")) {
            saw_arch_io_memtype = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("lib/devres.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "devm_arch_io_reserve_memtype_wc") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "arch_io_free_memtype_wc") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase13-devres-live-mmio-side-effects")) {
            saw_live_mmio_blocker = true;
            try std.testing.expectEqualStrings("blocked_on_live_mmio_state", gap.status);
            try std.testing.expectEqualStrings("lib/devres.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "devres_alloc_node") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "devres_add") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "ioremap") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase13-devres-live-dma-mappings")) {
            saw_dma_blocker = true;
            try std.testing.expectEqualStrings("blocked_on_dma_state", gap.status);
            try std.testing.expectEqualStrings("lib/devres.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "dmam_alloc_coherent") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "dma_map_resource") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "dma_map_sgtable") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase13-devres-live-scatterlist-ownership")) {
            saw_scatterlist_blocker = true;
            try std.testing.expectEqualStrings("blocked_on_scatterlist_state", gap.status);
            try std.testing.expectEqualStrings("lib/devres.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "struct scatterlist") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "sg_table") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "sg_*") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase13-devres-live-device-tree-walk")) {
            saw_device_tree_blocker = true;
            try std.testing.expectEqualStrings("blocked_on_device_tree_state", gap.status);
            try std.testing.expectEqualStrings("lib/devres.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "struct device_node") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "reg") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase13-devres-live-arch-memtype-state")) {
            saw_arch_memtype_blocker = true;
            try std.testing.expectEqualStrings("blocked_on_arch_memtype_state", gap.status);
            try std.testing.expectEqualStrings("lib/devres.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "arch_phys_wc_add") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "arch_io_reserve_memtype_wc") != null);
        }

        for (manifest.gaps[i + 1 ..]) |other| {
            try std.testing.expect(!std.mem.eql(u8, gap.id, other.id));
        }
    }

    try std.testing.expectEqual(@as(usize, 13), starter_landed_count);
    try std.testing.expectEqual(@as(usize, 1), blocked_live_mmio_count);
    try std.testing.expectEqual(@as(usize, 1), blocked_dma_count);
    try std.testing.expectEqual(@as(usize, 1), blocked_scatterlist_count);
    try std.testing.expectEqual(@as(usize, 1), blocked_device_tree_count);
    try std.testing.expectEqual(@as(usize, 1), blocked_arch_memtype_count);
    try std.testing.expect(saw_build_gate);
    try std.testing.expect(saw_make_target);
    try std.testing.expect(saw_starter);
    try std.testing.expect(saw_tests);
    try std.testing.expect(saw_slice_note);
    try std.testing.expect(saw_reviewability_gate);
    try std.testing.expect(saw_survey_note);
    try std.testing.expect(saw_ioremap_lifetime);
    try std.testing.expect(saw_ioremap_resource);
    try std.testing.expect(saw_of_iomap);
    try std.testing.expect(saw_ioport);
    try std.testing.expect(saw_arch_phys_wc);
    try std.testing.expect(saw_arch_io_memtype);
    try std.testing.expect(saw_live_mmio_blocker);
    try std.testing.expect(saw_dma_blocker);
    try std.testing.expect(saw_scatterlist_blocker);
    try std.testing.expect(saw_device_tree_blocker);
    try std.testing.expect(saw_arch_memtype_blocker);
}
