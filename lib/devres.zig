const std = @import("std");

pub const ModuleDescriptor = struct {
    name: []const u8,
    anchor: []const u8,
    provides_ioremap_lifetime_planning: bool,
    provides_release_pointer_match: bool,
    provides_ioremap_resource_planning: bool,
    provides_pretty_name_helper: bool,
    touches_live_device_lists: bool,
    touches_live_mmio: bool,
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

pub const ReleaseAction = enum {
    iounmap,
};

pub const ManagedIoremapAcquireResult = struct {
    anchor: []const u8,
    kind: ManagedIoremapKind,
    mapped_address: ?usize,
    added_to_devres: bool,
    release_record_retained: bool,
    release_record_freed: bool,
    release_action: ?ReleaseAction,
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

pub const IoremapResourceInput = struct {
    device_name: []const u8,
    resource: ?Resource,
    requested_type: IoremapType = .normal,
    fail_pretty_name_allocation: bool = false,
    request_region_granted: bool = true,
    remap_succeeds: bool = true,
};

pub const DevresHelperLab = struct {
    pub fn descriptor() ModuleDescriptor {
        return .{
            .name = "devres_helper_lab",
            .anchor = "lib/devres.c",
            .provides_ioremap_lifetime_planning = true,
            .provides_release_pointer_match = true,
            .provides_ioremap_resource_planning = true,
            .provides_pretty_name_helper = true,
            .touches_live_device_lists = false,
            .touches_live_mmio = false,
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
                .release_action = null,
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
            .release_action = .iounmap,
            .should_unmap_on_detach = true,
        };
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

    pub fn buildPrettyName(allocator: std.mem.Allocator, device_name: []const u8, resource_name: ?[]const u8) ![]u8 {
        if (resource_name) |name| {
            return std.fmt.allocPrint(allocator, "{s} {s}", .{ device_name, name });
        }
        return allocator.dupe(u8, device_name);
    }

    pub fn planManagedIoremapResource(allocator: std.mem.Allocator, input: IoremapResourceInput) !ManagedIoremapOutcome {
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
                .effective_type = effective_type,
                .size = size,
                .requests_region = true,
                .releases_region_on_remap_failure = false,
            },
        };
    }
};