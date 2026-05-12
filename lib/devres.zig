const std = @import("std");

pub const ModuleDescriptor = struct {
    name: []const u8,
    anchor: []const u8,
    provides_ioremap_lifetime_planning: bool,
    provides_ioremap_plain_wrapper_planning: bool,
    provides_ioremap_uc_wrapper_planning: bool,
    provides_ioremap_wc_wrapper_planning: bool,
    provides_release_pointer_match: bool,
    provides_iounmap_call_planning: bool,
    provides_ioremap_resource_planning: bool,
    provides_of_iomap_planning: bool,
    provides_pretty_name_helper: bool,
    provides_arch_io_wc_memtype_planning: bool,
    provides_arch_phys_wc_token_planning: bool,
    touches_live_device_lists: bool,
    touches_live_mmio: bool,
    touches_live_arch_memtype: bool,
};

pub const ManagedIoremapKind = enum {
    plain,
    uncached,
    write_combined,
    non_posted,
};

pub const ManagedIoremapAcquireInput = struct {
    kind: ManagedIoremapKind,
    release_record_allocated: bool,
    mapped_address: ?usize,
};

pub const ManagedIoremapAcquireWrapperInput = struct {
    release_record_allocated: bool,
    mapped_address: ?usize,
};

pub const ManagedIoremapAcquireResult = struct {
    anchor: []const u8,
    kind: ManagedIoremapKind,
    mapped_address: ?usize,
    added_to_devres: bool,
    release_record_retained: bool,
    release_record_freed: bool,
    should_unmap_on_detach: bool,
};

pub const ManagedIounmapPlan = struct {
    anchor: []const u8,
    tracked_address: usize,
    candidate_address: usize,
    release_matches: bool,
    warns_on_release_miss: bool,
};

pub const IoremapType = enum {
    normal,
    uc,
    wc,
    np,
};

pub const Resource = struct {
    start: u64,
    end: u64,
    is_memory: bool,
    nonposted: bool,
    name: ?[]const u8 = null,
};

pub const ErrorStage = enum {
    invalid_resource,
    pretty_name,
    request_region,
    remap,
};

pub const ErrorCode = enum(i32) {
    invalid = -22,
    no_memory = -12,
    busy = -16,
};

pub const ManagedIoremapPlan = struct {
    anchor: []const u8,
    pretty_name: []const u8,
    effective_type: IoremapType,
    size: u64,
    requests_region: bool,
    releases_region_on_remap_failure: bool,
};

pub const ManagedIoremapFailure = struct {
    anchor: []const u8,
    stage: ErrorStage,
    error_code: ErrorCode,
    effective_type: IoremapType,
    requests_region: bool,
    releases_region_on_remap_failure: bool,
};

pub const ManagedIoremapOutcome = union(enum) {
    mapped: ManagedIoremapPlan,
    err: ManagedIoremapFailure,
};

pub const DeviceTreeIomapInput = struct {
    device_name: []const u8,
    index: usize,
    resources: []const Resource,
    requested_type: IoremapType = .normal,
    report_size: bool = false,
    request_region_granted: bool = true,
    fail_pretty_name_allocation: bool = false,
    remap_succeeds: bool = true,
};

pub const DeviceTreeIomapStage = enum {
    address_translation,
    managed_ioremap_resource,
};

pub const DeviceTreeIomapPlan = struct {
    anchor: []const u8,
    index: usize,
    reported_size: ?u64,
    mapping: ManagedIoremapPlan,
};

pub const DeviceTreeIomapFailure = struct {
    anchor: []const u8,
    stage: DeviceTreeIomapStage,
    error_code: ErrorCode,
    index: usize,
    reported_size: ?u64,
    effective_type: IoremapType,
    requests_region: bool,
    releases_region_on_remap_failure: bool,
    resource_stage: ?ErrorStage,
};

pub const DeviceTreeIomapOutcome = union(enum) {
    mapped: DeviceTreeIomapPlan,
    err: DeviceTreeIomapFailure,
};

pub const IoremapResourceInput = struct {
    device_name: []const u8,
    resource: ?Resource,
    requested_type: IoremapType = .normal,
    fail_pretty_name_allocation: bool = false,
    request_region_granted: bool = true,
    remap_succeeds: bool = true,
};

