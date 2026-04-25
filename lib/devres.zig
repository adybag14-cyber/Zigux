const std = @import("std");

pub const ModuleDescriptor = struct {
    name: []const u8,
    anchor: []const u8,
    provides_ioremap_lifetime_planning: bool,
    provides_release_pointer_match: bool,
    touches_live_device_lists: bool,
    touches_live_mmio: bool,
};

pub const ManagedIoremapKind = enum {
    plain,
    uncached,
    write_combined,
    non_posted,
};

pub const ReleaseAction = enum {
    iounmap,
};

pub const ManagedIoremapAcquireInput = struct {
    kind: ManagedIoremapKind,
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
    release_action: ReleaseAction,
    should_unmap_on_detach: bool,
};

pub const DevresHelperLab = struct {
    pub fn descriptor() ModuleDescriptor {
        return .{
            .name = "devres_helper_lab",
            .anchor = "lib/devres.c",
            .provides_ioremap_lifetime_planning = true,
            .provides_release_pointer_match = true,
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
                .release_action = .iounmap,
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
};