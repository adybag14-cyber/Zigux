const std = @import("std");

fn requireContains(text: []const u8, needle: []const u8) !void {
    if (std.mem.indexOf(u8, text, needle) == null) {
        return error.MissingMarker;
    }
}

test "phase13 devres dmam_alloc_coherent planner manifest records planning-only dma scope" {
    const manifest = @embedFile("phase13_devres_dmam_alloc_coherent_planner_manifest.json");

    try requireContains(manifest, "\"lane_key\": \"P13-L08\"");
    try requireContains(manifest, "\"phase\": \"Phase 13\"");
    try requireContains(manifest, "\"packet\": \"phase13-devres-dmam-alloc-coherent-planner\"");
    try requireContains(manifest, "\"status\": \"planning_only\"");
    try requireContains(manifest, "\"id\": \"phase13-devres-live-dmam-alloc-side-effects\"");
    try requireContains(manifest, "\"status\": \"blocked_on_dma_state\"");
    try requireContains(manifest, "\"id\": \"phase13-devres-live-scatterlist-ownership\"");
    try requireContains(manifest, "\"status\": \"blocked_on_scatterlist_state\"");
}

test "phase13 devres dmam_alloc_coherent planner note keeps the slice helper-first and bounded" {
    const note = @embedFile("../../Documentation/zigux/phase13-devres-dmam-alloc-coherent-planner.md");

    try requireContains(note, "pure `dmam_alloc_coherent()` planning surface");
    try requireContains(note, "detach-time cleanup intent");
    try requireContains(note, "avoid retaining detach-time cleanup ownership");
    try requireContains(note, "zigux/tests/phase13_devres_dma_coherent.zig");
    try requireContains(note, "dma_map_*");
    try requireContains(note, "dma_unmap_*");
    try requireContains(note, "dma_sync_*");
    try requireContains(note, "dma_mmap_*");
    try requireContains(note, "dma_map_sgtable()");
    try requireContains(note, "struct scatterlist");
    try requireContains(note, "sg_table");
    try requireContains(note, "sg_*");
}

test "phase13 devres dmam_alloc_coherent planner note preserves standalone replay handle" {
    const note = @embedFile("../../Documentation/zigux/phase13-devres-dmam-alloc-coherent-planner.md");

    try requireContains(note, "zig test zigux/tests/phase13_devres_dmam_alloc_coherent_planner.zig");
}
