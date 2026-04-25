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
    try std.testing.expectEqualStrings("P13-L13", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 13", manifest.phase);
    try std.testing.expectEqualStrings("security/landlock/syscalls.c", manifest.anchor);
    try std.testing.expectEqualStrings("bfd60deac631b66bf5eab7608c8ffd8f982893cb", manifest.surveyed_commit);
    try std.testing.expectEqual(@as(usize, 3), manifest.roadmap_destinations.len);
    try std.testing.expect(manifest.survey_summary.syscalls_c_lines >= 500);
    try std.testing.expect(manifest.survey_summary.landlock_security_file_count >= 20);
    try std.testing.expect(manifest.survey_summary.preexisting_phase13_build_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase13_make_target_present);
    try std.testing.expect(manifest.survey_summary.preexisting_syscalls_zig_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase13_landlock_syscalls_test_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase13_landlock_syscalls_slice_note_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase13_landlock_syscalls_survey_note_present);
    try std.testing.expectEqual(@as(usize, 8), manifest.gaps.len);

    var starter_landed_count: usize = 0;
    var ready_next_count: usize = 0;
    var saw_build_gate = false;
    var saw_make_target = false;
    var saw_starter = false;
    var saw_test_gate = false;
    var saw_slice_note = false;
    var saw_survey_note = false;
    var saw_followup = false;
    var saw_blocked = false;

    for (manifest.gaps, 0..) |gap, i| {
        try std.testing.expect(gap.id.len > 0);
        try std.testing.expect(gap.kind.len > 0);
        try std.testing.expect(gap.why_now.len > 0);
        try std.testing.expect(isAllowedStatus(gap.status));

        if (std.mem.eql(u8, gap.status, "starter_landed")) {
            starter_landed_count += 1;
        } else if (std.mem.eql(u8, gap.status, "ready_next")) {
            ready_next_count += 1;
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
            saw_followup = true;
            try std.testing.expectEqualStrings("ready_next", gap.status);
            try std.testing.expectEqualStrings("security/landlock/syscalls.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "landlock_add_rule()") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "rule-type dispatch") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase13-landlock-live-fd-path-and-cred-state")) {
            saw_blocked = true;
            try std.testing.expectEqualStrings("blocked_on_live_lsm_state", gap.status);
            try std.testing.expectEqualStrings("zigux/tests/phase13_landlock_syscalls.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "anon_inode_getfd") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "prepare_creds") != null);
        }

        for (manifest.gaps[i + 1 ..]) |other| {
            try std.testing.expect(!std.mem.eql(u8, gap.id, other.id));
        }
    }

    try std.testing.expectEqual(@as(usize, 6), starter_landed_count);
    try std.testing.expectEqual(@as(usize, 1), ready_next_count);
    try std.testing.expect(saw_build_gate);
    try std.testing.expect(saw_make_target);
    try std.testing.expect(saw_starter);
    try std.testing.expect(saw_test_gate);
    try std.testing.expect(saw_slice_note);
    try std.testing.expect(saw_survey_note);
    try std.testing.expect(saw_followup);
    try std.testing.expect(saw_blocked);
}

test "phase13 landlock syscalls descriptor stays anchored to syscalls.c" {
    const descriptor = syscalls.SyscallsHelperLab.descriptor();

    try std.testing.expectEqualStrings("landlock_syscalls_helper_lab", descriptor.name);
    try std.testing.expectEqualStrings("security/landlock/syscalls.c", descriptor.anchor);
    try std.testing.expect(descriptor.provides_abi_shape_reporting);
    try std.testing.expect(descriptor.provides_create_ruleset_query_planning);
    try std.testing.expect(descriptor.provides_restrict_self_flag_planning);
    try std.testing.expect(!descriptor.touches_live_fd_table);
    try std.testing.expect(!descriptor.touches_live_paths);
    try std.testing.expect(!descriptor.touches_live_credentials);
    try std.testing.expect(!descriptor.touches_live_domains);
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
