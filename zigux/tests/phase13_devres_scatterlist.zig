const std = @import("std");
const devres_scatterlist = @import("devres_scatterlist");

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

test "phase13 devres descriptor records helper-first scatterlist planning" {
    const descriptor = devres_scatterlist.DevresScatterlistHelper.descriptor();

    try std.testing.expectEqualStrings("devres_scatterlist_helper", descriptor.name);
    try std.testing.expectEqualStrings("lib/devres.c", descriptor.anchor);
    try std.testing.expect(descriptor.provides_scatterlist_lifetime_planning);
    try std.testing.expect(descriptor.provides_scatterlist_table_teardown_planning);
    try std.testing.expect(!descriptor.touches_live_dma);
    try std.testing.expect(!descriptor.touches_live_scatterlist);
}

test "phase13 devres scatterlist helper stays planning-only at the boundary" {
    const helper = try readRepoFile(std.testing.allocator, "lib/devres_scatterlist.zig");
    defer std.testing.allocator.free(helper);

    try requireContains(helper, ".provides_scatterlist_lifetime_planning = true");
    try requireContains(helper, ".provides_scatterlist_table_teardown_planning = true");
    try requireContains(helper, ".touches_live_dma = false");
    try requireContains(helper, ".touches_live_scatterlist = false");
    try requireContains(helper, "pub fn planManagedScatterlistMap");
    try requireContains(helper, "pub fn scatterlistReleaseMatches");
    try requireContains(helper, "pub fn planManagedScatterlistUnmap");
    try requireContains(helper, "pub fn planManagedScatterlistTableTeardown");
    try requireAbsent(helper, "dma_map_sg(");
    try requireAbsent(helper, "dma_unmap_sg(");
    try requireAbsent(helper, "dma_map_sgtable(");
    try requireAbsent(helper, "sg_alloc_table(");
    try requireAbsent(helper, "sg_free_table(");
    try requireAbsent(helper, "sg_dma_address(");
    try requireAbsent(helper, "sg_dma_len(");
    try requireAbsent(helper, "struct scatterlist");
    try requireAbsent(helper, "sg_table");
}

test "phase13 devres retains the release record when helper-first scatterlist planning succeeds" {
    const plan = try devres_scatterlist.DevresScatterlistHelper.planManagedScatterlistMap(.{
        .original_entries = 6,
        .mapped_entries = 4,
        .release_record_allocated = true,
    });

    try std.testing.expectEqualStrings("lib/devres.c", plan.anchor);
    try std.testing.expectEqual(@as(u32, 6), plan.original_entries);
    try std.testing.expectEqual(@as(u32, 4), plan.mapped_entries);
    try std.testing.expect(plan.mapping_ready);
    try std.testing.expect(plan.added_to_devres);
    try std.testing.expect(plan.release_record_retained);
    try std.testing.expect(!plan.release_record_freed);
    try std.testing.expect(plan.should_unmap_on_detach);
}

test "phase13 devres frees the scatterlist release record when no mapped segments are returned" {
    const plan = try devres_scatterlist.DevresScatterlistHelper.planManagedScatterlistMap(.{
        .original_entries = 6,
        .mapped_entries = 0,
        .release_record_allocated = true,
    });

    try std.testing.expectEqual(@as(u32, 6), plan.original_entries);
    try std.testing.expectEqual(@as(u32, 0), plan.mapped_entries);
    try std.testing.expect(!plan.mapping_ready);
    try std.testing.expect(!plan.added_to_devres);
    try std.testing.expect(!plan.release_record_retained);
    try std.testing.expect(plan.release_record_freed);
    try std.testing.expect(!plan.should_unmap_on_detach);
}

