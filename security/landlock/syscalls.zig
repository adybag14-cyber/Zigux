const std = @import("std");

pub const fmode_can_read: u32 = 1 << 0;
pub const fmode_can_write: u32 = 1 << 1;

pub const rule_type_path_beneath: u32 = 1;
pub const rule_type_net_port: u32 = 2;

pub const ModuleDescriptor = struct {
    name: []const u8,
    anchor: []const u8,
    provides_restrict_self_planning: bool,
    provides_add_rule_planning: bool,
    validates_ruleset_fd: bool,
    validates_ruleset_write_access: bool,
    validates_restrict_self_flags: bool,
    validates_add_rule_flags: bool,
    validates_credential_gate: bool,
    touches_live_credentials: bool,
    touches_live_rulesets: bool,
};

pub const CredentialGate = enum {
    no_new_privs,
    cap_sys_admin_override,
};

pub const AddRuleAction = enum {
    path_beneath,
    net_port,
};

pub const RestrictSelfInput = struct {
    ruleset_fd: i32,
    flags: u32 = 0,
    no_new_privs_set: bool = false,
    caller_has_cap_sys_admin: bool = false,
};

pub const RestrictSelfPlan = struct {
    anchor: []const u8,
    ruleset_fd: i32,
    credential_gate: CredentialGate,
    handled_flags: u32,
};

pub const AddRuleInput = struct {
    ruleset_fd: i32,
    ruleset_mode: u32 = 0,
    flags: u32 = 0,
    rule_type: u32,
    handled_access_fs: u64 = 0,
    handled_access_net: u64 = 0,
    path_allowed_access: u64 = 0,
    parent_fd: i32 = -1,
    net_allowed_access: u64 = 0,
    port: ?u16 = null,
};

pub const AddRulePlan = struct {
    anchor: []const u8,
    ruleset_fd: i32,
    action: AddRuleAction,
    requires_ruleset_write_access: bool,
    requires_path_lookup: bool,
    handled_access: u64,
    requested_access: u64,
    parent_fd: i32 = -1,
    port: ?u16 = null,
};

pub const SyscallsHelperLab = struct {
    pub fn descriptor() ModuleDescriptor {
        return .{
            .name = "landlock_syscalls_helper_lab",
            .anchor = "security/landlock/syscalls.c",
            .provides_restrict_self_planning = true,
            .provides_add_rule_planning = true,
            .validates_ruleset_fd = true,
            .validates_ruleset_write_access = true,
            .validates_restrict_self_flags = true,
            .validates_add_rule_flags = true,
            .validates_credential_gate = true,
            .touches_live_credentials = false,
            .touches_live_rulesets = false,
        };
    }

    pub fn planRestrictSelf(input: RestrictSelfInput) !RestrictSelfPlan {
        if (input.ruleset_fd < 0) {
            return error.InvalidRulesetFd;
        }
        if (input.flags != 0) {
            return error.UnsupportedFlags;
        }

        const credential_gate: CredentialGate = if (input.no_new_privs_set)
            .no_new_privs
        else if (input.caller_has_cap_sys_admin)
            .cap_sys_admin_override
        else
            return error.MissingNoNewPrivs;

        return .{
            .anchor = descriptor().anchor,
            .ruleset_fd = input.ruleset_fd,
            .credential_gate = credential_gate,
            .handled_flags = input.flags,
        };
    }

    pub fn planAddRule(input: AddRuleInput) !AddRulePlan {
        if (input.ruleset_fd < 0) {
            return error.InvalidRulesetFd;
        }
        if (input.flags != 0) {
            return error.UnsupportedFlags;
        }
        if (input.ruleset_mode & fmode_can_write == 0) {
            return error.InsufficientRulesetMode;
        }

        switch (input.rule_type) {
            rule_type_path_beneath => {
                if (input.path_allowed_access == 0 or input.handled_access_fs == 0) {
                    return error.EmptyAccess;
                }
                if (input.path_allowed_access & ~input.handled_access_fs != 0) {
                    return error.AccessNotHandled;
                }
                if (input.parent_fd < 0) {
                    return error.InvalidParentFd;
                }

                return .{
                    .anchor = descriptor().anchor,
                    .ruleset_fd = input.ruleset_fd,
                    .action = .path_beneath,
                    .requires_ruleset_write_access = true,
                    .requires_path_lookup = true,
                    .handled_access = input.handled_access_fs,
                    .requested_access = input.path_allowed_access,
                    .parent_fd = input.parent_fd,
                };
            },
            rule_type_net_port => {
                if (input.net_allowed_access == 0 or input.handled_access_net == 0) {
                    return error.EmptyAccess;
                }
                if (input.net_allowed_access & ~input.handled_access_net != 0) {
                    return error.AccessNotHandled;
                }
                const port = input.port orelse return error.MissingPort;

                return .{
                    .anchor = descriptor().anchor,
                    .ruleset_fd = input.ruleset_fd,
                    .action = .net_port,
                    .requires_ruleset_write_access = true,
                    .requires_path_lookup = false,
                    .handled_access = input.handled_access_net,
                    .requested_access = input.net_allowed_access,
                    .port = port,
                };
            },
            else => return error.InvalidRuleType,
        }
    }
};

