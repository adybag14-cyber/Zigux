const std = @import("std");

pub const fmode_can_read: u32 = 1 << 0;
pub const fmode_can_write: u32 = 1 << 1;

pub const rule_type_path_beneath: u32 = 1;
pub const rule_type_net_port: u32 = 2;

pub const landlock_create_ruleset_version: u32 = 1 << 0;
pub const landlock_create_ruleset_errata: u32 = 1 << 1;
pub const landlock_mask_create_ruleset: u32 =
    landlock_create_ruleset_version |
    landlock_create_ruleset_errata;

pub const landlock_restrict_self_log_same_exec_off: u32 = 1 << 0;
pub const landlock_restrict_self_log_new_exec_on: u32 = 1 << 1;
pub const landlock_restrict_self_log_subdomains_off: u32 = 1 << 2;
pub const landlock_mask_restrict_self: u32 =
    landlock_restrict_self_log_same_exec_off |
    landlock_restrict_self_log_new_exec_on |
    landlock_restrict_self_log_subdomains_off;

pub const create_ruleset_attr_min_size: usize = 8;
pub const create_ruleset_attr_full_size: usize = 24;
pub const create_ruleset_attr_max_size: usize = 4096;

pub const ModuleDescriptor = struct {
    name: []const u8,
    anchor: []const u8,
    provides_create_ruleset_planning: bool,
    provides_restrict_self_planning: bool,
    provides_add_rule_planning: bool,
    provides_ruleset_release_planning: bool,
    provides_ruleset_fops_planning: bool,
    validates_create_ruleset_flags: bool,
    validates_create_ruleset_access_masks: bool,
    validates_create_ruleset_scope: bool,
    validates_ruleset_fd: bool,
    validates_ruleset_write_access: bool,
    validates_restrict_self_flags: bool,
    validates_restrict_self_logging: bool,
    validates_add_rule_flags: bool,
    validates_credential_gate: bool,
    touches_live_credentials: bool,
    touches_live_rulesets: bool,
};

pub const CreateRulesetMode = enum {
    create,
    abi_version_query,
    errata_query,
};

pub const CredentialGate = enum {
    no_new_privs,
    cap_sys_admin_override,
};

pub const AddRuleAction = enum {
    path_beneath,
    net_port,
};

pub const CreateRulesetInput = struct {
    attr_present: bool = true,
    size: usize = create_ruleset_attr_full_size,
    flags: u32 = 0,
    handled_access_fs: u64 = 0,
    handled_access_net: u64 = 0,
    scoped: u64 = 0,
    supported_access_fs_mask: u64 = std.math.maxInt(u64),
    supported_access_net_mask: u64 = std.math.maxInt(u64),
    supported_scope_mask: u64 = std.math.maxInt(u64),
};

pub const CreateRulesetPlan = struct {
    anchor: []const u8,
    mode: CreateRulesetMode,
    copied_size: usize,
    handled_access_fs: u64,
    handled_access_net: u64,
    scoped: u64,
    requires_empty_attr: bool,
    validates_attr_copy_min: bool,
    validates_access_fs: bool,
    validates_access_net: bool,
    validates_scope: bool,
    reaches_anon_inode_fd_installation: bool,
};

pub const RestrictSelfInput = struct {
    ruleset_fd: i32,
    flags: u32 = 0,
    no_new_privs_set: bool = false,
    caller_has_cap_sys_admin: bool = false,
};

pub const RestrictSelfLogging = struct {
    log_same_exec: bool,
    log_new_exec: bool,
    log_subdomains: bool,
};