pub const ManagedMemtypeReserveInput = struct {
    start: u64,
    size: u64,
    release_record_allocated: bool,
    reserve_result: i32,
};

pub const ManagedMemtypeReservePlan = struct {
    anchor: []const u8,
    start: u64,
    size: u64,
    added_to_devres: bool,
    release_record_retained: bool,
    release_record_freed: bool,
    should_release_on_detach: bool,
};

pub const ManagedMemtypeReserveFailure = struct {
    anchor: []const u8,
    error_code: i32,
    added_to_devres: bool,
    release_record_retained: bool,
    release_record_freed: bool,
    should_release_on_detach: bool,
};

pub const ManagedMemtypeReserveOutcome = union(enum) {
    reserved: ManagedMemtypeReservePlan,
    err: ManagedMemtypeReserveFailure,
};

pub const ManagedPhysWcAddInput = struct {
    start: u64,
    size: u64,
    release_record_allocated: bool,
    token_result: i32,
};

pub const ManagedPhysWcAddPlan = struct {
    anchor: []const u8,
    start: u64,
    size: u64,
    token: i32,
    added_to_devres: bool,
    release_record_retained: bool,
    release_record_freed: bool,
    should_remove_on_detach: bool,
};

pub const ManagedPhysWcAddFailure = struct {
    anchor: []const u8,
    error_code: i32,
    added_to_devres: bool,
    release_record_retained: bool,
    release_record_freed: bool,
    should_remove_on_detach: bool,
};

pub const ManagedPhysWcAddOutcome = union(enum) {
    added: ManagedPhysWcAddPlan,
    err: ManagedPhysWcAddFailure,
};

