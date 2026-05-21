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
    try std.testing.expect(descriptor.provides_release_record_lifetime_planning);
    try std.testing.expect(descriptor.provides_release_call_planning);
    try std.testing.expect(descriptor.provides_dmam_free_coherent_cleanup_planning);
    try std.testing.expect(!descriptor.touches_live_dma);
    try std.testing.expect(!descriptor.touches_live_scatterlist);
}

test "phase13 devres exposes shared release-record lifetime planning" {
    const retained = devres.DevresHelperLab.planManagedReleaseRecordLifetime(true);
    try std.testing.expect(retained.added_to_devres);
    try std.testing.expect(retained.release_record_retained);
    try std.testing.expect(!retained.release_record_freed);
    try std.testing.expect(retained.should_release_on_detach);

    const freed = devres.DevresHelperLab.planManagedReleaseRecordLifetime(false);
    try std.testing.expect(!freed.added_to_devres);
    try std.testing.expect(!freed.release_record_retained);
    try std.testing.expect(freed.release_record_freed);
    try std.testing.expect(!freed.should_release_on_detach);
}

test "phase13 devres exposes shared release-call planning" {
    const matched = devres.DevresHelperLab.planManagedReleaseCall(4096, true);
    try std.testing.expectEqualStrings("lib/devres.c", matched.anchor);
    try std.testing.expectEqual(@as(u64, 4096), matched.requested_size);
    try std.testing.expect(matched.releases_from_devres);
    try std.testing.expect(matched.release_record_consumed);
    try std.testing.expect(!matched.warns_on_release_miss);
    try std.testing.expect(matched.destroys_release_record_before_free);

    const missed = devres.DevresHelperLab.planManagedReleaseCall(4096, false);
    try std.testing.expect(!missed.releases_from_devres);
    try std.testing.expect(!missed.release_record_consumed);
    try std.testing.expect(missed.warns_on_release_miss);
    try std.testing.expect(missed.destroys_release_record_before_free);
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

test "phase13 devres turns successful coherent-allocation planning into explicit detach cleanup planning" {
    const plan = try devres.DevresHelperLab.planManagedDmamAllocCoherent(.{
        .requested_size = 4096,
        .release_record_allocated = true,
        .allocation_succeeds = true,
    });

    try std.testing.expect(plan.should_free_on_detach);

    const cleanup = devres.DevresHelperLab.planManagedDmamFreeCoherent(plan.requested_size, true);
    try std.testing.expectEqualStrings("lib/devres.c", cleanup.anchor);
    try std.testing.expectEqual(@as(u64, 4096), cleanup.requested_size);
    try std.testing.expect(cleanup.frees_allocation);
    try std.testing.expect(cleanup.releases_from_devres);
    try std.testing.expect(cleanup.release_record_consumed);
    try std.testing.expect(!cleanup.warns_on_release_miss);
    try std.testing.expect(cleanup.destroys_release_record_before_free);

    const source = try readRepoFile(std.testing.allocator, "lib/devres.zig");
    defer std.testing.allocator.free(source);
    try requireContains(source, ".provides_release_record_lifetime_planning = true");
    try requireContains(source, ".provides_release_call_planning = true");
    try requireContains(source, ".provides_dmam_free_coherent_cleanup_planning = true");
    try requireContains(source, "pub const ManagedReleaseCallPlan = struct");
    try requireContains(source, "pub fn planManagedReleaseCall(requested_size: u64, release_record_matches: bool) ManagedReleaseCallPlan");
    try requireContains(source, "const release_call = planManagedReleaseCall(requested_size, release_record_matches);");
    try requireContains(source, ".warns_on_release_miss = !release_record_matches");
    try requireContains(source, ".destroys_release_record_before_free = true");
}

test "phase13 devres warns when planned coherent free cannot find the devres record" {
    const cleanup = devres.DevresHelperLab.planManagedDmamFreeCoherent(4096, false);

    try std.testing.expectEqualStrings("lib/devres.c", cleanup.anchor);
    try std.testing.expectEqual(@as(u64, 4096), cleanup.requested_size);
    try std.testing.expect(cleanup.frees_allocation);
    try std.testing.expect(!cleanup.releases_from_devres);
    try std.testing.expect(!cleanup.release_record_consumed);
    try std.testing.expect(cleanup.warns_on_release_miss);
    try std.testing.expect(cleanup.destroys_release_record_before_free);
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

test "phase13 devres frees the release record for zero-sized coherent allocation planning" {
    const plan = try devres.DevresHelperLab.planManagedDmamAllocCoherent(.{
        .requested_size = 0,
        .release_record_allocated = true,
        .allocation_succeeds = true,
    });

    try std.testing.expectEqual(@as(u64, 0), plan.requested_size);
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
    try requireContains(manifest, "\"owned_surfaces\": [");
    try requireContains(manifest, "lib/devres.zig");
    try requireContains(manifest, "zigux/tests/phase13_devres_dmam_alloc_coherent_planner.zig");
    try requireContains(manifest, "\"release_record_lifetime_owner\": \"zigux/tests/phase13_devres_dmam_alloc_coherent_planner.zig\"");
    try requireContains(manifest, "\"release_call_owner\": \"zigux/tests/phase13_devres_dmam_alloc_coherent_planner.zig\"");
    try requireContains(manifest, "\"detach_cleanup_owner\": \"zigux/tests/phase13_devres_dmam_alloc_coherent_planner.zig\"");
    try requireContains(manifest, "\"zero_sized_request_owner\": \"zigux/tests/phase13_devres_dmam_alloc_coherent_planner.zig\"");
    try requireContains(manifest, "\"owner_map\": \"zigux/tests/phase13_devres_dmam_alloc_coherent_planner_manifest.json\"");
    try requireContains(manifest, "\"adjacent_boundary_evidence_only\": [");
    try requireContains(manifest, "zigux/tests/phase13_devres_dma_coherent.zig");
    try requireContains(manifest, "provides_release_record_lifetime_planning");
    try requireContains(manifest, "provides_release_call_planning");
    try requireContains(manifest, "provides_dmam_free_coherent_cleanup_planning");
    try requireContains(manifest, "planManagedReleaseRecordLifetime");
    try requireContains(manifest, "planManagedReleaseCall");
    try requireContains(manifest, "planManagedDmamFreeCoherent");
    try requireContains(manifest, "ManagedReleaseCallPlan");
    try requireContains(manifest, "zero-sized requests free the release record");
    try requireContains(manifest, "release_record_consumed");
    try requireContains(manifest, "releases_from_devres");
    try requireContains(manifest, "warns_on_release_miss");
    try requireContains(manifest, "destroys_release_record_before_free");
    try requireContains(manifest, "\"id\": \"phase13-devres-live-dmam-alloc-side-effects\"");
    try requireContains(manifest, "\"status\": \"blocked_on_dma_state\"");
    try requireContains(manifest, "\"id\": \"phase13-devres-live-scatterlist-ownership\"");
    try requireContains(manifest, "\"status\": \"blocked_on_scatterlist_state\"");
}

test "phase13 devres dmam_alloc_coherent planner note keeps the helper-first dma slice bounded" {
    const note = try readRepoFile(std.testing.allocator, "Documentation/zigux/phase13-devres-dmam-alloc-coherent-planner.md");
    defer std.testing.allocator.free(note);

    try requireContains(note, "lands one pure `dmam_alloc_coherent()` planning surface in `lib/devres.zig`");
    try requireContains(note, "descriptor records the shared release-record lifetime, release-call, and detach-cleanup planning markers");
    try requireContains(note, "routes `planManagedDmamAllocCoherent(...)` through `planManagedReleaseRecordLifetime(...)`");
    try requireContains(note, "promotes the coherent-free release-call shape into explicit shared helper planning through `planManagedReleaseCall(...)`");
    try requireContains(note, "routes `planManagedDmamFreeCoherent(...)` through that shared release-call helper");
    try requireContains(note, "accepts already-decided allocation inputs rather than talking to live hardware state");
    try requireContains(note, "retains detach-time cleanup ownership on success");
    try requireContains(note, "turns that successful allocation plan into explicit detach cleanup planning through `planManagedDmamFreeCoherent(...)`");
    try requireContains(note, "records whether that planned coherent free consumes the retained release record and releases the allocation from devres");
    try requireContains(note, "records that the planned coherent free destroys the release record before freeing the allocation");
    try requireContains(note, "records whether a missing release record still frees the allocation while surfacing a warn-on-release-miss outcome");
    try requireContains(note, "failed allocation frees the release record");
    try requireContains(note, "zero-sized requests free the release record and avoid retaining detach-time cleanup ownership");
    try requireContains(note, "Fixture governance stays helper-local:");
    try requireContains(note, "`zigux/tests/phase13_devres_dmam_alloc_coherent_planner.zig` owns the retained-release-record, release-call, freed-release-record, zero-sized-request, missing-release-record, detach-cleanup, and warn-on-release-miss fixture coverage");
    try requireContains(note, "`zigux/tests/phase13_devres_dmam_alloc_coherent_planner_manifest.json` is the packet-local owner map");
    try requireContains(note, "`zigux/tests/phase13_devres_dma_coherent.zig` remains adjacent boundary evidence only");
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
