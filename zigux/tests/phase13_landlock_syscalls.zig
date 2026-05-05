const std = @import("std");
const syscalls = @import("landlock_syscalls");

const SurveySummary = struct {
    syscalls_c_lines: usize,
    landlock_security_file_count: usize,
    preexisting_phase13_build_present: bool,
    preexisting_phase13_make_target_present: bool,
    preexisting_syscalls_zig_present: bool,
    preexisting_phase13_landlock_syscalls_test_present: bool,
    preexisting_phase13_landlock_syscalls_slice_note_present: bool,
    preexisting_phase13_landlock_syscalls_survey_note_present: bool,
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

fn isAllowedStatus(status: []const u8) bool {
    return std.mem.eql(u8, status, "starter_landed") or
        std.mem.eql(u8, status, "ready_next") or
        std.mem.eql(u8, status, "blocked_on_live_lsm_state");
}

test "phase13 landlock syscalls manifest records the starter and remaining gap" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const manifest_json = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase13_landlock_syscalls_manifest.json",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(manifest_json);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();

    const manifest = parsed.value;
    try std.testing.expectEqualStrings("P13-Y04", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 13", manifest.phase);
    try std.testing.expectEqualStrings("security/landlock/syscalls.c", manifest.anchor);
    try std.testing.expectEqualStrings("02f3325b2e289b7d492e022db0dbe7b61f2e22c3", manifest.surveyed_commit);
    try std.testing.expectEqual(@as(usize, 3), manifest.roadmap_destinations.len);
    try std.testing.expect(manifest.survey_summary.syscalls_c_lines >= 500);
    try std.testing.expect(manifest.survey_summary.landlock_security_file_count >= 20);
    try std.testing.expect(manifest.survey_summary.preexisting_phase13_build_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase13_make_target_present);
    try std.testing.expect(manifest.survey_summary.preexisting_syscalls_zig_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase13_landlock_syscalls_test_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase13_landlock_syscalls_slice_note_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase13_landlock_syscalls_survey_note_present);
    try std.testing.expectEqual(@as(usize, 11), manifest.gaps.len);

    var starter_landed_count: usize = 0;
    var ready_next_count: usize = 0;
    var blocked_count: usize = 0;
    var saw_build_gate = false;
    var saw_make_target = false;
    var saw_starter = false;
    var saw_test_gate = false;
    var saw_slice_note = false;
    var saw_survey_note = false;
    var saw_add_rule = false;
    var saw_fd_followup = false;
    var saw_path_followup = false;
    var saw_path_beneath_handoff = false;
    var saw_ruleset_release_followup = false;

    for (manifest.gaps, 0..) |gap, i| {
        try std.testing.expect(gap.id.len > 0);
        try std.testing.expect(gap.kind.len > 0);
        try std.testing.expect(gap.why_now.len > 0);
        try std.testing.expect(isAllowedStatus(gap.status));

        if (std.mem.eql(u8, gap.status, "starter_landed")) {
            starter_landed_count += 1;
        } else if (std.mem.eql(u8, gap.status, "ready_next")) {
            ready_next_count += 1;
        } else if (std.mem.eql(u8, gap.status, "blocked_on_live_lsm_state")) {
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
        if (std.mem.eql(u8, gap.id, "phase13-landlock-syscalls-starter")) {
            saw_starter = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("security/landlock/syscalls.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "build_check_abi()") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "landlock_create_ruleset()") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "landlock_restrict_self()") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "ruleset_fd == -1") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "mute-subdomains-only case") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase13-landlock-syscalls-test-gate")) {
            saw_test_gate = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("zigux/tests/phase13_landlock_syscalls.zig", gap.zigux_destination);
        }
        if (std.mem.eql(u8, gap.id, "phase13-landlock-syscalls-slice-note")) {
            saw_slice_note = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("Documentation/zigux/phase13-landlock-syscalls-slice.md", gap.zigux_destination);
        }
        if (std.mem.eql(u8, gap.id, "phase13-landlock-syscalls-survey-note")) {
            saw_survey_note = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("Documentation/zigux/phase13-landlock-syscalls-survey.md", gap.zigux_destination);
        }
        if (std.mem.eql(u8, gap.id, "phase13-landlock-add-rule-followup")) {
            saw_add_rule = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("security/landlock/syscalls.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "landlock_add_rule()") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "net-port bounds") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase13-landlock-ruleset-fd-mode-followup")) {
            saw_fd_followup = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("security/landlock/syscalls.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "get_ruleset_from_fd()") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "FMODE_CAN_WRITE") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase13-landlock-path-fd-followup")) {
            saw_path_followup = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("security/landlock/syscalls.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "get_path_from_fd()") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "private or non-user-visible inodes") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase13-landlock-path-beneath-handoff-followup")) {
            saw_path_beneath_handoff = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("security/landlock/syscalls.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "add_rule_path_beneath()") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "put_path()") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase13-landlock-ruleset-release-followup")) {
            saw_ruleset_release_followup = true;
            try std.testing.expectEqualStrings("ready_next", gap.status);
            try std.testing.expectEqualStrings("security/landlock/syscalls.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "fop_ruleset_release()") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "landlock_put_ruleset()") != null);
        }

        for (manifest.gaps[i + 1 ..]) |other| {
            try std.testing.expect(!std.mem.eql(u8, gap.id, other.id));
        }
    }

    try std.testing.expectEqual(@as(usize, 10), starter_landed_count);
    try std.testing.expectEqual(@as(usize, 1), ready_next_count);
    try std.testing.expectEqual(@as(usize, 0), blocked_count);
    try std.testing.expect(saw_build_gate);
    try std.testing.expect(saw_make_target);
    try std.testing.expect(saw_starter);
    try std.testing.expect(saw_test_gate);
    try std.testing.expect(saw_slice_note);
    try std.testing.expect(saw_survey_note);
    try std.testing.expect(saw_add_rule);
    try std.testing.expect(saw_fd_followup);
    try std.testing.expect(saw_path_followup);
    try std.testing.expect(saw_path_beneath_handoff);
    try std.testing.expect(saw_ruleset_release_followup);
}

test "phase13 landlock syscalls descriptor stays anchored to syscalls.c" {
    const descriptor = syscalls.SyscallsHelperLab.descriptor();

    try std.testing.expectEqualStrings("landlock_syscalls_helper_lab", descriptor.name);
    try std.testing.expectEqualStrings("security/landlock/syscalls.c", descriptor.anchor);
    try std.testing.expect(descriptor.provides_abi_shape_reporting);
    try std.testing.expect(descriptor.provides_create_ruleset_query_planning);
    try std.testing.expect(descriptor.provides_restrict_self_flag_planning);
    try std.testing.expect(descriptor.provides_add_rule_planning);
    try std.testing.expect(descriptor.provides_ruleset_fd_planning);
    try std.testing.expect(descriptor.provides_path_fd_planning);
    try std.testing.expect(descriptor.provides_path_beneath_handoff_planning);
    try std.testing.expect(!descriptor.touches_live_fd_table);
    try std.testing.expect(!descriptor.touches_live_paths);
    try std.testing.expect(!descriptor.touches_live_credentials);
    try std.testing.expect(!descriptor.touches_live_domains);
}

test "phase13 landlock syscalls survey note records the active lane key" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const survey_note = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase13-landlock-syscalls-survey.md",
        std.testing.allocator,
        .limited(16 * 1024),
    );
    defer std.testing.allocator.free(survey_note);

    try std.testing.expect(std.mem.indexOf(u8, survey_note, "`PHASE13_LANE_KEY=P13-Y04`") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "special `ruleset_fd == -1` mute-subdomains-only case") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "new in-memory `add_rule_path_beneath()` planner") != null);
}