pub const DevresHelperLab = struct {
    pub fn descriptor() ModuleDescriptor {
        return .{
            .name = "devres_helper_lab",
            .anchor = "lib/devres.c",
            .provides_ioremap_lifetime_planning = true,
            .provides_ioremap_plain_wrapper_planning = true,
            .provides_ioremap_uc_wrapper_planning = true,
            .provides_ioremap_wc_wrapper_planning = true,
            .provides_release_pointer_match = true,
            .provides_iounmap_call_planning = true,
            .provides_ioremap_resource_planning = true,
            .provides_of_iomap_planning = true,
            .provides_pretty_name_helper = true,
            .provides_arch_io_wc_memtype_planning = true,
            .provides_arch_phys_wc_token_planning = true,
            .touches_live_device_lists = false,
            .touches_live_mmio = false,
            .touches_live_arch_memtype = false,
        };
    }

    pub fn planManagedIoremapAcquire(input: ManagedIoremapAcquireInput) !ManagedIoremapAcquireResult {
        if (!input.release_record_allocated) {
            return error.OutOfMemory;
        }
        if (input.mapped_address == null) {
            return .{
                .anchor = descriptor().anchor,
                .kind = input.kind,
                .mapped_address = null,
                .added_to_devres = false,
                .release_record_retained = false,
                .release_record_freed = true,
                .should_unmap_on_detach = false,
            };
        }
        return .{
            .anchor = descriptor().anchor,
            .kind = input.kind,
            .mapped_address = input.mapped_address,
            .added_to_devres = true,
            .release_record_retained = true,
            .release_record_freed = false,
            .should_unmap_on_detach = true,
        };
    }

    pub fn planManagedIoremapAcquirePlain(input: ManagedIoremapAcquireWrapperInput) !ManagedIoremapAcquireResult {
        return planManagedIoremapAcquire(.{
            .kind = .plain,
            .release_record_allocated = input.release_record_allocated,
            .mapped_address = input.mapped_address,
        });
    }

    pub fn planManagedIoremapAcquireUc(input: ManagedIoremapAcquireWrapperInput) !ManagedIoremapAcquireResult {
        return planManagedIoremapAcquire(.{
            .kind = .uncached,
            .release_record_allocated = input.release_record_allocated,
            .mapped_address = input.mapped_address,
        });
    }

    pub fn planManagedIoremapAcquireWc(input: ManagedIoremapAcquireWrapperInput) !ManagedIoremapAcquireResult {
        return planManagedIoremapAcquire(.{
            .kind = .write_combined,
            .release_record_allocated = input.release_record_allocated,
            .mapped_address = input.mapped_address,
        });
    }

    pub fn ioremapReleaseMatches(tracked_address: usize, candidate_address: usize) bool {
        return tracked_address == candidate_address;
    }

    pub fn planManagedIounmap(tracked_address: usize, candidate_address: usize) ManagedIounmapPlan {
        const release_matches = ioremapReleaseMatches(tracked_address, candidate_address);
        return .{
            .anchor = descriptor().anchor,
            .tracked_address = tracked_address,
            .candidate_address = candidate_address,
            .release_matches = release_matches,
            .warns_on_release_miss = !release_matches,
        };
    }

    pub fn resolveIoremapType(resource: Resource, requested_type: IoremapType) IoremapType {
        if (requested_type == .normal and resource.nonposted) {
            return .np;
        }
        return requested_type;
    }

    pub fn resourceSize(resource: Resource) !u64 {
        if (resource.end < resource.start) {
            return error.InvalidRange;
        }
        return (resource.end - resource.start) + 1;
    }

    pub fn buildPrettyName(
        allocator: std.mem.Allocator,
        device_name: []const u8,
        resource_name: ?[]const u8,
    ) ![]u8 {
        if (resource_name) |name| {
            return std.fmt.allocPrint(allocator, "{s} {s}", .{ device_name, name });
        }
        return allocator.dupe(u8, device_name);
    }

    pub fn planManagedIoremapResource(
        allocator: std.mem.Allocator,
        input: IoremapResourceInput,
    ) !ManagedIoremapOutcome {
        const resource = input.resource orelse {
            return .{
                .err = .{
                    .anchor = descriptor().anchor,
                    .stage = .invalid_resource,
                    .error_code = .invalid,
                    .effective_type = input.requested_type,
                    .requests_region = false,
                    .releases_region_on_remap_failure = false,
                },
            };
        };
        if (!resource.is_memory) {
            return .{
                .err = .{
                    .anchor = descriptor().anchor,
                    .stage = .invalid_resource,
                    .error_code = .invalid,
                    .effective_type = input.requested_type,
                    .requests_region = false,
                    .releases_region_on_remap_failure = false,
                },
            };
        }

        const effective_type = resolveIoremapType(resource, input.requested_type);
        const size = resourceSize(resource) catch |err| switch (err) {
            error.InvalidRange => return .{
                .err = .{
                    .anchor = descriptor().anchor,
                    .stage = .invalid_resource,
                    .error_code = .invalid,
                    .effective_type = effective_type,
                    .requests_region = false,
                    .releases_region_on_remap_failure = false,
                },
            },
        };

        if (input.fail_pretty_name_allocation) {
            return .{
                .err = .{
                    .anchor = descriptor().anchor,
                    .stage = .pretty_name,
                    .error_code = .no_memory,
                    .effective_type = effective_type,
                    .requests_region = false,
                    .releases_region_on_remap_failure = false,
                },
            };
        }

        const pretty_name = try buildPrettyName(allocator, input.device_name, resource.name);
        errdefer allocator.free(pretty_name);

        if (!input.request_region_granted) {
            allocator.free(pretty_name);
            return .{
                .err = .{
                    .anchor = descriptor().anchor,
                    .stage = .request_region,
                    .error_code = .busy,
                    .effective_type = effective_type,
                    .requests_region = true,
                    .releases_region_on_remap_failure = false,
                },
            };
        }

        if (!input.remap_succeeds) {
            allocator.free(pretty_name);
            return .{
                .err = .{
                    .anchor = descriptor().anchor,
                    .stage = .remap,
                    .error_code = .no_memory,
                    .effective_type = effective_type,
                    .requests_region = true,
                    .releases_region_on_remap_failure = true,
                },
            };
        }

        return .{
            .mapped = .{
                .anchor = descriptor().anchor,
                .pretty_name = pretty_name,
                .effective_type = effective_type,
                .size = size,
                .requests_region = true,
                .releases_region_on_remap_failure = false,
            },
        };
    }

    pub fn planDeviceTreeIomap(
        allocator: std.mem.Allocator,
        input: DeviceTreeIomapInput,
    ) !DeviceTreeIomapOutcome {
        if (input.index >= input.resources.len) {
            return .{
                .err = .{
                    .anchor = descriptor().anchor,
                    .stage = .address_translation,
                    .error_code = .invalid,
                    .index = input.index,
                    .reported_size = null,
                    .effective_type = input.requested_type,
                    .requests_region = false,
                    .releases_region_on_remap_failure = false,
                    .resource_stage = null,
                },
            };
        }

        const resource = input.resources[input.index];
        const translated_size = resourceSize(resource) catch |err| switch (err) {
            error.InvalidRange => return .{
                .err = .{
                    .anchor = descriptor().anchor,
                    .stage = .address_translation,
                    .error_code = .invalid,
                    .index = input.index,
                    .reported_size = null,
                    .effective_type = input.requested_type,
                    .requests_region = false,
                    .releases_region_on_remap_failure = false,
                    .resource_stage = null,
                },
            },
        };
        const reported_size = if (input.report_size) translated_size else null;

        const mapped_or_err = try planManagedIoremapResource(allocator, .{
            .device_name = input.device_name,
            .resource = resource,
            .requested_type = input.requested_type,
            .fail_pretty_name_allocation = input.fail_pretty_name_allocation,
            .request_region_granted = input.request_region_granted,
            .remap_succeeds = input.remap_succeeds,
        });

        return switch (mapped_or_err) {
            .mapped => |plan| .{
                .mapped = .{
                    .anchor = descriptor().anchor,
                    .index = input.index,
                    .reported_size = reported_size,
                    .mapping = plan,
                },
            },
            .err => |failure| .{
                .err = .{
                    .anchor = descriptor().anchor,
                    .stage = .managed_ioremap_resource,
                    .error_code = failure.error_code,
                    .index = input.index,
                    .reported_size = reported_size,
                    .effective_type = failure.effective_type,
                    .requests_region = failure.requests_region,
                    .releases_region_on_remap_failure = failure.releases_region_on_remap_failure,
                    .resource_stage = failure.stage,
                },
            },
        };
    }

    pub fn planArchIoReserveMemtypeWc(
        input: ManagedMemtypeReserveInput,
    ) !ManagedMemtypeReserveOutcome {
        if (!input.release_record_allocated) {
            return error.OutOfMemory;
        }
        if (input.reserve_result < 0) {
            return .{
                .err = .{
                    .anchor = descriptor().anchor,
                    .error_code = input.reserve_result,
                    .added_to_devres = false,
                    .release_record_retained = false,
                    .release_record_freed = true,
                    .should_release_on_detach = false,
                },
            };
        }
        return .{
            .reserved = .{
                .anchor = descriptor().anchor,
                .start = input.start,
                .size = input.size,
                .added_to_devres = true,
                .release_record_retained = true,
                .release_record_freed = false,
                .should_release_on_detach = true,
            },
        };
    }

    pub fn planArchPhysWcAdd(input: ManagedPhysWcAddInput) !ManagedPhysWcAddOutcome {
        if (!input.release_record_allocated) {
            return error.OutOfMemory;
        }
        if (input.token_result < 0) {
            return .{
                .err = .{
                    .anchor = descriptor().anchor,
                    .error_code = input.token_result,
                    .added_to_devres = false,
                    .release_record_retained = false,
                    .release_record_freed = true,
                    .should_remove_on_detach = false,
                },
            };
        }
        return .{
            .added = .{
                .anchor = descriptor().anchor,
                .start = input.start,
                .size = input.size,
                .token = input.token_result,
                .added_to_devres = true,
                .release_record_retained = true,
                .release_record_freed = false,
                .should_remove_on_detach = true,
            },
        };
    }
};

