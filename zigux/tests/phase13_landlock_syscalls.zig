const std = @import("std");
const syscalls = @import("syscalls");
const manifest_text = @embedFile("phase13_landlock_syscalls_manifest.json");

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

test "phase13 landlock syscalls descriptor keeps the bounded helper scope explicit" {
    const descriptor = syscalls.SyscallsHelperLab.descriptor();

    try std.testing.expectEqualStrings("landlock_syscalls_helper_lab", descriptor.name);
    try std.testing.expectEqualStrings("security/landlock/syscalls.c", descriptor.anchor);
    try std.testing.expect(descriptor.provides_create_ruleset_planning);
    try std.testing.expect(descriptor.provides_restrict_self_planning);
    try std.testing.expect(descriptor.provides_add_rule_planning);
    try std.testing.expect(descriptor.provides_ruleset_release_planning);
    try std.testing.expect(descriptor.provides_ruleset_fops_planning);
    try std.testing.expect(descriptor.validates_create_ruleset_flags);
    try std.testing.expect(descriptor.validates_create_ruleset_access_masks);
    try std.testing.expect(descriptor.validates_create_ruleset_scope);
    try std.testing.expect(descriptor.validates_ruleset_fd);
    try std.testing.expect(descriptor.validates_ruleset_write_access);
    try std.testing.expect(descriptor.validates_restrict_self_flags);
    try std.testing.expect(descriptor.validates_restrict_self_logging);
    try std.testing.expect(descriptor.validates_add_rule_flags);
    try std.testing.expect(descriptor.validates_credential_gate);
    try std.testing.expect(!descriptor.touches_live_credentials);
    try std.testing.expect(!descriptor.touches_live_rulesets);
}

test "phase13 landlock syscalls keeps create-ruleset planning explicit before fd installation" {
    const version_plan = try syscalls.SyscallsHelperLab.planCreateRuleset(.{
        .attr_present = false,
        .size = 0,
        .flags = syscalls.landlock_create_ruleset_version,
    });
    try std.testing.expectEqual(syscalls.CreateRulesetMode.abi_version_query, version_plan.mode);
    try std.testing.expect(version_plan.requires_empty_attr);
    try std.testing.expect(!version_plan.reaches_anon_inode_fd_installation);

    const create_plan = try syscalls.SyscallsHelperLab.planCreateRuleset(.{
        .handled_access_fs = 0x3,
        .handled_access_net = 0x10,
        .scoped = 0x4,
        .supported_access_fs_mask = 0x7,
        .supported_access_net_mask = 0x30,
        .supported_scope_mask = 0x7,
    });
    try std.testing.expectEqual(syscalls.CreateRulesetMode.create, create_plan.mode);
    try std.testing.expectEqual(syscalls.create_ruleset_attr_full_size, create_plan.copied_size);
    try std.testing.expectEqual(@as(u64, 0x3), create_plan.handled_access_fs);
    try std.testing.expectEqual(@as(u64, 0x10), create_plan.handled_access_net);
    try std.testing.expectEqual(@as(u64, 0x4), create_plan.scoped);
    try std.testing.expect(create_plan.validates_attr_copy_min);
    try std.testing.expect(create_plan.validates_access_fs);
    try std.testing.expect(create_plan.validates_access_net);
    try std.testing.expect(create_plan.validates_scope);
    try std.testing.expect(!create_plan.reaches_anon_inode_fd_installation);
}

test "phase13 landlock syscalls keeps restrict-self logging and detached updates explicit" {
    const plan = try syscalls.SyscallsHelperLab.planRestrictSelf(.{
        .ruleset_fd = -1,
        .flags = syscalls.landlock_restrict_self_log_subdomains_off,
        .caller_has_cap_sys_admin = true,
    });

    try std.testing.expectEqual(syscalls.CredentialGate.cap_sys_admin_override, plan.credential_gate);
    try std.testing.expectEqual(@as(i32, -1), plan.ruleset_fd);
    try std.testing.expectEqual(syscalls.landlock_restrict_self_log_subdomains_off, plan.handled_flags);
    try std.testing.expect(!plan.requires_readable_ruleset_fd);
    try std.testing.expect(!plan.creates_domain);
    try std.testing.expect(plan.logging.log_same_exec);
    try std.testing.expect(!plan.logging.log_new_exec);
    try std.testing.expect(!plan.logging.log_subdomains);
}

