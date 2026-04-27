const std = @import("std");
const devres = @import("devres");

test "phase13 devres descriptor stays anchored to lib/devres.c" {
    const descriptor = devres.DevresHelperLab.descriptor();

    try std.testing.expectEqualStrings("devres_helper_lab", descriptor.name);
    try std.testing.expectEqualStrings("lib/devres.c", descriptor.anchor);
    try std.testing.expect(descriptor.provides_ioremap_lifetime_planning);
    try std.testing.expect(descriptor.provides_ioremap_uc_wrapper_planning);
    try std.testing.expect(descriptor.provides_release_pointer_match);
    try std.testing.expect(descriptor.provides_ioport_lifetime_planning);
    try std.testing.expect(descriptor.provides_ioremap_resource_planning);
    try std.testing.expect(descriptor.provides_ioremap_resource_uc_planning);
    try std.testing.expect(descriptor.provides_ioremap_resource_wc_planning);
    try std.testing.expect(descriptor.provides_of_iomap_planning);
    try std.testing.expect(descriptor.provides_pretty_name_helper);
    try std.testing.expect(descriptor.provides_arch_phys_wc_token_planning);
    try std.testing.expect(descriptor.provides_arch_io_wc_memtype_planning);
    try std.testing.expect(!descriptor.touches_live_device_lists);
    try std.testing.expect(!descriptor.touches_live_mmio);
    try std.testing.expect(!descriptor.touches_live_arch_memtype);
}

test "phase13 devres retains the release record when managed ioremap succeeds" {
    const result = try devres.DevresHelperLab.planManagedIoremapAcquire(.{
        .kind = .write_combined,
        .release_record_allocated = true,
        .mapped_address = 0x1000,
    });

    try std.testing.expectEqualStrings("lib/devres.c", result.anchor);
    try std.testing.expectEqual(devres.ManagedIoremapKind.write_combined, result.kind);
    try std.testing.expectEqual(@as(?usize, 0x1000), result.mapped_address);
    try std.testing.expect(result.added_to_devres);
    try std.testing.expect(result.release_record_retained);
    try std.testing.expect(!result.release_record_freed);
    try std.testing.expect(result.should_unmap_on_detach);
}

test "phase13 devres frees the release record when mapping fails after allocation" {
    const result = try devres.DevresHelperLab.planManagedIoremapAcquire(.{
        .kind = .non_posted,
        .release_record_allocated = true,
        .mapped_address = null,
    });

    try std.testing.expectEqual(devres.ManagedIoremapKind.non_posted, result.kind);
    try std.testing.expectEqual(@as(?usize, null), result.mapped_address);
    try std.testing.expect(!result.added_to_devres);
    try std.testing.expect(!result.release_record_retained);
    try std.testing.expect(result.release_record_freed);
    try std.testing.expect(!result.should_unmap_on_detach);
}

test "phase13 devres rejects ioremap planning when the release record cannot be allocated" {
    try std.testing.expectError(error.OutOfMemory, devres.DevresHelperLab.planManagedIoremapAcquire(.{
        .kind = .plain,
        .release_record_allocated = false,
        .mapped_address = 0x2000,
    }));
}

test "phase13 devres uncached ioremap wrapper forces the uncached lifetime path" {
    const result = try devres.DevresHelperLab.planManagedIoremapAcquireUc(.{
        .release_record_allocated = true,
        .mapped_address = 0x2400,
    });

    try std.testing.expectEqualStrings("lib/devres.c", result.anchor);
    try std.testing.expectEqual(devres.ManagedIoremapKind.uncached, result.kind);
    try std.testing.expectEqual(@as(?usize, 0x2400), result.mapped_address);
    try std.testing.expect(result.added_to_devres);
    try std.testing.expect(result.release_record_retained);
    try std.testing.expect(!result.release_record_freed);
    try std.testing.expect(result.should_unmap_on_detach);
}

test "phase13 devres uncached ioremap wrapper frees the release record on map failure" {
    const result = try devres.DevresHelperLab.planManagedIoremapAcquireUc(.{
        .release_record_allocated = true,
        .mapped_address = null,
    });

    try std.testing.expectEqual(devres.ManagedIoremapKind.uncached, result.kind);
    try std.testing.expectEqual(@as(?usize, null), result.mapped_address);
    try std.testing.expect(!result.added_to_devres);
    try std.testing.expect(!result.release_record_retained);
    try std.testing.expect(result.release_record_freed);
    try std.testing.expect(!result.should_unmap_on_detach);
}

