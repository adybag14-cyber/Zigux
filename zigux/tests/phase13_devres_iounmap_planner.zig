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

test "phase13 devres descriptor records helper-first iounmap cleanup planning" {
    const descriptor = devres.DevresHelperLab.descriptor();

    try std.testing.expectEqualStrings("devres_helper_lab", descriptor.name);
    try std.testing.expectEqualStrings("lib/devres.c", descriptor.anchor);
    try std.testing.expect(descriptor.provides_iounmap_cleanup_planning);
    try std.testing.expect(!descriptor.touches_live_mmio);
}

test "phase13 devres consumes the release record when helper-first iounmap cleanup matches" {
    const cleanup = devres.DevresHelperLab.planManagedIounmapCleanup(true, true);

    try std.testing.expectEqualStrings("lib/devres.c", cleanup.anchor);
    try std.testing.expect(cleanup.had_mapping_owner);
    try std.testing.expect(cleanup.generates_cleanup_plan);
    try std.testing.expect(cleanup.unmaps_mapping);
    try std.testing.expect(cleanup.releases_from_devres);
    try std.testing.expect(cleanup.release_record_consumed);
    try std.testing.expect(!cleanup.warns_on_release_miss);
}

test "phase13 devres still plans iounmap cleanup when the release record is missing" {
    const cleanup = devres.DevresHelperLab.planManagedIounmapCleanup(true, false);

    try std.testing.expect(cleanup.had_mapping_owner);
    try std.testing.expect(cleanup.generates_cleanup_plan);
    try std.testing.expect(cleanup.unmaps_mapping);
    try std.testing.expect(!cleanup.releases_from_devres);
    try std.testing.expect(!cleanup.release_record_consumed);
    try std.testing.expect(cleanup.warns_on_release_miss);
}

test "phase13 devres skips iounmap cleanup when no mapping owner exists" {
    const cleanup = devres.DevresHelperLab.planManagedIounmapCleanup(false, true);

    try std.testing.expect(!cleanup.had_mapping_owner);
    try std.testing.expect(!cleanup.generates_cleanup_plan);
    try std.testing.expect(!cleanup.unmaps_mapping);
    try std.testing.expect(!cleanup.releases_from_devres);
    try std.testing.expect(!cleanup.release_record_consumed);
    try std.testing.expect(!cleanup.warns_on_release_miss);
}

test "phase13 devres iounmap planner manifest records the landed helper-first mmio scope" {
    const manifest = try readRepoFile(std.testing.allocator, "zigux/tests/phase13_devres_iounmap_planner_manifest.json");
    defer std.testing.allocator.free(manifest);

    try requireContains(manifest, "\"lane_key\": \"P13-L09\"");
    try requireContains(manifest, "\"phase\": \"Phase 13\"");
    try requireContains(manifest, "\"packet\": \"phase13-devres-iounmap-planner\"");
    try requireContains(manifest, "\"status\": \"starter_landed\"");
    try requireContains(manifest, "lib/devres.zig");
    try requireContains(manifest, "Documentation/zigux/phase13-devres-iounmap-planner.md");
    try requireContains(manifest, "zigux/tests/phase13_devres_iounmap_planner.zig");
    try requireContains(manifest, "scripts/zigux/check-phase13-devres-iounmap-planner.py");
    try requireContains(manifest, "\"iounmap_cleanup_owner\": \"zigux/tests/phase13_devres_iounmap_planner.zig\"");
    try requireContains(manifest, "\"warn_on_release_miss_owner\": \"zigux/tests/phase13_devres_iounmap_planner.zig\"");
    try requireContains(manifest, "planManagedIounmapCleanup");
    try requireContains(manifest, "\"id\": \"phase13-devres-missing-devm-ioremap-np-surface\"");
    try requireContains(manifest, "\"id\": \"phase13-devres-missing-devm-of-iomap-surface\"");
    try requireContains(manifest, "\"id\": \"phase13-devres-live-mmio-mapping-state\"");
}

test "phase13 devres iounmap planner note keeps the helper-first mmio slice bounded" {
    const note = try readRepoFile(std.testing.allocator, "Documentation/zigux/phase13-devres-iounmap-planner.md");
    defer std.testing.allocator.free(note);

    try requireContains(note, "lands one pure `devm_iounmap()` cleanup planning surface in `lib/devres.zig`");
    try requireContains(note, "exposes `planManagedIounmapCleanup(...)`");
    try requireContains(note, "records whether a tracked mapping owner generates cleanup work");
    try requireContains(note, "records whether a missing release record still unmaps the tracked mapping while surfacing a warn-on-release-miss outcome");
    try requireContains(note, "does not claim live MMIO mapping state");
    try requireContains(note, "devm_ioremap_np()");
    try requireContains(note, "devm_of_iomap()");
    try requireContains(note, "devm_arch_phys_wc_add()");
    try requireContains(note, "devm_arch_io_reserve_memtype_wc()");
}

test "phase13 devres survey records the landed helper-first iounmap planner and remaining mmio gaps" {
    const survey = try readRepoFile(std.testing.allocator, "Documentation/zigux/phase13-devres-survey.md");
    defer std.testing.allocator.free(survey);

    try requireContains(survey, "`Documentation/zigux/phase13-devres-iounmap-planner.md` records a landed pure `devm_iounmap()` cleanup planning surface");
    try requireContains(survey, "`zigux/tests/phase13_devres_iounmap_planner_manifest.json` marks the packet as `starter_landed`");
    try requireContains(survey, "helper-first iounmap cleanup planning through `planManagedIounmapCleanup(...)`");
    try requireContains(survey, "blocked `phase13-devres-missing-devm-ioremap-np-surface`");
    try requireContains(survey, "blocked `phase13-devres-missing-devm-of-iomap-surface`");
    try requireContains(survey, "blocked `phase13-devres-live-mmio-mapping-state`");
}

test "phase13 devres slice records the helper-first iounmap packet in current evidence" {
    const slice = try readRepoFile(std.testing.allocator, "Documentation/zigux/phase13-devres-slice.md");
    defer std.testing.allocator.free(slice);

    try requireContains(slice, "`Documentation/zigux/phase13-devres-iounmap-planner.md`");
    try requireContains(slice, "`zigux/tests/phase13_devres_iounmap_planner.zig`");
    try requireContains(slice, "`scripts/zigux/check-phase13-devres-iounmap-planner.py`");
    try requireContains(slice, "current packet helper-first, planning-only, and MMIO-bounded");
}

test "phase13 devres iounmap planner checker stays packet-local" {
    const checker = try readRepoFile(std.testing.allocator, "scripts/zigux/check-phase13-devres-iounmap-planner.py");
    defer std.testing.allocator.free(checker);

    try requireContains(checker, "HELPER_PATH = Path(\"lib/devres.zig\")");
    try requireContains(checker, "NOTE_PATH = Path(\"Documentation/zigux/phase13-devres-iounmap-planner.md\")");
    try requireContains(checker, "MANIFEST_PATH = Path(\"zigux/tests/phase13_devres_iounmap_planner_manifest.json\")");
    try requireContains(checker, "REPLAY_PATH = Path(\"zigux/tests/phase13_devres_iounmap_planner.zig\")");
    try requireContains(checker, "PHASE13_DEVRES_IOUNMAP_PLANNER_SELF_TEST=pass");
    try requireContains(checker, "PHASE13_DEVRES_IOUNMAP_PLANNER=pass");
}
