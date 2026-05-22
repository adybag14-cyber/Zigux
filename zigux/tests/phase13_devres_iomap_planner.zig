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

test "phase13 devres descriptor records helper-first iomap planning" {
    const descriptor = devres.DevresHelperLab.descriptor();

    try std.testing.expectEqualStrings("devres_helper_lab", descriptor.name);
    try std.testing.expectEqualStrings("lib/devres.c", descriptor.anchor);
    try std.testing.expect(descriptor.provides_of_iomap_planning);
    try std.testing.expect(!descriptor.touches_live_mmio);
}

test "phase13 devres iomap planning stops before managed ioremap resource when translation is missing" {
    const plan = devres.DevresHelperLab.planDeviceTreeIomap(.{
        .index = 2,
        .translated_size = 4096,
        .translation_ready = false,
        .requests_region = true,
        .request_region_available = true,
        .remap_succeeds = true,
        .nonposted = true,
    });

    try std.testing.expectEqual(@as(u32, 2), plan.index);
    try std.testing.expectEqual(@as(u64, 4096), plan.translated_size);
    try std.testing.expect(!plan.translation_ready);
    try std.testing.expect(!plan.reaches_managed_ioremap_resource);
    try std.testing.expect(!plan.requests_region);
    try std.testing.expect(!plan.request_region_denied);
    try std.testing.expect(!plan.releases_region_on_remap_failure);
    try std.testing.expect(!plan.remap_ready);
    try std.testing.expect(!plan.keeps_nonposted_mapping_type);
}

test "phase13 devres iomap planning preserves translated size on request-region denial" {
    const plan = devres.DevresHelperLab.planDeviceTreeIomap(.{
        .index = 1,
        .translated_size = 8192,
        .translation_ready = true,
        .requests_region = true,
        .request_region_available = false,
        .remap_succeeds = true,
        .nonposted = true,
    });

    try std.testing.expectEqual(@as(u32, 1), plan.index);
    try std.testing.expectEqual(@as(u64, 8192), plan.translated_size);
    try std.testing.expect(plan.translation_ready);
    try std.testing.expect(plan.reaches_managed_ioremap_resource);
    try std.testing.expect(plan.requests_region);
    try std.testing.expect(plan.request_region_denied);
    try std.testing.expect(!plan.releases_region_on_remap_failure);
    try std.testing.expect(!plan.remap_ready);
    try std.testing.expect(plan.keeps_nonposted_mapping_type);
}

test "phase13 devres iomap planning reaches helper-first remap when translation succeeds without a region request" {
    const plan = devres.DevresHelperLab.planDeviceTreeIomap(.{
        .index = 3,
        .translated_size = 16384,
        .translation_ready = true,
        .requests_region = false,
        .request_region_available = true,
        .remap_succeeds = true,
        .nonposted = true,
    });

    try std.testing.expectEqual(@as(u32, 3), plan.index);
    try std.testing.expectEqual(@as(u64, 16384), plan.translated_size);
    try std.testing.expect(plan.translation_ready);
    try std.testing.expect(plan.reaches_managed_ioremap_resource);
    try std.testing.expect(!plan.requests_region);
    try std.testing.expect(!plan.request_region_denied);
    try std.testing.expect(!plan.releases_region_on_remap_failure);
    try std.testing.expect(plan.remap_ready);
    try std.testing.expect(plan.keeps_nonposted_mapping_type);
}

test "phase13 devres iomap planning releases the requested region when remap later fails" {
    const plan = devres.DevresHelperLab.planDeviceTreeIomap(.{
        .index = 0,
        .translated_size = 4096,
        .translation_ready = true,
        .requests_region = true,
        .request_region_available = true,
        .remap_succeeds = false,
        .nonposted = false,
    });

    try std.testing.expectEqual(@as(u32, 0), plan.index);
    try std.testing.expectEqual(@as(u64, 4096), plan.translated_size);
    try std.testing.expect(plan.translation_ready);
    try std.testing.expect(plan.reaches_managed_ioremap_resource);
    try std.testing.expect(plan.requests_region);
    try std.testing.expect(!plan.request_region_denied);
    try std.testing.expect(plan.releases_region_on_remap_failure);
    try std.testing.expect(!plan.remap_ready);
    try std.testing.expect(!plan.keeps_nonposted_mapping_type);
}