test "phase13 devres release matching stays pointer-exact" {
    try std.testing.expect(devres.DevresHelperLab.ioremapReleaseMatches(0x4000, 0x4000));
    try std.testing.expect(!devres.DevresHelperLab.ioremapReleaseMatches(0x4000, 0x4010));
}

test "phase13 devres retains the release record when managed ioport map succeeds" {
    const result = try devres.DevresHelperLab.planManagedIoportMap(.{
        .port = 0x3f8,
        .count = 8,
        .release_record_allocated = true,
        .mapped_address = 0xf000,
    });

    try std.testing.expectEqualStrings("lib/devres.c", result.anchor);
    try std.testing.expectEqual(@as(u64, 0x3f8), result.port);
    try std.testing.expectEqual(@as(u64, 8), result.count);
    try std.testing.expectEqual(@as(?usize, 0xf000), result.mapped_address);
    try std.testing.expect(result.added_to_devres);
    try std.testing.expect(result.release_record_retained);
    try std.testing.expect(!result.release_record_freed);
    try std.testing.expect(result.should_unmap_on_detach);
}

test "phase13 devres frees the ioport release record when mapping fails after allocation" {
    const result = try devres.DevresHelperLab.planManagedIoportMap(.{
        .port = 0x2f8,
        .count = 4,
        .release_record_allocated = true,
        .mapped_address = null,
    });

    try std.testing.expectEqual(@as(u64, 0x2f8), result.port);
    try std.testing.expectEqual(@as(u64, 4), result.count);
    try std.testing.expectEqual(@as(?usize, null), result.mapped_address);
    try std.testing.expect(!result.added_to_devres);
    try std.testing.expect(!result.release_record_retained);
    try std.testing.expect(result.release_record_freed);
    try std.testing.expect(!result.should_unmap_on_detach);
}

test "phase13 devres rejects ioport planning when the release record cannot be allocated" {
    try std.testing.expectError(error.OutOfMemory, devres.DevresHelperLab.planManagedIoportMap(.{
        .port = 0x378,
        .count = 3,
        .release_record_allocated = false,
        .mapped_address = 0xe000,
    }));
}

test "phase13 devres ioport release matching stays pointer-exact" {
    try std.testing.expect(devres.DevresHelperLab.ioportReleaseMatches(0xf000, 0xf000));
    try std.testing.expect(!devres.DevresHelperLab.ioportReleaseMatches(0xf000, 0xf010));
}

test "phase13 devres plans a non-posted managed ioremap resource mapping" {
    const outcome = try devres.DevresHelperLab.planManagedIoremapResource(std.testing.allocator, .{
        .device_name = "serial",
        .resource = .{
            .start = 0x1000,
            .end = 0x10ff,
            .is_memory = true,
            .nonposted = true,
            .name = "regs",
        },
    });

    switch (outcome) {
        .mapped => |plan| {
            defer std.testing.allocator.free(plan.pretty_name);
            try std.testing.expectEqualStrings("lib/devres.c", plan.anchor);
            try std.testing.expectEqualStrings("serial regs", plan.pretty_name);
            try std.testing.expectEqual(devres.IoremapType.np, plan.effective_type);
            try std.testing.expectEqual(@as(u64, 0x100), plan.size);
            try std.testing.expect(plan.requests_region);
            try std.testing.expect(!plan.releases_region_on_remap_failure);
        },
        .err => |failure| {
            std.debug.print("unexpected failure: {any}\n", .{failure});
            return error.UnexpectedFailure;
        },
    }
}

test "phase13 devres keeps requested mapping types and unnamed pretty names" {
    const outcome = try devres.DevresHelperLab.planManagedIoremapResource(std.testing.allocator, .{
        .device_name = "gpu0",
        .resource = .{
            .start = 0x2000,
            .end = 0x201f,
            .is_memory = true,
            .nonposted = true,
            .name = null,
        },
        .requested_type = .wc,
    });

    switch (outcome) {
        .mapped => |plan| {
            defer std.testing.allocator.free(plan.pretty_name);
            try std.testing.expectEqualStrings("gpu0", plan.pretty_name);
            try std.testing.expectEqual(devres.IoremapType.wc, plan.effective_type);
            try std.testing.expectEqual(@as(u64, 0x20), plan.size);
        },
        .err => return error.UnexpectedFailure,
    }
}