test "landlock syscalls descriptor stays scoped to pure planning helpers" {
    const descriptor = SyscallsHelperLab.descriptor();

    try std.testing.expectEqualStrings("landlock_syscalls_helper_lab", descriptor.name);
    try std.testing.expectEqualStrings("security/landlock/syscalls.c", descriptor.anchor);
    try std.testing.expect(descriptor.provides_restrict_self_planning);
    try std.testing.expect(descriptor.provides_add_rule_planning);
    try std.testing.expect(descriptor.validates_ruleset_fd);
    try std.testing.expect(descriptor.validates_ruleset_write_access);
    try std.testing.expect(descriptor.validates_restrict_self_flags);
    try std.testing.expect(descriptor.validates_add_rule_flags);
    try std.testing.expect(descriptor.validates_credential_gate);
    try std.testing.expect(!descriptor.touches_live_credentials);
    try std.testing.expect(!descriptor.touches_live_rulesets);
}

test "landlock restrict-self planning accepts no-new-privs callers" {
    const plan = try SyscallsHelperLab.planRestrictSelf(.{
        .ruleset_fd = 7,
        .no_new_privs_set = true,
    });

    try std.testing.expectEqualStrings(SyscallsHelperLab.descriptor().anchor, plan.anchor);
    try std.testing.expectEqual(@as(i32, 7), plan.ruleset_fd);
    try std.testing.expectEqual(CredentialGate.no_new_privs, plan.credential_gate);
    try std.testing.expectEqual(@as(u32, 0), plan.handled_flags);
}

test "landlock restrict-self planning accepts cap-sys-admin override" {
    const plan = try SyscallsHelperLab.planRestrictSelf(.{
        .ruleset_fd = 11,
        .caller_has_cap_sys_admin = true,
    });

    try std.testing.expectEqual(@as(i32, 11), plan.ruleset_fd);
    try std.testing.expectEqual(CredentialGate.cap_sys_admin_override, plan.credential_gate);
}

test "landlock restrict-self planning rejects negative ruleset fds" {
    try std.testing.expectError(error.InvalidRulesetFd, SyscallsHelperLab.planRestrictSelf(.{
        .ruleset_fd = -1,
        .no_new_privs_set = true,
    }));
}

test "landlock restrict-self planning rejects unsupported flags" {
    try std.testing.expectError(error.UnsupportedFlags, SyscallsHelperLab.planRestrictSelf(.{
        .ruleset_fd = 3,
        .flags = 0x4,
        .no_new_privs_set = true,
    }));
}

test "landlock restrict-self planning rejects callers without credential gate" {
    try std.testing.expectError(error.MissingNoNewPrivs, SyscallsHelperLab.planRestrictSelf(.{
        .ruleset_fd = 5,
    }));
}

test "landlock add-rule planning keeps write-fd and path handoff explicit" {
    const plan = try SyscallsHelperLab.planAddRule(.{
        .ruleset_fd = 9,
        .ruleset_mode = fmode_can_write,
        .rule_type = rule_type_path_beneath,
        .handled_access_fs = 0x7,
        .path_allowed_access = 0x3,
        .parent_fd = 42,
    });

    try std.testing.expectEqualStrings(SyscallsHelperLab.descriptor().anchor, plan.anchor);
    try std.testing.expectEqual(@as(i32, 9), plan.ruleset_fd);
    try std.testing.expectEqual(AddRuleAction.path_beneath, plan.action);
    try std.testing.expect(plan.requires_ruleset_write_access);
    try std.testing.expect(plan.requires_path_lookup);
    try std.testing.expectEqual(@as(u64, 0x7), plan.handled_access);
    try std.testing.expectEqual(@as(u64, 0x3), plan.requested_access);
    try std.testing.expectEqual(@as(i32, 42), plan.parent_fd);
    try std.testing.expectEqual(@as(?u16, null), plan.port);
}

test "landlock add-rule planning keeps net-port dispatch explicit" {
    const plan = try SyscallsHelperLab.planAddRule(.{
        .ruleset_fd = 12,
        .ruleset_mode = fmode_can_write,
        .rule_type = rule_type_net_port,
        .handled_access_net = 0x7,
        .net_allowed_access = 0x1,
        .port = 443,
    });

    try std.testing.expectEqual(AddRuleAction.net_port, plan.action);
    try std.testing.expect(plan.requires_ruleset_write_access);
    try std.testing.expect(!plan.requires_path_lookup);
    try std.testing.expectEqual(@as(u64, 0x7), plan.handled_access);
    try std.testing.expectEqual(@as(u64, 0x1), plan.requested_access);
    try std.testing.expectEqual(@as(?u16, 443), plan.port);
}

test "landlock add-rule planning rejects flags non-writable rulesets and invalid dispatch" {
    try std.testing.expectError(error.UnsupportedFlags, SyscallsHelperLab.planAddRule(.{
        .ruleset_fd = 9,
        .ruleset_mode = fmode_can_write,
        .flags = 1,
        .rule_type = rule_type_path_beneath,
        .handled_access_fs = 0x1,
        .path_allowed_access = 0x1,
        .parent_fd = 4,
    }));

    try std.testing.expectError(error.InsufficientRulesetMode, SyscallsHelperLab.planAddRule(.{
        .ruleset_fd = 9,
        .ruleset_mode = fmode_can_read,
        .rule_type = rule_type_path_beneath,
        .handled_access_fs = 0x1,
        .path_allowed_access = 0x1,
        .parent_fd = 4,
    }));

    try std.testing.expectError(error.AccessNotHandled, SyscallsHelperLab.planAddRule(.{
        .ruleset_fd = 9,
        .ruleset_mode = fmode_can_write,
        .rule_type = rule_type_path_beneath,
        .handled_access_fs = 0x1,
        .path_allowed_access = 0x3,
        .parent_fd = 4,
    }));

    try std.testing.expectError(error.InvalidRuleType, SyscallsHelperLab.planAddRule(.{
        .ruleset_fd = 9,
        .ruleset_mode = fmode_can_write,
        .rule_type = 99,
    }));
}