test "phase13 landlock syscalls abi shape report matches build_check_abi expectations" {
    const report = syscalls.SyscallsHelperLab.reportAbiShapes();

    try std.testing.expectEqualStrings("security/landlock/syscalls.c", report.anchor);
    try std.testing.expectEqual(@as(usize, 24), report.ruleset_attr_size);
    try std.testing.expectEqual(@as(usize, 8), report.min_ruleset_attr_size);
    try std.testing.expectEqual(@as(usize, 12), report.path_beneath_attr_size);
    try std.testing.expectEqual(@as(usize, 16), report.net_port_attr_size);
    try std.testing.expectEqual(@as(usize, 4096), report.page_size_limit);
}

test "phase13 landlock syscalls create_ruleset planning covers queries and validated creation" {
    const version_query = try syscalls.SyscallsHelperLab.planCreateRuleset(.{
        .attr_present = false,
        .size = 0,
        .flags = syscalls.create_ruleset_version_flag,
        .allowed_fs_mask = 0,
        .allowed_net_mask = 0,
        .allowed_scope_mask = 0,
    });
    try std.testing.expectEqual(syscalls.CreateRulesetAction.abi_version_query, version_query.action);
    try std.testing.expectEqual(syscalls.abi_version, version_query.returned_value);

    const errata_query = try syscalls.SyscallsHelperLab.planCreateRuleset(.{
        .attr_present = false,
        .size = 0,
        .flags = syscalls.create_ruleset_errata_flag,
        .allowed_fs_mask = 0,
        .allowed_net_mask = 0,
        .allowed_scope_mask = 0,
        .errata_value = 12,
    });
    try std.testing.expectEqual(syscalls.CreateRulesetAction.errata_query, errata_query.action);
    try std.testing.expectEqual(@as(u32, 12), errata_query.returned_value);

    const plan = try syscalls.SyscallsHelperLab.planCreateRuleset(.{
        .attr = .{
            .handled_access_fs = 0b1010,
            .handled_access_net = 0b0011,
            .scoped = 0b0100,
        },
        .allowed_fs_mask = 0b1111,
        .allowed_net_mask = 0b1111,
        .allowed_scope_mask = 0b1111,
    });
    try std.testing.expectEqual(syscalls.CreateRulesetAction.create, plan.action);
    try std.testing.expectEqual(@as(u64, 0b1010), plan.handled_access_fs);
    try std.testing.expectEqual(@as(u64, 0b0011), plan.handled_access_net);
    try std.testing.expectEqual(@as(u64, 0b0100), plan.scoped);
}

