const std = @import("std");

pub const page_size_limit: usize = 4096;
pub const abi_version: u32 = 9;

pub const create_ruleset_version_flag: u32 = 1 << 0;
pub const create_ruleset_errata_flag: u32 = 1 << 1;

pub const restrict_self_log_same_exec_off: u32 = 1 << 0;
pub const restrict_self_log_new_exec_on: u32 = 1 << 1;

pub const restrict_self_log_subdomains_off: u32 = 1 << 2;
pub const restrict_self_tsync: u32 = 1 << 3;

pub const rule_type_path_beneath: u32 = 1;
pub const rule_type_net_port: u32 = 2;

pub const fmode_can_read: u32 = 1 << 0;
pub const fmode_can_write: u32 = 1 << 1;

pub const ModuleDescriptor = struct {
    name: []const u8,
    anchor: []const u8,
    provides_abi_shape_reporting: bool,
    provides_create_ruleset_query_planning: bool,
    provides_restrict_self_flag_planning: bool,
    provides_add_rule_planning: bool,
    provides_ruleset_fd_planning: bool,
    provides_path_fd_planning: bool,
    provides_path_beneath_handoff_planning: bool,
    provides_ruleset_release_planning: bool,
    provides_ruleset_fops_planning: bool,
    touches_live_fd_table: bool,
    touches_live_paths: bool,
    touches_live_credentials: bool,
    touches_live_domains: bool,
};

pub const RulesetAttr = struct {
    handled_access_fs: u64 = 0,
    handled_access_net: u64 = 0,
    scoped: u64 = 0,
};

pub const PathBeneathAttr = struct {
    allowed_access: u64 = 0,
    parent_fd: i32 = -1,
};

pub const NetPortAttr = struct {
    allowed_access: u64 = 0,
    port: u64 = 0,
};

pub const AbiShapeReport = struct {
    anchor: []const u8,
    ruleset_attr_size: usize,
    min_ruleset_attr_size: usize,
    path_beneath_attr_size: usize,
    net_port_attr_size: usize,
    page_size_limit: usize,
};

pub const CreateRulesetAction = enum {
    create,
    abi_version_query,
    errata_query,
};

pub const CreateRulesetRequest = struct {
    attr_present: bool = true,
    size: usize = @sizeOf(RulesetAttr),
    flags: u32 = 0,
    attr: RulesetAttr = .{},
    allowed_fs_mask: u64,
    allowed_net_mask: u64,
    allowed_scope_mask: u64,
    errata_value: u32 = 0,
};

pub const CreateRulesetPlan = struct {
    anchor: []const u8,
    action: CreateRulesetAction,
    returned_value: u32 = 0,
    handled_access_fs: u64 = 0,
    handled_access_net: u64 = 0,
    scoped: u64 = 0,
};

pub const RestrictSelfPlan = struct {
    anchor: []const u8,
    requires_ruleset: bool,
    log_same_exec: bool,
    log_new_exec: bool,
    log_subdomains: bool,
    propagates_to_siblings: bool,
};

pub const AddRuleAction = enum {
    path_beneath,
    net_port,
};

pub const AddRuleRequest = struct {
    flags: u32 = 0,
    rule_type: u32,
    handled_access_fs: u64 = 0,
    handled_access_net: u64 = 0,
    path_beneath_attr: PathBeneathAttr = .{},
    net_port_attr: NetPortAttr = .{},
};

pub const AddRulePlan = struct {
    anchor: []const u8,
    action: AddRuleAction,
    allowed_access: u64,
    requires_ruleset_write_access: bool,
    requires_path_lookup: bool,
    parent_fd: i32 = -1,
    port: ?u16 = null,
};

pub const AddRuleSyscallRequest = struct {
    initialized: bool = true,
    ruleset_fd: RulesetFdRequest,
    flags: u32 = 0,
    rule_type: u32,
    handled_access_fs: u64 = 0,
    handled_access_net: u64 = 0,
    path_beneath_attr: PathBeneathAttr = .{},
    net_port_attr: NetPortAttr = .{},
};

pub const AddRuleSyscallPlan = struct {
    anchor: []const u8,
    checks_initialization_gate: bool,
    requires_zero_flags: bool,
    acquires_ruleset_with_write_access: bool,
    reuses_add_rule_validation: bool,
    dispatched_rule: AddRulePlan,
};

pub const RulesetFdKind = enum {
    ruleset,
    other,
};

pub const RulesetFdRequest = struct {
    fd_present: bool = true,
    file_kind: RulesetFdKind = .ruleset,
    file_mode: u32 = 0,
    required_mode: u32,
    layer_count: usize = 1,
};

pub const RulesetFdPlan = struct {
    anchor: []const u8,
    required_mode: u32,
    validates_fd_type: bool,
    validates_mode: bool,
    acquires_ruleset_reference: bool,
    expected_layer_count: usize,
};

