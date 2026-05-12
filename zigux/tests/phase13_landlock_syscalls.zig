const std = @import("std");
const landlock_syscalls = @import("landlock_syscalls");
const manifest_text = @embedFile("phase13_landlock_syscalls_manifest.json");

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

test "phase13 landlock syscalls descriptor stays scoped to planning-only helpers" {
    const descriptor = landlock_syscalls.SyscallsHelperLab.descriptor();

    try std.testing.expectEqualStrings("landlock_syscalls_helper_lab", descriptor.name);
    try std.testing.expectEqualStrings("security/landlock/syscalls.c", descriptor.anchor);
    try std.testing.expect(descriptor.provides_restrict_self_planning);
    try std.testing.expect(descriptor.provides_add_rule_planning);
    try std.testing.expect(descriptor.provides_ruleset_release_planning);
    try std.testing.expect(descriptor.provides_ruleset_fops_planning);
    try std.testing.expect(descriptor.validates_ruleset_fd);
    try std.testing.expect(descriptor.validates_ruleset_write_access);
    try std.testing.expect(descriptor.validates_restrict_self_flags);
    try std.testing.expect(descriptor.validates_restrict_self_logging);
    try std.testing.expect(descriptor.validates_add_rule_flags);
    try std.testing.expect(descriptor.validates_credential_gate);
    try std.testing.expect(!descriptor.touches_live_credentials);
    try std.testing.expect(!descriptor.touches_live_rulesets);
}

test "phase13 landlock restrict-self replay keeps detached logging updates explicit" {
    const plan = try landlock_syscalls.SyscallsHelperLab.planRestrictSelf(.{
        .ruleset_fd = -1,
        .flags = landlock_syscalls.landlock_restrict_self_log_subdomains_off,
        .caller_has_cap_sys_admin = true,
    });

    try std.testing.expectEqualStrings("security/landlock/syscalls.c", plan.anchor);
    try std.testing.expectEqual(landlock_syscalls.CredentialGate.cap_sys_admin_override, plan.credential_gate);
    try std.testing.expectEqual(@as(i32, -1), plan.ruleset_fd);
    try std.testing.expectEqual(landlock_syscalls.landlock_restrict_self_log_subdomains_off, plan.handled_flags);
    try std.testing.expect(!plan.requires_readable_ruleset_fd);
    try std.testing.expect(!plan.creates_domain);
    try std.testing.expect(plan.logging.log_same_exec);
    try std.testing.expect(!plan.logging.log_new_exec);
    try std.testing.expect(!plan.logging.log_subdomains);
}

test "phase13 landlock add-rule replay keeps syscall wrapper dispatch explicit" {
    const path_plan = try landlock_syscalls.SyscallsHelperLab.planLandlockAddRule(.{
        .ruleset_fd = 21,
        .ruleset_mode = landlock_syscalls.fmode_can_write,
        .rule_type = landlock_syscalls.rule_type_path_beneath,
        .handled_access_fs = 0x7,
        .path_allowed_access = 0x3,
        .parent_fd = 42,
    });

    try std.testing.expectEqualStrings("security/landlock/syscalls.c", path_plan.anchor);
    try std.testing.expectEqual(@as(i32, 21), path_plan.ruleset_fd);
    try std.testing.expect(path_plan.validates_ruleset_fd);
    try std.testing.expect(path_plan.validates_zero_flags);
    try std.testing.expect(path_plan.requires_ruleset_write_access);
    try std.testing.expect(path_plan.reuses_add_rule_planning);
    try std.testing.expectEqual(landlock_syscalls.AddRuleAction.path_beneath, path_plan.dispatched_rule.action);
    try std.testing.expect(path_plan.dispatched_rule.requires_path_lookup);
    try std.testing.expectEqual(@as(i32, 42), path_plan.dispatched_rule.parent_fd);

    const net_plan = try landlock_syscalls.SyscallsHelperLab.planLandlockAddRule(.{
        .ruleset_fd = 22,
        .ruleset_mode = landlock_syscalls.fmode_can_write,
        .rule_type = landlock_syscalls.rule_type_net_port,
        .handled_access_net = 0x30,
        .net_allowed_access = 0x10,
        .port = 443,
    });

    try std.testing.expectEqual(landlock_syscalls.AddRuleAction.net_port, net_plan.dispatched_rule.action);
    try std.testing.expect(!net_plan.dispatched_rule.requires_path_lookup);
    try std.testing.expectEqual(@as(?u16, 443), net_plan.dispatched_rule.port);
}