test "phase13 landlock syscalls keeps add-rule dispatch explicit for both helper branches" {
    const path_plan = try syscalls.SyscallsHelperLab.planLandlockAddRule(.{
        .ruleset_fd = 21,
        .ruleset_mode = syscalls.fmode_can_write,
        .rule_type = syscalls.rule_type_path_beneath,
        .handled_access_fs = 0x7,
        .path_allowed_access = 0x3,
        .parent_fd = 42,
    });
    try std.testing.expectEqual(syscalls.AddRuleAction.path_beneath, path_plan.dispatched_rule.action);
    try std.testing.expect(path_plan.dispatched_rule.requires_path_lookup);
    try std.testing.expectEqual(@as(i32, 42), path_plan.dispatched_rule.parent_fd);

    const net_plan = try syscalls.SyscallsHelperLab.planLandlockAddRule(.{
        .ruleset_fd = 22,
        .ruleset_mode = syscalls.fmode_can_write,
        .rule_type = syscalls.rule_type_net_port,
        .handled_access_net = 0x30,
        .net_allowed_access = 0x10,
        .port = 443,
    });
    try std.testing.expectEqual(syscalls.AddRuleAction.net_port, net_plan.dispatched_rule.action);
    try std.testing.expect(!net_plan.dispatched_rule.requires_path_lookup);
    try std.testing.expectEqual(@as(?u16, 443), net_plan.dispatched_rule.port);
}

test "phase13 landlock syscalls keeps add-rule wrapper rejection explicit" {
    try std.testing.expectError(error.InvalidRulesetFd, syscalls.SyscallsHelperLab.planLandlockAddRule(.{
        .ruleset_fd = -1,
        .ruleset_mode = syscalls.fmode_can_write,
        .rule_type = syscalls.rule_type_path_beneath,
        .handled_access_fs = 0x1,
        .path_allowed_access = 0x1,
        .parent_fd = 3,
    }));

    try std.testing.expectError(error.UnsupportedFlags, syscalls.SyscallsHelperLab.planLandlockAddRule(.{
        .ruleset_fd = 7,
        .ruleset_mode = syscalls.fmode_can_write,
        .flags = 1,
        .rule_type = syscalls.rule_type_path_beneath,
        .handled_access_fs = 0x1,
        .path_allowed_access = 0x1,
        .parent_fd = 3,
    }));

    try std.testing.expectError(error.InsufficientRulesetMode, syscalls.SyscallsHelperLab.planLandlockAddRule(.{
        .ruleset_fd = 7,
        .ruleset_mode = syscalls.fmode_can_read,
        .rule_type = syscalls.rule_type_net_port,
        .handled_access_net = 0x10,
        .net_allowed_access = 0x10,
        .port = 443,
    }));
}

test "phase13 landlock syscalls keeps release-side helper discipline explicit" {
    try std.testing.expectError(error.MissingFile, syscalls.SyscallsHelperLab.planFopRulesetRelease(.{
        .file_present = false,
    }));
    try std.testing.expectError(error.MissingRuleset, syscalls.SyscallsHelperLab.planFopRulesetRelease(.{
        .ruleset_present = false,
    }));

    const plan = try syscalls.SyscallsHelperLab.planRulesetFops(.{});
    try std.testing.expect(plan.release.reads_file_private_data);
    try std.testing.expect(plan.release.invokes_landlock_put_ruleset);
    try std.testing.expect(plan.release.returns_zero);
    try std.testing.expect(plan.enables_fmode_can_read);
    try std.testing.expect(plan.enables_fmode_can_write);
    try std.testing.expect(plan.read_returns_einval);
    try std.testing.expect(plan.write_returns_einval);
}

test "phase13 landlock syscalls manifest records the bounded syscall helper packet" {
    try expectContains(manifest_text, "\"lane_key\": \"P13-L17\"");
    try expectContains(manifest_text, "\"surveyed_commit\": \"master-readback-2026-05-13\"");
    try expectContains(manifest_text, "\"anchor\": \"security/landlock/syscalls.c\"");
    try expectContains(manifest_text, "\"preexisting_phase13_build_present\": false");
    try expectContains(manifest_text, "\"preexisting_syscalls_zig_present\": true");
    try expectContains(manifest_text, "\"preexisting_phase13_landlock_syscalls_test_present\": true");
    try expectContains(manifest_text, "\"preexisting_phase13_landlock_syscalls_reviewability_present\": true");
    try expectContains(manifest_text, "\"id\": \"phase13-build-gate\"");
    try expectContains(manifest_text, "\"id\": \"phase13-landlock-syscalls-helper-starter\"");
    try expectContains(manifest_text, "\"id\": \"phase13-landlock-syscalls-direct-test-gate\"");
    try expectContains(manifest_text, "\"id\": \"phase13-landlock-syscalls-reviewability-gate\"");
    try expectContains(manifest_text, "\"id\": \"phase13-landlock-live-fd-installation\"");
    try expectContains(manifest_text, "\"id\": \"phase13-landlock-live-credential-state\"");
    try expectContains(manifest_text, "\"id\": \"phase13-landlock-live-ruleset-state\"");
    try expectContains(manifest_text, "\"status\": \"starter_landed\"");
    try expectContains(manifest_text, "\"status\": \"blocked_on_missing_shared_build_surface\"");
    try expectContains(manifest_text, "\"status\": \"blocked_on_live_fd_installation\"");
    try expectContains(manifest_text, "\"status\": \"blocked_on_live_credential_state\"");
    try expectContains(manifest_text, "\"status\": \"blocked_on_live_ruleset_state\"");
    try expectContains(manifest_text, "create-ruleset planning");
    try expectContains(manifest_text, "anon_inode_getfd()");
    try expectContains(manifest_text, "ruleset_fops");
}