test "phase13 devres frees the scatterlist release record when mapped segments exceed the original count" {
    const plan = try devres_scatterlist.DevresScatterlistHelper.planManagedScatterlistMap(.{
        .original_entries = 3,
        .mapped_entries = 5,
        .release_record_allocated = true,
    });

    try std.testing.expectEqual(@as(u32, 3), plan.original_entries);
    try std.testing.expectEqual(@as(u32, 5), plan.mapped_entries);
    try std.testing.expect(!plan.mapping_ready);
    try std.testing.expect(!plan.added_to_devres);
    try std.testing.expect(!plan.release_record_retained);
    try std.testing.expect(plan.release_record_freed);
    try std.testing.expect(!plan.should_unmap_on_detach);
}

test "phase13 devres rejects scatterlist planning when the release record cannot be allocated" {
    try std.testing.expectError(error.OutOfMemory, devres_scatterlist.DevresScatterlistHelper.planManagedScatterlistMap(.{
        .original_entries = 2,
        .mapped_entries = 2,
        .release_record_allocated = false,
    }));
}

test "phase13 devres scatterlist release matching stays exact across original and mapped counts" {
    const exact = devres_scatterlist.DevresScatterlistHelper.planManagedScatterlistUnmap(6, 4, 6, 4);
    try std.testing.expectEqualStrings("lib/devres.c", exact.anchor);
    try std.testing.expectEqual(@as(u32, 6), exact.tracked_original_entries);
    try std.testing.expectEqual(@as(u32, 4), exact.tracked_mapped_entries);
    try std.testing.expectEqual(@as(u32, 6), exact.candidate_original_entries);
    try std.testing.expectEqual(@as(u32, 4), exact.candidate_mapped_entries);
    try std.testing.expect(exact.release_matches);
    try std.testing.expect(!exact.warns_on_release_miss);
}

test "phase13 devres scatterlist unmap planning warns when release counts drift" {
    const miss = devres_scatterlist.DevresScatterlistHelper.planManagedScatterlistUnmap(6, 4, 6, 3);
    try std.testing.expectEqualStrings("lib/devres.c", miss.anchor);
    try std.testing.expectEqual(@as(u32, 6), miss.tracked_original_entries);
    try std.testing.expectEqual(@as(u32, 4), miss.tracked_mapped_entries);
    try std.testing.expectEqual(@as(u32, 6), miss.candidate_original_entries);
    try std.testing.expectEqual(@as(u32, 3), miss.candidate_mapped_entries);
    try std.testing.expect(!miss.release_matches);
    try std.testing.expect(miss.warns_on_release_miss);
}

test "phase13 devres scatterlist table teardown becomes free-ready once mapped entries drain" {
    const plan = devres_scatterlist.DevresScatterlistHelper.planManagedScatterlistTableTeardown(.{
        .original_entries = 6,
        .mapped_entries = 0,
        .table_initialized = true,
        .release_record_present = true,
    });

    try std.testing.expectEqualStrings("lib/devres.c", plan.anchor);
    try std.testing.expectEqual(@as(u32, 6), plan.original_entries);
    try std.testing.expectEqual(@as(u32, 0), plan.mapped_entries);
    try std.testing.expect(plan.table_initialized);
    try std.testing.expect(plan.release_record_present);
    try std.testing.expect(plan.free_table_ready);
    try std.testing.expect(!plan.requires_unmap_before_free);
    try std.testing.expect(!plan.warns_on_missing_release_record);
    try std.testing.expect(!plan.warns_on_overmapped_release);
}

test "phase13 devres scatterlist table teardown requires unmap before free when mapped entries remain" {
    const plan = devres_scatterlist.DevresScatterlistHelper.planManagedScatterlistTableTeardown(.{
        .original_entries = 6,
        .mapped_entries = 2,
        .table_initialized = true,
        .release_record_present = true,
    });

    try std.testing.expect(!plan.free_table_ready);
    try std.testing.expect(plan.requires_unmap_before_free);
    try std.testing.expect(!plan.warns_on_missing_release_record);
    try std.testing.expect(!plan.warns_on_overmapped_release);
}