test "phase13 landlock ruleset_fops replay keeps the bounded release contract explicit" {
    const plan = try landlock_syscalls.SyscallsHelperLab.planRulesetFops(.{});

    try std.testing.expectEqualStrings("security/landlock/syscalls.c", plan.anchor);
    try std.testing.expect(plan.release.reads_file_private_data);
    try std.testing.expect(plan.release.invokes_landlock_put_ruleset);
    try std.testing.expect(plan.release.returns_zero);
    try std.testing.expect(plan.enables_fmode_can_read);
    try std.testing.expect(plan.enables_fmode_can_write);
    try std.testing.expect(plan.read_returns_einval);
    try std.testing.expect(plan.write_returns_einval);
}

test "phase13 landlock syscalls manifest records the current helper packet" {
    try expectContains(manifest_text, "\"lane_key\": \"P13-L18\"");
    try expectContains(manifest_text, "\"surveyed_commit\": \"master-readback-2026-05-12\"");
    try expectContains(manifest_text, "\"preexisting_phase13_build_present\": false");
    try expectContains(manifest_text, "\"preexisting_phase13_make_target_present\": true");
    try expectContains(manifest_text, "\"preexisting_syscalls_zig_present\": true");
    try expectContains(manifest_text, "\"preexisting_phase13_landlock_syscalls_test_present\": true");
    try expectContains(manifest_text, "\"preexisting_phase13_landlock_syscalls_manifest_present\": true");
    try expectContains(manifest_text, "\"preexisting_phase13_landlock_syscalls_slice_present\": false");
    try expectContains(manifest_text, "\"preexisting_phase13_landlock_syscalls_reviewability_present\": false");
    try expectContains(manifest_text, "\"preexisting_phase13_landlock_syscalls_survey_present\": true");
    try expectContains(manifest_text, "\"preexisting_phase13_landlock_syscalls_governance_present\": true");
    try expectContains(manifest_text, "\"id\": \"phase13-build-gate\"");
    try expectContains(manifest_text, "\"id\": \"phase13-landlock-syscalls-test-gate\"");
    try expectContains(manifest_text, "\"id\": \"phase13-landlock-syscalls-manifest\"");
    try expectContains(manifest_text, "\"id\": \"phase13-landlock-syscalls-reviewability-gate\"");
    try expectContains(manifest_text, "\"id\": \"phase13-landlock-live-credential-mutation\"");
    try expectContains(manifest_text, "\"id\": \"phase13-landlock-live-ruleset-ownership\"");
    try expectContains(manifest_text, "\"id\": \"phase13-landlock-live-syscall-enforcement\"");
    try expectContains(manifest_text, "\"status\": \"blocked_on_missing_shared_build_surface\"");
    try expectContains(manifest_text, "\"status\": \"starter_landed\"");
    try expectContains(manifest_text, "\"status\": \"blocked_on_reviewability_packet\"");
    try expectContains(manifest_text, "\"status\": \"blocked_on_live_credential_state\"");
    try expectContains(manifest_text, "planning-only helper packet");
    try expectContains(manifest_text, "direct replay is now present");
    try expectContains(manifest_text, "paired manifest is now present");
    try expectContains(manifest_text, "dedicated reviewability shard");
    try expectContains(manifest_text, "Live syscall enforcement remains blocked");
}
