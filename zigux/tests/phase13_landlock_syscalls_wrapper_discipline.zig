const std = @import("std");
const syscalls = @import("landlock_syscalls");

test "phase13 landlock add-rule wrapper composition keeps path-beneath handoff explicit" {
    const plan = try syscalls.SyscallsHelperLab.planLandlockAddRule(.{
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

    try std.testing.expectEqualStrings("security/landlock/syscalls.c", plan.anchor);
    try std.testing.expect(plan.checks_initialization_gate);
    try std.testing.expect(plan.requires_zero_flags);
    try std.testing.expect(plan.acquires_ruleset_with_write_access);
    try std.testing.expect(plan.reuses_add_rule_validation);
    try std.testing.expectEqual(syscalls.AddRuleAction.path_beneath, plan.dispatched_rule.action);
    try std.testing.expectEqual(@as(u64, 0x3), plan.dispatched_rule.allowed_access);
    try std.testing.expect(plan.dispatched_rule.requires_ruleset_write_access);
    try std.testing.expect(plan.dispatched_rule.requires_path_lookup);
    try std.testing.expectEqual(@as(i32, 42), plan.dispatched_rule.parent_fd);
    try std.testing.expectEqual(@as(?u16, null), plan.dispatched_rule.port);

    const path_plan = try syscalls.SyscallsHelperLab.planAddRulePathBeneath(.{
        .handled_access_fs = 0x7,
        .path_beneath_attr = .{
            .allowed_access = 0x3,
            .parent_fd = 42,
        },
        .path_fd = .{},
    });
    try std.testing.expectEqualStrings("security/landlock/syscalls.c", path_plan.anchor);
    try std.testing.expectEqual(@as(u64, 0x3), path_plan.allowed_access);
    try std.testing.expectEqual(@as(i32, 42), path_plan.parent_fd);
    try std.testing.expect(path_plan.path_lookup.rejects_ruleset_fd);
    try std.testing.expect(path_plan.path_lookup.rejects_internal_mount);
    try std.testing.expect(path_plan.path_lookup.rejects_nouser_superblock);
    try std.testing.expect(path_plan.path_lookup.rejects_private_inode);
    try std.testing.expect(path_plan.path_lookup.acquires_path_reference);
    try std.testing.expect(path_plan.imports_path_beneath_rule);
    try std.testing.expect(path_plan.releases_path_after_import);
}

test "phase13 landlock add-rule wrapper composition keeps net-port import explicit" {
    const plan = try syscalls.SyscallsHelperLab.planLandlockAddRule(.{
        .ruleset_fd = .{
            .file_mode = syscalls.fmode_can_write,
            .required_mode = syscalls.fmode_can_write,
        },
        .rule_type = syscalls.rule_type_net_port,
        .handled_access_net = 0x9,
        .net_port_attr = .{
            .allowed_access = 0x1,
            .port = 443,
        },
    });

    try std.testing.expect(plan.checks_initialization_gate);
    try std.testing.expect(plan.requires_zero_flags);
    try std.testing.expect(plan.acquires_ruleset_with_write_access);
    try std.testing.expect(plan.reuses_add_rule_validation);
    try std.testing.expectEqual(syscalls.AddRuleAction.net_port, plan.dispatched_rule.action);
    try std.testing.expectEqual(@as(u64, 0x1), plan.dispatched_rule.allowed_access);
    try std.testing.expect(!plan.dispatched_rule.requires_path_lookup);
    try std.testing.expectEqual(@as(?u16, 443), plan.dispatched_rule.port);

    const import_plan = try syscalls.SyscallsHelperLab.planAddRuleNetPort(.{
        .handled_access_net = 0x9,
        .net_port_attr = .{
            .allowed_access = 0x1,
            .port = 443,
        },
    });
    try std.testing.expectEqualStrings("security/landlock/syscalls.c", import_plan.anchor);
    try std.testing.expectEqual(@as(u64, 0x1), import_plan.allowed_access);
    try std.testing.expectEqual(@as(u16, 443), import_plan.port);
    try std.testing.expect(import_plan.copies_net_port_attr);
    try std.testing.expect(import_plan.reuses_add_rule_validation);
    try std.testing.expect(import_plan.invokes_append_net_rule);
}

test "phase13 landlock add-rule wrapper rejects disabled, flaggy, and read-only calls" {
    try std.testing.expectError(error.BootDisabled, syscalls.SyscallsHelperLab.planLandlockAddRule(.{
        .initialized = false,
        .ruleset_fd = .{
            .file_mode = syscalls.fmode_can_write,
            .required_mode = syscalls.fmode_can_write,
        },
        .rule_type = syscalls.rule_type_net_port,
        .handled_access_net = 0x1,
        .net_port_attr = .{
            .allowed_access = 0x1,
            .port = 53,
        },
    }));

    try std.testing.expectError(error.InvalidFlags, syscalls.SyscallsHelperLab.planLandlockAddRule(.{
        .ruleset_fd = .{
            .file_mode = syscalls.fmode_can_write,
            .required_mode = syscalls.fmode_can_write,
        },
        .flags = 1,
        .rule_type = syscalls.rule_type_net_port,
        .handled_access_net = 0x1,
        .net_port_attr = .{
            .allowed_access = 0x1,
            .port = 53,
        },
    }));

    try std.testing.expectError(error.InsufficientMode, syscalls.SyscallsHelperLab.planLandlockAddRule(.{
        .ruleset_fd = .{
            .file_mode = syscalls.fmode_can_read,
            .required_mode = syscalls.fmode_can_write,
        },
        .rule_type = syscalls.rule_type_path_beneath,
        .handled_access_fs = 0x3,
        .path_beneath_attr = .{
            .allowed_access = 0x1,
            .parent_fd = 7,
        },
    }));
}
