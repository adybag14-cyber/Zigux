pub const ModuleDescriptor = struct {
    name: []const u8,
    anchor: []const u8,
    provides_scatterlist_lifetime_planning: bool,
    provides_scatterlist_table_teardown_planning: bool,
    touches_live_dma: bool,
    touches_live_scatterlist: bool,
};

pub const ManagedScatterlistMapInput = struct {
    original_entries: u32,
    mapped_entries: u32,
    release_record_allocated: bool,
};

pub const ManagedScatterlistMapResult = struct {
    anchor: []const u8,
    original_entries: u32,
    mapped_entries: u32,
    mapping_ready: bool,
    added_to_devres: bool,
    release_record_retained: bool,
    release_record_freed: bool,
    should_unmap_on_detach: bool,
};

pub const ManagedScatterlistUnmapPlan = struct {
    anchor: []const u8,
    tracked_original_entries: u32,
    tracked_mapped_entries: u32,
    candidate_original_entries: u32,
    candidate_mapped_entries: u32,
    release_matches: bool,
    warns_on_release_miss: bool,
};

pub const ManagedScatterlistTableTeardownInput = struct {
    original_entries: u32,
    mapped_entries: u32,
    table_initialized: bool,
    release_record_present: bool,
};

pub const ManagedScatterlistTableTeardownPlan = struct {
    anchor: []const u8,
    original_entries: u32,
    mapped_entries: u32,
    table_initialized: bool,
    release_record_present: bool,
    free_table_ready: bool,
    requires_unmap_before_free: bool,
    warns_on_missing_release_record: bool,
    warns_on_overmapped_release: bool,
};

const ReleaseRecordOutcome = struct {
    added_to_devres: bool,
    release_record_retained: bool,
    release_record_freed: bool,
};

pub const DevresScatterlistHelper = struct {
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

    fn scatterlistReleaseMatchesExact(
        tracked_original_entries: u32,
        tracked_mapped_entries: u32,
        candidate_original_entries: u32,
        candidate_mapped_entries: u32,
    ) bool {
        return tracked_original_entries == candidate_original_entries and
            tracked_mapped_entries == candidate_mapped_entries;
    }

    pub fn descriptor() ModuleDescriptor {
        return .{
            .name = "devres_scatterlist_helper",
            .anchor = "lib/devres.c",
            .provides_scatterlist_lifetime_planning = true,
            .provides_scatterlist_table_teardown_planning = true,
            .touches_live_dma = false,
            .touches_live_scatterlist = false,
        };
    }

    pub fn planManagedScatterlistMap(input: ManagedScatterlistMapInput) !ManagedScatterlistMapResult {
        try requireReleaseRecordAllocated(input.release_record_allocated);
        const mapping_ready = input.original_entries > 0 and
            input.mapped_entries > 0 and
            input.mapped_entries <= input.original_entries;
        const lifetime = planReleaseRecordOutcome(mapping_ready);

        return .{
            .anchor = descriptor().anchor,
            .original_entries = input.original_entries,
            .mapped_entries = input.mapped_entries,
            .mapping_ready = mapping_ready,
            .added_to_devres = lifetime.added_to_devres,
            .release_record_retained = lifetime.release_record_retained,
            .release_record_freed = lifetime.release_record_freed,
            .should_unmap_on_detach = lifetime.added_to_devres,
        };
    }

    pub fn scatterlistReleaseMatches(
        tracked_original_entries: u32,
        tracked_mapped_entries: u32,
        candidate_original_entries: u32,
        candidate_mapped_entries: u32,
    ) bool {
        return scatterlistReleaseMatchesExact(
            tracked_original_entries,
            tracked_mapped_entries,
            candidate_original_entries,
            candidate_mapped_entries,
        );
    }

    pub fn planManagedScatterlistUnmap(
        tracked_original_entries: u32,
        tracked_mapped_entries: u32,
        candidate_original_entries: u32,
        candidate_mapped_entries: u32,
    ) ManagedScatterlistUnmapPlan {
        const release_matches = scatterlistReleaseMatchesExact(
            tracked_original_entries,
            tracked_mapped_entries,
            candidate_original_entries,
            candidate_mapped_entries,
        );
        return .{
            .anchor = descriptor().anchor,
            .tracked_original_entries = tracked_original_entries,
            .tracked_mapped_entries = tracked_mapped_entries,
            .candidate_original_entries = candidate_original_entries,
            .candidate_mapped_entries = candidate_mapped_entries,
            .release_matches = release_matches,
            .warns_on_release_miss = !release_matches,
        };
    }

    pub fn planManagedScatterlistTableTeardown(
        input: ManagedScatterlistTableTeardownInput,
    ) ManagedScatterlistTableTeardownPlan {
        const count_consistent = input.original_entries > 0 and
            input.mapped_entries <= input.original_entries;
        const requires_unmap_before_free = input.table_initialized and
            count_consistent and
            input.mapped_entries > 0;
        const free_table_ready = input.table_initialized and
            input.release_record_present and
            count_consistent and
            input.mapped_entries == 0;

        return .{
            .anchor = descriptor().anchor,
            .original_entries = input.original_entries,
            .mapped_entries = input.mapped_entries,
            .table_initialized = input.table_initialized,
            .release_record_present = input.release_record_present,
            .free_table_ready = free_table_ready,
            .requires_unmap_before_free = requires_unmap_before_free,
            .warns_on_missing_release_record = input.table_initialized and !input.release_record_present,
            .warns_on_overmapped_release = input.table_initialized and
                input.mapped_entries > input.original_entries,
        };
    }
};