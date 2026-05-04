const std = @import("std");
const devres = @import("devres");

const SurveySummary = struct {
    devres_c_lines: usize,
    previous_surveyed_commit: []const u8,
    devres_helper_sha256: []const u8,
    devres_test_sha256: []const u8,
    devres_dma_coherent_helper_sha256: []const u8,
    devres_dma_coherent_test_sha256: []const u8,
    devres_helper_matches_previous_surveyed_commit: bool,
    devres_test_matches_previous_surveyed_commit: bool,
    preexisting_phase13_build_present: bool,
    preexisting_phase13_make_target_present: bool,
    preexisting_devres_zig_present: bool,
    preexisting_devres_dma_coherent_zig_present: bool,
    preexisting_phase13_devres_test_present: bool,
    preexisting_phase13_devres_dma_coherent_test_present: bool,
    preexisting_phase13_devres_slice_present: bool,
    preexisting_phase13_devres_reviewability_present: bool,
    preexisting_phase13_devres_iounmap_reviewability_present: bool,
    preexisting_phase13_devres_iomap_reviewability_present: bool,
    preexisting_phase13_devres_survey_present: bool,
    preexisting_devres_scatterlist_zig_present: bool,
    preexisting_phase13_devres_scatterlist_test_present: bool,
    preexisting_phase13_devres_scatterlist_slice_present: bool,
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

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectNotContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

fn isAllowedStatus(status: []const u8) bool {
    return std.mem.eql(u8, status, "starter_landed") or
        std.mem.eql(u8, status, "blocked_on_live_mmio_state") or
        std.mem.eql(u8, status, "blocked_on_dma_state") or
        std.mem.eql(u8, status, "blocked_on_scatterlist_state") or
        std.mem.eql(u8, status, "blocked_on_device_tree_state") or
        std.mem.eql(u8, status, "blocked_on_arch_memtype_state");
}

test "phase13 devres manifest records the current helper boundary and explicit dma/scatterlist blockers" {
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
    try std.testing.expectEqualStrings("aa01b37be5500e6a1e4f959c9fe07f0e39d39bfb", manifest.surveyed_commit);
    try std.testing.expectEqual(@as(usize, 3), manifest.roadmap_destinations.len);
    try std.testing.expect(manifest.survey_summary.devres_c_lines >= 390);
    try std.testing.expectEqualStrings("66b55d8a9a800345097f3c04b9f95130b1f8d0b8", manifest.survey_summary.previous_surveyed_commit);
    try std.testing.expectEqualStrings("11b2d4e475b7d21c1086679a438a851f1f12df15aa655b75e8a78fee7427bc21", manifest.survey_summary.devres_helper_sha256);
    try std.testing.expectEqualStrings("7dc45ab99f46d5424e3d757f720e58654aaea326b13db1af601be88c3cbff476", manifest.survey_summary.devres_test_sha256);
    try std.testing.expectEqualStrings("944f595b5434603dd21e77b33af03d317613e2f2f1a81d574c9d1b5f4e422c05", manifest.survey_summary.devres_dma_coherent_helper_sha256);
    try std.testing.expectEqualStrings("898655bd8bdcdbad0074011ae92b3ca3f4c5272d58812253ea8b2aa0542f8dce", manifest.survey_summary.devres_dma_coherent_test_sha256);
    try std.testing.expect(!manifest.survey_summary.devres_helper_matches_previous_surveyed_commit);
    try std.testing.expect(manifest.survey_summary.devres_test_matches_previous_surveyed_commit);
    try std.testing.expect(manifest.survey_summary.preexisting_phase13_build_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase13_make_target_present);
    try std.testing.expect(manifest.survey_summary.preexisting_devres_zig_present);
    try std.testing.expect(manifest.survey_summary.preexisting_devres_dma_coherent_zig_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase13_devres_test_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase13_devres_dma_coherent_test_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase13_devres_slice_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase13_devres_reviewability_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase13_devres_iounmap_reviewability_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase13_devres_iomap_reviewability_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase13_devres_survey_present);
    try std.testing.expect(manifest.survey_summary.preexisting_devres_scatterlist_zig_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase13_devres_scatterlist_test_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase13_devres_scatterlist_slice_present);
    try std.testing.expectEqual(@as(usize, 22), manifest.gaps.len);

    const descriptor = devres.DevresHelperLab.descriptor();
    try std.testing.expectEqualStrings("lib/devres.c", descriptor.anchor);
    try std.testing.expect(descriptor.provides_ioremap_lifetime_planning);
    try std.testing.expect(descriptor.provides_ioremap_plain_wrapper_planning);
    try std.testing.expect(descriptor.provides_ioremap_uc_wrapper_planning);
    try std.testing.expect(descriptor.provides_ioremap_wc_wrapper_planning);
    try std.testing.expect(descriptor.provides_ioremap_np_wrapper_planning);
    try std.testing.expect(descriptor.provides_release_pointer_match);
    try std.testing.expect(descriptor.provides_ioport_lifetime_planning);
    try std.testing.expect(descriptor.provides_ioremap_resource_planning);
    try std.testing.expect(descriptor.provides_ioremap_resource_plain_wrapper_planning);
    try std.testing.expect(descriptor.provides_ioremap_resource_uc_planning);
    try std.testing.expect(descriptor.provides_ioremap_resource_wc_planning);
    try std.testing.expect(descriptor.provides_of_iomap_planning);
    try std.testing.expect(descriptor.provides_pretty_name_helper);
    try std.testing.expect(descriptor.provides_arch_phys_wc_token_planning);
    try std.testing.expect(descriptor.provides_arch_io_wc_memtype_planning);
    try std.testing.expect(!descriptor.touches_live_device_lists);
    try std.testing.expect(!descriptor.touches_live_mmio);
    try std.testing.expect(!descriptor.touches_live_dma);
    try std.testing.expect(!descriptor.touches_live_scatterlist);
    try std.testing.expect(!descriptor.touches_live_arch_memtype);

    const devres_source = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "lib/devres.zig",
        std.testing.allocator,
        .limited(64 * 1024),
    );
    defer std.testing.allocator.free(devres_source);

    try std.testing.expectEqual(@as(usize, 2), std.mem.count(u8, devres_source, "touches_live_dma"));
    try std.testing.expectEqual(@as(usize, 2), std.mem.count(u8, devres_source, "touches_live_scatterlist"));
    try std.testing.expectEqual(@as(usize, 2), std.mem.count(u8, devres_source, "provides_ioremap_resource_plain_wrapper_planning"));
    try expectNotContains(devres_source, "devres_alloc_node");
    try expectNotContains(devres_source, "devres_add");
    try expectNotContains(devres_source, "devm_request_mem_region");
    try expectNotContains(devres_source, "ioremap(");
    try expectNotContains(devres_source, "iounmap(");
    try expectNotContains(devres_source, "ioport_map(");
    try expectNotContains(devres_source, "ioport_unmap(");
    try expectNotContains(devres_source, "dmam_alloc_coherent");
    try expectNotContains(devres_source, "dmam_free_coherent");
    try expectNotContains(devres_source, "dma_map_resource");
    try expectNotContains(devres_source, "dma_unmap_resource");
    try expectNotContains(devres_source, "dma_map_sgtable");
    try expectNotContains(devres_source, "dma_unmap_sgtable");
    try expectNotContains(devres_source, "dma_map_sg_attrs");
    try expectNotContains(devres_source, "dma_unmap_sg_attrs");
    try expectNotContains(devres_source, "dma_map_sg(");
    try expectNotContains(devres_source, "dma_unmap_sg(");
    try expectNotContains(devres_source, "struct scatterlist");
    try expectNotContains(devres_source, "sg_table");
    try std.testing.expectEqual(@as(usize, 0), std.mem.count(u8, devres_source, "sg_"));

    const dma_coherent_source = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "lib/devres_dma_coherent.zig",
        std.testing.allocator,
        .limited(16 * 1024),
    );
    defer std.testing.allocator.free(dma_coherent_source);

    try expectContains(dma_coherent_source, "provides_dma_coherent_lifetime_planning = true");
    try expectContains(dma_coherent_source, "touches_live_dma = false");
    try expectContains(dma_coherent_source, "touches_live_scatterlist = false");
    try expectContains(dma_coherent_source, "planManagedDmaCoherentAlloc");
    try expectContains(dma_coherent_source, "planManagedDmaCoherentFree");
    try expectNotContains(dma_coherent_source, "dma_map_resource");
    try expectNotContains(dma_coherent_source, "dma_unmap_resource");
    try expectNotContains(dma_coherent_source, "dma_map_sgtable");
    try expectNotContains(dma_coherent_source, "dma_unmap_sgtable");
    try expectNotContains(dma_coherent_source, "struct scatterlist");
    try expectNotContains(dma_coherent_source, "sg_table");
    try std.testing.expectEqual(@as(usize, 0), std.mem.count(u8, dma_coherent_source, "sg_"));

    const scatterlist_source = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "lib/devres_scatterlist.zig",
        std.testing.allocator,
        .limited(16 * 1024),
    );
    defer std.testing.allocator.free(scatterlist_source);

    try expectContains(scatterlist_source, "provides_scatterlist_lifetime_planning = true");
    try expectContains(scatterlist_source, "touches_live_dma = false");
    try expectContains(scatterlist_source, "touches_live_scatterlist = false");
    try expectContains(scatterlist_source, "planManagedScatterlistMap");
    try expectContains(scatterlist_source, "planManagedScatterlistUnmap");
    try expectNotContains(scatterlist_source, "dma_map_sgtable");
    try expectNotContains(scatterlist_source, "dma_unmap_sgtable");
    try expectNotContains(scatterlist_source, "struct scatterlist");
    try expectNotContains(scatterlist_source, "sg_table");
    try std.testing.expectEqual(@as(usize, 0), std.mem.count(u8, scatterlist_source, "sg_"));

    const slice_note = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase13-devres-slice.md",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(slice_note);

    try expectContains(slice_note, "pure helper-first foothold anchored to `lib/devres.c`");
    try expectContains(slice_note, "without claiming any live MMIO side effects");
    try expectContains(slice_note, "without pretending to read a live device tree");
    try expectContains(slice_note, "adds the adjacent `devm_ioremap_resource()` wrapper step as a pure helper that keeps the plain managed-resource export explicit instead of leaving it only implied by the base planner entrypoint");
    try expectContains(slice_note, "does not expose `dmam_*`, `dma_map_*`, `dma_unmap_*`, `dma_map_sgtable()`, `struct scatterlist`, `sg_table`, or `sg_*` traversal behavior at all");
    try expectContains(slice_note, "does not claim live `devres_alloc_node()` ownership");
    try expectContains(slice_note, "adds one adjacent helper-first coherent DMA lifetime planner in `lib/devres_dma_coherent.zig`");

    const scatterlist_slice_note = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase13-devres-scatterlist-slice.md",
        std.testing.allocator,
        .limited(16 * 1024),
    );
    defer std.testing.allocator.free(scatterlist_slice_note);

    try expectContains(scatterlist_slice_note, "# Phase 13 devres scatterlist helper slice");
    try expectContains(scatterlist_slice_note, "`DevresScatterlistHelper.descriptor()` names the same `lib/devres.c` anchor while keeping `touches_live_dma = false` and `touches_live_scatterlist = false`");
    try expectContains(scatterlist_slice_note, "`planManagedScatterlistMap()` models a helper-first retained-record decision around original segment count, mapped segment count, and detach-time unmap readiness");
    try expectContains(scatterlist_slice_note, "`planManagedScatterlistUnmap()` keeps the release match exact across original and mapped segment counts so the detach bookkeeping surface stays reviewable");
    try expectContains(scatterlist_slice_note, "no live `dma_map_sgtable()` or `dma_unmap_sgtable()` execution");

    const survey_note = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase13-devres-survey.md",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(survey_note);

    try expectContains(survey_note, "# Phase 13 devres helper DMA/scatterlist boundary survey");
    try expectContains(survey_note, "## Status");
    try expectContains(survey_note, "- `PHASE13_STATUS=active`");
    try expectContains(survey_note, "- `PHASE13_SLICE=devres-helper-dma-scatterlist-boundary-reviewability`");
    try expectContains(survey_note, "- `PHASE13_SURVEYED_COMMIT=aa01b37be5500e6a1e4f959c9fe07f0e39d39bfb`");
    try expectContains(survey_note, "- product boundary:");
    try expectContains(survey_note, "- `lib/devres.zig`");
    try expectContains(survey_note, "- `zigux/tests/phase13_devres_manifest.json`");
    try expectContains(survey_note, "- `Documentation/zigux/phase13-devres-survey.md`");
    try expectContains(survey_note, "helper-first iomap or resource planners plus explicit DMA/scatterlist blockers pinned to the current repo state");
    try expectContains(survey_note, "rejecting full-width inclusive MMIO resource spans that would overflow size math before request-region or remap planning begins");
    try expectContains(survey_note, "sha256 11b2d4e475b7d21c1086679a438a851f1f12df15aa655b75e8a78fee7427bc21");
    try expectContains(survey_note, "sha256 7dc45ab99f46d5424e3d757f720e58654aaea326b13db1af601be88c3cbff476");
    try expectContains(survey_note, "the dedicated `zigux/tests/phase13_devres.zig` replay remains hash-stable");
    try expectContains(survey_note, "only the `touches_live_dma` and `touches_live_scatterlist` descriptor markers");
    try expectContains(survey_note, "`dma_unmap_sgtable`, `dma_map_sg_attrs`, `dma_unmap_sg_attrs`, `struct scatterlist`, `sg_table`, or `sg_` helper entrypoints");
    try expectContains(survey_note, "`devres_alloc_node()` ownership, `devres_add()` installation, `devm_request_mem_region()` side effects");
    try expectContains(survey_note, "the direct `devm_ioremap_resource()` wrapper path that keeps the plain managed-resource export explicit instead of leaving it implied only by `__devm_ioremap_resource()` and the UC/WC wrapper pair");
    try expectContains(survey_note, "`lib/devres_dma_coherent.zig` plus `zigux/tests/phase13_devres_dma_coherent.zig` now keep the helper-first coherent-DMA lifetime packet reviewable on current `master`");
    try expectContains(survey_note, "the adjacent helper-first coherent-DMA lifetime planner in `lib/devres_dma_coherent.zig`");
    try expectContains(survey_note, "beyond the helper-first coherent-DMA lifetime planner's retained-record bookkeeping surface");
    try expectContains(survey_note, "`lib/devres_scatterlist.zig`, `zigux/tests/phase13_devres_scatterlist.zig`, and `Documentation/zigux/phase13-devres-scatterlist-slice.md`");
    try expectContains(survey_note, "the adjacent helper-first scatterlist bookkeeping slice in `lib/devres_scatterlist.zig`");

    const devres_tests = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase13_devres.zig",
        std.testing.allocator,
        .limited(64 * 1024),
    );
    defer std.testing.allocator.free(devres_tests);

    try expectContains(devres_tests, "test \"phase13 devres plans a plain managed ioremap resource wrapper\"");
    try expectContains(devres_tests, "test \"phase13 devres propagates plain managed resource wrapper failures\"");
    try expectContains(devres_tests, "planManagedIoremapResourcePlain(");

    const dma_coherent_tests = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase13_devres_dma_coherent.zig",
        std.testing.allocator,
        .limited(16 * 1024),
    );
    defer std.testing.allocator.free(dma_coherent_tests);

    try expectContains(dma_coherent_tests, "phase13 devres descriptor records helper-first dma coherent planning");
    try expectContains(dma_coherent_tests, "planManagedDmaCoherentAlloc");
    try expectContains(dma_coherent_tests, "planManagedDmaCoherentFree");

    const scatterlist_tests = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase13_devres_scatterlist.zig",
        std.testing.allocator,
        .limited(16 * 1024),
    );
    defer std.testing.allocator.free(scatterlist_tests);

    try expectContains(scatterlist_tests, "phase13 devres descriptor records helper-first scatterlist planning");
    try expectContains(scatterlist_tests, "planManagedScatterlistMap");
    try expectContains(scatterlist_tests, "planManagedScatterlistUnmap");

    const phase13_build = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase13_build.zig",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(phase13_build);

    try expectContains(phase13_build, "../../lib/devres_dma_coherent.zig");
    try expectContains(phase13_build, "phase13_devres_dma_coherent.zig");
    try expectContains(phase13_build, "phase13-devres-dma-coherent-tests");
    try expectContains(phase13_build, "../../lib/devres_scatterlist.zig");
    try expectContains(phase13_build, "phase13_devres_scatterlist.zig");
    try expectContains(phase13_build, "phase13-devres-scatterlist-tests");

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
    var saw_iounmap_reviewability_gate = false;
    var saw_survey_note = false;
    var saw_ioremap_lifetime = false;
    var saw_ioremap_np = false;
    var saw_ioremap_resource = false;
    var saw_of_iomap = false;
    var saw_ioport = false;
    var saw_arch_phys_wc = false;
    var saw_arch_io_memtype = false;
    var saw_dma_coherent = false;
    var saw_scatterlist = false;
    var saw_live_mmio_blocker = false;
    var saw_dma_blocker = false;
    var saw_scatterlist_blocker = false;
    var saw_deviceTreeBlocker = false;
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
        if (std.mem.eql(u8, gap.id, "phase13-devres-iounmap-reviewability-gate")) {
            saw_iounmap_reviewability_gate = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("zigux/tests/phase13_devres_iounmap_reviewability.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "devm_iounmap()") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "provides_iounmap_call_planning") != null);
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
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "devm_ioremap()") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "devm_ioremap_uc") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "devm_ioremap_wc") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "devm_ioremap_np") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "devm_iounmap") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase13-devres-managed-ioremap-np-wrapper")) {
            saw_ioremap_np = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("lib/devres.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "devm_ioremap_np") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "non-posted") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase13-devres-managed-resource-planner")) {
            saw_ioremap_resource = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("lib/devres.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "__devm_ioremap_resource") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "direct devm_ioremap_resource() plain wrapper explicit") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "devm_ioremap_resource_wc") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "overflow-safe inclusive size calculation") != null);
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
        if (std.mem.eql(u8, gap.id, "phase13-devres-dma-coherent-lifetime-planner")) {
            saw_dma_coherent = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("lib/devres_dma_coherent.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "dmam_alloc_coherent()") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "dmam_free_coherent()") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "scatterlist execution") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase13-devres-scatterlist-lifetime-planner")) {
            saw_scatterlist = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("lib/devres_scatterlist.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "planManagedScatterlistMap()") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "planManagedScatterlistUnmap()") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "dma_map_sgtable()") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "sg_table") != null);
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
            saw_deviceTreeBlocker = true;
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

    try std.testing.expectEqual(@as(usize, 17), starter_landed_count);
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
    try std.testing.expect(saw_iounmap_reviewability_gate);
    try std.testing.expect(saw_survey_note);
    try std.testing.expect(saw_ioremap_lifetime);
    try std.testing.expect(saw_ioremap_np);
    try std.testing.expect(saw_ioremap_resource);
    try std.testing.expect(saw_of_iomap);
    try std.testing.expect(saw_ioport);
    try std.testing.expect(saw_arch_phys_wc);
    try std.testing.expect(saw_arch_io_memtype);
    try std.testing.expect(saw_dma_coherent);
    try std.testing.expect(saw_scatterlist);
    try std.testing.expect(saw_live_mmio_blocker);
    try std.testing.expect(saw_dma_blocker);
    try std.testing.expect(saw_scatterlist_blocker);
    try std.testing.expect(saw_deviceTreeBlocker);
    try std.testing.expect(saw_arch_memtype_blocker);
}

test "phase13 devres managed-resource planners reject full-width inclusive spans that overflow size math" {
    const full_width = try devres.DevresHelperLab.planManagedIoremapResource(std.testing.allocator, .{
        .device_name = "uart6",
        .resource = .{
            .start = 0,
            .end = std.math.maxInt(u64),
            .is_memory = true,
            .nonposted = false,
            .name = "regs",
        },
    });

    switch (full_width) {
        .mapped => return error.ExpectedFailure,
        .err => |failure| {
            try std.testing.expectEqual(devres.ErrorStage.invalid_resource, failure.stage);
            try std.testing.expectEqual(devres.ErrorCode.invalid, failure.error_code);
            try std.testing.expectEqual(devres.IoremapType.normal, failure.effective_type);
            try std.testing.expect(!failure.requests_region);
            try std.testing.expect(!failure.releases_region_on_remap_failure);
        },
    }

    const resources = [_]devres.Resource{
        .{
            .start = 0,
            .end = std.math.maxInt(u64),
            .is_memory = true,
            .nonposted = false,
            .name = "wide",
        },
    };

    const translated = try devres.DevresHelperLab.planDeviceTreeIomap(std.testing.allocator, .{
        .device_name = "uart7",
        .index = 0,
        .resources = &resources,
        .report_size = true,
    });

    switch (translated) {
        .mapped => return error.ExpectedFailure,
        .err => |failure| {
            try std.testing.expectEqualStrings("lib/devres.c", failure.anchor);
            try std.testing.expectEqual(devres.DeviceTreeIomapStage.address_translation, failure.stage);
            try std.testing.expectEqual(devres.ErrorCode.invalid, failure.error_code);
            try std.testing.expectEqual(@as(usize, 0), failure.index);
            try std.testing.expectEqual(@as(?u64, null), failure.reported_size);
            try std.testing.expectEqual(devres.IoremapType.normal, failure.effective_type);
            try std.testing.expect(!failure.requests_region);
            try std.testing.expect(!failure.releases_region_on_remap_failure);
            try std.testing.expectEqual(@as(?devres.ErrorStage, null), failure.resource_stage);
        },
    }
}