pub const PathFdRequest = struct {
    fd_present: bool = true,
    is_ruleset_fd: bool = false,
    mount_is_internal: bool = false,
    superblock_is_nouser: bool = false,
    inode_is_private: bool = false,
};

pub const PathFdPlan = struct {
    anchor: []const u8,
    rejects_ruleset_fd: bool,
    rejects_internal_mount: bool,
    rejects_nouser_superblock: bool,
    rejects_private_inode: bool,
    acquires_path_reference: bool,
};

pub const PathBeneathHandoffRequest = struct {
    handled_access_fs: u64 = 0,
    path_beneath_attr: PathBeneathAttr = .{},
    parent_path: PathFdRequest = .{},
};

pub const PathBeneathHandoffPlan = struct {
    anchor: []const u8,
    allowed_access: u64,
    parent_fd: i32,
    reuses_add_rule_validation: bool,
    reuses_path_fd_validation: bool,
    acquires_parent_path_reference: bool,
    releases_parent_path_reference: bool,
};

pub const RulesetReleaseRequest = struct {
    private_data_present: bool = true,
    private_data_is_ruleset: bool = true,
    private_data_ref_owned: bool = true,
};

pub const RulesetReleasePlan = struct {
    anchor: []const u8,
    requires_private_data_ruleset: bool,
    releases_retained_ruleset_reference: bool,
    returns_zero: bool,
};

pub const RulesetFopsOperation = enum {
    release,
    read,
    write,
};

pub const RulesetFopsPlan = struct {
    anchor: []const u8,
    operation: RulesetFopsOperation,
    requires_private_data_ruleset: bool = false,
    releases_retained_ruleset_reference: bool = false,
    enables_mode: u32 = 0,
    returns_zero: bool = false,
    returns_einval: bool = false,
};

