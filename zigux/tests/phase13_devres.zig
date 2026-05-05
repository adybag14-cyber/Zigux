const std = @import("std");
const devres = @import("devres");

const SurveySummary = struct {
    devres_c_lines: usize,
    preexisting_phase13_build_present: bool,
    preexisting_phase13_make_target_present: bool,
    preexisting_lib_devres_zig_present: bool,
    preexisting_phase13_devres_test_present: bool,
    preexisting_phase13_slice_note_present: bool,
    preexisting_phase13_survey_note_present: bool,
    preexisting_managed_ioremap_resource_present: bool,
    preexisting_of_iomap_planner_present: bool,
    preexisting_arch_io_wc_memtype_planner_present: bool,
};

const Gap = struct {
    id: []const u8,
    status: []const u8,
    kind: []const u8,
    zigux_destination: []const u8,
    why_now: []const u8,
};

const Manifest = struct {
    lane_key: []const u8,
    phase: []const u8,
    surveyed_commit: []const u8,
    anchor: []const u8,
    roadmap_destinations: []const []const u8,
    survey_summary: SurveySummary,
    gaps: []const Gap,
};

fn isAllowedManifestStatus(status: []const u8) bool {
    return std.mem.eql(u8, status, "starter_landed") or
        std.mem.eql(u8, status, "ready_next") or
        std.mem.eql(u8, status, "blocked_on_live_resource_state");
}

