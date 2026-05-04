const std = @import("std");
const devres = @import("devres");

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectNotContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

test "phase13 devres of_iomap descriptor keeps the planner explicit" {
    const descriptor = devres.DevresHelperLab.descriptor();

    try std.testing.expectEqualStrings("lib/devres.c", descriptor.anchor);
    try std.testing.expect(descriptor.provides_of_iomap_planning);

    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const devres_source = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "lib/devres.zig",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(devres_source);

    try expectContains(devres_source, ".provides_of_iomap_planning = true");
    try expectContains(devres_source, "pub fn planDeviceTreeIomap(");
    try expectContains(devres_source, "reported_size = if (input.report_size) translated_size else null;");
    try expectContains(devres_source, ".fail_pretty_name_allocation = input.fail_pretty_name_allocation,");
    try expectContains(devres_source, ".stage = .managed_ioremap_resource");
    try expectNotContains(devres_source, "struct device_node");
}

test "phase13 devres of_iomap planner keeps translated size explicit on success" {
    const resources = [_]devres.Resource{
        .{
            .start = 0x7000,
            .end = 0x70ff,
            .is_memory = true,
            .nonposted = false,
            .name = "ctrl",
        },
        .{
            .start = 0x7100,
            .end = 0x717f,
            .is_memory = true,
            .nonposted = true,
            .name = "data",
        },
    };

    const outcome = try devres.DevresHelperLab.planDeviceTreeIomap(std.testing.allocator, .{
        .device_name = "uart1",
        .index = 1,
        .resources = &resources,
        .report_size = true,
    });

    switch (outcome) {
        .mapped => |plan| {
            defer std.testing.allocator.free(plan.mapping.pretty_name);
            try std.testing.expectEqualStrings("lib/devres.c", plan.anchor);
            try std.testing.expectEqual(@as(usize, 1), plan.index);
            try std.testing.expectEqual(@as(?u64, 0x80), plan.reported_size);
            try std.testing.expectEqualStrings("uart1 data", plan.mapping.pretty_name);
            try std.testing.expectEqual(devres.IoremapType.np, plan.mapping.effective_type);
            try std.testing.expect(plan.mapping.requests_region);
            try std.testing.expect(!plan.mapping.releases_region_on_remap_failure);
        },
        .err => return error.UnexpectedFailure,
    }
}

test "phase13 devres of_iomap planner rejects address-translation misses before managed remap" {
    const resources = [_]devres.Resource{
        .{
            .start = 0x8000,
            .end = 0x801f,
            .is_memory = true,
            .nonposted = false,
            .name = "only",
        },
    };

    const outcome = try devres.DevresHelperLab.planDeviceTreeIomap(std.testing.allocator, .{
        .device_name = "uart2",
        .index = 2,
        .resources = &resources,
        .report_size = true,
    });

    switch (outcome) {
        .mapped => return error.ExpectedFailure,
        .err => |failure| {
            try std.testing.expectEqualStrings("lib/devres.c", failure.anchor);
            try std.testing.expectEqual(devres.DeviceTreeIomapStage.address_translation, failure.stage);
            try std.testing.expectEqual(devres.ErrorCode.invalid, failure.error_code);
            try std.testing.expectEqual(@as(usize, 2), failure.index);
            try std.testing.expectEqual(@as(?u64, null), failure.reported_size);
            try std.testing.expectEqual(devres.IoremapType.normal, failure.effective_type);
            try std.testing.expect(!failure.requests_region);
            try std.testing.expect(!failure.releases_region_on_remap_failure);
            try std.testing.expectEqual(@as(?devres.ErrorStage, null), failure.resource_stage);
        },
    }
}