test "phase13 landlock syscalls create_ruleset planning rejects invalid queries and masks" {
    try std.testing.expectError(error.InvalidQueryArguments, syscalls.SyscallsHelperLab.planCreateRuleset(.{
        .flags = syscalls.create_ruleset_version_flag,
        .allowed_fs_mask = 0,
        .allowed_net_mask = 0,
        .allowed_scope_mask = 0,
    }));
    try std.testing.expectError(error.StructTooSmall, syscalls.SyscallsHelperLab.planCreateRuleset(.{
        .size = 4,
        .allowed_fs_mask = 0xff,
        .allowed_net_mask = 0xff,
        .allowed_scope_mask = 0xff,
    }));
    try std.testing.expectError(error.StructTooLarge, syscalls.SyscallsHelperLab.planCreateRuleset(.{
        .size = 8192,
        .allowed_fs_mask = 0xff,
        .allowed_net_mask = 0xff,
        .allowed_scope_mask = 0xff,
    }));
    try std.testing.expectError(error.InvalidFsAccessMask, syscalls.SyscallsHelperLab.planCreateRuleset(.{
        .attr = .{ .handled_access_fs = 0b10000 },
        .allowed_fs_mask = 0b01111,
        .allowed_net_mask = 0,
        .allowed_scope_mask = 0,
    }));
    try std.testing.expectError(error.EmptyRuleset, syscalls.SyscallsHelperLab.planCreateRuleset(.{
        .allowed_fs_mask = 0xff,
        .allowed_net_mask = 0xff,
        .allowed_scope_mask = 0xff,
    }));
}

test "phase13 landlock syscalls restrict_self planning models the mute-only exception and translated flags" {
    const mute_plan = try syscalls.SyscallsHelperLab.planRestrictSelf(
        -1,
        syscalls.restrict_self_log_subdomains_off | syscalls.restrict_self_tsync,
    );
    try std.testing.expect(!mute_plan.requires_ruleset);
    try std.testing.expect(mute_plan.log_same_exec);
    try std.testing.expect(!mute_plan.log_new_exec);
    try std.testing.expect(!mute_plan.log_subdomains);
    try std.testing.expect(mute_plan.propagates_to_siblings);

    const restrict_plan = try syscalls.SyscallsHelperLab.planRestrictSelf(
        7,
        syscalls.restrict_self_log_same_exec_off | syscalls.restrict_self_log_new_exec_on,
    );
    try std.testing.expect(restrict_plan.requires_ruleset);
    try std.testing.expect(!restrict_plan.log_same_exec);
    try std.testing.expect(restrict_plan.log_new_exec);
    try std.testing.expect(restrict_plan.log_subdomains);
    try std.testing.expect(!restrict_plan.propagates_to_siblings);

    try std.testing.expectError(error.MissingRuleset, syscalls.SyscallsHelperLab.planRestrictSelf(
        -1,
        syscalls.restrict_self_log_new_exec_on,
    ));
    try std.testing.expectError(error.InvalidFlags, syscalls.SyscallsHelperLab.planRestrictSelf(3, 1 << 7));
}

