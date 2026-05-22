pub const ModuleDescriptor = struct {
    name: []const u8,
    anchor: []const u8,
    provides_dmam_alloc_coherent_planning: bool,
    provides_release_record_lifetime_planning: bool,
    provides_release_call_planning: bool,
    provides_dmam_free_coherent_cleanup_planning: bool,
    provides_dmam_detach_cleanup_transition_planning: bool,
    provides_of_iomap_planning: bool,
    provides_iounmap_cleanup_planning: bool,
    touches_live_dma: bool,
    touches_live_scatterlist: bool,
    touches_live_mmio: bool,
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

pub const ManagedDmamFreeCoherentPlan = struct {
    anchor: []const u8,
    requested_size: u64,
    frees_allocation: bool,
    releases_from_devres: bool,
    release_record_consumed: bool,
    warns_on_release_miss: bool,
    destroys_release_record_before_free: bool,
};

pub const ManagedDmamDetachCleanupPlan = struct {
    anchor: []const u8,
    requested_size: u64,
    had_detach_cleanup_owner: bool,
    generates_cleanup_plan: bool,
    releases_from_devres: bool,
    release_record_consumed: bool,
    warns_on_release_miss: bool,
    destroys_release_record_before_free: bool,
};

pub const ReleaseRecordLifetimePlan = struct {
    added_to_devres: bool,
    release_record_retained: bool,
    release_record_freed: bool,
    should_release_on_detach: bool,
};

pub const ManagedReleaseCallPlan = struct {
    anchor: []const u8,
    requested_size: u64,
    releases_from_devres: bool,
    release_record_consumed: bool,
    warns_on_release_miss: bool,
    destroys_release_record_before_free: bool,
};

pub const DeviceTreeIomapInput = struct {
    index: u32,
    translated_size: u64,
    translation_ready: bool,
    requests_region: bool,
    request_region_available: bool,
    remap_succeeds: bool,
    nonposted: bool,
};

pub const DeviceTreeIomapPlan = struct {
    anchor: []const u8,
    index: u32,
    translated_size: u64,
    translation_ready: bool,
    reaches_managed_ioremap_resource: bool,
    requests_region: bool,
    request_region_denied: bool,
    releases_region_on_remap_failure: bool,
    remap_ready: bool,
    keeps_nonposted_mapping_type: bool,
};

pub const ManagedIounmapCleanupPlan = struct {
    anchor: []const u8,
    had_mapping_owner: bool,
    generates_cleanup_plan: bool,
    unmaps_mapping: bool,
    releases_from_devres: bool,
    release_record_consumed: bool,
    warns_on_release_miss: bool,
};

pub const DevresHelperLab = struct {
    fn requireReleaseRecordAllocated(release_record_allocated: bool) !void {
        if (!release_record_allocated) {
            return error.OutOfMemory;
        }
    }

    pub fn planManagedReleaseCall(requested_size: u64, release_record_matches: bool) ManagedReleaseCallPlan {
        return .{
            .anchor = descriptor().anchor,
            .requested_size = requested_size,
            .releases_from_devres = release_record_matches,
            .release_record_consumed = release_record_matches,
            .warns_on_release_miss = !release_record_matches,
            .destroys_release_record_before_free = true,
        };
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
            .provides_release_record_lifetime_planning = true,
            .provides_release_call_planning = true,
            .provides_dmam_free_coherent_cleanup_planning = true,
            .provides_dmam_detach_cleanup_transition_planning = true,
            .provides_of_iomap_planning = true,
            .provides_iounmap_cleanup_planning = true,
            .touches_live_dma = false,
            .touches_live_scatterlist = false,
            .touches_live_mmio = false,
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

    pub fn planManagedDmamFreeCoherent(requested_size: u64, release_record_matches: bool) ManagedDmamFreeCoherentPlan {
        const release_call = planManagedReleaseCall(requested_size, release_record_matches);

        return .{
            .anchor = release_call.anchor,
            .requested_size = release_call.requested_size,
            .frees_allocation = true,
            .releases_from_devres = release_call.releases_from_devres,
            .release_record_consumed = release_call.release_record_consumed,
            .warns_on_release_miss = release_call.warns_on_release_miss,
            .destroys_release_record_before_free = release_call.destroys_release_record_before_free,
        };
    }

    pub fn planManagedDmamDetachCleanup(
        allocation_plan: ManagedDmamAllocCoherentPlan,
        release_record_matches: bool,
    ) ManagedDmamDetachCleanupPlan {
        if (!allocation_plan.should_free_on_detach) {
            return .{
                .anchor = allocation_plan.anchor,
                .requested_size = allocation_plan.requested_size,
                .had_detach_cleanup_owner = false,
                .generates_cleanup_plan = false,
                .releases_from_devres = false,
                .release_record_consumed = false,
                .warns_on_release_miss = false,
                .destroys_release_record_before_free = false,
            };
        }

        const cleanup = planManagedDmamFreeCoherent(allocation_plan.requested_size, release_record_matches);

        return .{
            .anchor = cleanup.anchor,
            .requested_size = cleanup.requested_size,
            .had_detach_cleanup_owner = true,
            .generates_cleanup_plan = true,
            .releases_from_devres = cleanup.releases_from_devres,
            .release_record_consumed = cleanup.release_record_consumed,
            .warns_on_release_miss = cleanup.warns_on_release_miss,
            .destroys_release_record_before_free = cleanup.destroys_release_record_before_free,
        };
    }

    pub fn planDeviceTreeIomap(input: DeviceTreeIomapInput) DeviceTreeIomapPlan {
        const translation_ready = input.translation_ready and input.translated_size > 0;
        const reaches_managed_ioremap_resource = translation_ready;
        const request_region_denied = reaches_managed_ioremap_resource and input.requests_region and !input.request_region_available;
        const remap_ready = reaches_managed_ioremap_resource and !request_region_denied and input.remap_succeeds;
        const releases_region_on_remap_failure = reaches_managed_ioremap_resource and input.requests_region and !request_region_denied and !input.remap_succeeds;

        return .{
            .anchor = descriptor().anchor,
            .index = input.index,
            .translated_size = input.translated_size,
            .translation_ready = translation_ready,
            .reaches_managed_ioremap_resource = reaches_managed_ioremap_resource,
            .requests_region = reaches_managed_ioremap_resource and input.requests_region,
            .request_region_denied = request_region_denied,
            .releases_region_on_remap_failure = releases_region_on_remap_failure,
            .remap_ready = remap_ready,
            .keeps_nonposted_mapping_type = reaches_managed_ioremap_resource and input.nonposted,
        };
    }

    pub fn planManagedIounmapCleanup(had_mapping_owner: bool, release_record_matches: bool) ManagedIounmapCleanupPlan {
        if (!had_mapping_owner) {
            return .{
                .anchor = descriptor().anchor,
                .had_mapping_owner = false,
                .generates_cleanup_plan = false,
                .unmaps_mapping = false,
                .releases_from_devres = false,
                .release_record_consumed = false,
                .warns_on_release_miss = false,
            };
        }

        return .{
            .anchor = descriptor().anchor,
            .had_mapping_owner = true,
            .generates_cleanup_plan = true,
            .unmaps_mapping = true,
            .releases_from_devres = release_record_matches,
            .release_record_consumed = release_record_matches,
            .warns_on_release_miss = !release_record_matches,
        };
    }
};

const std = @import("std");

test "descriptor stays helper-local" {
    const descriptor = DevresHelperLab.descriptor();

    try std.testing.expectEqualStrings("devres_helper_lab", descriptor.name);
    try std.testing.expectEqualStrings("lib/devres.c", descriptor.anchor);
    try std.testing.expect(descriptor.provides_dmam_alloc_coherent_planning);
    try std.testing.expect(descriptor.provides_release_record_lifetime_planning);
    try std.testing.expect(descriptor.provides_release_call_planning);
    try std.testing.expect(descriptor.provides_dmam_free_coherent_cleanup_planning);
    try std.testing.expect(descriptor.provides_dmam_detach_cleanup_transition_planning);
    try std.testing.expect(descriptor.provides_of_iomap_planning);
    try std.testing.expect(descriptor.provides_iounmap_cleanup_planning);
    try std.testing.expect(!descriptor.touches_live_dma);
    try std.testing.expect(!descriptor.touches_live_scatterlist);
    try std.testing.expect(!descriptor.touches_live_mmio);
}

test "managed allocation retains release record when acquisition succeeds" {
    const plan = try DevresHelperLab.planManagedDmamAllocCoherent(.{
        .requested_size = 4096,
        .release_record_allocated = true,
        .allocation_succeeds = true,
    });

    try std.testing.expectEqual(@as(u64, 4096), plan.requested_size);
    try std.testing.expect(plan.allocation_ready);
    try std.testing.expect(plan.added_to_devres);
    try std.testing.expect(plan.release_record_retained);
    try std.testing.expect(!plan.release_record_freed);
    try std.testing.expect(plan.should_free_on_detach);
}

test "managed allocation frees release record when allocation fails" {
    const plan = try DevresHelperLab.planManagedDmamAllocCoherent(.{
        .requested_size = 4096,
        .release_record_allocated = true,
        .allocation_succeeds = false,
    });

    try std.testing.expect(!plan.allocation_ready);
    try std.testing.expect(!plan.added_to_devres);
    try std.testing.expect(!plan.release_record_retained);
    try std.testing.expect(plan.release_record_freed);
    try std.testing.expect(!plan.should_free_on_detach);
}

test "managed allocation frees release record for zero-sized requests" {
    const plan = try DevresHelperLab.planManagedDmamAllocCoherent(.{
        .requested_size = 0,
        .release_record_allocated = true,
        .allocation_succeeds = true,
    });

    try std.testing.expectEqual(@as(u64, 0), plan.requested_size);
    try std.testing.expect(!plan.allocation_ready);
    try std.testing.expect(!plan.added_to_devres);
    try std.testing.expect(plan.release_record_freed);
    try std.testing.expect(!plan.should_free_on_detach);
}

test "managed allocation requires a release record" {
    try std.testing.expectError(error.OutOfMemory, DevresHelperLab.planManagedDmamAllocCoherent(.{
        .requested_size = 512,
        .release_record_allocated = false,
        .allocation_succeeds = true,
    }));
}

test "release-call planning consumes the matching devres release record" {
    const release_call = DevresHelperLab.planManagedReleaseCall(2048, true);

    try std.testing.expectEqual(@as(u64, 2048), release_call.requested_size);
    try std.testing.expect(release_call.releases_from_devres);
    try std.testing.expect(release_call.release_record_consumed);
    try std.testing.expect(!release_call.warns_on_release_miss);
    try std.testing.expect(release_call.destroys_release_record_before_free);
}

test "release-call planning still warns when the devres release record is missing" {
    const release_call = DevresHelperLab.planManagedReleaseCall(2048, false);

    try std.testing.expectEqual(@as(u64, 2048), release_call.requested_size);
    try std.testing.expect(!release_call.releases_from_devres);
    try std.testing.expect(!release_call.release_record_consumed);
    try std.testing.expect(release_call.warns_on_release_miss);
    try std.testing.expect(release_call.destroys_release_record_before_free);
}

test "managed free planning consumes the matching devres release record" {
    const plan = DevresHelperLab.planManagedDmamFreeCoherent(2048, true);

    try std.testing.expectEqual(@as(u64, 2048), plan.requested_size);
    try std.testing.expect(plan.frees_allocation);
    try std.testing.expect(plan.releases_from_devres);
    try std.testing.expect(plan.release_record_consumed);
    try std.testing.expect(!plan.warns_on_release_miss);
    try std.testing.expect(plan.destroys_release_record_before_free);
}

test "managed free planning still frees allocations when the release record is missing" {
    const plan = DevresHelperLab.planManagedDmamFreeCoherent(2048, false);

    try std.testing.expectEqual(@as(u64, 2048), plan.requested_size);
    try std.testing.expect(plan.frees_allocation);
    try std.testing.expect(!plan.releases_from_devres);
    try std.testing.expect(!plan.release_record_consumed);
    try std.testing.expect(plan.warns_on_release_miss);
    try std.testing.expect(plan.destroys_release_record_before_free);
}

test "detach cleanup planning materializes a coherent free when allocation retained ownership" {
    const allocation_plan = try DevresHelperLab.planManagedDmamAllocCoherent(.{
        .requested_size = 4096,
        .release_record_allocated = true,
        .allocation_succeeds = true,
    });
    const cleanup = DevresHelperLab.planManagedDmamDetachCleanup(allocation_plan, true);

    try std.testing.expectEqualStrings("lib/devres.c", cleanup.anchor);
    try std.testing.expectEqual(@as(u64, 4096), cleanup.requested_size);
    try std.testing.expect(cleanup.had_detach_cleanup_owner);
    try std.testing.expect(cleanup.generates_cleanup_plan);
    try std.testing.expect(cleanup.releases_from_devres);
    try std.testing.expect(cleanup.release_record_consumed);
    try std.testing.expect(!cleanup.warns_on_release_miss);
    try std.testing.expect(cleanup.destroys_release_record_before_free);
}

test "detach cleanup planning keeps missing release records warnable" {
    const allocation_plan = try DevresHelperLab.planManagedDmamAllocCoherent(.{
        .requested_size = 4096,
        .release_record_allocated = true,
        .allocation_succeeds = true,
    });
    const cleanup = DevresHelperLab.planManagedDmamDetachCleanup(allocation_plan, false);

    try std.testing.expect(cleanup.had_detach_cleanup_owner);
    try std.testing.expect(cleanup.generates_cleanup_plan);
    try std.testing.expect(!cleanup.releases_from_devres);
    try std.testing.expect(!cleanup.release_record_consumed);
    try std.testing.expect(cleanup.warns_on_release_miss);
    try std.testing.expect(cleanup.destroys_release_record_before_free);
}

test "detach cleanup planning skips cleanup when allocation never retained ownership" {
    const allocation_plan = try DevresHelperLab.planManagedDmamAllocCoherent(.{
        .requested_size = 0,
        .release_record_allocated = true,
        .allocation_succeeds = true,
    });
    const cleanup = DevresHelperLab.planManagedDmamDetachCleanup(allocation_plan, true);

    try std.testing.expectEqualStrings("lib/devres.c", cleanup.anchor);
    try std.testing.expectEqual(@as(u64, 0), cleanup.requested_size);
    try std.testing.expect(!cleanup.had_detach_cleanup_owner);
    try std.testing.expect(!cleanup.generates_cleanup_plan);
    try std.testing.expect(!cleanup.releases_from_devres);
    try std.testing.expect(!cleanup.release_record_consumed);
    try std.testing.expect(!cleanup.warns_on_release_miss);
    try std.testing.expect(!cleanup.destroys_release_record_before_free);
}

test "iomap planning stops before the managed ioremap-resource stage when translation is missing" {
    const plan = DevresHelperLab.planDeviceTreeIomap(.{
        .index = 2,
        .translated_size = 4096,
        .translation_ready = false,
        .requests_region = true,
        .request_region_available = true,
        .remap_succeeds = true,
        .nonposted = true,
    });

    try std.testing.expectEqual(@as(u32, 2), plan.index);
    try std.testing.expectEqual(@as(u64, 4096), plan.translated_size);
    try std.testing.expect(!plan.translation_ready);
    try std.testing.expect(!plan.reaches_managed_ioremap_resource);
    try std.testing.expect(!plan.requests_region);
    try std.testing.expect(!plan.request_region_denied);
    try std.testing.expect(!plan.releases_region_on_remap_failure);
    try std.testing.expect(!plan.remap_ready);
    try std.testing.expect(!plan.keeps_nonposted_mapping_type);
}

test "iomap planning preserves translated size and busy denial when the request region is unavailable" {
    const plan = DevresHelperLab.planDeviceTreeIomap(.{
        .index = 1,
        .translated_size = 8192,
        .translation_ready = true,
        .requests_region = true,
        .request_region_available = false,
        .remap_succeeds = true,
        .nonposted = true,
    });

    try std.testing.expectEqual(@as(u32, 1), plan.index);
    try std.testing.expectEqual(@as(u64, 8192), plan.translated_size);
    try std.testing.expect(plan.translation_ready);
    try std.testing.expect(plan.reaches_managed_ioremap_resource);
    try std.testing.expect(plan.requests_region);
    try std.testing.expect(plan.request_region_denied);
    try std.testing.expect(!plan.releases_region_on_remap_failure);
    try std.testing.expect(!plan.remap_ready);
    try std.testing.expect(plan.keeps_nonposted_mapping_type);
}

test "iomap planning releases the requested region when remap later fails" {
    const plan = DevresHelperLab.planDeviceTreeIomap(.{
        .index = 0,
        .translated_size = 4096,
        .translation_ready = true,
        .requests_region = true,
        .request_region_available = true,
        .remap_succeeds = false,
        .nonposted = false,
    });

    try std.testing.expectEqual(@as(u32, 0), plan.index);
    try std.testing.expectEqual(@as(u64, 4096), plan.translated_size);
    try std.testing.expect(plan.translation_ready);
    try std.testing.expect(plan.reaches_managed_ioremap_resource);
    try std.testing.expect(plan.requests_region);
    try std.testing.expect(!plan.request_region_denied);
    try std.testing.expect(plan.releases_region_on_remap_failure);
    try std.testing.expect(!plan.remap_ready);
    try std.testing.expect(!plan.keeps_nonposted_mapping_type);
}

test "iounmap cleanup planning consumes the matching devres release record" {
    const cleanup = DevresHelperLab.planManagedIounmapCleanup(true, true);

    try std.testing.expectEqualStrings("lib/devres.c", cleanup.anchor);
    try std.testing.expect(cleanup.had_mapping_owner);
    try std.testing.expect(cleanup.generates_cleanup_plan);
    try std.testing.expect(cleanup.unmaps_mapping);
    try std.testing.expect(cleanup.releases_from_devres);
    try std.testing.expect(cleanup.release_record_consumed);
    try std.testing.expect(!cleanup.warns_on_release_miss);
}

test "iounmap cleanup planning still unmaps when the release record is missing" {
    const cleanup = DevresHelperLab.planManagedIounmapCleanup(true, false);

    try std.testing.expect(cleanup.had_mapping_owner);
    try std.testing.expect(cleanup.generates_cleanup_plan);
    try std.testing.expect(cleanup.unmaps_mapping);
    try std.testing.expect(!cleanup.releases_from_devres);
    try std.testing.expect(!cleanup.release_record_consumed);
    try std.testing.expect(cleanup.warns_on_release_miss);
}

test "iounmap cleanup planning stays inert when no mapping owner exists" {
    const cleanup = DevresHelperLab.planManagedIounmapCleanup(false, true);

    try std.testing.expectEqualStrings("lib/devres.c", cleanup.anchor);
    try std.testing.expect(!cleanup.had_mapping_owner);
    try std.testing.expect(!cleanup.generates_cleanup_plan);
    try std.testing.expect(!cleanup.unmaps_mapping);
    try std.testing.expect(!cleanup.releases_from_devres);
    try std.testing.expect(!cleanup.release_record_consumed);
    try std.testing.expect(!cleanup.warns_on_release_miss);
}