test "phase13 devres iomap planner manifest records the landed helper-first mmio scope" {
    const manifest = try readRepoFile(std.testing.allocator, "zigux/tests/phase13_devres_iomap_planner_manifest.json");
    defer std.testing.allocator.free(manifest);

    try requireContains(manifest, "\"lane_key\": \"P13-L02\"");
    try requireContains(manifest, "\"phase\": \"Phase 13\"");
    try requireContains(manifest, "\"packet\": \"phase13-devres-iomap-planner\"");
    try requireContains(manifest, "\"status\": \"starter_landed\"");
    try requireContains(manifest, "lib/devres.zig");
    try requireContains(manifest, "Documentation/zigux/phase13-devres-iomap-planner.md");
    try requireContains(manifest, "zigux/tests/phase13_devres_iomap_planner.zig");
    try requireContains(manifest, "scripts/zigux/check-phase13-devres-iomap-planner.py");
    try requireContains(manifest, "\"translation_miss_owner\": \"zigux/tests/phase13_devres_iomap_planner.zig\"");
    try requireContains(manifest, "\"request_region_denial_owner\": \"zigux/tests/phase13_devres_iomap_planner.zig\"");
    try requireContains(manifest, "planDeviceTreeIomap");
    try requireContains(manifest, "\"id\": \"phase13-devres-missing-devm-ioremap-np-surface\"");
    try requireContains(manifest, "\"id\": \"phase13-devres-live-device-tree-walks\"");
    try requireContains(manifest, "\"id\": \"phase13-devres-live-mmio-mapping-state\"");
}

test "phase13 devres iomap planner note keeps the helper-first mmio slice bounded" {
    const note = try readRepoFile(std.testing.allocator, "Documentation/zigux/phase13-devres-iomap-planner.md");
    defer std.testing.allocator.free(note);

    try requireContains(note, "lands one pure `devm_of_iomap()` planning surface in `lib/devres.zig`");
    try requireContains(note, "exposes `planDeviceTreeIomap(...)`");
    try requireContains(note, "translated size is preserved when a requested region is denied as busy");
    try requireContains(note, "requested region is released again when remap later fails");
    try requireContains(note, "requested non-posted mapping type stays attached to the planning surface");
    try requireContains(note, "does not claim live MMIO mapping state");
    try requireContains(note, "devm_ioremap_np()");
    try requireContains(note, "devm_iounmap()");
    try requireContains(note, "devm_arch_phys_wc_add()");
    try requireContains(note, "devm_arch_io_reserve_memtype_wc()");
}

test "phase13 devres survey records the landed helper-first iomap planner and remaining mmio gaps" {
    const survey = try readRepoFile(std.testing.allocator, "Documentation/zigux/phase13-devres-survey.md");
    defer std.testing.allocator.free(survey);

    try requireContains(survey, "helper-first iomap planning evidence");
    try requireContains(survey, "`Documentation/zigux/phase13-devres-iomap-planner.md` records a landed pure `devm_of_iomap()` planning surface");
    try requireContains(survey, "`zigux/tests/phase13_devres_iomap_planner_manifest.json` marks the packet as `starter_landed`");
    try requireContains(survey, "helper-first iomap planning through `planDeviceTreeIomap(...)`");
    try requireContains(survey, "blocked `phase13-devres-missing-devm-ioremap-np-surface`");
    try requireContains(survey, "blocked `phase13-devres-live-mmio-mapping-state`");
}

test "phase13 devres slice records the helper-first iomap packet in current evidence" {
    const slice = try readRepoFile(std.testing.allocator, "Documentation/zigux/phase13-devres-slice.md");
    defer std.testing.allocator.free(slice);

    try requireContains(slice, "`Documentation/zigux/phase13-devres-iomap-planner.md`");
    try requireContains(slice, "`zigux/tests/phase13_devres_iomap_planner.zig`");
    try requireContains(slice, "`scripts/zigux/check-phase13-devres-iomap-planner.py`");
    try requireContains(slice, "current packet helper-first, planning-only, and MMIO-bounded");
}

test "phase13 devres iomap planner checker stays packet-local" {
    const checker = try readRepoFile(std.testing.allocator, "scripts/zigux/check-phase13-devres-iomap-planner.py");
    defer std.testing.allocator.free(checker);

    try requireContains(checker, "HELPER_PATH = Path(\"lib/devres.zig\")");
    try requireContains(checker, "NOTE_PATH = Path(\"Documentation/zigux/phase13-devres-iomap-planner.md\")");
    try requireContains(checker, "MANIFEST_PATH = Path(\"zigux/tests/phase13_devres_iomap_planner_manifest.json\")");
    try requireContains(checker, "REPLAY_PATH = Path(\"zigux/tests/phase13_devres_iomap_planner.zig\")");
    try requireContains(checker, "PHASE13_DEVRES_IOMAP_PLANNER_SELF_TEST=pass");
    try requireContains(checker, "PHASE13_DEVRES_IOMAP_PLANNER=pass");
}
