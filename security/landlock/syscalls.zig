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

pub const ruleset_fd_display_name = "[landlock-ruleset]";
pub const ruleset_fd_open_rdwr: u32 = 0x2;
pub const ruleset_fd_open_cloexec: u32 = 0x80000;

pub const ModuleDescriptor = struct {
    name: []const u8,
    anchor: []const u8,
    provides_abi_shape_reporting: bool,
    provides_create_ruleset_query_planning: bool,
    provides_create_ruleset_syscall_planning: bool,
    provides_restrict_self_flag_planning: bool,
    provides_restrict_self_syscall_planning: bool,
    provides_add_rule_planning: bool,
    provides_ruleset_fd_planning: bool,
    provides_path_fd_planning: bool,
    provides_path_beneath_handoff_planning: bool,
    provides_ruleset_release_planning: bool,
    provides_ruleset_fd_install_planning: bool,
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

pub const CreateRulesetSyscallRequest = struct {
    initialized: bool = true,
    create_ruleset: CreateRulesetRequest,
    install_errno: ?i32 = null,
};

pub const RestrictSelfPlan = struct {
    anchor: []const u8,
    requires_ruleset: bool,
    log_same_exec: bool,
    log_new_exec: bool,
    log_subdomains: bool,
    propagates_to_siblings: bool,
};

pub const RestrictSelfSyscallRequest = struct {
    initialized: bool = true,
    ruleset_fd: RulesetFdRequest = .{
        .required_mode = fmode_can_read,
    },
    flags: u32 = 0,
};

pub const RestrictSelfSyscallPlan = struct {
    anchor: []const u8,
    checks_initialization_gate: bool,
    allows_log_subdomains_toggle_without_ruleset: bool,
    acquires_ruleset_with_read_access: bool,
    reuses_flag_planning: bool,
    dispatched_restriction: RestrictSelfPlan,
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
    path_beneath_parent_path: PathFdRequest = .{},
    net_port_attr: NetPortAttr = .{},
};

pub const AddRuleSyscallPlan = struct {
    anchor: []const u8,
    checks_initialization_gate: bool,
    requires_zero_flags: bool,
    acquires_ruleset_with_write_access: bool,
    reuses_add_rule_validation: bool,
    reuses_path_beneath_handoff: bool,
    acquires_parent_path_reference: bool,
    releases_parent_path_reference: bool,
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

pub const RulesetFdInstallRequest = struct {
    ruleset_created: bool = true,
    install_errno: ?i32 = null,
};

pub const RulesetFdInstallPlan = struct {
    anchor: []const u8,
    display_name: []const u8,
    uses_ruleset_fops: bool,
    exposes_read_write_fd: bool,
    cloexec: bool,
    returns_installed_fd: bool,
    releases_ruleset_on_failure: bool,
    failure_errno: ?i32 = null,
};

pub const CreateRulesetSyscallPlan = struct {
    anchor: []const u8,
    checks_initialization_gate: bool,
    reuses_create_ruleset_validation: bool,
    attempts_ruleset_fd_install: bool,
    releases_ruleset_on_install_failure: bool,
    dispatched_create: CreateRulesetPlan,
    installed_fd: ?RulesetFdInstallPlan = null,
};

pub const SyscallsHelperLab = struct {
    pub fn descriptor() ModuleDescriptor {
        return .{
            .name = "landlock_syscalls_helper_lab",
            .anchor = "security/landlock/syscalls.c",
            .provides_abi_shape_reporting = true,
            .provides_create_ruleset_query_planning = true,
            .provides_create_ruleset_syscall_planning = true,
            .provides_restrict_self_flag_planning = true,
            .provides_restrict_self_syscall_planning = true,
            .provides_add_rule_planning = true,
            .provides_ruleset_fd_planning = true,
            .provides_path_fd_planning = true,
            .provides_path_beneath_handoff_planning = true,
            .provides_ruleset_release_planning = true,
            .provides_ruleset_fd_install_planning = true,
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

    pub fn planLandlockRestrictSelf(request: RestrictSelfSyscallRequest) !RestrictSelfSyscallPlan {
        if (!request.initialized) {
            return error.BootDisabled;
        }

        const no_ruleset = !request.ruleset_fd.fd_present;
        const mute_subdomains_only = no_ruleset and
            (request.flags & ~restrict_self_tsync) == restrict_self_log_subdomains_off;

        if (!mute_subdomains_only) {
            _ = try planGetRulesetFromFd(.{
                .fd_present = request.ruleset_fd.fd_present,
                .file_kind = request.ruleset_fd.file_kind,
                .file_mode = request.ruleset_fd.file_mode,
                .required_mode = fmode_can_read,
                .layer_count = request.ruleset_fd.layer_count,
            });
        }

        const dispatched_restriction = try planRestrictSelf(
            if (no_ruleset) -1 else 0,
            request.flags,
        );

        return .{
            .anchor = descriptor().anchor,
            .checks_initialization_gate = true,
            .allows_log_subdomains_toggle_without_ruleset = true,
            .acquires_ruleset_with_read_access = !mute_subdomains_only,
            .reuses_flag_planning = true,
            .dispatched_restriction = dispatched_restriction,
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

        const path_beneath_handoff = switch (dispatched_rule.action) {
            .path_beneath => try planAddRulePathBeneathHandoff(.{
                .handled_access_fs = request.handled_access_fs,
                .path_beneath_attr = request.path_beneath_attr,
                .parent_path = request.path_beneath_parent_path,
            }),
            .net_port => null,
        };

        return .{
            .anchor = descriptor().anchor,
            .checks_initialization_gate = true,
            .requires_zero_flags = true,
            .acquires_ruleset_with_write_access = true,
            .reuses_add_rule_validation = true,
            .reuses_path_beneath_handoff = path_beneath_handoff != null,
            .acquires_parent_path_reference = if (path_beneath_handoff) |handoff| handoff.acquires_parent_path_reference else false,
            .releases_parent_path_reference = if (path_beneath_handoff) |handoff| handoff.releases_parent_path_reference else false,
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

    pub fn planInstallRulesetFd(request: RulesetFdInstallRequest) !RulesetFdInstallPlan {
        if (!request.ruleset_created) {
            return error.MissingRuleset;
        }
        if (request.install_errno) |install_errno| {
            if (install_errno >= 0) {
                return error.InvalidInstallErrno;
            }
        }

        return .{
            .anchor = descriptor().anchor,
            .display_name = ruleset_fd_display_name,
            .uses_ruleset_fops = true,
            .exposes_read_write_fd = true,
            .cloexec = true,
            .returns_installed_fd = request.install_errno == null,
            .releases_ruleset_on_failure = request.install_errno != null,
            .failure_errno = request.install_errno,
        };
    }

    pub fn planLandlockCreateRuleset(request: CreateRulesetSyscallRequest) !CreateRulesetSyscallPlan {
        if (!request.initialized) {
            return error.BootDisabled;
        }

        const dispatched_create = try planCreateRuleset(request.create_ruleset);
        const installed_fd = switch (dispatched_create.action) {
            .create => try planInstallRulesetFd(.{
                .install_errno = request.install_errno,
            }),
            .abi_version_query, .errata_query => null,
        };

        return .{
            .anchor = descriptor().anchor,
            .checks_initialization_gate = true,
            .reuses_create_ruleset_validation = true,
            .attempts_ruleset_fd_install = installed_fd != null,
            .releases_ruleset_on_install_failure = if (installed_fd) |fd_plan| fd_plan.releases_ruleset_on_failure else false,
            .dispatched_create = dispatched_create,
            .installed_fd = installed_fd,
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

test "landlock create-ruleset syscall planning distinguishes query and install paths" {
    const descriptor = SyscallsHelperLab.descriptor();
    try std.testing.expect(descriptor.provides_create_ruleset_query_planning);
    try std.testing.expect(descriptor.provides_create_ruleset_syscall_planning);

    const query_plan = try SyscallsHelperLab.planLandlockCreateRuleset(.{
        .create_ruleset = .{
            .attr_present = false,
            .size = 0,
            .flags = create_ruleset_version_flag,
            .allowed_fs_mask = 0,
            .allowed_net_mask = 0,
            .allowed_scope_mask = 0,
        },
    });
    try std.testing.expect(query_plan.checks_initialization_gate);
    try std.testing.expect(query_plan.reuses_create_ruleset_validation);
    try std.testing.expectEqual(CreateRulesetAction.abi_version_query, query_plan.dispatched_create.action);
    try std.testing.expect(!query_plan.attempts_ruleset_fd_install);
    try std.testing.expect(!query_plan.releases_ruleset_on_install_failure);
    try std.testing.expectEqual(@as(?RulesetFdInstallPlan, null), query_plan.installed_fd);

    const create_plan = try SyscallsHelperLab.planLandlockCreateRuleset(.{
        .create_ruleset = .{
            .allowed_fs_mask = 0x7,
            .allowed_net_mask = 0,
            .allowed_scope_mask = 0,
            .attr = .{
                .handled_access_fs = 0x3,
            },
        },
    });
    try std.testing.expectEqual(CreateRulesetAction.create, create_plan.dispatched_create.action);
    try std.testing.expect(create_plan.attempts_ruleset_fd_install);
    try std.testing.expect(!create_plan.releases_ruleset_on_install_failure);
    try std.testing.expect(create_plan.installed_fd != null);
    try std.testing.expect(create_plan.installed_fd.?.returns_installed_fd);
}

test "landlock create-ruleset syscall planning rejects disabled state and surfaces install failures" {
    try std.testing.expectError(error.BootDisabled, SyscallsHelperLab.planLandlockCreateRuleset(.{
        .initialized = false,
        .create_ruleset = .{
            .allowed_fs_mask = 0x1,
            .allowed_net_mask = 0,
            .allowed_scope_mask = 0,
            .attr = .{
                .handled_access_fs = 0x1,
            },
        },
    }));

    const failed_install = try SyscallsHelperLab.planLandlockCreateRuleset(.{
        .create_ruleset = .{
            .allowed_fs_mask = 0x1,
            .allowed_net_mask = 0,
            .allowed_scope_mask = 0,
            .attr = .{
                .handled_access_fs = 0x1,
            },
        },
        .install_errno = -24,
    });
    try std.testing.expect(failed_install.attempts_ruleset_fd_install);
    try std.testing.expect(failed_install.releases_ruleset_on_install_failure);
    try std.testing.expect(failed_install.installed_fd != null);
    try std.testing.expectEqual(@as(?i32, -24), failed_install.installed_fd.?.failure_errno);

    try std.testing.expectError(error.InvalidInstallErrno, SyscallsHelperLab.planLandlockCreateRuleset(.{
        .create_ruleset = .{
            .allowed_fs_mask = 0x1,
            .allowed_net_mask = 0,
            .allowed_scope_mask = 0,
            .attr = .{
                .handled_access_fs = 0x1,
            },
        },
        .install_errno = 0,
    }));
}

test "landlock restrict self syscall planning requires an initialized readable ruleset" {
    const descriptor = SyscallsHelperLab.descriptor();
    try std.testing.expect(descriptor.provides_restrict_self_flag_planning);
    try std.testing.expect(descriptor.provides_restrict_self_syscall_planning);

    const plan = try SyscallsHelperLab.planLandlockRestrictSelf(.{
        .ruleset_fd = .{
            .file_mode = fmode_can_read,
            .required_mode = fmode_can_read,
        },
        .flags = restrict_self_tsync,
    });
    try std.testing.expect(plan.checks_initialization_gate);
    try std.testing.expect(plan.acquires_ruleset_with_read_access);
    try std.testing.expect(plan.reuses_flag_planning);
    try std.testing.expect(plan.dispatched_restriction.requires_ruleset);
    try std.testing.expect(plan.dispatched_restriction.propagates_to_siblings);
}

test "landlock restrict self syscall planning allows subdomain log toggles without a ruleset fd" {
    const plan = try SyscallsHelperLab.planLandlockRestrictSelf(.{
        .ruleset_fd = .{
            .fd_present = false,
            .required_mode = fmode_can_read,
        },
        .flags = restrict_self_log_subdomains_off | restrict_self_tsync,
    });

    try std.testing.expect(plan.allows_log_subdomains_toggle_without_ruleset);
    try std.testing.expect(!plan.acquires_ruleset_with_read_access);
    try std.testing.expect(!plan.dispatched_restriction.requires_ruleset);
    try std.testing.expect(!plan.dispatched_restriction.log_subdomains);
    try std.testing.expect(plan.dispatched_restriction.propagates_to_siblings);
}

test "landlock add-rule syscall planning keeps write-fd dispatch explicit" {
    const descriptor = SyscallsHelperLab.descriptor();
    try std.testing.expect(descriptor.provides_add_rule_planning);

    const path_plan = try SyscallsHelperLab.planLandlockAddRule(.{
        .ruleset_fd = .{
            .file_mode = fmode_can_write,
            .required_mode = fmode_can_write,
        },
        .rule_type = rule_type_path_beneath,
        .handled_access_fs = 0x7,
        .path_beneath_attr = .{
            .allowed_access = 0x3,
            .parent_fd = 42,
        },
    });
    try std.testing.expectEqualStrings(descriptor.anchor, path_plan.anchor);
    try std.testing.expect(path_plan.checks_initialization_gate);
    try std.testing.expect(path_plan.requires_zero_flags);
    try std.testing.expect(path_plan.acquires_ruleset_with_write_access);
    try std.testing.expect(path_plan.reuses_add_rule_validation);
    try std.testing.expectEqual(AddRuleAction.path_beneath, path_plan.dispatched_rule.action);
    try std.testing.expect(path_plan.dispatched_rule.requires_ruleset_write_access);
    try std.testing.expect(path_plan.dispatched_rule.requires_path_lookup);
    try std.testing.expectEqual(@as(i32, 42), path_plan.dispatched_rule.parent_fd);
    try std.testing.expect(path_plan.reuses_path_beneath_handoff);
    try std.testing.expect(path_plan.acquires_parent_path_reference);
    try std.testing.expect(path_plan.releases_parent_path_reference);

    const net_plan = try SyscallsHelperLab.planLandlockAddRule(.{
        .ruleset_fd = .{
            .file_mode = fmode_can_write,
            .required_mode = fmode_can_write,
        },
        .rule_type = rule_type_net_port,
        .handled_access_net = 0x5,
        .net_port_attr = .{
            .allowed_access = 0x1,
            .port = 443,
        },
    });
    try std.testing.expectEqual(AddRuleAction.net_port, net_plan.dispatched_rule.action);
    try std.testing.expectEqual(@as(?u16, 443), net_plan.dispatched_rule.port);
    try std.testing.expect(!net_plan.dispatched_rule.requires_path_lookup);
    try std.testing.expect(!net_plan.reuses_path_beneath_handoff);
    try std.testing.expect(!net_plan.acquires_parent_path_reference);
    try std.testing.expect(!net_plan.releases_parent_path_reference);
}

test "landlock add-rule syscall planning rejects disabled state flags and non-writable rulesets" {
    try std.testing.expectError(error.BootDisabled, SyscallsHelperLab.planLandlockAddRule(.{
        .initialized = false,
        .ruleset_fd = .{
            .file_mode = fmode_can_write,
            .required_mode = fmode_can_write,
        },
        .rule_type = rule_type_path_beneath,
        .handled_access_fs = 0x1,
        .path_beneath_attr = .{ .allowed_access = 0x1 },
    }));

    try std.testing.expectError(error.InvalidFlags, SyscallsHelperLab.planLandlockAddRule(.{
        .ruleset_fd = .{
            .file_mode = fmode_can_write,
            .required_mode = fmode_can_write,
        },
        .flags = 1,
        .rule_type = rule_type_path_beneath,
        .handled_access_fs = 0x1,
        .path_beneath_attr = .{ .allowed_access = 0x1 },
    }));

    try std.testing.expectError(error.InsufficientMode, SyscallsHelperLab.planLandlockAddRule(.{
        .ruleset_fd = .{
            .file_mode = fmode_can_read,
            .required_mode = fmode_can_write,
        },
        .rule_type = rule_type_net_port,
        .handled_access_net = 0x1,
        .net_port_attr = .{ .allowed_access = 0x1, .port = 80 },
    }));
}

test "landlock add-rule syscall planning rejects invalid path-beneath parent paths through the handoff" {
    try std.testing.expectError(error.PrivateInode, SyscallsHelperLab.planLandlockAddRule(.{
        .ruleset_fd = .{
            .file_mode = fmode_can_write,
            .required_mode = fmode_can_write,
        },
        .rule_type = rule_type_path_beneath,
        .handled_access_fs = 0x1,
        .path_beneath_attr = .{
            .allowed_access = 0x1,
            .parent_fd = 7,
        },
        .path_beneath_parent_path = .{
            .inode_is_private = true,
        },
    }));
}

test "landlock ruleset-fd install planning keeps anon-fd handoff explicit" {
    const descriptor = SyscallsHelperLab.descriptor();
    try std.testing.expect(descriptor.provides_ruleset_fd_install_planning);

    const plan = try SyscallsHelperLab.planInstallRulesetFd(.{});
    try std.testing.expectEqualStrings(descriptor.anchor, plan.anchor);
    try std.testing.expectEqualStrings(ruleset_fd_display_name, plan.display_name);
    try std.testing.expect(plan.uses_ruleset_fops);
    try std.testing.expect(plan.exposes_read_write_fd);
    try std.testing.expect(plan.cloexec);
    try std.testing.expect(plan.returns_installed_fd);
    try std.testing.expect(!plan.releases_ruleset_on_failure);
    try std.testing.expectEqual(@as(?i32, null), plan.failure_errno);
}

test "landlock ruleset-fd install planning releases the ruleset on anon-fd failure" {
    const plan = try SyscallsHelperLab.planInstallRulesetFd(.{
        .install_errno = -24,
    });
    try std.testing.expect(!plan.returns_installed_fd);
    try std.testing.expect(plan.releases_ruleset_on_failure);
    try std.testing.expectEqual(@as(?i32, -24), plan.failure_errno);

    try std.testing.expectError(error.MissingRuleset, SyscallsHelperLab.planInstallRulesetFd(.{
        .ruleset_created = false,
    }));
    try std.testing.expectError(error.InvalidInstallErrno, SyscallsHelperLab.planInstallRulesetFd(.{
        .install_errno = 0,
    }));
}

test "landlock syscalls ruleset fops release stays aligned with the release planner" {
    const descriptor = SyscallsHelperLab.descriptor();
    try std.testing.expect(descriptor.provides_ruleset_fops_planning);

    const release_plan = try SyscallsHelperLab.planRulesetRelease(.{});
    const fops_release = SyscallsHelperLab.planRulesetFops(.release);
    try std.testing.expectEqualStrings(release_plan.anchor, fops_release.anchor);
    try std.testing.expectEqual(release_plan.requires_private_data_ruleset, fops_release.requires_private_data_ruleset);
    try std.testing.expectEqual(release_plan.releases_retained_ruleset_reference, fops_release.releases_retained_ruleset_reference);
    try std.testing.expectEqual(release_plan.returns_zero, fops_release.returns_zero);
}