test "phase13 landlock syscalls add_rule planning dispatches path and net rules" {
    const path_plan = try syscalls.SyscallsHelperLab.planAddRule(.{
        .rule_type = syscalls.rule_type_path_beneath,
        .handled_access_fs = 0b1111,
        .path_beneath_attr = .{
            .allowed_access = 0b0011,
            .parent_fd = 42,
        },
    });
    try std.testing.expectEqual(syscalls.AddRuleAction.path_beneath, path_plan.action);
    try std.testing.expect(path_plan.requires_ruleset_write_access);
    try std.testing.expect(path_plan.requires_path_lookup);
    try std.testing.expectEqual(@as(i32, 42), path_plan.parent_fd);
    try std.testing.expectEqual(@as(?u16, null), path_plan.port);

    const net_plan = try syscalls.SyscallsHelperLab.planAddRule(.{
        .rule_type = syscalls.rule_type_net_port,
        .handled_access_net = 0b0111,
        .net_port_attr = .{
            .allowed_access = 0b0011,
            .port = 443,
        },
    });
    try std.testing.expectEqual(syscalls.AddRuleAction.net_port, net_plan.action);
    try std.testing.expect(net_plan.requires_ruleset_write_access);
    try std.testing.expect(!net_plan.requires_path_lookup);
    try std.testing.expectEqual(@as(?u16, 443), net_plan.port);
}

test "phase13 landlock syscalls add_rule planning rejects invalid flags and bounds drift" {
    try std.testing.expectError(error.InvalidFlags, syscalls.SyscallsHelperLab.planAddRule(.{
        .flags = 1,
        .rule_type = syscalls.rule_type_path_beneath,
    }));
    try std.testing.expectError(error.EmptyAccess, syscalls.SyscallsHelperLab.planAddRule(.{
        .rule_type = syscalls.rule_type_path_beneath,
        .handled_access_fs = 0b1111,
    }));
    try std.testing.expectError(error.InvalidPathAccessMask, syscalls.SyscallsHelperLab.planAddRule(.{
        .rule_type = syscalls.rule_type_path_beneath,
        .handled_access_fs = 0b0001,
        .path_beneath_attr = .{ .allowed_access = 0b0010 },
    }));
    try std.testing.expectError(error.InvalidNetAccessMask, syscalls.SyscallsHelperLab.planAddRule(.{
        .rule_type = syscalls.rule_type_net_port,
        .handled_access_net = 0b0001,
        .net_port_attr = .{
            .allowed_access = 0b0010,
            .port = 80,
        },
    }));
    try std.testing.expectError(error.PortTooLarge, syscalls.SyscallsHelperLab.planAddRule(.{
        .rule_type = syscalls.rule_type_net_port,
        .handled_access_net = 0b1111,
        .net_port_attr = .{
            .allowed_access = 0b0010,
            .port = 70000,
        },
    }));
    try std.testing.expectError(error.InvalidRuleType, syscalls.SyscallsHelperLab.planAddRule(.{
        .rule_type = 99,
    }));
}