test "phase13 devres of_iomap planner preserves translated size on pretty-name allocation failure" {
    const resources = [_]devres.Resource{
        .{
            .start = 0x8400,
            .end = 0x847f,
            .is_memory = true,
            .nonposted = true,
            .name = "regs",
        },
    };

    const outcome = try devres.DevresHelperLab.planDeviceTreeIomap(std.testing.allocator, .{
        .device_name = "spi2",
        .index = 0,
        .resources = &resources,
        .report_size = true,
        .fail_pretty_name_allocation = true,
    });

    switch (outcome) {
        .mapped => return error.ExpectedFailure,
        .err => |failure| {
            try std.testing.expectEqualStrings("lib/devres.c", failure.anchor);
            try std.testing.expectEqual(devres.DeviceTreeIomapStage.managed_ioremap_resource, failure.stage);
            try std.testing.expectEqual(devres.ErrorCode.no_memory, failure.error_code);
            try std.testing.expectEqual(@as(usize, 0), failure.index);
            try std.testing.expectEqual(@as(?u64, 0x80), failure.reported_size);
            try std.testing.expectEqual(devres.IoremapType.np, failure.effective_type);
            try std.testing.expect(!failure.requests_region);
            try std.testing.expect(!failure.releases_region_on_remap_failure);
            try std.testing.expectEqual(@as(?devres.ErrorStage, .pretty_name), failure.resource_stage);
        },
    }
}

test "phase13 devres of_iomap planner preserves translated size on request-region denial" {
    const resources = [_]devres.Resource{
        .{
            .start = 0x8800,
            .end = 0x88ff,
            .is_memory = true,
            .nonposted = false,
            .name = "busy",
        },
    };

    const outcome = try devres.DevresHelperLab.planDeviceTreeIomap(std.testing.allocator, .{
        .device_name = "uart3",
        .index = 0,
        .resources = &resources,
        .report_size = true,
        .request_region_granted = false,
    });

    switch (outcome) {
        .mapped => return error.ExpectedFailure,
        .err => |failure| {
            try std.testing.expectEqualStrings("lib/devres.c", failure.anchor);
            try std.testing.expectEqual(devres.DeviceTreeIomapStage.managed_ioremap_resource, failure.stage);
            try std.testing.expectEqual(devres.ErrorCode.busy, failure.error_code);
            try std.testing.expectEqual(@as(usize, 0), failure.index);
            try std.testing.expectEqual(@as(?u64, 0x100), failure.reported_size);
            try std.testing.expectEqual(devres.IoremapType.normal, failure.effective_type);
            try std.testing.expect(failure.requests_region);
            try std.testing.expect(!failure.releases_region_on_remap_failure);
            try std.testing.expectEqual(@as(?devres.ErrorStage, .request_region), failure.resource_stage);
        },
    }
}

test "phase13 devres of_iomap planner preserves translated size on downstream remap failure" {
    const resources = [_]devres.Resource{
        .{
            .start = 0x9000,
            .end = 0x903f,
            .is_memory = true,
            .nonposted = false,
            .name = "regs",
        },
    };

    const outcome = try devres.DevresHelperLab.planDeviceTreeIomap(std.testing.allocator, .{
        .device_name = "spi0",
        .index = 0,
        .resources = &resources,
        .report_size = true,
        .remap_succeeds = false,
    });

    switch (outcome) {
        .mapped => return error.ExpectedFailure,
        .err => |failure| {
            try std.testing.expectEqualStrings("lib/devres.c", failure.anchor);
            try std.testing.expectEqual(devres.DeviceTreeIomapStage.managed_ioremap_resource, failure.stage);
            try std.testing.expectEqual(devres.ErrorCode.no_memory, failure.error_code);
            try std.testing.expectEqual(@as(usize, 0), failure.index);
            try std.testing.expectEqual(@as(?u64, 0x40), failure.reported_size);
            try std.testing.expectEqual(devres.IoremapType.normal, failure.effective_type);
            try std.testing.expect(failure.requests_region);
            try std.testing.expect(failure.releases_region_on_remap_failure);
            try std.testing.expectEqual(@as(?devres.ErrorStage, .remap), failure.resource_stage);
        },
    }
}
