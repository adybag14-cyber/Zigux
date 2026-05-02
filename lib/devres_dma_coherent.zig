pub const ModuleDescriptor = struct {
    name: []const u8,
    anchor: []const u8,
    provides_dma_coherent_lifetime_planning: bool,
    touches_live_dma: bool,
    touches_live_scatterlist: bool,
};

pub const ManagedDmaCoherentAllocInput = struct {
    size: u64,
    release_record_allocated: bool,
    cpu_address: ?usize,
    dma_handle: ?u64,
};

pub const ManagedDmaCoherentAllocResult = struct {
    anchor: []const u8,
    size: u64,
    cpu_address: ?usize,
    dma_handle: ?u64,
    mapping_ready: bool,
    added_to_devres: bool,
    release_record_retained: bool,
    release_record_freed: bool,
    should_free_on_detach: bool,
};

pub const ManagedDmaCoherentFreePlan = struct {
    anchor: []const u8,
    tracked_cpu_address: usize,
    tracked_dma_handle: u64,
    candidate_cpu_address: usize,
    candidate_dma_handle: u64,
    release_matches: bool,
    warns_on_release_miss: bool,
};

const ReleaseRecordOutcome = struct {
    added_to_devres: bool,
    release_record_retained: bool,
    release_record_freed: bool,
};

pub const DevresDmaCoherentHelper = struct {
    fn requireReleaseRecordAllocated(release_record_allocated: bool) !void {
        if (!release_record_allocated) {
            return error.OutOfMemory;
        }
    }

    fn planReleaseRecordOutcome(retain: bool) ReleaseRecordOutcome {
        if (retain) {
            return .{
                .added_to_devres = true,
                .release_record_retained = true,
                .release_record_freed = false,
            };
        }

        return .{
            .added_to_devres = false,
            .release_record_retained = false,
            .release_record_freed = true,
        };
    }

    fn dmaCoherentReleaseMatchesExact(
        tracked_cpu_address: usize,
        tracked_dma_handle: u64,
        candidate_cpu_address: usize,
        candidate_dma_handle: u64,
    ) bool {
        return tracked_cpu_address == candidate_cpu_address and tracked_dma_handle == candidate_dma_handle;
    }

    pub fn descriptor() ModuleDescriptor {
        return .{
            .name = "devres_dma_coherent_helper",
            .anchor = "lib/devres.c",
            .provides_dma_coherent_lifetime_planning = true,
            .touches_live_dma = false,
            .touches_live_scatterlist = false,
        };
    }

    pub fn planManagedDmaCoherentAlloc(input: ManagedDmaCoherentAllocInput) !ManagedDmaCoherentAllocResult {
        try requireReleaseRecordAllocated(input.release_record_allocated);
        const mapping_ready = input.cpu_address != null and input.dma_handle != null;
        const lifetime = planReleaseRecordOutcome(mapping_ready);

        return .{
            .anchor = descriptor().anchor,
            .size = input.size,
            .cpu_address = input.cpu_address,
            .dma_handle = input.dma_handle,
            .mapping_ready = mapping_ready,
            .added_to_devres = lifetime.added_to_devres,
            .release_record_retained = lifetime.release_record_retained,
            .release_record_freed = lifetime.release_record_freed,
            .should_free_on_detach = lifetime.added_to_devres,
        };
    }

    pub fn dmaCoherentReleaseMatches(
        tracked_cpu_address: usize,
        tracked_dma_handle: u64,
        candidate_cpu_address: usize,
        candidate_dma_handle: u64,
    ) bool {
        return dmaCoherentReleaseMatchesExact(
            tracked_cpu_address,
            tracked_dma_handle,
            candidate_cpu_address,
            candidate_dma_handle,
        );
    }

    pub fn planManagedDmaCoherentFree(
        tracked_cpu_address: usize,
        tracked_dma_handle: u64,
        candidate_cpu_address: usize,
        candidate_dma_handle: u64,
    ) ManagedDmaCoherentFreePlan {
        const release_matches = dmaCoherentReleaseMatchesExact(
            tracked_cpu_address,
            tracked_dma_handle,
            candidate_cpu_address,
            candidate_dma_handle,
        );
        return .{
            .anchor = descriptor().anchor,
            .tracked_cpu_address = tracked_cpu_address,
            .tracked_dma_handle = tracked_dma_handle,
            .candidate_cpu_address = candidate_cpu_address,
            .candidate_dma_handle = candidate_dma_handle,
            .release_matches = release_matches,
            .warns_on_release_miss = !release_matches,
        };
    }
};