test "phase13 devres plain ioremap wrapper preserves the managed lifetime path" {
    const result = try DevresHelperLab.planManagedIoremapAcquirePlain(.{
        .release_record_allocated = true,
        .mapped_address = 0x2200,
    });

    try std.testing.expectEqualStrings("lib/devres.c", result.anchor);
    try std.testing.expectEqual(ManagedIoremapKind.plain, result.kind);
    try std.testing.expectEqual(@as(?usize, 0x2200), result.mapped_address);
    try std.testing.expect(result.added_to_devres);
    try std.testing.expect(result.release_record_retained);
    try std.testing.expect(!result.release_record_freed);
    try std.testing.expect(result.should_unmap_on_detach);
}

test "phase13 devres plain ioremap wrapper frees the release record on map failure" {
    const result = try DevresHelperLab.planManagedIoremapAcquirePlain(.{
        .release_record_allocated = true,
        .mapped_address = null,
    });

    try std.testing.expectEqual(ManagedIoremapKind.plain, result.kind);
    try std.testing.expectEqual(@as(?usize, null), result.mapped_address);
    try std.testing.expect(!result.added_to_devres);
    try std.testing.expect(!result.release_record_retained);
    try std.testing.expect(result.release_record_freed);
    try std.testing.expect(!result.should_unmap_on_detach);
}