test "phase13 landlock add-rule wrapper planner keeps write-fd dispatch explicit" {
    const path_plan = try syscalls.SyscallsHelperLab.planLandlockAddRule(.{
        .ruleset_fd = .{
            .file_mode = syscalls.fmode_can_write,
            .required_mode = syscalls.fmode_can_write,
        },
        .rule_type = syscalls.rule_type_path_beneath,
        .handled_access_fs = 0x7,
        .path_beneath_attr = .{
            .allowed_access = 0x3,
            .parent_fd = 42,
        },
    });

    try std.testing.expectEqualStrings("security/landlock/syscalls.c", path_plan.anchor);
    try std.testing.expect(path_plan.checks_initialization_gate);
    try std.testing.expect(path_plan.requires_zero_flags);
    try std.testing.expect(path_plan.acquires_ruleset_with_write_access);
    try std.testing.expect(path_plan.reuses_add_rule_validation);
    try std.testing.expectEqual(syscalls.AddRuleAction.path_beneath, path_plan.dispatched_rule.action);
    try std.testing.expect(path_plan.dispatched_rule.requires_ruleset_write_access);
    try std.testing.expect(path_plan.dispatched_rule.requires_path_lookup);
    try std.testing.expectEqual(@as(i32, 42), path_plan.dispatched_rule.parent_fd);

    const net_plan = try syscalls.SyscallsHelperLab.planLandlockAddRule(.{
        .ruleset_fd = .{
            .file_mode = syscalls.fmode_can_write,
            .required_mode = syscalls.fmode_can_write,
        },
        .rule_type = syscalls.rule_type_net_port,
        .handled_access_net = 0x5,
        .net_port_attr = .{
            .allowed_access = 0x1,
            .port = 443,
        },
    });

    try std.testing.expectEqual(syscalls.AddRuleAction.net_port, net_plan.dispatched_rule.action);
    try std.testing.expectEqual(@as(?u16, 443), net_plan.dispatched_rule.port);
    try std.testing.expect(!net_plan.dispatched_rule.requires_path_lookup);
}

test "phase13 landlock add-rule wrapper planner rejects disabled state flags and non-writable rulesets" {
    try std.testing.expectError(error.BootDisabled, syscalls.SyscallsHelperLab.planLandlockAddRule(.{
        .initialized = false,
        .ruleset_fd = .{
            .file_mode = syscalls.fmode_can_write,
            .required_mode = syscalls.fmode_can_write,
        },
        .rule_type = syscalls.rule_type_path_beneath,
        .handled_access_fs = 0x1,
        .path_beneath_attr = .{ .allowed_access = 0x1 },
    }));

    try std.testing.expectError(error.InvalidFlags, syscalls.SyscallsHelperLab.planLandlockAddRule(.{
        .ruleset_fd = .{
            .file_mode = syscalls.fmode_can_write,
            .required_mode = syscalls.fmode_can_write,
        },
        .flags = 1,
        .rule_type = syscalls.rule_type_path_beneath,
        .handled_access_fs = 0x1,
        .path_beneath_attr = .{ .allowed_access = 0x1 },
    }));

    try std.testing.expectError(error.InsufficientMode, syscalls.SyscallsHelperLab.planLandlockAddRule(.{
        .ruleset_fd = .{
            .file_mode = syscalls.fmode_can_read,
            .required_mode = syscalls.fmode_can_write,
        },
        .rule_type = syscalls.rule_type_net_port,
        .handled_access_net = 0x1,
        .net_port_attr = .{ .allowed_access = 0x1, .port = 80 },
    }));
}

test "phase13 landlock syscalls get_ruleset_from_fd planning models mode checks and retained references" {
    const write_plan = try syscalls.SyscallsHelperLab.planGetRulesetFromFd(.{
        .file_mode = syscalls.fmode_can_read | syscalls.fmode_can_write,
        .required_mode = syscalls.fmode_can_write,
    });
    try std.testing.expectEqual(@as(u32, syscalls.fmode_can_write), write_plan.required_mode);
    try std.testing.expect(write_plan.validates_fd_type);
    try std.testing.expect(write_plan.validates_mode);
    try std.testing.expect(write_plan.acquires_ruleset_reference);
    try std.testing.expectEqual(@as(usize, 1), write_plan.expected_layer_count);

    const read_plan = try syscalls.SyscallsHelperLab.planGetRulesetFromFd(.{
        .file_mode = syscalls.fmode_can_read,
        .required_mode = syscalls.fmode_can_read,
    });
    try std.testing.expectEqual(@as(u32, syscalls.fmode_can_read), read_plan.required_mode);
}