pub const SyscallsHelperLab = struct {
    pub fn descriptor() ModuleDescriptor {
        return .{
            .name = "landlock_syscalls_helper_lab",
            .anchor = "security/landlock/syscalls.c",
            .provides_abi_shape_reporting = true,
            .provides_create_ruleset_query_planning = true,
            .provides_restrict_self_flag_planning = true,
            .provides_add_rule_planning = true,
            .provides_ruleset_fd_planning = true,
            .provides_path_fd_planning = true,
            .provides_path_beneath_handoff_planning = true,
            .provides_ruleset_release_planning = true,
            .provides_ruleset_fops_planning = true,
            .touches_live_fd_table = false,
            .touches_live_paths = false,
            .touches_live_credentials = false,
            .touches_live_domains = false,
        };
    }

    pub fn reportAbiShapes() AbiShapeReport {
        comptime {
            if (@sizeOf(RulesetAttr) != 24) {
                @compileError("landlock_ruleset_attr size drift");
            }
            if (@sizeOf(NetPortAttr) != 16) {
                @compileError("landlock_net_port_attr size drift");
            }
        }

        return .{
            .anchor = descriptor().anchor,
            .ruleset_attr_size = @sizeOf(RulesetAttr),
            .min_ruleset_attr_size = @offsetOf(RulesetAttr, "handled_access_fs") + @sizeOf(u64),
            .path_beneath_attr_size = 12,
            .net_port_attr_size = @sizeOf(NetPortAttr),
            .page_size_limit = page_size_limit,
        };
    }

    pub fn planCreateRuleset(request: CreateRulesetRequest) !CreateRulesetPlan {
        if (request.flags != 0) {
            if (request.attr_present or request.size != 0) {
                return error.InvalidQueryArguments;
            }

            if (request.flags == create_ruleset_version_flag) {
                return .{
                    .anchor = descriptor().anchor,
                    .action = .abi_version_query,
                    .returned_value = abi_version,
                };
            }

            if (request.flags == create_ruleset_errata_flag) {
                return .{
                    .anchor = descriptor().anchor,
                    .action = .errata_query,
                    .returned_value = request.errata_value,
                };
            }

            return error.UnsupportedFlags;
        }

        if (!request.attr_present) {
            return error.MissingAttr;
        }

        const abi_shapes = reportAbiShapes();
        if (request.size < abi_shapes.min_ruleset_attr_size) {
            return error.StructTooSmall;
        }
        if (request.size > abi_shapes.page_size_limit) {
            return error.StructTooLarge;
        }

        if ((request.attr.handled_access_fs | request.allowed_fs_mask) != request.allowed_fs_mask) {
            return error.InvalidFsAccessMask;
        }
        if ((request.attr.handled_access_net | request.allowed_net_mask) != request.allowed_net_mask) {
            return error.InvalidNetAccessMask;
        }
        if ((request.attr.scoped | request.allowed_scope_mask) != request.allowed_scope_mask) {
            return error.InvalidScopeMask;
        }
        if (request.attr.handled_access_fs == 0 and request.attr.handled_access_net == 0 and request.attr.scoped == 0) {
            return error.EmptyRuleset;
        }

        return .{
            .anchor = descriptor().anchor,
            .action = .create,
            .handled_access_fs = request.attr.handled_access_fs,
            .handled_access_net = request.attr.handled_access_net,
            .scoped = request.attr.scoped,
        };
    }

    pub fn planRestrictSelf(ruleset_fd: i32, flags: u32) !RestrictSelfPlan {
        const allowed_flags = restrict_self_log_same_exec_off |
            restrict_self_log_new_exec_on |
            restrict_self_log_subdomains_off |
            restrict_self_tsync;
        if ((flags | allowed_flags) != allowed_flags) {
            return error.InvalidFlags;
        }

        const mute_subdomains_only = ruleset_fd == -1 and
            (flags & ~restrict_self_tsync) == restrict_self_log_subdomains_off;
        if (ruleset_fd == -1 and !mute_subdomains_only) {
            return error.MissingRuleset;
        }

        return .{
            .anchor = descriptor().anchor,
            .requires_ruleset = !mute_subdomains_only,
            .log_same_exec = (flags & restrict_self_log_same_exec_off) == 0,
            .log_new_exec = (flags & restrict_self_log_new_exec_on) != 0,
            .log_subdomains = (flags & restrict_self_log_subdomains_off) == 0,
            .propagates_to_siblings = (flags & restrict_self_tsync) != 0,
        };
    }

    pub fn planAddRule(request: AddRuleRequest) !AddRulePlan {
        if (request.flags != 0) {
            return error.InvalidFlags;
        }

        switch (request.rule_type) {
            rule_type_path_beneath => {
                if (request.path_beneath_attr.allowed_access == 0) {
                    return error.EmptyAccess;
                }
                if ((request.path_beneath_attr.allowed_access | request.handled_access_fs) != request.handled_access_fs) {
                    return error.InvalidPathAccessMask;
                }

                return .{
                    .anchor = descriptor().anchor,
                    .action = .path_beneath,
                    .allowed_access = request.path_beneath_attr.allowed_access,
                    .requires_ruleset_write_access = true,
                    .requires_path_lookup = true,
                    .parent_fd = request.path_beneath_attr.parent_fd,
                };
            },
            rule_type_net_port => {
                if (request.net_port_attr.allowed_access == 0) {
                    return error.EmptyAccess;
                }
                if ((request.net_port_attr.allowed_access | request.handled_access_net) != request.handled_access_net) {
                    return error.InvalidNetAccessMask;
                }
                if (request.net_port_attr.port > std.math.maxInt(u16)) {
                    return error.PortTooLarge;
                }

                return .{
                    .anchor = descriptor().anchor,
                    .action = .net_port,
                    .allowed_access = request.net_port_attr.allowed_access,
                    .requires_ruleset_write_access = true,
                    .requires_path_lookup = false,
                    .port = @intCast(request.net_port_attr.port),
                };
            },
            else => return error.InvalidRuleType,
        }
    }

    pub fn planLandlockAddRule(request: AddRuleSyscallRequest) !AddRuleSyscallPlan {
        if (!request.initialized) {
            return error.BootDisabled;
        }
        if (request.flags != 0) {
            return error.InvalidFlags;
        }

        _ = try planGetRulesetFromFd(.{
            .fd_present = request.ruleset_fd.fd_present,
            .file_kind = request.ruleset_fd.file_kind,
            .file_mode = request.ruleset_fd.file_mode,
            .required_mode = fmode_can_write,
            .layer_count = request.ruleset_fd.layer_count,
        });

        const dispatched_rule = try planAddRule(.{
            .rule_type = request.rule_type,
            .handled_access_fs = request.handled_access_fs,
            .handled_access_net = request.handled_access_net,
            .path_beneath_attr = request.path_beneath_attr,
            .net_port_attr = request.net_port_attr,
        });

        return .{
            .anchor = descriptor().anchor,
            .checks_initialization_gate = true,
            .requires_zero_flags = true,
            .acquires_ruleset_with_write_access = true,
            .reuses_add_rule_validation = true,
            .dispatched_rule = dispatched_rule,
        };
    }

    pub fn planGetRulesetFromFd(request: RulesetFdRequest) !RulesetFdPlan {
        switch (request.required_mode) {
            fmode_can_read, fmode_can_write => {},
            else => return error.InvalidRequestedMode,
        }

        if (!request.fd_present) {
            return error.BadFileDescriptor;
        }
        if (request.file_kind != .ruleset) {
            return error.InvalidRulesetFdType;
        }
        if ((request.file_mode & request.required_mode) == 0) {
            return error.InsufficientMode;
        }
        if (request.layer_count != 1) {
            return error.InvalidLayerCount;
        }

        return .{
            .anchor = descriptor().anchor,
            .required_mode = request.required_mode,
            .validates_fd_type = true,
            .validates_mode = true,
            .acquires_ruleset_reference = true,
            .expected_layer_count = 1,
        };
    }

    pub fn planGetPathFromFd(request: PathFdRequest) !PathFdPlan {
        if (!request.fd_present) {
            return error.BadFileDescriptor;
        }
        if (request.is_ruleset_fd) {
            return error.InvalidPathFdType;
        }
        if (request.mount_is_internal) {
            return error.InternalMount;
        }
        if (request.superblock_is_nouser) {
            return error.NonUserVisiblePath;
        }
        if (request.inode_is_private) {
            return error.PrivateInode;
        }

        return .{
            .anchor = descriptor().anchor,
            .rejects_ruleset_fd = true,
            .rejects_internal_mount = true,
            .rejects_nouser_superblock = true,
            .rejects_private_inode = true,
            .acquires_path_reference = true,
        };
    }

    pub fn planAddRulePathBeneathHandoff(request: PathBeneathHandoffRequest) !PathBeneathHandoffPlan {
        const add_rule_plan = try planAddRule(.{
            .rule_type = rule_type_path_beneath,
            .handled_access_fs = request.handled_access_fs,
            .path_beneath_attr = request.path_beneath_attr,
        });
        const path_plan = try planGetPathFromFd(request.parent_path);

        return .{
            .anchor = descriptor().anchor,
            .allowed_access = add_rule_plan.allowed_access,
            .parent_fd = add_rule_plan.parent_fd,
            .reuses_add_rule_validation = true,
            .reuses_path_fd_validation = true,
            .acquires_parent_path_reference = path_plan.acquires_path_reference,
            .releases_parent_path_reference = true,
        };
    }

    pub fn planRulesetRelease(request: RulesetReleaseRequest) !RulesetReleasePlan {
        if (!request.private_data_present) {
            return error.MissingPrivateData;
        }
        if (!request.private_data_is_ruleset) {
            return error.InvalidPrivateData;
        }
        if (!request.private_data_ref_owned) {
            return error.UnownedRuleset;
        }

        return .{
            .anchor = descriptor().anchor,
            .requires_private_data_ruleset = true,
            .releases_retained_ruleset_reference = true,
            .returns_zero = true,
        };
    }

    pub fn planRulesetFops(operation: RulesetFopsOperation) RulesetFopsPlan {
        return switch (operation) {
            .release => .{
                .anchor = descriptor().anchor,
                .operation = .release,
                .requires_private_data_ruleset = true,
                .releases_retained_ruleset_reference = true,
                .returns_zero = true,
            },
            .read => .{
                .anchor = descriptor().anchor,
                .operation = .read,
                .enables_mode = fmode_can_read,
                .returns_einval = true,
            },
            .write => .{
                .anchor = descriptor().anchor,
                .operation = .write,
                .enables_mode = fmode_can_write,
                .returns_einval = true,
            },
        };
    }
};