test "phase13 devres plans an uncached managed ioremap resource wrapper" {
    const outcome = try devres.DevresHelperLab.planManagedIoremapResourceUc(std.testing.allocator, .{
        .device_name = "uart3",
        .resource = .{
            .start = 0x2400,
            .end = 0x243f,
            .is_memory = true,
            .nonposted = true,
            .name = "cfg",
        },
    });

    switch (outcome) {
        .mapped => |plan| {
            defer std.testing.allocator.free(plan.pretty_name);
            try std.testing.expectEqualStrings("lib/devres.c", plan.anchor);
            try std.testing.expectEqualStrings("uart3 cfg", plan.pretty_name);
            try std.testing.expectEqual(devres.IoremapType.uc, plan.effective_type);
            try std.testing.expectEqual(@as(u64, 0x40), plan.size);
            try std.testing.expect(plan.requests_region);
            try std.testing.expect(!plan.releases_region_on_remap_failure);
        },
        .err => return error.UnexpectedFailure,
    }
}

test "phase13 devres propagates uncached managed resource failures" {
    const outcome = try devres.DevresHelperLab.planManagedIoremapResourceUc(std.testing.allocator, .{
        .device_name = "uart4",
        .resource = .{
            .start = 0x2500,
            .end = 0x257f,
            .is_memory = true,
            .nonposted = false,
            .name = "cfg",
        },
        .remap_succeeds = false,
    });

    switch (outcome) {
        .mapped => return error.ExpectedFailure,
        .err => |failure| {
            try std.testing.expectEqual(devres.ErrorStage.remap, failure.stage);
            try std.testing.expectEqual(devres.ErrorCode.no_memory, failure.error_code);
            try std.testing.expectEqual(devres.IoremapType.uc, failure.effective_type);
            try std.testing.expect(failure.requests_region);
            try std.testing.expect(failure.releases_region_on_remap_failure);
        },
    }
}

test "phase13 devres plans a write-combined managed ioremap resource wrapper" {
    const outcome = try devres.DevresHelperLab.planManagedIoremapResourceWc(std.testing.allocator, .{
        .device_name = "fb0",
        .resource = .{
            .start = 0x2800,
            .end = 0x287f,
            .is_memory = true,
            .nonposted = true,
            .name = "bar0",
        },
    });

    switch (outcome) {
        .mapped => |plan| {
            defer std.testing.allocator.free(plan.pretty_name);
            try std.testing.expectEqualStrings("lib/devres.c", plan.anchor);
            try std.testing.expectEqualStrings("fb0 bar0", plan.pretty_name);
            try std.testing.expectEqual(devres.IoremapType.wc, plan.effective_type);
            try std.testing.expectEqual(@as(u64, 0x80), plan.size);
            try std.testing.expect(plan.requests_region);
            try std.testing.expect(!plan.releases_region_on_remap_failure);
        },
        .err => return error.UnexpectedFailure,
    }
}

test "phase13 devres propagates write-combined managed resource failures" {
    const outcome = try devres.DevresHelperLab.planManagedIoremapResourceWc(std.testing.allocator, .{
        .device_name = "fb1",
        .resource = .{
            .start = 0x2900,
            .end = 0x297f,
            .is_memory = true,
            .nonposted = false,
            .name = "bar1",
        },
        .remap_succeeds = false,
    });

    switch (outcome) {
        .mapped => return error.ExpectedFailure,
        .err => |failure| {
            try std.testing.expectEqual(devres.ErrorStage.remap, failure.stage);
            try std.testing.expectEqual(devres.ErrorCode.no_memory, failure.error_code);
            try std.testing.expectEqual(devres.IoremapType.wc, failure.effective_type);
            try std.testing.expect(failure.requests_region);
            try std.testing.expect(failure.releases_region_on_remap_failure);
        },
    }
}