test "phase13 landlock syscalls get_ruleset_from_fd planning rejects bad fd, type, mode, and layer drift" {
    try std.testing.expectError(error.InvalidRequestedMode, syscalls.SyscallsHelperLab.planGetRulesetFromFd(.{
        .required_mode = 0,
    }));
    try std.testing.expectError(error.BadFileDescriptor, syscalls.SyscallsHelperLab.planGetRulesetFromFd(.{
        .fd_present = false,
        .required_mode = syscalls.fmode_can_write,
    }));
    try std.testing.expectError(error.InvalidRulesetFdType, syscalls.SyscallsHelperLab.planGetRulesetFromFd(.{
        .file_kind = .other,
        .file_mode = syscalls.fmode_can_write,
        .required_mode = syscalls.fmode_can_write,
    }));
    try std.testing.expectError(error.InsufficientMode, syscalls.SyscallsHelperLab.planGetRulesetFromFd(.{
        .file_mode = syscalls.fmode_can_read,
        .required_mode = syscalls.fmode_can_write,
    }));
    try std.testing.expectError(error.InvalidLayerCount, syscalls.SyscallsHelperLab.planGetRulesetFromFd(.{
        .file_mode = syscalls.fmode_can_read,
        .required_mode = syscalls.fmode_can_read,
        .layer_count = 2,
    }));
}

test "phase13 landlock syscalls get_path_from_fd planning models bounded path acquisition" {
    const plan = try syscalls.SyscallsHelperLab.planGetPathFromFd(.{});
    try std.testing.expectEqualStrings("security/landlock/syscalls.c", plan.anchor);
    try std.testing.expect(plan.rejects_ruleset_fd);
    try std.testing.expect(plan.rejects_internal_mount);
    try std.testing.expect(plan.rejects_nouser_superblock);
    try std.testing.expect(plan.rejects_private_inode);
    try std.testing.expect(plan.acquires_path_reference);
}

test "phase13 landlock syscalls get_path_from_fd planning rejects invalid path sources" {
    try std.testing.expectError(error.BadFileDescriptor, syscalls.SyscallsHelperLab.planGetPathFromFd(.{
        .fd_present = false,
    }));
    try std.testing.expectError(error.InvalidPathFdType, syscalls.SyscallsHelperLab.planGetPathFromFd(.{
        .is_ruleset_fd = true,
    }));
    try std.testing.expectError(error.InternalMount, syscalls.SyscallsHelperLab.planGetPathFromFd(.{
        .mount_is_internal = true,
    }));
    try std.testing.expectError(error.NonUserVisiblePath, syscalls.SyscallsHelperLab.planGetPathFromFd(.{
        .superblock_is_nouser = true,
    }));
    try std.testing.expectError(error.PrivateInode, syscalls.SyscallsHelperLab.planGetPathFromFd(.{
        .inode_is_private = true,
    }));
}

test "phase13 landlock syscalls path-beneath handoff planner keeps parent-path and put_path responsibility explicit" {
    const plan = try syscalls.SyscallsHelperLab.planAddRulePathBeneathHandoff(.{
        .handled_access_fs = 0x7,
        .path_beneath_attr = .{
            .allowed_access = 0x3,
            .parent_fd = 42,
        },
        .parent_path = .{},
    });

    try std.testing.expectEqualStrings("security/landlock/syscalls.c", plan.anchor);
    try std.testing.expectEqual(@as(u64, 0x3), plan.allowed_access);
    try std.testing.expectEqual(@as(i32, 42), plan.parent_fd);
    try std.testing.expect(plan.reuses_add_rule_validation);
    try std.testing.expect(plan.reuses_path_fd_validation);
    try std.testing.expect(plan.acquires_parent_path_reference);
    try std.testing.expect(plan.releases_parent_path_reference);
}

test "phase13 landlock syscalls path-beneath handoff planner rejects bad path sources and invalid access masks" {
    try std.testing.expectError(error.InvalidPathAccessMask, syscalls.SyscallsHelperLab.planAddRulePathBeneathHandoff(.{
        .handled_access_fs = 0x1,
        .path_beneath_attr = .{
            .allowed_access = 0x2,
            .parent_fd = 42,
        },
    }));

    try std.testing.expectError(error.InternalMount, syscalls.SyscallsHelperLab.planAddRulePathBeneathHandoff(.{
        .handled_access_fs = 0x3,
        .path_beneath_attr = .{
            .allowed_access = 0x1,
            .parent_fd = 42,
        },
        .parent_path = .{
            .mount_is_internal = true,
        },
    }));
}
