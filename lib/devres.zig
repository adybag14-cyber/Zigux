pub const ModuleDescriptor = struct {
    name: []const u8,
    anchor: []const u8,
    provides_dmam_alloc_coherent_planning: bool,
    touches_live_dma: bool,
    touches_live_scatterlist: bool,
};

pub const ManagedDmamAllocCoherentInput = struct {
    requested_size: u64,
    release_record_allocated: bool,
    allocation_succeeds: bool,
};

pub const ManagedDmamAllocCoherentPlan = struct {
    anchor: []const u8,
    requested_size: u64,
    allocation_ready: bool,
    added_to_devres: bool,
    release_record_retained: bool,
    release_record_freed: bool,
    should_free_on_detach: bool,
};

pub const ReleaseRecordLifetimePlan = struct {
    added_to_devres: bool,
    release_record_retained: bool,
    release_record_freed: bool,
    should_release_on_detach: bool,
};

pub const DevresHelperLab = struct {
    fn requireReleaseRecordAllocated(release_record_allocated: bool) !void {
        if (!release_record_allocated) {
            return error.OutOfMemory;
        }
    }

    pub fn planManagedReleaseRecordLifetime(retain: bool) ReleaseRecordLifetimePlan {
        if (retain) {
            return .{
                .added_to_devres = true,
                .release_record_retained = true,
                .release_record_freed = false,
                .should_release_on_detach = true,
            };
        }

        return .{
            .added_to_devres = false,
            .release_record_retained = false,
            .release_record_freed = true,
            .should_release_on_detach = false,
        };
    }

    pub fn descriptor() ModuleDescriptor {
        return .{
            .name = "devres_helper_lab",
            .anchor = "lib/devres.c",
            .provides_dmam_alloc_coherent_planning = true,
            .touches_live_dma = false,
            .touches_live_scatterlist = false,
        };
    }

    pub fn planManagedDmamAllocCoherent(input: ManagedDmamAllocCoherentInput) !ManagedDmamAllocCoherentPlan {
        try requireReleaseRecordAllocated(input.release_record_allocated);

        const allocation_ready = input.requested_size > 0 and input.allocation_succeeds;
        const lifetime = planManagedReleaseRecordLifetime(allocation_ready);

        return .{
            .anchor = descriptor().anchor,
            .requested_size = input.requested_size,
            .allocation_ready = allocation_ready,
            .added_to_devres = lifetime.added_to_devres,
            .release_record_retained = lifetime.release_record_retained,
            .release_record_freed = lifetime.release_record_freed,
            .should_free_on_detach = lifetime.should_release_on_detach,
        };
    }
};