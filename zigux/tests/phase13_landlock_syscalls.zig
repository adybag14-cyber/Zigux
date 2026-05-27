const std = @import("std");

const syscalls = @import("syscalls");
const ruleset = @import("ruleset");

test "phase13 landlock syscalls descriptor keeps the current bounded helper scope explicit" {
    const descriptor = syscalls.SyscallsHelperLab.descriptor();

    try std.testing.expectEqualStrings("landlock_syscalls_helper_lab", descriptor.name);
    try std.testing.expectEqualStrings("security/landlock/syscalls.c", descriptor.anchor);
    try std.testing.expect(descriptor.provides_create_ruleset_planning);
    try std.testing.expect(descriptor.provides_abi_version_query_planning);
    try std.testing.expect(descriptor.provides_abi_errata_query_planning);
    try std.testing.expect(descriptor.provides_restrict_self_planning);
    try std.testing.expect(descriptor.provides_add_rule_planning);
    try std.testing.expect(descriptor.provides_ruleset_fd_lookup_planning);
    try std.testing.expect(descriptor.provides_ruleset_fd_install_planning);
    try std.testing.expect(descriptor.provides_ruleset_fd_stub_planning);
    try std.testing.expect(descriptor.provides_ruleset_release_planning);
    try std.testing.expect(!descriptor.touches_live_fd_installation);
    try std.testing.expect(!descriptor.touches_live_cred_replacement);
}

test "phase13 landlock syscalls create-handle path reuses the fd install planner" {
    const plan = try syscalls.SyscallsHelperLab.planLandlockCreateRuleset(.{
        .input = .{
            .attr = .{
                .handled_access_fs = 0x3,
                .handled_access_net = 0x4,
                .scoped = 0x1,
            },
        },
    });

    try std.testing.expect(plan.checks_initialization_gate);
    try std.testing.expect(plan.checks_attr_presence_before_copy_from_user);
    try std.testing.expect(plan.reuses_create_ruleset_validation);
    try std.testing.expect(plan.reuses_ruleset_fd_install_planning);
    try std.testing.expectEqual(syscalls.CreateRulesetMode.create_handle, plan.create_ruleset_plan.mode);
    try std.testing.expect(plan.ruleset_fd_install_plan != null);
    try std.testing.expectEqualStrings("security/landlock/ruleset.c", plan.create_ruleset_plan.ruleset_plan.?.anchor);
    try std.testing.expectEqual(@as(u32, 0x3), plan.create_ruleset_plan.ruleset_plan.?.access_masks.fs);
    try std.testing.expectEqual(@as(u32, 0x4), plan.create_ruleset_plan.ruleset_plan.?.access_masks.net);
    try std.testing.expectEqual(@as(u32, 0x1), plan.create_ruleset_plan.ruleset_plan.?.access_masks.scope);
    try std.testing.expect(plan.ruleset_fd_install_plan.?.performs_anon_inode_getfd);
    try std.testing.expect(plan.ruleset_fd_install_plan.?.returns_new_fd);
}

test "phase13 landlock syscalls errata query keeps the fd install path disabled" {
    const plan = try syscalls.SyscallsHelperLab.planLandlockCreateRuleset(.{
        .input = .{
            .attr_size = 0,
            .flags = syscalls.LANDLOCK_CREATE_RULESET_ERRATA,
        },
    });

    try std.testing.expectEqual(syscalls.CreateRulesetMode.abi_errata_query, plan.create_ruleset_plan.mode);
    try std.testing.expect(!plan.checks_attr_presence_before_copy_from_user);
    try std.testing.expect(!plan.reuses_ruleset_fd_install_planning);
    try std.testing.expectEqual(@as(?syscalls.RulesetFdInstallPlan, null), plan.ruleset_fd_install_plan);
    try std.testing.expect(!plan.create_ruleset_plan.performs_copy_from_user);
    try std.testing.expect(plan.create_ruleset_plan.ruleset_plan == null);
}