test "phase13 devres scatterlist table teardown warns when the release record is missing" {
    const plan = devres_scatterlist.DevresScatterlistHelper.planManagedScatterlistTableTeardown(.{
        .original_entries = 4,
        .mapped_entries = 0,
        .table_initialized = true,
        .release_record_present = false,
    });

    try std.testing.expect(!plan.free_table_ready);
    try std.testing.expect(!plan.requires_unmap_before_free);
    try std.testing.expect(plan.warns_on_missing_release_record);
    try std.testing.expect(!plan.warns_on_overmapped_release);
}

test "phase13 devres scatterlist table teardown warns on overmapped release drift" {
    const plan = devres_scatterlist.DevresScatterlistHelper.planManagedScatterlistTableTeardown(.{
        .original_entries = 3,
        .mapped_entries = 5,
        .table_initialized = true,
        .release_record_present = true,
    });

    try std.testing.expect(!plan.free_table_ready);
    try std.testing.expect(!plan.requires_unmap_before_free);
    try std.testing.expect(!plan.warns_on_missing_release_record);
    try std.testing.expect(plan.warns_on_overmapped_release);
}

test "phase13 devres scatterlist planner manifest records the dedicated helper-first packet" {
    const manifest = try readRepoFile(std.testing.allocator, "zigux/tests/phase13_devres_scatterlist_planner_manifest.json");
    defer std.testing.allocator.free(manifest);

    try requireContains(manifest, "\"lane_key\": \"P13-L08\"");
    try requireContains(manifest, "\"phase\": \"Phase 13\"");
    try requireContains(manifest, "\"packet\": \"phase13-devres-scatterlist-planner\"");
    try requireContains(manifest, "\"status\": \"starter_landed\"");
    try requireContains(manifest, "\"owned_surfaces\": [");
    try requireContains(manifest, "lib/devres_scatterlist.zig");
    try requireContains(manifest, "Documentation/zigux/phase13-devres-scatterlist-planner.md");
    try requireContains(manifest, "Documentation/zigux/phase13-devres-scatterlist-slice.md");
    try requireContains(manifest, "zigux/tests/phase13_devres_scatterlist.zig");
    try requireContains(manifest, "zigux/tests/phase13_devres_scatterlist_build.zig");
    try requireContains(manifest, "scripts/zigux/check-phase13-devres-scatterlist-planner.py");
    try requireContains(manifest, "\"scatterlist_lifetime_owner\": \"zigux/tests/phase13_devres_scatterlist.zig\"");
    try requireContains(manifest, "\"release_match_owner\": \"zigux/tests/phase13_devres_scatterlist.zig\"");
    try requireContains(manifest, "\"overmapped_request_owner\": \"zigux/tests/phase13_devres_scatterlist.zig\"");
    try requireContains(manifest, "\"warn_on_release_miss_owner\": \"zigux/tests/phase13_devres_scatterlist.zig\"");
    try requireContains(manifest, "\"scatterlist_table_teardown_owner\": \"zigux/tests/phase13_devres_scatterlist.zig\"");
    try requireContains(manifest, "\"slice_note_owner\": \"Documentation/zigux/phase13-devres-scatterlist-slice.md\"");
    try requireContains(manifest, "\"build_shard_owner\": \"zigux/tests/phase13_devres_scatterlist_build.zig\"");
    try requireContains(manifest, "\"validation_guard\": \"scripts/zigux/check-phase13-devres-scatterlist-planner.py\"");
    try requireContains(manifest, "\"owner_map\": \"zigux/tests/phase13_devres_scatterlist_planner_manifest.json\"");
    try requireContains(manifest, "planManagedScatterlistMap");
    try requireContains(manifest, "scatterlistReleaseMatches");
    try requireContains(manifest, "planManagedScatterlistUnmap");
    try requireContains(manifest, "planManagedScatterlistTableTeardown");
    try requireContains(manifest, "helper-first `sg_table` free eligibility stays reviewable");
    try requireContains(manifest, "requires unmap-before-free planning");
    try requireContains(manifest, "warn rather than claiming live `sg_table` lifecycle mutation");
    try requireContains(manifest, "impossible over-mapped scatterlist results free the release record");
    try requireContains(manifest, "warn-on-release-miss outcome");
    try requireContains(manifest, "phase13-devres-scatterlist-tests");
    try requireContains(manifest, "\"id\": \"phase13-devres-live-scatterlist-ownership\"");
    try requireContains(manifest, "\"status\": \"blocked_on_scatterlist_state\"");
    try requireContains(manifest, "\"id\": \"phase13-devres-live-sg-table-lifecycle\"");
    try requireContains(manifest, "\"status\": \"blocked_on_sg_table_lifecycle\"");
    try requireContains(manifest, "\"id\": \"phase13-devres-generic-dma-map-family\"");
    try requireContains(manifest, "\"status\": \"blocked_on_dma_mapping_state\"");
}