test "phase13 devres uncached ioremap wrapper preserves the managed lifetime path" {
    const descriptor = DevresHelperLab.descriptor();
    const result = try DevresHelperLab.planManagedIoremapAcquireUc(.{
        .release_record_allocated = true,
        .mapped_address = 0x2300,
    });

    try std.testing.expect(descriptor.provides_ioremap_uc_wrapper_planning);
    try std.testing.expectEqualStrings("lib/devres.c", result.anchor);
    try std.testing.expectEqual(ManagedIoremapKind.uncached, result.kind);
    try std.testing.expectEqual(@as(?usize, 0x2300), result.mapped_address);
    try std.testing.expect(result.added_to_devres);
    try std.testing.expect(result.release_record_retained);
    try std.testing.expect(!result.release_record_freed);
    try std.testing.expect(result.should_unmap_on_detach);
}

test "phase13 devres uncached ioremap wrapper frees the release record on map failure" {
    const result = try DevresHelperLab.planManagedIoremapAcquireUc(.{
        .release_record_allocated = true,
        .mapped_address = null,
    });

    try std.testing.expectEqual(ManagedIoremapKind.uncached, result.kind);
    try std.testing.expectEqual(@as(?usize, null), result.mapped_address);
    try std.testing.expect(!result.added_to_devres);
    try std.testing.expect(!result.release_record_retained);
    try std.testing.expect(result.release_record_freed);
    try std.testing.expect(!result.should_unmap_on_detach);
}

test "phase13 devres wc ioremap wrapper preserves the managed lifetime path" {
    const result = try DevresHelperLab.planManagedIoremapAcquireWc(.{
        .release_record_allocated = true,
        .mapped_address = 0x4400,
    });

    try std.testing.expectEqualStrings("lib/devres.c", result.anchor);
    try std.testing.expectEqual(ManagedIoremapKind.write_combined, result.kind);
    try std.testing.expectEqual(@as(?usize, 0x4400), result.mapped_address);
    try std.testing.expect(result.added_to_devres);
    try std.testing.expect(result.release_record_retained);
    try std.testing.expect(!result.release_record_freed);
    try std.testing.expect(result.should_unmap_on_detach);
}

test "phase13 devres wc ioremap wrapper frees the release record on map failure" {
    const result = try DevresHelperLab.planManagedIoremapAcquireWc(.{
        .release_record_allocated = true,
        .mapped_address = null,
    });

    try std.testing.expectEqual(ManagedIoremapKind.write_combined, result.kind);
    try std.testing.expectEqual(@as(?usize, null), result.mapped_address);
    try std.testing.expect(!result.added_to_devres);
    try std.testing.expect(!result.release_record_retained);
    try std.testing.expect(result.release_record_freed);
    try std.testing.expect(!result.should_unmap_on_detach);
}

test "phase13 devres iounmap plan warns on release pointer mismatch" {
    const plan = DevresHelperLab.planManagedIounmap(0x5000, 0x5100);

    try std.testing.expectEqualStrings("lib/devres.c", plan.anchor);
    try std.testing.expectEqual(@as(usize, 0x5000), plan.tracked_address);
    try std.testing.expectEqual(@as(usize, 0x5100), plan.candidate_address);
    try std.testing.expect(!plan.release_matches);
    try std.testing.expect(plan.warns_on_release_miss);
}

test "managed ioremap resource remap failure records nonposted unwind planning" {
    const allocator = std.testing.allocator;
    const outcome = try DevresHelperLab.planManagedIoremapResource(allocator, .{
        .device_name = "eth0",
        .resource = .{
            .start = 0x2000,
            .end = 0x20ff,
            .is_memory = true,
            .nonposted = true,
            .name = "regs",
        },
        .remap_succeeds = false,
    });

    switch (outcome) {
        .err => |failure| {
            try std.testing.expectEqual(ErrorStage.remap, failure.stage);
            try std.testing.expectEqual(ErrorCode.no_memory, failure.error_code);
            try std.testing.expectEqual(IoremapType.np, failure.effective_type);
            try std.testing.expect(failure.requests_region);
            try std.testing.expect(failure.releases_region_on_remap_failure);
        },
        .mapped => return error.UnexpectedSuccess,
    }
}

