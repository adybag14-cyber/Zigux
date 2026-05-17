const std = @import("std");

fn requireContains(text: []const u8, needle: []const u8) !void {
    if (std.mem.indexOf(u8, text, needle) == null) {
        return error.MissingMarker;
    }
}

fn readRepoFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, allocator, .limited(1 << 20));
}

test "phase13 devres dma coherent replay records blocked dma and scatterlist boundaries" {
    const manifest = try readRepoFile(std.testing.allocator, "zigux/tests/phase13_devres_dmam_alloc_coherent_planner_manifest.json");
    defer std.testing.allocator.free(manifest);

    try requireContains(manifest, "\"anchor\": \"lib/devres.c\"");
    try requireContains(manifest, "\"packet\": \"phase13-devres-dmam-alloc-coherent-planner\"");
    try requireContains(manifest, "\"id\": \"phase13-devres-live-dmam-alloc-side-effects\"");
    try requireContains(manifest, "\"status\": \"blocked_on_dma_state\"");
    try requireContains(manifest, "\"id\": \"phase13-devres-live-scatterlist-ownership\"");
    try requireContains(manifest, "\"status\": \"blocked_on_scatterlist_state\"");
}

test "phase13 devres dma coherent replay anchors the current slice reality" {
    const slice = try readRepoFile(std.testing.allocator, "Documentation/zigux/phase13-devres-slice.md");
    defer std.testing.allocator.free(slice);

    try requireContains(slice, "`zigux/tests/phase13_devres_dma_coherent.zig` now materializes one direct replay surface");
    try requireContains(slice, "`Documentation/zigux/phase13-devres-survey.md`");
    try requireContains(slice, "`lib/devres.zig`");
    try requireContains(slice, "repo-reality gaps");
}

test "phase13 devres dma coherent replay keeps the planner note helper-first" {
    const note = try readRepoFile(std.testing.allocator, "Documentation/zigux/phase13-devres-dmam-alloc-coherent-planner.md");
    defer std.testing.allocator.free(note);

    try requireContains(note, "pure `dmam_alloc_coherent()` planning surface");
    try requireContains(note, "`zigux/tests/phase13_devres_dma_coherent.zig` materialized on current `master`");
    try requireContains(note, "`lib/devres.zig` itself remains an explicit repo-reality gap");
    try requireContains(note, "does not treat the replay as proof");
    try requireContains(note, "dma_map_*");
    try requireContains(note, "dma_unmap_*");
    try requireContains(note, "dma_sync_*");
    try requireContains(note, "dma_mmap_*");
    try requireContains(note, "dma_map_sgtable()");
    try requireContains(note, "struct scatterlist");
    try requireContains(note, "sg_table");
    try requireContains(note, "sg_*");
}
