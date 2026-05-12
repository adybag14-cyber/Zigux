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
    provides_ruleset_release_planning: bool,
    provides_ruleset_fops_planning: bool,
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

pub const RulesetReleaseRequest = struct {
    file_present: bool = true,
    ruleset_present: bool = true,
};

pub const RulesetReleasePlan = struct {
    anchor: []const u8,
    reads_file_private_data: bool,
    invokes_landlock_put_ruleset: bool,
    returns_zero: bool,
};

pub const RulesetFopsPlan = struct {
    anchor: []const u8,
    release: RulesetReleasePlan,
    enables_fmode_can_read: bool,
    enables_fmode_can_write: bool,
    read_returns_einval: bool,
    write_returns_einval: bool,
};

pub const SyscallsHelperLab = struct {
    pub fn descriptor() ModuleDescriptor {
        return .{
            .name = "landlock_syscalls_helper_lab",
            .anchor = "security/landlock/syscalls.c",
            .provides_restrict_self_planning = true,
            .provides_add_rule_planning = true,
            .provides_ruleset_release_planning = true,
            .provides_ruleset_fops_planning = true,
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

    pub fn planFopRulesetRelease(request: RulesetReleaseRequest) !RulesetReleasePlan {
        if (!request.file_present) {
            return error.MissingFile;
        }
        if (!request.ruleset_present) {
            return error.MissingRuleset;
        }

        return .{
            .anchor = descriptor().anchor,
            .reads_file_private_data = true,
            .invokes_landlock_put_ruleset = true,
            .returns_zero = true,
        };
    }

    pub fn planRulesetFops(request: RulesetReleaseRequest) !RulesetFopsPlan {
        return .{
            .anchor = descriptor().anchor,
            .release = try planFopRulesetRelease(request),
            .enables_fmode_can_read = true,
            .enables_fmode_can_write = true,
            .read_returns_einval = true,
            .write_returns_einval = true,
        };
    }
};

test "landlock syscalls descriptor stays scoped to pure planning helpers" {
    const descriptor = SyscallsHelperLab.descriptor();

    try std.testing.expectEqualStrings("landlock_syscalls_helper_lab", descriptor.name);
    try std.testing.expectEqualStrings("security/landlock/syscalls.c", descriptor.anchor);
    try std.testing.expect(descriptor.provides_restrict_self_planning);
    try std.testing.expect(descriptor.provides_add_rule_planning);
    try std.testing.expect(descriptor.provides_ruleset_release_planning);
    try std.testing.expect(descriptor.provides_ruleset_fops_planning);
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

test "landlock restrict-self planning accepts CAP_SYS_ADMIN override callers" {
    const plan = try SyscallsHelperLab.planRestrictSelf(.{
        .ruleset_fd = 11,
        .caller_has_cap_sys_admin = true,
    });

    try std.testing.expectEqualStrings(SyscallsHelperLab.descriptor().anchor, plan.anchor);
    try std.testing.expectEqual(@as(i32, 11), plan.ruleset_fd);
    try std.testing.expectEqual(CredentialGate.cap_sys_admin_override, plan.credential_gate);
    try std.testing.expectEqual(@as(u32, 0), plan.handled_flags);
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

    try std.testing.expectEqual(AddRuleAction.path_beneath, plan.action);
    try std.testing.expect(plan.requires_ruleset_write_access);
    try std.testing.expect(plan.requires_path_lookup);
    try std.testing.expectEqual(@as(u64, 0x7), plan.handled_access);
    try std.testing.expectEqual(@as(u64, 0x3), plan.requested_access);
    try std.testing.expectEqual(@as(i32, 42), plan.parent_fd);
}

test "landlock add-rule planning keeps net-port handoff explicit" {
    const plan = try SyscallsHelperLab.planAddRule(.{
        .ruleset_fd = 13,
        .ruleset_mode = fmode_can_write,
        .rule_type = rule_type_net_port,
        .handled_access_net = 0x30,
        .net_allowed_access = 0x10,
        .port = 443,
    });

    try std.testing.expectEqual(AddRuleAction.net_port, plan.action);
    try std.testing.expect(plan.requires_ruleset_write_access);
    try std.testing.expect(!plan.requires_path_lookup);
    try std.testing.expectEqual(@as(u64, 0x30), plan.handled_access);
    try std.testing.expectEqual(@as(u64, 0x10), plan.requested_access);
    try std.testing.expectEqual(@as(?u16, 443), plan.port);
}

test "landlock ruleset release planning rejects missing file or ruleset state" {
    try std.testing.expectError(error.MissingFile, SyscallsHelperLab.planFopRulesetRelease(.{
        .file_present = false,
    }));
    try std.testing.expectError(error.MissingRuleset, SyscallsHelperLab.planFopRulesetRelease(.{
        .ruleset_present = false,
    }));
}

test "landlock ruleset_fops planning keeps release and invalid read write stubs explicit" {
    const plan = try SyscallsHelperLab.planRulesetFops(.{});

    try std.testing.expect(plan.release.reads_file_private_data);
    try std.testing.expect(plan.release.invokes_landlock_put_ruleset);
    try std.testing.expect(plan.release.returns_zero);
    try std.testing.expect(plan.enables_fmode_can_read);
    try std.testing.expect(plan.enables_fmode_can_write);
    try std.testing.expect(plan.read_returns_einval);
    try std.testing.expect(plan.write_returns_einval);
}