test "landlock syscalls descriptor reports ruleset fops planning" {
    const descriptor = SyscallsHelperLab.descriptor();

    try std.testing.expect(descriptor.provides_ruleset_fops_planning);
}

test "landlock syscalls ruleset fops planner keeps release and dummy handlers explicit" {
    const release = SyscallsHelperLab.planRulesetFops(.release);
    try std.testing.expectEqualStrings("security/landlock/syscalls.c", release.anchor);
    try std.testing.expectEqual(RulesetFopsOperation.release, release.operation);
    try std.testing.expect(release.requires_private_data_ruleset);
    try std.testing.expect(release.releases_retained_ruleset_reference);
    try std.testing.expect(release.returns_zero);
    try std.testing.expectEqual(@as(u32, 0), release.enables_mode);
    try std.testing.expect(!release.returns_einval);

    const read = SyscallsHelperLab.planRulesetFops(.read);
    try std.testing.expectEqual(RulesetFopsOperation.read, read.operation);
    try std.testing.expectEqual(fmode_can_read, read.enables_mode);
    try std.testing.expect(read.returns_einval);
    try std.testing.expect(!read.requires_private_data_ruleset);
    try std.testing.expect(!read.releases_retained_ruleset_reference);
    try std.testing.expect(!read.returns_zero);

    const write = SyscallsHelperLab.planRulesetFops(.write);
    try std.testing.expectEqual(RulesetFopsOperation.write, write.operation);
    try std.testing.expectEqual(fmode_can_write, write.enables_mode);
    try std.testing.expect(write.returns_einval);
    try std.testing.expect(!write.requires_private_data_ruleset);
    try std.testing.expect(!write.releases_retained_ruleset_reference);
    try std.testing.expect(!write.returns_zero);
}