test "phase13 devres descriptor stays anchored to lib/devres.c" {
    const descriptor = devres.DevresHelperLab.descriptor();

    try std.testing.expectEqualStrings("devres_helper_lab", descriptor.name);
    try std.testing.expectEqualStrings("lib/devres.c", descriptor.anchor);
    try std.testing.expect(descriptor.provides_ioremap_lifetime_planning);
    try std.testing.expect(descriptor.provides_release_pointer_match);
    try std.testing.expect(descriptor.provides_ioremap_resource_planning);
    try std.testing.expect(descriptor.provides_of_iomap_planning);
    try std.testing.expect(descriptor.provides_pretty_name_helper);
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

test "phase13 devres release matching stays pointer-exact" {
    try std.testing.expect(devres.DevresHelperLab.ioremapReleaseMatches(0x4000, 0x4000));
    try std.testing.expect(!devres.DevresHelperLab.ioremapReleaseMatches(0x4000, 0x4010));
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

test "phase13 devres manifest records the helper-only MMIO safety packet and remaining live gaps" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const manifest_json = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase13_devres_manifest.json",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(manifest_json);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();

    const manifest = parsed.value;
    try std.testing.expectEqualStrings("P13-L01", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 13", manifest.phase);
    try std.testing.expectEqualStrings("master-reviewability", manifest.surveyed_commit);
    try std.testing.expectEqualStrings("lib/devres.c", manifest.anchor);
    try std.testing.expectEqual(@as(usize, 3), manifest.roadmap_destinations.len);
    try std.testing.expectEqual(@as(usize, 399), manifest.survey_summary.devres_c_lines);
    try std.testing.expect(manifest.survey_summary.preexisting_phase13_build_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase13_make_target_present);
    try std.testing.expect(manifest.survey_summary.preexisting_lib_devres_zig_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase13_devres_test_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase13_slice_note_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase13_survey_note_present);
    try std.testing.expect(manifest.survey_summary.preexisting_managed_ioremap_resource_present);
    try std.testing.expect(manifest.survey_summary.preexisting_of_iomap_planner_present);
    try std.testing.expect(manifest.survey_summary.preexisting_arch_io_wc_memtype_planner_present);
    try std.testing.expectEqual(@as(usize, 13), manifest.gaps.len);

    const descriptor = devres.DevresHelperLab.descriptor();
    try std.testing.expectEqualStrings("lib/devres.c", descriptor.anchor);
    try std.testing.expect(descriptor.provides_ioremap_lifetime_planning);
    try std.testing.expect(descriptor.provides_ioremap_resource_planning);
    try std.testing.expect(descriptor.provides_of_iomap_planning);
    try std.testing.expect(descriptor.provides_arch_io_wc_memtype_planning);
    try std.testing.expect(!descriptor.touches_live_mmio);
    try std.testing.expect(!descriptor.touches_live_device_lists);
    try std.testing.expect(!descriptor.touches_live_arch_memtype);

    var starter_landed_count: usize = 0;
    var ready_next_count: usize = 0;
    var blocked_count: usize = 0;
    var saw_build_gate = false;
    var saw_make_target = false;
    var saw_helper_starter = false;
    var saw_test_gate = false;
    var saw_slice_note = false;
    var saw_survey_note = false;
    var saw_managed_resource = false;
    var saw_of_iomap = false;
    var saw_wc_memtype = false;
    var saw_phys_wc_followup = false;
    var saw_live_mmio_blocker = false;
    var saw_device_tree_blocker = false;
    var saw_arch_memtype_blocker = false;

    for (manifest.gaps, 0..) |gap, i| {
        try std.testing.expect(gap.id.len > 0);
        try std.testing.expect(gap.kind.len > 0);
        try std.testing.expect(gap.why_now.len > 0);
        try std.testing.expect(isAllowedManifestStatus(gap.status));

        if (std.mem.eql(u8, gap.status, "starter_landed")) {
            starter_landed_count += 1;
        } else if (std.mem.eql(u8, gap.status, "ready_next")) {
            ready_next_count += 1;
        } else if (std.mem.eql(u8, gap.status, "blocked_on_live_resource_state")) {
            blocked_count += 1;
        }

        if (std.mem.eql(u8, gap.id, "phase13-build-gate")) {
            saw_build_gate = true;
            try std.testing.expectEqualStrings("zigux/tests/phase13_build.zig", gap.zigux_destination);
        }
        if (std.mem.eql(u8, gap.id, "phase13-make-target")) {
            saw_make_target = true;
            try std.testing.expectEqualStrings("zigux/Makefile", gap.zigux_destination);
        }
        if (std.mem.eql(u8, gap.id, "phase13-devres-helper-starter")) {
            saw_helper_starter = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("lib/devres.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "__devm_ioremap") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase13-devres-test-gate")) {
            saw_test_gate = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("zigux/tests/phase13_devres.zig", gap.zigux_destination);
        }
        if (std.mem.eql(u8, gap.id, "phase13-devres-slice-note")) {
            saw_slice_note = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("Documentation/zigux/phase13-devres-slice.md", gap.zigux_destination);
        }
        if (std.mem.eql(u8, gap.id, "phase13-devres-survey-note")) {
            saw_survey_note = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("Documentation/zigux/phase13-devres-survey.md", gap.zigux_destination);
        }
        if (std.mem.eql(u8, gap.id, "phase13-devres-managed-resource-planner")) {
            saw_managed_resource = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("lib/devres.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "__devm_ioremap_resource") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase13-devres-of-iomap-planner")) {
            saw_of_iomap = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("lib/devres.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "devm_of_iomap") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase13-devres-arch-io-wc-planner")) {
            saw_wc_memtype = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("lib/devres.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "devm_arch_io_reserve_memtype_wc") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase13-devres-arch-phys-wc-token")) {
            saw_phys_wc_followup = true;
            try std.testing.expectEqualStrings("ready_next", gap.status);
            try std.testing.expectEqualStrings("lib/devres.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "devm_arch_phys_wc_add") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase13-devres-live-mmio-mappings")) {
            saw_live_mmio_blocker = true;
            try std.testing.expectEqualStrings("blocked_on_live_resource_state", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "live MMIO mappings") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase13-devres-live-device-tree-walk")) {
            saw_device_tree_blocker = true;
            try std.testing.expectEqualStrings("blocked_on_live_resource_state", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "device-tree") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase13-devres-live-arch-memtype-state")) {
            saw_arch_memtype_blocker = true;
            try std.testing.expectEqualStrings("blocked_on_live_resource_state", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "arch memtype") != null);
        }

        for (manifest.gaps[i + 1 ..]) |other| {
            try std.testing.expect(!std.mem.eql(u8, gap.id, other.id));
        }
    }

    try std.testing.expectEqual(@as(usize, 9), starter_landed_count);
    try std.testing.expectEqual(@as(usize, 1), ready_next_count);
    try std.testing.expectEqual(@as(usize, 3), blocked_count);
    try std.testing.expect(saw_build_gate);
    try std.testing.expect(saw_make_target);
    try std.testing.expect(saw_helper_starter);
    try std.testing.expect(saw_test_gate);
    try std.testing.expect(saw_slice_note);
    try std.testing.expect(saw_survey_note);
    try std.testing.expect(saw_managed_resource);
    try std.testing.expect(saw_of_iomap);
    try std.testing.expect(saw_wc_memtype);
    try std.testing.expect(saw_phys_wc_followup);
    try std.testing.expect(saw_live_mmio_blocker);
    try std.testing.expect(saw_device_tree_blocker);
    try std.testing.expect(saw_arch_memtype_blocker);
}
