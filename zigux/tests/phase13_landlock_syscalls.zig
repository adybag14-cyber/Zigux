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

const expected_surveyed_commit = "9c17b0790799d8240ef9f964903f5ce2db64af89";
const expected_slice_marker = "PHASE13_SLICE=landlock-syscalls-helper-restrict-self-credential-handoff";

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
    const survey_note = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase13-landlock-syscalls-survey.md",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(survey_note);

    try std.testing.expectEqualStrings("P13-L14", manifest.lane_key);
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
    try std.testing.expect(manifest.survey_summary.preexisting_phase13_landlock_syscalls_slice_note_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase13_landlock_syscalls_survey_note_present);
    try std.testing.expectEqual(@as(usize, 14), manifest.gaps.len);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, expected_surveyed_commit) != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "PHASE13_SURVEYED_COMMIT=") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, expected_slice_marker) != null);

    var starter_landed_count: usize = 0;
    var ready_next_count: usize = 0;
    var saw_build_gate = false;
    var saw_make_target = false;
    var saw_starter = false;
    var saw_test_gate = false;
    var saw_slice_note = false;
    var saw_survey_note = false;
    var saw_copy_min_struct = false;
    var saw_add_rule = false;
    var saw_fd_followup = false;
    var saw_path_followup = false;
    var saw_path_beneath_handoff = false;
    var saw_net_port_handoff = false;
    var saw_ruleset_fd_creation_handoff = false;
    var saw_restrict_self_credential_handoff = false;

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

        for (manifest.gaps[i + 1 ..]) |other| {
            try std.testing.expect(!std.mem.eql(u8, gap.id, other.id));
        }
    }

    try std.testing.expectEqual(@as(usize, 14), starter_landed_count);
    try std.testing.expectEqual(@as(usize, 0), ready_next_count);
    try std.testing.expect(saw_build_gate);
    try std.testing.expect(saw_make_target);
    try std.testing.expect(saw_starter);
    try std.testing.expect(saw_test_gate);
    try std.testing.expect(saw_slice_note);
    try std.testing.expect(saw_survey_note);
    try std.testing.expect(saw_copy_min_struct);
    try std.testing.expect(saw_add_rule);
    try std.testing.expect(saw_fd_followup);
    try std.testing.expect(saw_path_followup);
    try std.testing.expect(saw_path_beneath_handoff);
    try std.testing.expect(saw_net_port_handoff);
    try std.testing.expect(saw_ruleset_fd_creation_handoff);
    try std.testing.expect(saw_restrict_self_credential_handoff);
}

test "phase13 landlock syscalls descriptor stays anchored to syscalls.c" {
    const descriptor = syscalls.SyscallsHelperLab.descriptor();

    try std.testing.expectEqualStrings("landlock_syscalls_helper_lab", descriptor.name);
    try std.testing.expectEqualStrings("security/landlock/syscalls.c", descriptor.anchor);
    try std.testing.expect(descriptor.provides_abi_shape_reporting);
    try std.testing.expect(descriptor.provides_min_struct_copy_planning);
    try std.testing.expect(descriptor.provides_create_ruleset_query_planning);
    try std.testing.expect(descriptor.provides_restrict_self_flag_planning);
    try std.testing.expect(descriptor.provides_restrict_self_credential_handoff_planning);
    try std.testing.expect(descriptor.provides_add_rule_planning);
    try std.testing.expect(descriptor.provides_ruleset_fd_planning);
    try std.testing.expect(descriptor.provides_ruleset_fd_creation_planning);
    try std.testing.expect(descriptor.provides_path_fd_planning);
    try std.testing.expect(descriptor.provides_path_beneath_handoff_planning);
    try std.testing.expect(descriptor.provides_net_port_handoff_planning);
    try std.testing.expect(!descriptor.touches_live_fd_table);
    try std.testing.expect(!descriptor.touches_live_paths);
    try std.testing.expect(!descriptor.touches_live_credentials);
    try std.testing.expect(!descriptor.touches_live_domains);
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
