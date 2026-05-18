const std = @import("std");
const devres = @import("devres");

fn requireContains(text: []const u8, needle: []const u8) !void {
    if (std.mem.indexOf(u8, text, needle) == null) {
        return error.MissingMarker;
    }
}

fn readRepoFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, allocator, .limited(1 << 20));
}

test "phase13 devres descriptor records helper-first dmam_alloc_coherent planning" {
    const descriptor = devres.DevresHelperLab.descriptor();

    try std.testing.expectEqualStrings("devres_helper_lab", descriptor.name);
    try std.testing.expectEqualStrings("lib/devres.c", descriptor.anchor);
    try std.testing.expect(descriptor.provides_dmam_alloc_coherent_planning);
    try std.testing.expect(!descriptor.touches_live_dma);
    try std.testing.expect(!descriptor.touches_live_scatterlist);
}

test "phase13 devres retains detach-time cleanup ownership when planned coherent allocation succeeds" {
    const plan = try devres.DevresHelperLab.planManagedDmamAllocCoherent(.{
        .requested_size = 4096,
        .release_record_allocated = true,
        .allocation_succeeds = true,
    });

    try std.testing.expectEqualStrings("lib/devres.c", plan.anchor);
    try std.testing.expectEqual(@as(u64, 4096), plan.requested_size);
    try std.testing.expect(plan.allocation_ready);
    try std.testing.expect(plan.added_to_devres);
    try std.testing.expect(plan.release_record_retained);
    try std.testing.expect(!plan.release_record_freed);
    try std.testing.expect(plan.should_free_on_detach);
}

test "phase13 devres drops detach-time cleanup ownership when planned coherent allocation fails" {
    const plan = try devres.DevresHelperLab.planManagedDmamAllocCoherent(.{
        .requested_size = 4096,
        .release_record_allocated = true,
        .allocation_succeeds = false,
    });

    try std.testing.expectEqual(@as(u64, 4096), plan.requested_size);
    try std.testing.expect(!plan.allocation_ready);
    try std.testing.expect(!plan.added_to_devres);
    try std.testing.expect(!plan.release_record_retained);
    try std.testing.expect(plan.release_record_freed);
    try std.testing.expect(!plan.should_free_on_detach);
}

test "phase13 devres rejects coherent planning when the release record cannot be allocated" {
    try std.testing.expectError(error.OutOfMemory, devres.DevresHelperLab.planManagedDmamAllocCoherent(.{
        .requested_size = 4096,
        .release_record_allocated = false,
        .allocation_succeeds = true,
    }));
}

test "phase13 devres dmam_alloc_coherent planner manifest records the landed helper-first dma scope" {
    const manifest = try readRepoFile(std.testing.allocator, "zigux/tests/phase13_devres_dmam_alloc_coherent_planner_manifest.json");
    defer std.testing.allocator.free(manifest);

    try requireContains(manifest, "\"lane_key\": \"P13-L08\"");
    try requireContains(manifest, "\"phase\": \"Phase 13\"");
    try requireContains(manifest, "\"packet\": \"phase13-devres-dmam-alloc-coherent-planner\"");
    try requireContains(manifest, "\"status\": \"starter_landed\"");
    try requireContains(manifest, "lib/devres.zig");
    try requireContains(manifest, "zigux/tests/phase13_devres_dmam_alloc_coherent_planner.zig");
    try requireContains(manifest, "\"id\": \"phase13-devres-live-dmam-alloc-side-effects\"");
    try requireContains(manifest, "\"status\": \"blocked_on_dma_state\"");
    try requireContains(manifest, "\"id\": \"phase13-devres-live-scatterlist-ownership\"");
    try requireContains(manifest, "\"status\": \"blocked_on_scatterlist_state\"");
}

test "phase13 devres dmam_alloc_coherent planner note keeps the helper-first dma slice bounded" {
    const note = try readRepoFile(std.testing.allocator, "Documentation/zigux/phase13-devres-dmam-alloc-coherent-planner.md");
    defer std.testing.allocator.free(note);

    try requireContains(note, "lands one pure `dmam_alloc_coherent()` planning surface in `lib/devres.zig`");
    try requireContains(note, "accepts already-decided allocation inputs");
    try requireContains(note, "retains detach-time cleanup ownership on success");
    try requireContains(note, "failed allocation frees the release record");
    try requireContains(note, "does not claim live DMA allocation side effects");
    try requireContains(note, "dma_map_*");
    try requireContains(note, "dma_unmap_*");
    try requireContains(note, "dma_sync_*");
    try requireContains(note, "dma_mmap_*");
    try requireContains(note, "dma_map_sgtable()");
    try requireContains(note, "struct scatterlist");
    try requireContains(note, "sg_table");
    try requireContains(note, "sg_*");
}

test "phase13 devres dmam_alloc_coherent planner note preserves standalone replay handles" {
    const note = try readRepoFile(std.testing.allocator, "Documentation/zigux/phase13-devres-dmam-alloc-coherent-planner.md");
    defer std.testing.allocator.free(note);

    try requireContains(note, "zig test --dep devres -Mroot=zigux/tests/phase13_devres_dmam_alloc_coherent_planner.zig -Mdevres=lib/devres.zig");
    try requireContains(note, "zig test zigux/tests/phase13_devres_dma_coherent.zig");
}

test "phase13 devres slice note records the narrow landed dmam planner without claiming the broader packet" {
    const slice = try readRepoFile(std.testing.allocator, "Documentation/zigux/phase13-devres-slice.md");
    defer std.testing.allocator.free(slice);

    try requireContains(slice, "`lib/devres.zig` and `zigux/tests/phase13_devres_dmam_alloc_coherent_planner.zig` now provide one pure helper-first `dmam_alloc_coherent()` planning surface");
    try requireContains(slice, "the older direct devres replay, reviewability gate, manifest-backed packet, and packet-alignment checker remain repo-reality gaps");
    try requireContains(slice, "does not claim live DMA helper delivery");
}

test "phase13 devres survey records the landed dmam planner and keeps the blocked dma boundaries explicit" {
    const survey = try readRepoFile(std.testing.allocator, "Documentation/zigux/phase13-devres-survey.md");
    defer std.testing.allocator.free(survey);

    try requireContains(survey, "`lib/devres.zig` now ships a pure `dmam_alloc_coherent()` planning surface");
    try requireContains(survey, "`zigux/tests/phase13_devres_dmam_alloc_coherent_planner.zig` replays that helper directly");
    try requireContains(survey, "current `master` does not ship `zigux/tests/phase13_devres.zig`");
    try requireContains(survey, "blocked `phase13-devres-live-dmam-alloc-side-effects`");
    try requireContains(survey, "blocked `phase13-devres-broader-direct-helper-packet`");
}