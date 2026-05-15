const std = @import("std");
const devres = @import("devres");

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

test "phase13 devres boundary evidence keeps the manifest-backed blocked surfaces explicit" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();
    const manifest = try std.Io.Dir.cwd().readFileAlloc(io_instance.io(), "zigux/tests/phase13_devres_manifest.json", std.testing.allocator, .limited(64 * 1024));
    defer std.testing.allocator.free(manifest);

    try requireContains(manifest, "\"preexisting_phase13_devres_boundary_evidence_present\": true");
    try requireContains(manifest, "\"id\": \"phase13-devres-boundary-evidence-gate\"");
    try requireContains(manifest, "\"zigux_destination\": \"zigux/tests/phase13_devres_boundary_evidence.zig\"");
    try requireContains(manifest, "\"id\": \"phase13-devres-live-region-reservation\"");
    try requireContains(manifest, "\"id\": \"phase13-devres-live-release-region-mutation\"");
    try requireContains(manifest, "\"id\": \"phase13-devres-live-device-tree-walk\"");
    try requireContains(manifest, "\"id\": \"phase13-devres-live-arch-memtype-state\"");
    try requireContains(manifest, "\"status\": \"blocked_on_live_mmio_state\"");
    try requireContains(manifest, "\"status\": \"blocked_on_live_device_tree_state\"");
    try requireContains(manifest, "\"status\": \"blocked_on_live_arch_memtype_state\"");
}

test "phase13 devres helper stays planner-only across region, device-tree, and arch memtype boundaries" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();
    const helper = try std.Io.Dir.cwd().readFileAlloc(io_instance.io(), "lib/devres.zig", std.testing.allocator, .limited(48 * 1024));
    defer std.testing.allocator.free(helper);

    try requireContains(helper, "pub fn planManagedIoremapResource(");
    try requireContains(helper, ".requests_region = true");
    try requireContains(helper, ".releases_region_on_remap_failure = true");
    try requireContains(helper, "pub fn planDeviceTreeIomap(");
    try requireContains(helper, "pub fn planArchIoReserveMemtypeWc(");
    try requireContains(helper, "pub fn planArchPhysWcAdd(");
    try requireAbsent(helper, "request_mem_region(");
    try requireAbsent(helper, "release_mem_region(");
    try requireAbsent(helper, "of_address_to_resource(");
    try requireAbsent(helper, "arch_phys_wc_del(");
}

test "phase13 devres boundary survey keeps the direct replay explicit beside the shared mmio packet" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();
    const survey = try std.Io.Dir.cwd().readFileAlloc(io_instance.io(), "Documentation/zigux/phase13-devres-survey.md", std.testing.allocator, .limited(32 * 1024));
    defer std.testing.allocator.free(survey);

    try requireContains(survey, "zigux/tests/phase13_devres_boundary_evidence.zig");
    try requireContains(survey, "direct boundary-evidence replay");
    try requireContains(survey, "live region reservation");
    try requireContains(survey, "live release-region mutation");
    try requireContains(survey, "live device-tree walking");
    try requireContains(survey, "live arch memtype state transitions");
    try requireContains(survey, "helper-only DMA/scatterlist boundary");
}

test "phase13 devres planners keep blocked region and translated-resource boundaries in planning-only form" {
    const busy = try devres.DevresHelperLab.planManagedIoremapResource(std.testing.allocator, .{
        .device_name = "eth0",
        .resource = .{ .start = 0x4000, .end = 0x40ff, .is_memory = true, .nonposted = false, .name = "mmio" },
        .request_region_granted = false,
    });
    switch (busy) {
        .mapped => return error.ExpectedFailure,
        .err => |failure| {
            try std.testing.expectEqual(devres.ErrorStage.request_region, failure.stage);
            try std.testing.expectEqual(devres.ErrorCode.busy, failure.error_code);
            try std.testing.expect(failure.requests_region);
            try std.testing.expect(!failure.releases_region_on_remap_failure);
        },
    }

    const remap_failure = try devres.DevresHelperLab.planManagedIoremapResource(std.testing.allocator, .{
        .device_name = "eth0",
        .resource = .{ .start = 0x5000, .end = 0x507f, .is_memory = true, .nonposted = false, .name = "mmio" },
        .remap_succeeds = false,
    });
    switch (remap_failure) {
        .mapped => return error.ExpectedFailure,
        .err => |failure| {
            try std.testing.expectEqual(devres.ErrorStage.remap, failure.stage);
            try std.testing.expectEqual(devres.ErrorCode.no_memory, failure.error_code);
            try std.testing.expect(failure.requests_region);
            try std.testing.expect(failure.releases_region_on_remap_failure);
        },
    }

    const translated = [_]devres.Resource{
        .{ .start = 0x7000, .end = 0x70ff, .is_memory = true, .nonposted = false, .name = "ctrl" },
    };
    const address_translation_failure = try devres.DevresHelperLab.planDeviceTreeIomap(std.testing.allocator, .{
        .device_name = "uart2",
        .index = 1,
        .resources = &translated,
        .report_size = true,
    });
    switch (address_translation_failure) {
        .mapped => return error.ExpectedFailure,
        .err => |failure| {
            try std.testing.expectEqual(devres.DeviceTreeIomapStage.address_translation, failure.stage);
            try std.testing.expectEqual(devres.ErrorCode.invalid, failure.error_code);
            try std.testing.expectEqual(@as(?u64, null), failure.reported_size);
            try std.testing.expect(!failure.requests_region);
        },
    }
}

test "phase13 devres planners keep blocked arch memtype boundaries in detach-bookkeeping form" {
    const memtype_failure = try devres.DevresHelperLab.planArchIoReserveMemtypeWc(.{
        .start = 0x7100,
        .size = 0x40,
        .release_record_allocated = true,
        .reserve_result = -16,
    });
    switch (memtype_failure) {
        .reserved => return error.ExpectedFailure,
        .err => |failure| {
            try std.testing.expectEqual(@as(i32, -16), failure.error_code);
            try std.testing.expect(!failure.added_to_devres);
            try std.testing.expect(!failure.release_record_retained);
            try std.testing.expect(failure.release_record_freed);
            try std.testing.expect(!failure.should_release_on_detach);
        },
    }

    const phys_wc_failure = try devres.DevresHelperLab.planArchPhysWcAdd(.{
        .start = 0x7400,
        .size = 0x80,
        .release_record_allocated = true,
        .token_result = -12,
    });
    switch (phys_wc_failure) {
        .added => return error.ExpectedFailure,
        .err => |failure| {
            try std.testing.expectEqual(@as(i32, -12), failure.error_code);
            try std.testing.expect(!failure.added_to_devres);
            try std.testing.expect(!failure.release_record_retained);
            try std.testing.expect(failure.release_record_freed);
            try std.testing.expect(!failure.should_remove_on_detach);
        },
    }
}