test "phase13 devres scatterlist planner note keeps the helper-first scatterlist slice bounded" {
    const note = try readRepoFile(std.testing.allocator, "Documentation/zigux/phase13-devres-scatterlist-planner.md");
    defer std.testing.allocator.free(note);

    try requireContains(note, "lands one pure scatterlist lifetime planning surface in `lib/devres_scatterlist.zig`");
    try requireContains(note, "routes `planManagedScatterlistMap(...)` through one helper-local release-record outcome");
    try requireContains(note, "retains detach-time unmap ownership on success");
    try requireContains(note, "failed mapping frees the release record");
    try requireContains(note, "records whether impossible over-mapped scatterlist results free the release record and avoid retaining detach-time unmap ownership");
    try requireContains(note, "routes `planManagedScatterlistUnmap(...)` through exact original-entry and mapped-entry matching");
    try requireContains(note, "records whether a release-count mismatch surfaces a warn-on-release-miss outcome without claiming live unmap side effects");
    try requireContains(note, "exposes `scatterlistReleaseMatches(...)` as the helper-first exact-match check");
    try requireContains(note, "routes `planManagedScatterlistTableTeardown(...)` through initialized-table, release-record, and mapped-count gating");
    try requireContains(note, "records whether an initialized table becomes free-ready once mapped entries drain to zero and the release record is still present");
    try requireContains(note, "records whether mapped scatterlist state still requires unmap-before-free planning instead of claiming live table teardown");
    try requireContains(note, "records whether missing release records or over-mapped counts warn rather than claiming live `sg_table` lifecycle mutation");
    try requireContains(note, "`zigux/tests/phase13_devres_scatterlist.zig` owns the retained-release-record, freed-release-record, impossible-overmapped-request, missing-release-record, exact-release-match, warn-on-release-miss, free-ready-teardown, unmap-before-free, and overmapped-teardown-warning fixture coverage");
    try requireContains(note, "`Documentation/zigux/phase13-devres-scatterlist-slice.md` keeps the helper-local scope and non-goals aligned with this planner note, the manifest, and the replay");
    try requireContains(note, "`zigux/tests/phase13_devres_scatterlist_build.zig` keeps the dedicated build shard aligned with the helper-first scatterlist replay");
    try requireContains(note, "`scripts/zigux/check-phase13-devres-scatterlist-planner.py` is the packet-local validation guard");
    try requireContains(note, "`zigux/tests/phase13_devres_scatterlist_planner_manifest.json` is the packet-local owner map");
    try requireContains(note, "`zigux/tests/phase13_devres_dma_coherent.zig` remains adjacent boundary evidence only");
    try requireContains(note, "`Documentation/zigux/phase13-devres-survey.md` remains adjacent boundary evidence only");
    try requireContains(note, "sg_alloc_table()");
    try requireContains(note, "sg_free_table()");
    try requireContains(note, "sg_dma_address()");
    try requireContains(note, "sg_dma_len()");
    try requireContains(note, "dma_map_sg()");
    try requireContains(note, "dma_unmap_sg()");
    try requireContains(note, "dma_map_sgtable()");
    try requireContains(note, "sg_table");
}

