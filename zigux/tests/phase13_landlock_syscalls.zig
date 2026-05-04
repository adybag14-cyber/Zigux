const std = @import("std");
const syscalls = @import("landlock_syscalls");

const SurveySummary = struct {
    syscalls_c_lines: usize,
    landlock_security_file_count: usize,
    preexisting_phase13_build_present: bool,
    preexisting_phase13_make_target_present: bool,
    preexisting_syscalls_zig_present: bool,
    preexisting_phase13_landlock_syscalls_test_present: bool,
    preexisting_phase13_landlock_syscalls_reviewability_present: bool,
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

const expected_surveyed_commit = "672d03034b090ab859f4088396160ea13120e1d6";
const expected_slice_marker = "PHASE13_SLICE=landlock-syscalls-helper-pure-handoff-boundary";

fn isAllowedStatus(status: []const u8) bool {
    return std.mem.eql(u8, status, "starter_landed") or
        std.mem.eql(u8, status, "ready_next") or
        std.mem.eql(u8, status, "blocked_on_live_lsm_state");
}

test "phase13 landlock syscalls manifest records the current landed packet" {
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
    const survey_note = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase13-landlock-syscalls-survey.md",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(survey_note);

    try std.testing.expectEqualStrings("P13-L16", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 13", manifest.phase);
    try std.testing.expectEqualStrings("security/landlock/syscalls.c", manifest.anchor);
    try std.testing.expectEqualStrings(expected_surveyed_commit, manifest.surveyed_commit);
    try std.testing.expectEqual(@as(usize, 3), manifest.roadmap_destinations.len);
    try std.testing.expect(manifest.survey_summary.syscalls_c_lines >= 500);
    try std.testing.expectEqual(@as(usize, 35), manifest.survey_summary.landlock_security_file_count);
    try std.testing.expect(manifest.survey_summary.preexisting_phase13_build_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase13_make_target_present);
    try std.testing.expect(manifest.survey_summary.preexisting_syscalls_zig_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase13_landlock_syscalls_test_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase13_landlock_syscalls_reviewability_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase13_landlock_syscalls_slice_note_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase13_landlock_syscalls_survey_note_present);
    try std.testing.expectEqual(@as(usize, 17), manifest.gaps.len);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, expected_surveyed_commit) != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "PHASE13_SURVEYED_COMMIT=") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, expected_slice_marker) != null);

    var starter_landed_count: usize = 0;
    var ready_next_count: usize = 0;
    var saw_build_gate = false;
    var saw_make_target = false;
    var saw_starter = false;
    var saw_test_gate = false;
    var saw_reviewability_gate = false;
    var saw_slice_note = false;
    var saw_survey_note = false;
    var saw_initialization_gate = false;
    var saw_copy_min_struct = false;
    var saw_add_rule = false;
    var saw_fd_followup = false;
    var saw_path_followup = false;
    var saw_path_beneath_handoff = false;
    var saw_net_port_handoff = false;
    var saw_ruleset_fd_creation_handoff = false;
    var saw_restrict_self_credential_handoff = false;
    var saw_ruleset_fops_followup = false;

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
        if (std.mem.eql(u8, gap.id, "phase13-landlock-syscalls-reviewability-gate")) {
            saw_reviewability_gate = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("zigux/tests/phase13_landlock_syscalls_reviewability.zig", gap.zigux_destination);
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
        if (std.mem.eql(u8, gap.id, "phase13-landlock-initialization-gate-followup")) {
            saw_initialization_gate = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("security/landlock/syscalls.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "is_initialized()") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "-EOPNOTSUPP") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase13-landlock-copy-min-struct-followup")) {
            saw_copy_min_struct = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("security/landlock/syscalls.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "copy_min_struct_from_user()") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "zero-fill") != null);
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
        if (std.mem.eql(u8, gap.id, "phase13-landlock-net-port-import-followup")) {
            saw_net_port_handoff = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("security/landlock/syscalls.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "add_rule_net_port()") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "landlock_append_net_rule()") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase13-landlock-ruleset-fd-creation-handoff-followup")) {
            saw_ruleset_fd_creation_handoff = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("security/landlock/syscalls.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "anon_inode_getfd()") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "landlock_put_ruleset()") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase13-landlock-restrict-self-credential-handoff-followup")) {
            saw_restrict_self_credential_handoff = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("security/landlock/syscalls.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "prepare_creds()") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "commit_creds()") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase13-landlock-ruleset-fops-followup")) {
            saw_ruleset_fops_followup = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("security/landlock/syscalls.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "ruleset_fops") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "fop_ruleset_release()") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "FMODE_CAN_READ") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "FMODE_CAN_WRITE") != null);
        }

        for (manifest.gaps[i + 1 ..]) |other| {
            try std.testing.expect(!std.mem.eql(u8, gap.id, other.id));
        }
    }

    try std.testing.expectEqual(@as(usize, 17), starter_landed_count);
    try std.testing.expectEqual(@as(usize, 0), ready_next_count);
    try std.testing.expect(saw_build_gate);
    try std.testing.expect(saw_make_target);
    try std.testing.expect(saw_starter);
    try std.testing.expect(saw_test_gate);
    try std.testing.expect(saw_reviewability_gate);
    try std.testing.expect(saw_slice_note);
    try std.testing.expect(saw_survey_note);
    try std.testing.expect(saw_initialization_gate);
    try std.testing.expect(saw_copy_min_struct);
    try std.testing.expect(saw_add_rule);
    try std.testing.expect(saw_fd_followup);
    try std.testing.expect(saw_path_followup);
    try std.testing.expect(saw_path_beneath_handoff);
    try std.testing.expect(saw_net_port_handoff);
    try std.testing.expect(saw_ruleset_fd_creation_handoff);
    try std.testing.expect(saw_restrict_self_credential_handoff);
    try std.testing.expect(saw_ruleset_fops_followup);
}

test "phase13 landlock syscalls descriptor stays anchored to syscalls.c" {
    const descriptor = syscalls.SyscallsHelperLab.descriptor();

    try std.testing.expectEqualStrings("landlock_syscalls_helper_lab", descriptor.name);
    try std.testing.expectEqualStrings("security/landlock/syscalls.c", descriptor.anchor);
    try std.testing.expect(descriptor.provides_abi_shape_reporting);
    try std.testing.expect(descriptor.provides_initialization_gate_planning);
    try std.testing.expect(descriptor.provides_min_struct_copy_planning);
    try std.testing.expect(descriptor.provides_create_ruleset_query_planning);
    try std.testing.expect(descriptor.provides_restrict_self_flag_planning);
    try std.testing.expect(descriptor.provides_restrict_self_credential_handoff_planning);
    try std.testing.expect(descriptor.provides_add_rule_planning);
    try std.testing.expect(descriptor.provides_rule_attr_copy_planning);
    try std.testing.expect(descriptor.provides_ruleset_fd_planning);
    try std.testing.expect(descriptor.provides_ruleset_fd_creation_planning);
    try std.testing.expect(descriptor.provides_ruleset_fops_planning);
    try std.testing.expect(descriptor.provides_path_fd_planning);
    try std.testing.expect(descriptor.provides_path_beneath_handoff_planning);
    try std.testing.expect(descriptor.provides_net_port_handoff_planning);
    try std.testing.expect(!descriptor.touches_live_fd_table);
    try std.testing.expect(!descriptor.touches_live_paths);
    try std.testing.expect(!descriptor.touches_live_credentials);
    try std.testing.expect(!descriptor.touches_live_domains);
}

test "phase13 landlock initialization gate planner keeps shared boot-disabled contract explicit" {
    const initialized = syscalls.SyscallsHelperLab.planInitializationGate(true);
    try std.testing.expectEqualStrings("security/landlock/syscalls.c", initialized.anchor);
    try std.testing.expect(initialized.initialized);
    try std.testing.expect(!initialized.returns_eopnotsupp_when_disabled);
    try std.testing.expect(!initialized.emits_boot_disabled_warning);
    try std.testing.expect(initialized.gates_create_ruleset);
    try std.testing.expect(initialized.gates_add_rule);
    try std.testing.expect(initialized.gates_restrict_self);

    const disabled = syscalls.SyscallsHelperLab.planInitializationGate(false);
    try std.testing.expect(!disabled.initialized);
    try std.testing.expect(disabled.returns_eopnotsupp_when_disabled);
    try std.testing.expect(disabled.emits_boot_disabled_warning);
    try std.testing.expect(disabled.gates_create_ruleset);
    try std.testing.expect(disabled.gates_add_rule);
    try std.testing.expect(disabled.gates_restrict_self);
}

test "phase13 landlock rule attr copy planner keeps fixed-size imports explicit" {
    const path_plan = try syscalls.SyscallsHelperLab.planCopyRuleAttr(.{
        .kind = .path_beneath,
    });
    try std.testing.expectEqualStrings("security/landlock/syscalls.c", path_plan.anchor);
    try std.testing.expectEqual(syscalls.RuleAttrKind.path_beneath, path_plan.kind);
    try std.testing.expectEqual(@as(usize, 12), path_plan.copy_bytes);
    try std.testing.expect(path_plan.uses_copy_from_user);
    try std.testing.expect(path_plan.rejects_partial_copy);
    try std.testing.expect(path_plan.returns_bad_pointer_on_copy_failure);
    try std.testing.expect(path_plan.follows_with_empty_access_check);

    const net_plan = try syscalls.SyscallsHelperLab.planCopyRuleAttr(.{
        .kind = .net_port,
    });
    try std.testing.expectEqual(syscalls.RuleAttrKind.net_port, net_plan.kind);
    try std.testing.expectEqual(@as(usize, 16), net_plan.copy_bytes);
    try std.testing.expect(net_plan.uses_copy_from_user);
    try std.testing.expect(net_plan.rejects_partial_copy);
    try std.testing.expect(net_plan.returns_bad_pointer_on_copy_failure);
    try std.testing.expect(net_plan.follows_with_empty_access_check);
}

test "phase13 landlock rule attr copy planner rejects missing and partial user buffers" {
    try std.testing.expectError(error.BadUserPointer, syscalls.SyscallsHelperLab.planCopyRuleAttr(.{
        .kind = .path_beneath,
        .attr_present = false,
    }));
    try std.testing.expectError(error.BadUserPointer, syscalls.SyscallsHelperLab.planCopyRuleAttr(.{
        .kind = .net_port,
        .uncopied_bytes = 1,
    }));
}

test "phase13 landlock restrict_self credential handoff models merge and tsync flow" {
    const plan = try syscalls.SyscallsHelperLab.planRestrictSelfCredentialHandoff(.{
        .ruleset_fd = 7,
        .flags = syscalls.restrict_self_log_new_exec_on | syscalls.restrict_self_tsync,
        .has_no_new_privs = true,
    });

    try std.testing.expectEqualStrings("security/landlock/syscalls.c", plan.anchor);
    try std.testing.expect(plan.requires_privilege_gate);
    try std.testing.expect(plan.acquires_ruleset_with_read_access);
    try std.testing.expect(plan.prepares_new_credentials);
    try std.testing.expect(plan.updates_log_subdomains_state);
    try std.testing.expect(plan.merges_ruleset_domain);
    try std.testing.expect(plan.replaces_prepared_domain);
    try std.testing.expect(plan.releases_previous_domain);
    try std.testing.expect(plan.propagates_to_siblings);
    try std.testing.expect(plan.aborts_creds_on_merge_failure);
    try std.testing.expect(plan.aborts_creds_on_tsync_failure);
    try std.testing.expect(plan.commits_prepared_credentials);
}

test "phase13 landlock restrict_self credential handoff allows mute-only update without ruleset" {
    const plan = try syscalls.SyscallsHelperLab.planRestrictSelfCredentialHandoff(.{
        .ruleset_fd = -1,
        .flags = syscalls.restrict_self_log_subdomains_off,
        .has_cap_sys_admin = true,
    });

    try std.testing.expect(plan.requires_privilege_gate);
    try std.testing.expect(!plan.acquires_ruleset_with_read_access);
    try std.testing.expect(plan.prepares_new_credentials);
    try std.testing.expect(plan.updates_log_subdomains_state);
    try std.testing.expect(!plan.merges_ruleset_domain);
    try std.testing.expect(!plan.replaces_prepared_domain);
    try std.testing.expect(!plan.releases_previous_domain);
    try std.testing.expect(!plan.propagates_to_siblings);
    try std.testing.expect(!plan.aborts_creds_on_merge_failure);
    try std.testing.expect(!plan.aborts_creds_on_tsync_failure);
    try std.testing.expect(plan.commits_prepared_credentials);
}

test "phase13 landlock restrict_self credential handoff requires privilege gate" {
    try std.testing.expectError(error.MissingPrivilege, syscalls.SyscallsHelperLab.planRestrictSelfCredentialHandoff(.{
        .ruleset_fd = 3,
        .flags = 0,
    }));
}

test "phase13 landlock syscalls ruleset fd creation plan captures file-operations contract" {
    const plan = try syscalls.SyscallsHelperLab.planCreateRulesetFd(.{});

    try std.testing.expectEqualStrings("security/landlock/syscalls.c", plan.anchor);
    try std.testing.expectEqualStrings(syscalls.ruleset_fd_label, plan.label);
    try std.testing.expectEqual(syscalls.ruleset_fd_flags, plan.flags);
    try std.testing.expect(plan.invokes_anon_inode_getfd);
    try std.testing.expect(plan.installs_release_handler);
    try std.testing.expect(plan.release_handler_puts_ruleset);
    try std.testing.expect(plan.installs_dummy_read_handler);
    try std.testing.expect(plan.installs_dummy_write_handler);
    try std.testing.expect(plan.transfers_ruleset_to_fd_on_success);
    try std.testing.expect(plan.releases_ruleset_on_fd_failure);
}


test "phase13 landlock ruleset fops planner keeps release and dummy handler contracts explicit" {
    const release = syscalls.SyscallsHelperLab.planRulesetFops(.release);
    try std.testing.expectEqualStrings("security/landlock/syscalls.c", release.anchor);
    try std.testing.expectEqual(syscalls.RulesetFopsOperation.release, release.operation);
    try std.testing.expectEqual(@as(u32, 0), release.enables_mode);
    try std.testing.expect(release.drops_ruleset_reference);
    try std.testing.expect(release.returns_zero);
    try std.testing.expect(!release.returns_einval);
    try std.testing.expect(!release.mutates_ruleset_state);

    const read = syscalls.SyscallsHelperLab.planRulesetFops(.read);
    try std.testing.expectEqual(syscalls.RulesetFopsOperation.read, read.operation);
    try std.testing.expectEqual(syscalls.fmode_can_read, read.enables_mode);
    try std.testing.expect(!read.drops_ruleset_reference);
    try std.testing.expect(!read.returns_zero);
    try std.testing.expect(read.returns_einval);
    try std.testing.expect(!read.mutates_ruleset_state);

    const write = syscalls.SyscallsHelperLab.planRulesetFops(.write);
    try std.testing.expectEqual(syscalls.RulesetFopsOperation.write, write.operation);
    try std.testing.expectEqual(syscalls.fmode_can_write, write.enables_mode);
    try std.testing.expect(!write.drops_ruleset_reference);
    try std.testing.expect(!write.returns_zero);
    try std.testing.expect(write.returns_einval);
    try std.testing.expect(!write.mutates_ruleset_state);
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
