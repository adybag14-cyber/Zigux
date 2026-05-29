const std = @import("std");

fn requireContains(text: []const u8, needle: []const u8) !void {
    if (std.mem.indexOf(u8, text, needle) == null) {
        return error.MissingMarker;
    }
}

fn requireAbsent(text: []const u8, needle: []const u8) !void {
    if (std.mem.indexOf(u8, text, needle) != null) {
        return error.UnexpectedMarker;
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

test "phase13 devres dma coherent replay proves lib/devres stays planning-only at the boundary" {
    const helper = try readRepoFile(std.testing.allocator, "lib/devres.zig");
    defer std.testing.allocator.free(helper);

    try requireContains(helper, ".provides_dmam_alloc_coherent_planning = true");
    try requireContains(helper, ".touches_live_dma = false");
    try requireContains(helper, ".touches_live_scatterlist = false");
    try requireContains(helper, "planManagedDmamAllocCoherent");
    try requireContains(helper, "planManagedDmamFreeCoherent");
    try requireAbsent(helper, "dmam_alloc_coherent(");
    try requireAbsent(helper, "dmam_free_coherent(");
    try requireAbsent(helper, "dma_map_");
    try requireAbsent(helper, "dma_unmap_");
    try requireAbsent(helper, "dma_sync_");
    try requireAbsent(helper, "dma_mmap_");
    try requireAbsent(helper, "dma_map_sgtable()");
    try requireAbsent(helper, "struct scatterlist");
    try requireAbsent(helper, "sg_table");
    try requireAbsent(helper, "sg_init_table(");
    try requireAbsent(helper, "dma_map_sg(");
    try requireAbsent(helper, "dma_unmap_sg(");
    try requireAbsent(helper, "sg_alloc_table(");
    try requireAbsent(helper, "sg_free_table(");
    try requireAbsent(helper, "sg_dma_address(");
    try requireAbsent(helper, "sg_dma_len(");
}

test "phase13 devres dma coherent replay anchors the current slice reality" {
    const slice = try readRepoFile(std.testing.allocator, "Documentation/zigux/phase13-devres-slice.md");
    defer std.testing.allocator.free(slice);

    try requireContains(slice, "`zigux/tests/phase13_devres_dma_coherent.zig` plus `Documentation/zigux/phase13-devres-dmam-alloc-coherent-planner.md`, `Documentation/zigux/phase13-devres-scatterlist-planner.md`, `zigux/tests/phase13_devres_scatterlist_planner_manifest.json`, `lib/devres_scatterlist.zig`, and `zigux/tests/phase13_devres_scatterlist.zig` keep the current packet helper-first and planning-only");
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
    try requireContains(survey, "`Documentation/zigux/phase13-devres-scatterlist-planner.md` records a landed pure scatterlist lifetime planning surface");
    try requireContains(survey, "`zigux/tests/phase13_devres_scatterlist_planner_manifest.json` marks the packet as `starter_landed`");
    try requireContains(survey, "blocked `phase13-devres-live-scatterlist-ownership`");
    try requireContains(survey, "blocked `phase13-devres-live-sg-table-lifecycle`");
    try requireContains(survey, "blocked `phase13-devres-generic-dma-map-family`");
    try requireContains(survey, "helper-source readback shows `lib/devres.zig` still omits");
    try requireContains(survey, "`dmam_alloc_coherent()`");
    try requireContains(survey, "`dmam_free_coherent()`");
    try requireContains(survey, "`dma_map_sgtable()`");
    try requireContains(survey, "`sg_table`");
    try requireContains(survey, "`zigux/tests/phase13_devres_dmam_alloc_zero_size_replay_build.zig`");
    try requireContains(survey, "`zigux/tests/phase13_devres_scatterlist_build.zig`");
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
    try requireContains(replay, "phase13 devres scatterlist planner manifest records the dedicated helper-first packet");
    try requireContains(replay, "phase13 devres scatterlist planner note keeps the helper-first scatterlist slice bounded");
}

test "phase13 devres dma coherent replay keeps build-shard boundary checks explicit" {
    const checker = try readRepoFile(std.testing.allocator, "scripts/zigux/check-phase13-devres-dma-boundary.py");
    defer std.testing.allocator.free(checker);

    try requireContains(checker, "DMA_REPLAY_BUILD_PATH = Path(\"zigux/tests/phase13_devres_dmam_alloc_zero_size_replay_build.zig\")");
    try requireContains(checker, "SCATTERLIST_BUILD_PATH = Path(\"zigux/tests/phase13_devres_scatterlist_build.zig\")");
    try requireContains(checker, "`zigux/tests/phase13_devres_dmam_alloc_zero_size_replay_build.zig` keeps the zero-sized coherent allocation replay directly runnable through its dedicated build shard");
    try requireContains(checker, "`zigux/tests/phase13_devres_scatterlist_build.zig` keeps the helper-first scatterlist replay directly runnable through a dedicated build shard");
}