test "phase13 landlock syscalls restrict-self planner keeps logging and tsync flags explicit" {
    const plan = try syscalls.SyscallsHelperLab.planLandlockRestrictSelf(.{
        .flags = syscalls.LANDLOCK_RESTRICT_SELF_LOG_NEW_EXEC_ON | syscalls.LANDLOCK_RESTRICT_SELF_TSYNC,
    });

    try std.testing.expect(plan.checks_initialization_gate);
    try std.testing.expect(plan.validates_ruleset_presence);
    try std.testing.expect(plan.validates_no_new_privs);
    try std.testing.expect(plan.validates_flags);
    try std.testing.expect(plan.reuses_ruleset_fd_lookup_planning);
    try std.testing.expect(plan.logs_new_exec_transitions);
    try std.testing.expect(plan.requests_tsync);
    try std.testing.expect(plan.prepares_new_domain);
    try std.testing.expect(plan.merges_ruleset_into_domain);
    try std.testing.expect(!plan.updates_current_cred);
}

test "phase13 landlock syscalls add-rule planner reuses fd lookup and delegated tree helpers" {
    const existing = ruleset.RulePlan{
        .num_layers = 1,
        .layers = [_]ruleset.Layer{
            .{ .level = 1, .access = 0x2 },
        } ++ ([_]ruleset.Layer{.{ .level = 0, .access = 0 }} ** (ruleset.max_num_layers - 1)),
    };

    const plan = try syscalls.SyscallsHelperLab.planLandlockAddRule(.{
        .ruleset_fd_mode_bits = syscalls.FMODE_CAN_WRITE,
        .input = .{
            .key_type = .inode,
            .root_present = true,
            .search_key_data = 99,
            .walker_keys = &.{ 60, 99 },
            .current_num_rules = 4,
            .existing_rule = existing,
            .incoming_layers = &.{.{ .level = 3, .access = 0x8 }},
        },
    });

    try std.testing.expect(plan.checks_initialization_gate);
    try std.testing.expect(plan.checks_attr_presence_before_copy_from_user);
    try std.testing.expect(plan.requires_zero_flags);
    try std.testing.expect(plan.validates_ruleset_fd_write_mode);
    try std.testing.expectEqual(syscalls.FMODE_CAN_WRITE, plan.required_ruleset_fd_mode_bits);
    try std.testing.expect(plan.reuses_add_rule_validation);
    try std.testing.expect(plan.add_rule_plan.reuses_ruleset_fd_lookup_planning);
    try std.testing.expect(plan.add_rule_plan.delegates_rule_tree_search_planning);
    try std.testing.expect(plan.add_rule_plan.delegates_rule_insertion_planning);
    try std.testing.expect(plan.add_rule_plan.search_plan.matched_existing_rule);
    try std.testing.expectEqual(ruleset.InsertRuleBranchMode.replace_existing_rule, plan.add_rule_plan.branch_plan.mode);
    try std.testing.expectEqual(@as(usize, 2), plan.add_rule_plan.branch_plan.resulting_rule.num_layers);
    try std.testing.expectEqual(@as(u16, 3), plan.add_rule_plan.branch_plan.resulting_rule.layers[1].level);
}

test "phase13 landlock syscalls stub and release helpers stay planning-only" {
    const read_stub = try syscalls.SyscallsHelperLab.planRulesetFdStub(.{
        .operation = .read,
        .mode_bits = syscalls.FMODE_CAN_READ,
    });
    const write_stub = try syscalls.SyscallsHelperLab.planRulesetFdStub(.{
        .operation = .write,
        .mode_bits = syscalls.FMODE_CAN_WRITE,
    });
    const release_plan = try syscalls.SyscallsHelperLab.planFopRulesetRelease(.{});

    try std.testing.expect(read_stub.enables_read_mode);
    try std.testing.expect(!read_stub.enables_write_mode);
    try std.testing.expect(write_stub.enables_write_mode);
    try std.testing.expect(!write_stub.enables_read_mode);
    try std.testing.expect(read_stub.returns_einval);
    try std.testing.expect(write_stub.returns_einval);
    try std.testing.expect(!read_stub.mutates_ruleset_state);
    try std.testing.expect(!write_stub.mutates_ruleset_state);
    try std.testing.expect(release_plan.reads_file_private_data);
    try std.testing.expect(release_plan.invokes_landlock_put_ruleset);
    try std.testing.expect(release_plan.returns_zero);
}