test "phase13 devres scatterlist slice and build shard stay packet-local" {
    const slice = try readRepoFile(std.testing.allocator, "Documentation/zigux/phase13-devres-scatterlist-slice.md");
    defer std.testing.allocator.free(slice);

    try requireContains(slice, "helper-first scatterlist planner beside the existing `lib/devres.zig` and `lib/devres_dma_coherent.zig` packet");
    try requireContains(slice, "focused replay: `zigux/tests/phase13_devres_scatterlist.zig`");
    try requireContains(slice, "provides_scatterlist_table_teardown_planning = true");
    try requireContains(slice, "`planManagedScatterlistTableTeardown()` models helper-first `sg_table` teardown readiness");
    try requireContains(slice, "no live `dma_map_sgtable()` or `dma_unmap_sgtable()` execution");
    try requireContains(slice, "no `struct scatterlist`, `sg_table`, or `sg_*` iteration helpers");
    try requireContains(slice, "no live `sg_free_table()` lifecycle mutation or `sg_alloc_table()` ownership claims");

    const build = try readRepoFile(std.testing.allocator, "zigux/tests/phase13_devres_scatterlist_build.zig");
    defer std.testing.allocator.free(build);

    try requireContains(build, "phase13-devres-scatterlist-tests");
    try requireContains(build, "Run Phase 13 devres scatterlist helper tests");
    try requireContains(build, "../../lib/devres_scatterlist.zig");
    try requireContains(build, "phase13_devres_scatterlist.zig");
}

test "phase13 devres scatterlist planner note preserves standalone replay handles" {
    const note = try readRepoFile(std.testing.allocator, "Documentation/zigux/phase13-devres-scatterlist-planner.md");
    defer std.testing.allocator.free(note);

    try requireContains(note, "zig test --dep devres_scatterlist -Mroot=zigux/tests/phase13_devres_scatterlist.zig -Mdevres_scatterlist=lib/devres_scatterlist.zig");
    try requireContains(note, "zig build test --build-file zigux/tests/phase13_devres_scatterlist_build.zig");
    try requireContains(note, "python3 scripts/zigux/check-phase13-devres-scatterlist-planner.py");
    try requireContains(note, "python3 scripts/zigux/check-phase13-devres-scatterlist-planner.py --self-test");
    try requireContains(note, "zig test zigux/tests/phase13_devres_dma_coherent.zig");
}

test "phase13 devres scatterlist planner checker stays packet-local" {
    const checker = try readRepoFile(std.testing.allocator, "scripts/zigux/check-phase13-devres-scatterlist-planner.py");
    defer std.testing.allocator.free(checker);

    try requireContains(checker, "HELPER_PATH = Path(\"lib/devres_scatterlist.zig\")");
    try requireContains(checker, "NOTE_PATH = Path(\"Documentation/zigux/phase13-devres-scatterlist-planner.md\")");
    try requireContains(checker, "SLICE_PATH = Path(\"Documentation/zigux/phase13-devres-scatterlist-slice.md\")");
    try requireContains(checker, "MANIFEST_PATH = Path(\"zigux/tests/phase13_devres_scatterlist_planner_manifest.json\")");
    try requireContains(checker, "REPLAY_PATH = Path(\"zigux/tests/phase13_devres_scatterlist.zig\")");
    try requireContains(checker, "BUILD_PATH = Path(\"zigux/tests/phase13_devres_scatterlist_build.zig\")");
    try requireContains(checker, ".provides_scatterlist_table_teardown_planning = true");
    try requireContains(checker, "pub fn planManagedScatterlistTableTeardown");
    try requireContains(checker, "PHASE13_DEVRES_SCATTERLIST_PLANNER_SELF_TEST=pass");
    try requireContains(checker, "PHASE13_DEVRES_SCATTERLIST_PLANNER=pass");
}
