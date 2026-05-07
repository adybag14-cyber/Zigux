const std = @import("std");

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
    gaps: []const Gap,
};

fn findGap(gaps: []const Gap, id: []const u8) ?Gap {
    for (gaps) |gap| {
        if (std.mem.eql(u8, gap.id, id)) return gap;
    }
    return null;
}

fn expectContains(text: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, text, needle) != null);
}

test "phase13 devres boundary evidence keeps dma and scatterlist blockers aligned" {
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

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{
        .ignore_unknown_fields = true,
    });
    defer parsed.deinit();

    const manifest = parsed.value;
    try std.testing.expectEqualStrings("Phase 13", manifest.phase);
    try std.testing.expectEqualStrings("lib/devres.c", manifest.anchor);

    const boundary_gate = findGap(manifest.gaps, "phase13-devres-boundary-evidence-gate") orelse return error.MissingBoundaryGate;
    try std.testing.expectEqualStrings("starter_landed", boundary_gate.status);
    try std.testing.expectEqualStrings("validation", boundary_gate.kind);
    try std.testing.expectEqualStrings("zigux/tests/phase13_devres_boundary_evidence.zig", boundary_gate.zigux_destination);
    try expectContains(boundary_gate.why_now, "manifest, slice note, and survey note");
    try expectContains(boundary_gate.why_now, "DMA-backed");
    try expectContains(boundary_gate.why_now, "scatterlist-owned");

    const dma_block = findGap(manifest.gaps, "phase13-devres-live-dma-backed-helpers") orelse return error.MissingDmaBlock;
    try std.testing.expectEqualStrings("blocked_on_dma_state", dma_block.status);
    try expectContains(dma_block.why_now, "dmam_alloc_*");
    try expectContains(dma_block.why_now, "dma_map_sgtable()");
    try expectContains(dma_block.why_now, "helper-first");

    const scatterlist_block = findGap(manifest.gaps, "phase13-devres-live-scatterlist-ownership") orelse return error.MissingScatterlistBlock;
    try std.testing.expectEqualStrings("blocked_on_scatterlist_state", scatterlist_block.status);
    try expectContains(scatterlist_block.why_now, "struct scatterlist");
    try expectContains(scatterlist_block.why_now, "sg_table lifecycle");
    try expectContains(scatterlist_block.why_now, "sg_* ownership transfer");

    try expectContains(slice_note, "live DMA-backed helpers");
    try expectContains(slice_note, "live scatter-gather ownership");
    try expectContains(slice_note, "sg_table lifecycle");
    try expectContains(survey_note, "zigux/tests/phase13_devres_boundary_evidence.zig");
    try expectContains(survey_note, "exact boundary evidence");
    try expectContains(survey_note, "dmam_alloc_*");
    try expectContains(survey_note, "dma_map_sgtable()");
    try expectContains(survey_note, "struct scatterlist");
    try expectContains(survey_note, "sg_table lifecycle");
}