test "managed ioremap resource maps the success path into a caller-owned pretty-name plan" {
    const allocator = std.testing.allocator;
    const outcome = try DevresHelperLab.planManagedIoremapResource(allocator, .{
        .device_name = "eth0",
        .resource = .{
            .start = 0x2000,
            .end = 0x20ff,
            .is_memory = true,
            .nonposted = true,
            .name = "regs",
        },
    });

    switch (outcome) {
        .mapped => |plan| {
            defer allocator.free(plan.pretty_name);
            try std.testing.expectEqualStrings("lib/devres.c", plan.anchor);
            try std.testing.expectEqualStrings("eth0 regs", plan.pretty_name);
            try std.testing.expectEqual(IoremapType.np, plan.effective_type);
            try std.testing.expectEqual(@as(u64, 0x100), plan.size);
            try std.testing.expect(plan.requests_region);
            try std.testing.expect(!plan.releases_region_on_remap_failure);
        },
        .err => return error.UnexpectedFailure,
    }
}

test "managed ioremap resource maps invalid range into structured invalid_resource failure" {
    const allocator = std.testing.allocator;
    const outcome = try DevresHelperLab.planManagedIoremapResource(allocator, .{
        .device_name = "eth0",
        .resource = .{
            .start = 0x2000,
            .end = 0x1fff,
            .is_memory = true,
            .nonposted = false,
            .name = "regs",
        },
    });

    switch (outcome) {
        .err => |failure| {
            try std.testing.expectEqual(ErrorStage.invalid_resource, failure.stage);
            try std.testing.expectEqual(ErrorCode.invalid, failure.error_code);
            try std.testing.expectEqual(false, failure.requests_region);
            try std.testing.expectEqual(false, failure.releases_region_on_remap_failure);
        },
        .mapped => return error.UnexpectedSuccess,
    }
}

test "device tree iomap success preserves reported size and mapping plan" {
    const allocator = std.testing.allocator;
    const resources = [_]Resource{.{
        .start = 0x3000,
        .end = 0x307f,
        .is_memory = true,
        .nonposted = false,
        .name = "ctrl",
    }};

    const outcome = try DevresHelperLab.planDeviceTreeIomap(allocator, .{
        .device_name = "uart0",
        .index = 0,
        .resources = &resources,
        .requested_type = .wc,
        .report_size = true,
    });

    switch (outcome) {
        .mapped => |plan| {
            defer allocator.free(plan.mapping.pretty_name);
            try std.testing.expectEqualStrings("lib/devres.c", plan.anchor);
            try std.testing.expectEqual(@as(usize, 0), plan.index);
            try std.testing.expectEqual(@as(?u64, 0x80), plan.reported_size);
            try std.testing.expectEqualStrings("uart0 ctrl", plan.mapping.pretty_name);
            try std.testing.expectEqual(IoremapType.wc, plan.mapping.effective_type);
            try std.testing.expectEqual(@as(u64, 0x80), plan.mapping.size);
            try std.testing.expect(plan.mapping.requests_region);
            try std.testing.expect(!plan.mapping.releases_region_on_remap_failure);
        },
        .err => return error.UnexpectedFailure,
    }
}

test "device tree iomap invalid range stays in address translation stage" {
    const allocator = std.testing.allocator;
    const resources = [_]Resource{.{
        .start = 0x3000,
        .end = 0x2fff,
        .is_memory = true,
        .nonposted = false,
        .name = "mmio",
    }};

    const outcome = try DevresHelperLab.planDeviceTreeIomap(allocator, .{
        .device_name = "uart0",
        .index = 0,
        .resources = &resources,
        .report_size = true,
    });

    switch (outcome) {
        .err => |failure| {
            try std.testing.expectEqual(DeviceTreeIomapStage.address_translation, failure.stage);
            try std.testing.expectEqual(ErrorCode.invalid, failure.error_code);
            try std.testing.expectEqual(@as(?u64, null), failure.reported_size);
            try std.testing.expectEqual(@as(?ErrorStage, null), failure.resource_stage);
        },
        .mapped => return error.UnexpectedSuccess,
    }
}
