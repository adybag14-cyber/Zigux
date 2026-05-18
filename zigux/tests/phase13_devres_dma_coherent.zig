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

    try requireContains(slice, "`zigux/tests/phase13_devres_dma_coherent.zig` plus `Documentation/zigux/phase13-devres-dmam-alloc-coherent-planner.md`, `lib/devres_scatterlist.zig`, and `zigux/tests/phase13_devres_scatterlist.zig` keep the current packet helper-first and planning-only");
    try requireContains(slice, "`Documentation/zigux/phase13-devres-survey.md`");
    try requireContains(slice, "`lib/devres.zig`");
    try requireContains(slice, "repo-reality gaps");
}

test "phase13 devres dma coherent replay keeps missing checker surfaces framed as gaps" {
    const slice = try readRepoFile(std.testing.allocator, "Documentation/zigux/phase13-devres-slice.md");
    defer std.testing.allocator.free(slice);

    try requireContains(slice, "`scripts/zigux/check-phase13-devres-packet-alignment.py`");
    try requireContains(slice, "the older direct devres replay, reviewability gate, manifest-backed packet, and packet-alignment checker remain repo-reality gaps");
    try requireContains(slice, "the broader direct helper packet stays an explicit repo-reality gap");
}

test "phase13 devres dma coherent replay keeps the planner note helper-first" {
    const note = try readRepoFile(std.testing.allocator, "Documentation/zigux/phase13-devres-dmam-alloc-coherent-planner.md");
    defer std.testing.allocator.free(note);

    try requireContains(note, "pure `dmam_alloc_coherent()` planning surface");
    try requireContains(note, "Adjacent boundary evidence stays unchanged:");
    try requireContains(note, "`zigux/tests/phase13_devres_dma_coherent.zig`");
    try requireContains(note, "while keeping live DMA state, scatterlist ownership, and broader devres-group behavior blocked");
    try requireContains(note, "dma_map_*");
    try requireContains(note, "dma_unmap_*");
    try requireContains(note, "dma_sync_*");
    try requireContains(note, "dma_mmap_*");
    try requireContains(note, "dma_map_sgtable()");
    try requireContains(note, "struct scatterlist");
    try requireContains(note, "sg_table");
    try requireContains(note, "sg_*");
}

test "phase13 devres dma coherent replay anchors the survey-side scatterlist boundary" {
    const survey = try readRepoFile(std.testing.allocator, "Documentation/zigux/phase13-devres-survey.md");
    defer std.testing.allocator.free(survey);

    try requireContains(survey, "helper-first scatterlist helper and replay");
    try requireContains(survey, "`lib/devres_scatterlist.zig` and `zigux/tests/phase13_devres_scatterlist.zig` keep the helper-first scatterlist lifetime slice reviewable");
    try requireContains(survey, "blocked `phase13-devres-live-scatterlist-ownership`");
    try requireContains(survey, "blocked `phase13-devres-live-sg-table-lifecycle`");
    try requireContains(survey, "blocked `phase13-devres-generic-dma-map-family`");
}

test "phase13 devres dma coherent replay keeps scatterlist helper evidence helper-first" {
    const helper = try readRepoFile(std.testing.allocator, "lib/devres_scatterlist.zig");
    defer std.testing.allocator.free(helper);
    const replay = try readRepoFile(std.testing.allocator, "zigux/tests/phase13_devres_scatterlist.zig");
    defer std.testing.allocator.free(replay);

    try requireContains(helper, ".provides_scatterlist_lifetime_planning = true");
    try requireContains(helper, ".touches_live_dma = false");
    try requireContains(helper, ".touches_live_scatterlist = false");
    try requireContains(helper, "pub fn planManagedScatterlistMap");
    try requireContains(helper, "pub fn planManagedScatterlistUnmap");

    try requireContains(replay, "phase13 devres descriptor records helper-first scatterlist planning");
    try requireContains(replay, "phase13 devres rejects scatterlist planning when the release record cannot be allocated");
    try requireContains(replay, "phase13 devres scatterlist release matching stays exact across original and mapped counts");
}
