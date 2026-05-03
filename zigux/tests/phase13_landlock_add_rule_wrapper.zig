const std = @import("std");
const syscalls = @import("landlock_syscalls");

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
