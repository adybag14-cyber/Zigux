const std = @import("std");

pub const ModuleDescriptor = struct {
    name: []const u8,
    anchor: []const u8,
    provides_ioremap_lifetime_planning: bool,
    provides_ioremap_wc_wrapper_planning: bool,
    provides_release_pointer_match: bool,
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
    pretty_name_owned_by_plan: bool,
    effective_type: IoremapType,
    size: u64,
    requests_region: bool,
    releases_region_on_remap_failure: bool,

    pub fn deinit(self: *ManagedIoremapPlan, allocator: std.mem.Allocator) void {
        if (!self.pretty_name_owned_by_plan) {
            return;
        }
        allocator.free(@constCast(self.pretty_name));
        self.pretty_name = "";
        self.pretty_name_owned_by_plan = false;
    }
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
            .provides_ioremap_wc_wrapper_planning = true,
            .provides_release_pointer_match = true,
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
        const size = try resourceSize(resource);

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
                .pretty_name_owned_by_plan = true,
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
        const translated_size = try resourceSize(resource);
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

test "managed ioremap resource exposes owned pretty name cleanup" {
    const allocator = std.testing.allocator;

    const outcome = try DevresHelperLab.planManagedIoremapResource(allocator, .{
        .device_name = "virtio0",
        .resource = .{
            .start = 0x1000,
            .end = 0x10ff,
            .is_memory = true,
            .nonposted = false,
            .name = "cfg",
        },
    });

    switch (outcome) {
        .mapped => |plan_value| {
            var plan = plan_value;
            defer plan.deinit(allocator);
            try std.testing.expect(plan.pretty_name_owned_by_plan);
            try std.testing.expectEqualStrings("virtio0 cfg", plan.pretty_name);
            plan.deinit(allocator);
            try std.testing.expect(!plan.pretty_name_owned_by_plan);
            try std.testing.expectEqualStrings("", plan.pretty_name);
        },
        .err => return error.UnexpectedError,
    }
}

test "device tree iomap preserves pretty name ownership contract" {
    const allocator = std.testing.allocator;

    const resources = [_]Resource{.{
        .start = 0x2000,
        .end = 0x20ff,
        .is_memory = true,
        .nonposted = true,
        .name = "bar0",
    }};

    const outcome = try DevresHelperLab.planDeviceTreeIomap(allocator, .{
        .device_name = "of-node",
        .index = 0,
        .resources = &resources,
        .report_size = true,
    });

    switch (outcome) {
        .mapped => |plan_value| {
            var plan = plan_value;
            defer plan.mapping.deinit(allocator);
            try std.testing.expect(plan.mapping.pretty_name_owned_by_plan);
            try std.testing.expectEqualStrings("of-node bar0", plan.mapping.pretty_name);
            try std.testing.expectEqual(@as(?u64, 0x100), plan.reported_size);
            try std.testing.expectEqual(.np, plan.mapping.effective_type);
        },
        .err => return error.UnexpectedError,
    }
}