test "phase13 devres rejects missing or non-memory resources" {
    const missing = try devres.DevresHelperLab.planManagedIoremapResource(std.testing.allocator, .{
        .device_name = "i2c0",
        .resource = null,
    });
    switch (missing) {
        .mapped => return error.ExpectedFailure,
        .err => |failure| {
            try std.testing.expectEqual(devres.ErrorStage.invalid_resource, failure.stage);
            try std.testing.expectEqual(devres.ErrorCode.invalid, failure.error_code);
            try std.testing.expect(!failure.requests_region);
        },
    }

    const wrong_type = try devres.DevresHelperLab.planManagedIoremapResource(std.testing.allocator, .{
        .device_name = "i2c0",
        .resource = .{
            .start = 0x3000,
            .end = 0x300f,
            .is_memory = false,
            .nonposted = false,
            .name = "ports",
        },
    });
    switch (wrong_type) {
        .mapped => return error.ExpectedFailure,
        .err => |failure| {
            try std.testing.expectEqual(devres.ErrorStage.invalid_resource, failure.stage);
            try std.testing.expectEqual(devres.ErrorCode.invalid, failure.error_code);
        },
    }
}

test "phase13 devres records busy region requests and remap cleanup" {
    const busy = try devres.DevresHelperLab.planManagedIoremapResource(std.testing.allocator, .{
        .device_name = "eth0",
        .resource = .{
            .start = 0x4000,
            .end = 0x40ff,
            .is_memory = true,
            .nonposted = false,
            .name = "mmio",
        },
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
        .resource = .{
            .start = 0x5000,
            .end = 0x507f,
            .is_memory = true,
            .nonposted = false,
            .name = "mmio",
        },
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
}

test "phase13 devres models pretty-name allocation failure and resource sizing" {
    const alloc_failure = try devres.DevresHelperLab.planManagedIoremapResource(std.testing.allocator, .{
        .device_name = "uart0",
        .resource = .{
            .start = 0x6000,
            .end = 0x6003,
            .is_memory = true,
            .nonposted = false,
            .name = "regs",
        },
        .fail_pretty_name_allocation = true,
    });
    switch (alloc_failure) {
        .mapped => return error.ExpectedFailure,
        .err => |failure| {
            try std.testing.expectEqual(devres.ErrorStage.pretty_name, failure.stage);
            try std.testing.expectEqual(devres.ErrorCode.no_memory, failure.error_code);
            try std.testing.expect(!failure.requests_region);
        },
    }

    try std.testing.expectError(error.InvalidRange, devres.DevresHelperLab.resourceSize(.{
        .start = 9,
        .end = 3,
        .is_memory = true,
        .nonposted = false,
    }));
}

test "phase13 devres plans devm_of_iomap around translated resources and optional size reporting" {
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
        },
        .err => return error.UnexpectedFailure,
    }
}

test "phase13 devres reports address-translation failure before managed resource planning" {
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
            try std.testing.expectEqual(@as(?devres.ErrorStage, null), failure.resource_stage);
        },
    }
}