pub const RestrictSelfPlan = struct {
    anchor: []const u8,
    ruleset_fd: i32,
    credential_gate: CredentialGate,
    handled_flags: u32,
    requires_readable_ruleset_fd: bool,
    creates_domain: bool,
    logging: RestrictSelfLogging,
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

pub const AddRuleSyscallPlan = struct {
    anchor: []const u8,
    ruleset_fd: i32,
    validates_ruleset_fd: bool,
    validates_zero_flags: bool,
    requires_ruleset_write_access: bool,
    reuses_add_rule_planning: bool,
    dispatched_rule: AddRulePlan,
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
            .provides_create_ruleset_planning = true,
            .provides_restrict_self_planning = true,
            .provides_add_rule_planning = true,
            .provides_ruleset_release_planning = true,
            .provides_ruleset_fops_planning = true,
            .validates_create_ruleset_flags = true,
            .validates_create_ruleset_access_masks = true,
            .validates_create_ruleset_scope = true,
            .validates_ruleset_fd = true,
            .validates_ruleset_write_access = true,
            .validates_restrict_self_flags = true,
            .validates_restrict_self_logging = true,
            .validates_add_rule_flags = true,
            .validates_credential_gate = true,
            .touches_live_credentials = false,
            .touches_live_rulesets = false,
        };
    }

    pub fn planCreateRuleset(input: CreateRulesetInput) !CreateRulesetPlan {
        if (input.flags != 0) {
            if (input.attr_present or input.size != 0) {
                return error.InvalidCreateRulesetQuery;
            }

            const mode: CreateRulesetMode = switch (input.flags) {
                landlock_create_ruleset_version => .abi_version_query,
                landlock_create_ruleset_errata => .errata_query,
                else => return error.UnsupportedFlags,
            };

            return .{
                .anchor = descriptor().anchor,
                .mode = mode,
                .copied_size = 0,
                .handled_access_fs = 0,
                .handled_access_net = 0,
                .scoped = 0,
                .requires_empty_attr = true,
                .validates_attr_copy_min = false,
                .validates_access_fs = false,
                .validates_access_net = false,
                .validates_scope = false,
                .reaches_anon_inode_fd_installation = false,
            };
        }

        if (!input.attr_present) {
            return error.MissingAttr;
        }
        if (input.size < create_ruleset_attr_min_size) {
            return error.AttrSizeTooSmall;
        }
        if (input.size > create_ruleset_attr_max_size) {
            return error.AttrSizeTooLarge;
        }
        if (input.handled_access_fs & ~input.supported_access_fs_mask != 0) {
            return error.AccessFsNotSupported;
        }
        if (input.handled_access_net & ~input.supported_access_net_mask != 0) {
            return error.AccessNetNotSupported;
        }
        if (input.scoped & ~input.supported_scope_mask != 0) {
            return error.ScopeNotSupported;
        }

        return .{
            .anchor = descriptor().anchor,
            .mode = .create,
            .copied_size = input.size,
            .handled_access_fs = input.handled_access_fs,
            .handled_access_net = input.handled_access_net,
            .scoped = input.scoped,
            .requires_empty_attr = false,
            .validates_attr_copy_min = true,
            .validates_access_fs = true,
            .validates_access_net = true,
            .validates_scope = true,
            .reaches_anon_inode_fd_installation = false,
        };
    }

    pub fn planRestrictSelf(input: RestrictSelfInput) !RestrictSelfPlan {
        if ((input.flags | landlock_mask_restrict_self) != landlock_mask_restrict_self) {
            return error.UnsupportedFlags;
        }

        const credential_gate: CredentialGate = if (input.no_new_privs_set)
            .no_new_privs
        else if (input.caller_has_cap_sys_admin)
            .cap_sys_admin_override
        else
            return error.MissingNoNewPrivs;

        const logging: RestrictSelfLogging = .{
            .log_same_exec = input.flags & landlock_restrict_self_log_same_exec_off == 0,
            .log_new_exec = input.flags & landlock_restrict_self_log_new_exec_on != 0,
            .log_subdomains = input.flags & landlock_restrict_self_log_subdomains_off == 0,
        };
        const detached_subdomain_log_update =
            input.ruleset_fd == -1 and input.flags == landlock_restrict_self_log_subdomains_off;

        if (!detached_subdomain_log_update and input.ruleset_fd < 0) {
            return error.InvalidRulesetFd;
        }

        return .{
            .anchor = descriptor().anchor,
            .ruleset_fd = input.ruleset_fd,
            .credential_gate = credential_gate,
            .handled_flags = input.flags,
            .requires_readable_ruleset_fd = !detached_subdomain_log_update,
            .creates_domain = !detached_subdomain_log_update,
            .logging = logging,
        };
    }

    fn validateAddRuleSyscallContext(input: AddRuleInput) !void {
        if (input.ruleset_fd < 0) {
            return error.InvalidRulesetFd;
        }
        if (input.flags != 0) {
            return error.UnsupportedFlags;
        }
        if (input.ruleset_mode & fmode_can_write == 0) {
            return error.InsufficientRulesetMode;
        }
    }

    fn planAddRuleDispatch(input: AddRuleInput) !AddRulePlan {
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

    pub fn planAddRule(input: AddRuleInput) !AddRulePlan {
        try validateAddRuleSyscallContext(input);
        return try planAddRuleDispatch(input);
    }

    pub fn planLandlockAddRule(input: AddRuleInput) !AddRuleSyscallPlan {
        try validateAddRuleSyscallContext(input);

        return .{
            .anchor = descriptor().anchor,
            .ruleset_fd = input.ruleset_fd,
            .validates_ruleset_fd = true,
            .validates_zero_flags = true,
            .requires_ruleset_write_access = true,
            .reuses_add_rule_planning = true,
            .dispatched_rule = try planAddRuleDispatch(input),
        };
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

test "landlock create-ruleset planning keeps query-only flags explicit" {
    const version_plan = try SyscallsHelperLab.planCreateRuleset(.{
        .attr_present = false,
        .size = 0,
        .flags = landlock_create_ruleset_version,
    });

    try std.testing.expectEqual(CreateRulesetMode.abi_version_query, version_plan.mode);
    try std.testing.expect(version_plan.requires_empty_attr);
    try std.testing.expectEqual(@as(usize, 0), version_plan.copied_size);
    try std.testing.expect(!version_plan.validates_attr_copy_min);
    try std.testing.expect(!version_plan.reaches_anon_inode_fd_installation);

    const errata_plan = try SyscallsHelperLab.planCreateRuleset(.{
        .attr_present = false,
        .size = 0,
        .flags = landlock_create_ruleset_errata,
    });

    try std.testing.expectEqual(CreateRulesetMode.errata_query, errata_plan.mode);
    try std.testing.expect(errata_plan.requires_empty_attr);
    try std.testing.expect(!errata_plan.reaches_anon_inode_fd_installation);
}

test "landlock create-ruleset planning keeps handled access and scope validation explicit" {
    const plan = try SyscallsHelperLab.planCreateRuleset(.{
        .handled_access_fs = 0x3,
        .handled_access_net = 0x10,
        .scoped = 0x4,
        .supported_access_fs_mask = 0x7,
        .supported_access_net_mask = 0x30,
        .supported_scope_mask = 0x7,
    });

    try std.testing.expectEqualStrings(SyscallsHelperLab.descriptor().anchor, plan.anchor);
    try std.testing.expectEqual(CreateRulesetMode.create, plan.mode);
    try std.testing.expectEqual(create_ruleset_attr_full_size, plan.copied_size);
    try std.testing.expectEqual(@as(u64, 0x3), plan.handled_access_fs);
    try std.testing.expectEqual(@as(u64, 0x10), plan.handled_access_net);
    try std.testing.expectEqual(@as(u64, 0x4), plan.scoped);
    try std.testing.expect(!plan.requires_empty_attr);
    try std.testing.expect(plan.validates_attr_copy_min);
    try std.testing.expect(plan.validates_access_fs);
    try std.testing.expect(plan.validates_access_net);
    try std.testing.expect(plan.validates_scope);
    try std.testing.expect(!plan.reaches_anon_inode_fd_installation);
}

test "landlock create-ruleset planning rejects invalid query and attr shapes" {
    try std.testing.expectError(error.InvalidCreateRulesetQuery, SyscallsHelperLab.planCreateRuleset(.{
        .flags = landlock_create_ruleset_version,
    }));
    try std.testing.expectError(error.MissingAttr, SyscallsHelperLab.planCreateRuleset(.{
        .attr_present = false,
        .size = create_ruleset_attr_full_size,
    }));
    try std.testing.expectError(error.AttrSizeTooSmall, SyscallsHelperLab.planCreateRuleset(.{
        .size = create_ruleset_attr_min_size - 1,
    }));
    try std.testing.expectError(error.AttrSizeTooLarge, SyscallsHelperLab.planCreateRuleset(.{
        .size = create_ruleset_attr_max_size + 1,
    }));
    try std.testing.expectError(error.AccessFsNotSupported, SyscallsHelperLab.planCreateRuleset(.{
        .handled_access_fs = 0x8,
        .supported_access_fs_mask = 0x7,
    }));
    try std.testing.expectError(error.AccessNetNotSupported, SyscallsHelperLab.planCreateRuleset(.{
        .handled_access_net = 0x40,
        .supported_access_net_mask = 0x30,
    }));
    try std.testing.expectError(error.ScopeNotSupported, SyscallsHelperLab.planCreateRuleset(.{
        .scoped = 0x8,
        .supported_scope_mask = 0x7,
    }));
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
    try std.testing.expect(plan.requires_readable_ruleset_fd);
    try std.testing.expect(plan.creates_domain);
    try std.testing.expect(plan.logging.log_same_exec);
    try std.testing.expect(!plan.logging.log_new_exec);
    try std.testing.expect(plan.logging.log_subdomains);
}

test "landlock restrict-self planning models detached subdomain log updates" {
    const plan = try SyscallsHelperLab.planRestrictSelf(.{
        .ruleset_fd = -1,
        .flags = landlock_restrict_self_log_subdomains_off,
        .caller_has_cap_sys_admin = true,
    });

    try std.testing.expectEqual(CredentialGate.cap_sys_admin_override, plan.credential_gate);
    try std.testing.expectEqual(@as(i32, -1), plan.ruleset_fd);
    try std.testing.expectEqual(landlock_restrict_self_log_subdomains_off, plan.handled_flags);
    try std.testing.expect(!plan.requires_readable_ruleset_fd);
    try std.testing.expect(!plan.creates_domain);
    try std.testing.expect(plan.logging.log_same_exec);
    try std.testing.expect(!plan.logging.log_new_exec);
    try std.testing.expect(!plan.logging.log_subdomains);
}

test "landlock restrict-self planning keeps logging flag translation explicit" {
    const plan = try SyscallsHelperLab.planRestrictSelf(.{
        .ruleset_fd = 5,
        .flags = landlock_restrict_self_log_same_exec_off | landlock_restrict_self_log_new_exec_on,
        .no_new_privs_set = true,
    });

    try std.testing.expect(plan.requires_readable_ruleset_fd);
    try std.testing.expect(plan.creates_domain);
    try std.testing.expect(!plan.logging.log_same_exec);
    try std.testing.expect(plan.logging.log_new_exec);
    try std.testing.expect(plan.logging.log_subdomains);
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
    try std.testing.expect(plan.requires_readable_ruleset_fd);
    try std.testing.expect(plan.creates_domain);
    try std.testing.expect(plan.logging.log_same_exec);
    try std.testing.expect(!plan.logging.log_new_exec);
    try std.testing.expect(plan.logging.log_subdomains);
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

test "landlock add-rule syscall wrapper planning keeps top-level dispatch explicit" {
    const path_plan = try SyscallsHelperLab.planLandlockAddRule(.{
        .ruleset_fd = 21,
        .ruleset_mode = fmode_can_write,
        .rule_type = rule_type_path_beneath,
        .handled_access_fs = 0x7,
        .path_allowed_access = 0x3,
        .parent_fd = 42,
    });

    try std.testing.expectEqualStrings(SyscallsHelperLab.descriptor().anchor, path_plan.anchor);
    try std.testing.expectEqual(@as(i32, 21), path_plan.ruleset_fd);
    try std.testing.expect(path_plan.validates_ruleset_fd);
    try std.testing.expect(path_plan.validates_zero_flags);
    try std.testing.expect(path_plan.requires_ruleset_write_access);
    try std.testing.expect(path_plan.reuses_add_rule_planning);
    try std.testing.expectEqual(AddRuleAction.path_beneath, path_plan.dispatched_rule.action);
    try std.testing.expect(path_plan.dispatched_rule.requires_ruleset_write_access);
    try std.testing.expect(path_plan.dispatched_rule.requires_path_lookup);
    try std.testing.expectEqual(@as(i32, 42), path_plan.dispatched_rule.parent_fd);

    const net_plan = try SyscallsHelperLab.planLandlockAddRule(.{
        .ruleset_fd = 22,
        .ruleset_mode = fmode_can_write,
        .rule_type = rule_type_net_port,
        .handled_access_net = 0x30,
        .net_allowed_access = 0x10,
        .port = 443,
    });

    try std.testing.expectEqual(AddRuleAction.net_port, net_plan.dispatched_rule.action);
    try std.testing.expect(!net_plan.dispatched_rule.requires_path_lookup);
    try std.testing.expectEqual(@as(?u16, 443), net_plan.dispatched_rule.port);
}

test "landlock add-rule syscall wrapper planning rejects invalid wrapper state" {
    try std.testing.expectError(error.InvalidRulesetFd, SyscallsHelperLab.planLandlockAddRule(.{
        .ruleset_fd = -1,
        .ruleset_mode = fmode_can_write,
        .rule_type = rule_type_path_beneath,
        .handled_access_fs = 0x1,
        .path_allowed_access = 0x1,
        .parent_fd = 3,
    }));

    try std.testing.expectError(error.UnsupportedFlags, SyscallsHelperLab.planLandlockAddRule(.{
        .ruleset_fd = 7,
        .ruleset_mode = fmode_can_write,
        .flags = 1,
        .rule_type = rule_type_path_beneath,
        .handled_access_fs = 0x1,
        .path_allowed_access = 0x1,
        .parent_fd = 3,
    }));

    try std.testing.expectError(error.InsufficientRulesetMode, SyscallsHelperLab.planLandlockAddRule(.{
        .ruleset_fd = 7,
        .ruleset_mode = fmode_can_read,
        .rule_type = rule_type_net_port,
        .handled_access_net = 0x10,
        .net_allowed_access = 0x10,
        .port = 443,
    }));
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