test "phase13 devres preserves translated size when devm_of_iomap hits downstream remap failure" {
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

test "phase13 devres preserves translated size when devm_of_iomap hits downstream region busy" {
    const resources = [_]devres.Resource{
        .{
            .start = 0xa000,
            .end = 0xa05f,
            .is_memory = true,
            .nonposted = true,
            .name = "regs",
        },
    };

    const outcome = try devres.DevresHelperLab.planDeviceTreeIomap(std.testing.allocator, .{
        .device_name = "spi1",
        .index = 0,
        .resources = &resources,
        .report_size = true,
        .request_region_granted = false,
    });

    switch (outcome) {
        .mapped => return error.ExpectedFailure,
        .err => |failure| {
            try std.testing.expectEqual(devres.DeviceTreeIomapStage.managed_ioremap_resource, failure.stage);
            try std.testing.expectEqual(devres.ErrorCode.busy, failure.error_code);
            try std.testing.expectEqual(@as(usize, 0), failure.index);
            try std.testing.expectEqual(@as(?u64, 0x60), failure.reported_size);
            try std.testing.expectEqual(devres.IoremapType.np, failure.effective_type);
            try std.testing.expect(failure.requests_region);
            try std.testing.expect(!failure.releases_region_on_remap_failure);
            try std.testing.expectEqual(@as(?devres.ErrorStage, .request_region), failure.resource_stage);
        },
    }
}

test "phase13 devres retains WC tokens on successful managed arch_phys_wc_add planning" {
    const outcome = try devres.DevresHelperLab.planArchPhysWcAdd(.{
        .base = 0xb000,
        .size = 0x100,
        .release_record_allocated = true,
        .token_result = 7,
    });

    switch (outcome) {
        .added => |plan| {
            try std.testing.expectEqualStrings("lib/devres.c", plan.anchor);
            try std.testing.expectEqual(@as(u64, 0xb000), plan.base);
            try std.testing.expectEqual(@as(u64, 0x100), plan.size);
            try std.testing.expectEqual(@as(i32, 7), plan.token);
            try std.testing.expect(plan.added_to_devres);
            try std.testing.expect(plan.release_record_retained);
            try std.testing.expect(!plan.release_record_freed);
            try std.testing.expect(plan.should_remove_on_detach);
        },
        .err => return error.UnexpectedFailure,
    }
}

test "phase13 devres frees WC token records when managed arch_phys_wc_add fails" {
    const outcome = try devres.DevresHelperLab.planArchPhysWcAdd(.{
        .base = 0xb100,
        .size = 0x80,
        .release_record_allocated = true,
        .token_result = -16,
    });

    switch (outcome) {
        .added => return error.ExpectedFailure,
        .err => |failure| {
            try std.testing.expectEqualStrings("lib/devres.c", failure.anchor);
            try std.testing.expectEqual(@as(i32, -16), failure.error_code);
            try std.testing.expect(!failure.added_to_devres);
            try std.testing.expect(!failure.release_record_retained);
            try std.testing.expect(failure.release_record_freed);
            try std.testing.expect(!failure.should_remove_on_detach);
        },
    }
}

test "phase13 devres rejects WC token planning when the release record cannot be allocated" {
    try std.testing.expectError(error.OutOfMemory, devres.DevresHelperLab.planArchPhysWcAdd(.{
        .base = 0xb200,
        .size = 0x40,
        .release_record_allocated = false,
        .token_result = 3,
    }));
}

test "phase13 devres retains memtype release records on successful WC reservation" {
    const outcome = try devres.DevresHelperLab.planArchIoReserveMemtypeWc(.{
        .start = 0x7000,
        .size = 0x80,
        .release_record_allocated = true,
        .reserve_result = 0,
    });

    switch (outcome) {
        .reserved => |plan| {
            try std.testing.expectEqualStrings("lib/devres.c", plan.anchor);
            try std.testing.expectEqual(@as(u64, 0x7000), plan.start);
            try std.testing.expectEqual(@as(u64, 0x80), plan.size);
            try std.testing.expect(plan.added_to_devres);
            try std.testing.expect(plan.release_record_retained);
            try std.testing.expect(!plan.release_record_freed);
            try std.testing.expect(plan.should_release_on_detach);
        },
        .err => return error.UnexpectedFailure,
    }
}

test "phase13 devres frees memtype release records when WC reservation fails" {
    const outcome = try devres.DevresHelperLab.planArchIoReserveMemtypeWc(.{
        .start = 0x7100,
        .size = 0x40,
        .release_record_allocated = true,
        .reserve_result = -16,
    });

    switch (outcome) {
        .reserved => return error.ExpectedFailure,
        .err => |failure| {
            try std.testing.expectEqualStrings("lib/devres.c", failure.anchor);
            try std.testing.expectEqual(@as(i32, -16), failure.error_code);
            try std.testing.expect(!failure.added_to_devres);
            try std.testing.expect(!failure.release_record_retained);
            try std.testing.expect(failure.release_record_freed);
            try std.testing.expect(!failure.should_release_on_detach);
        },
    }
}

test "phase13 devres rejects memtype planning when the release record cannot be allocated" {
    try std.testing.expectError(error.OutOfMemory, devres.DevresHelperLab.planArchIoReserveMemtypeWc(.{
        .start = 0x7200,
        .size = 0x20,
        .release_record_allocated = false,
        .reserve_result = 0,
    }));
}
