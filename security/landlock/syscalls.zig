const std = @import("std");
const landlock_ruleset = @import("ruleset.zig");

pub const LANDLOCK_CREATE_RULESET_VERSION: u32 = 1 << 0;
pub const LANDLOCK_CREATE_RULESET_ERRATA: u32 = 1 << 1;
pub const LANDLOCK_RESTRICT_SELF_LOG_NEW_EXEC_ON: u32 = 1 << 0;
pub const LANDLOCK_RESTRICT_SELF_TSYNC: u32 = 1 << 1;
pub const O_RDWR: u32 = 0x2;
pub const O_CLOEXEC: u32 = 0x80000;
pub const FMODE_CAN_READ: u32 = 1 << 0;
pub const FMODE_CAN_WRITE: u32 = 1 << 1;

pub const ModuleDescriptor = struct {
    name: []const u8,
    anchor: []const u8,
    provides_create_ruleset_planning: bool,
    provides_abi_version_query_planning: bool,
    provides_abi_errata_query_planning: bool,
    provides_restrict_self_planning: bool,
    provides_add_rule_planning: bool,
    provides_ruleset_fd_lookup_planning: bool,
    provides_ruleset_fd_install_planning: bool,
    provides_ruleset_fd_stub_planning: bool,
    provides_ruleset_release_planning: bool,
    validates_handled_access: bool,
    validates_attr_size: bool,
    validates_flags: bool,
    validates_add_rule_layers: bool,
    validates_add_rule_tree_walk: bool,
    delegates_ruleset_creation_planning: bool,
    delegates_rule_tree_search_planning: bool,
    delegates_rule_insertion_planning: bool,
    touches_live_fd_installation: bool,
    touches_live_cred_replacement: bool,
};

pub const CreateRulesetAttr = struct {
    handled_access_fs: u32 = 0,
    handled_access_net: u32 = 0,
    scoped: u32 = 0,
};

pub const CreateRulesetInput = struct {
    attr: CreateRulesetAttr = .{},
    attr_size: usize = @sizeOf(CreateRulesetAttr),
    flags: u32 = 0,
};

pub const CreateRulesetMode = enum {
    create_handle,
    abi_version_query,
    abi_errata_query,
};

pub const CreateRulesetPlan = struct {
    anchor: []const u8,
    mode: CreateRulesetMode,
    attr_size: usize,
    validates_flags: bool,
    validates_attr_size: bool,
    validates_handled_access: bool,
    performs_copy_from_user: bool,
    delegates_ruleset_creation_planning: bool,
    performs_anon_inode_getfd: bool,
    returns_new_fd: bool,
    ruleset_plan: ?landlock_ruleset.CreationPlan,
};

pub const CreateRulesetSyscallRequest = struct {
    initialized: bool = true,
    attr_present: bool = true,
    ruleset_fops_present: bool = true,
    input: CreateRulesetInput = .{},
};

pub const CreateRulesetSyscallPlan = struct {
    anchor: []const u8,
    checks_initialization_gate: bool,
    checks_attr_presence_before_copy_from_user: bool,
    reuses_create_ruleset_validation: bool,
    reuses_ruleset_fd_install_planning: bool,
    create_ruleset_plan: CreateRulesetPlan,
    ruleset_fd_install_plan: ?RulesetFdInstallPlan,
};

pub const GetRulesetFromFdRequest = struct {
    ruleset_fd_present: bool = true,
    file_present: bool = true,
    ruleset_fops_present: bool = true,
    private_data_present: bool = true,
    ruleset_present: bool = true,
    file_mode_bits: u32 = FMODE_CAN_READ | FMODE_CAN_WRITE,
    required_mode_bits: ?u32 = null,
};

pub const GetRulesetFromFdPlan = struct {
    anchor: []const u8,
    validates_ruleset_fd: bool,
    obtains_file_from_fd: bool,
    validates_file_operations_binding: bool,
    validates_required_mode_bits: bool,
    required_mode_bits: ?u32,
    reads_file_private_data: bool,
    validates_ruleset_presence: bool,
    returns_ruleset_handle: bool,
};

pub const RestrictSelfRequest = struct {
    initialized: bool = true,
    ruleset_fd: GetRulesetFromFdRequest = .{},
    no_new_privs: bool = true,
    flags: u32 = 0,
};

pub const RestrictSelfPlan = struct {
    anchor: []const u8,
    checks_initialization_gate: bool,
    validates_ruleset_presence: bool,
    validates_no_new_privs: bool,
    validates_flags: bool,
    reuses_ruleset_fd_lookup_planning: bool,
    ruleset_fd_lookup_plan: GetRulesetFromFdPlan,
    logs_new_exec_transitions: bool,
    requests_tsync: bool,
    prepares_new_domain: bool,
    merges_ruleset_into_domain: bool,
    updates_current_cred: bool,
};

pub const AddRuleInput = struct {
    key_type: landlock_ruleset.KeyType = .inode,
    root_present: bool = false,
    search_key_data: u64 = 0,
    walker_keys: []const u64 = &.{},
    current_num_rules: u32 = 0,
    existing_rule: ?landlock_ruleset.RulePlan = null,
    incoming_layers: []const landlock_ruleset.Layer = &.{},
};

pub const AddRulePlan = struct {
    anchor: []const u8,
    validates_ruleset_fd: bool,
    validates_incoming_layers: bool,
    validates_tree_walk: bool,
    performs_copy_from_user: bool,
    reuses_ruleset_fd_lookup_planning: bool,
    delegates_rule_tree_search_planning: bool,
    delegates_rule_insertion_planning: bool,
    ruleset_fd_lookup_plan: GetRulesetFromFdPlan,
    search_plan: landlock_ruleset.RuleTreeSearchPlan,
    branch_plan: landlock_ruleset.InsertRuleBranchPlan,
};

pub const AddRuleSyscallRequest = struct {
    initialized: bool = true,
    attr_present: bool = true,
    flags: u32 = 0,
    ruleset_fd_mode_bits: u32 = FMODE_CAN_WRITE,
    ruleset_fd: GetRulesetFromFdRequest = .{},
    input: AddRuleInput = .{},
};

pub const AddRuleSyscallPlan = struct {
    anchor: []const u8,
    checks_initialization_gate: bool,
    checks_attr_presence_before_copy_from_user: bool,
    requires_zero_flags: bool,
    validates_ruleset_fd_write_mode: bool,
    required_ruleset_fd_mode_bits: u32,
    reuses_add_rule_validation: bool,
    add_rule_plan: AddRulePlan,
};

pub const RulesetFdInstallRequest = struct {
    label: []const u8 = "[landlock-ruleset]",
    flags: u32 = O_RDWR | O_CLOEXEC,
    ruleset_present: bool = true,
    ruleset_fops_present: bool = true,
};

pub const RulesetFdInstallPlan = struct {
    anchor: []const u8,
    label: []const u8,
    validates_label: bool,
    validates_install_flags: bool,
    validates_file_operations_binding: bool,
    performs_anon_inode_getfd: bool,
    returns_new_fd: bool,
    releases_ruleset_on_fd_failure: bool,
    install_flags: u32,
};

pub const RulesetFdStubOperation = enum {
    read,
    write,
};

pub const RulesetFdStubRequest = struct {
    operation: RulesetFdStubOperation,
    mode_bits: u32,
};

pub const RulesetFdStubPlan = struct {
    anchor: []const u8,
    operation: RulesetFdStubOperation,
    validates_mode_bits: bool,
    required_mode_bits: u32,
    enables_read_mode: bool,
    enables_write_mode: bool,
    returns_einval: bool,
    mutates_ruleset_state: bool,
};

pub const RulesetReleaseRequest = struct {
    file_present: bool = true,
    private_data_present: bool = true,
    ruleset_present: bool = true,
};

pub const RulesetReleasePlan = struct {
    anchor: []const u8,
    reads_file_private_data: bool,
    invokes_landlock_put_ruleset: bool,
    returns_zero: bool,
};

pub const SyscallsHelperLab = struct {
    pub fn descriptor() ModuleDescriptor {
        return .{
            .name = "landlock_syscalls_helper_lab",
            .anchor = "security/landlock/syscalls.c",
            .provides_create_ruleset_planning = true,
            .provides_abi_version_query_planning = true,
            .provides_abi_errata_query_planning = true,
            .provides_restrict_self_planning = true,
            .provides_add_rule_planning = true,
            .provides_ruleset_fd_lookup_planning = true,
            .provides_ruleset_fd_install_planning = true,
            .provides_ruleset_fd_stub_planning = true,
            .provides_ruleset_release_planning = true,
            .validates_handled_access = true,
            .validates_attr_size = true,
            .validates_flags = true,
            .validates_add_rule_layers = true,
            .validates_add_rule_tree_walk = true,
            .delegates_ruleset_creation_planning = true,
            .delegates_rule_tree_search_planning = true,
            .delegates_rule_insertion_planning = true,
            .touches_live_fd_installation = false,
            .touches_live_cred_replacement = false,
        };
    }

    pub fn planCreateRuleset(input: CreateRulesetInput) !CreateRulesetPlan {
        if (input.flags != 0) {
            if (input.attr_size != 0) {
                return error.UnexpectedAttrPayload;
            }
            if (input.attr.handled_access_fs != 0 or input.attr.handled_access_net != 0 or input.attr.scoped != 0) {
                return error.UnexpectedAttrPayload;
            }

            const mode = switch (input.flags) {
                LANDLOCK_CREATE_RULESET_VERSION => CreateRulesetMode.abi_version_query,
                LANDLOCK_CREATE_RULESET_ERRATA => CreateRulesetMode.abi_errata_query,
                else => return error.UnsupportedCreateRulesetFlags,
            };

            return .{
                .anchor = descriptor().anchor,
                .mode = mode,
                .attr_size = input.attr_size,
                .validates_flags = true,
                .validates_attr_size = true,
                .validates_handled_access = true,
                .performs_copy_from_user = false,
                .delegates_ruleset_creation_planning = false,
                .performs_anon_inode_getfd = false,
                .returns_new_fd = false,
                .ruleset_plan = null,
            };
        }

        if (input.attr_size < @sizeOf(CreateRulesetAttr)) {
            return error.AttrTooSmall;
        }

        const ruleset_plan = try landlock_ruleset.RulesetHelperLab.planRulesetCreation(.{
            .fs = input.attr.handled_access_fs,
            .net = input.attr.handled_access_net,
            .scope = input.attr.scoped,
        });

        return .{
            .anchor = descriptor().anchor,
            .mode = .create_handle,
            .attr_size = input.attr_size,
            .validates_flags = true,
            .validates_attr_size = true,
            .validates_handled_access = true,
            .performs_copy_from_user = true,
            .delegates_ruleset_creation_planning = true,
            .performs_anon_inode_getfd = false,
            .returns_new_fd = false,
            .ruleset_plan = ruleset_plan,
        };
    }

    pub fn planLandlockCreateRuleset(request: CreateRulesetSyscallRequest) !CreateRulesetSyscallPlan {
        if (!request.initialized) {
            return error.BootDisabled;
        }

        const create_ruleset_plan = try planCreateRuleset(request.input);
        if (create_ruleset_plan.performs_copy_from_user and !request.attr_present) {
            return error.BadUserPointer;
        }

        const ruleset_fd_install_plan = switch (create_ruleset_plan.mode) {
            .create_handle => try planInstallRulesetFd(.{
                .ruleset_fops_present = request.ruleset_fops_present,
            }),
            .abi_version_query, .abi_errata_query => null,
        };

        return .{
            .anchor = descriptor().anchor,
            .checks_initialization_gate = true,
            .checks_attr_presence_before_copy_from_user = create_ruleset_plan.performs_copy_from_user,
            .reuses_create_ruleset_validation = true,
            .reuses_ruleset_fd_install_planning = create_ruleset_plan.mode == .create_handle,
            .create_ruleset_plan = create_ruleset_plan,
            .ruleset_fd_install_plan = ruleset_fd_install_plan,
        };
    }

    pub fn planGetRulesetFromFd(request: GetRulesetFromFdRequest) !GetRulesetFromFdPlan {
        if (!request.ruleset_fd_present) {
            return error.MissingRulesetFd;
        }
        if (!request.file_present) {
            return error.MissingFile;
        }
        if (!request.ruleset_fops_present) {
            return error.MissingRulesetFileOperations;
        }
        if (request.required_mode_bits) |required_mode_bits| {
            if ((request.file_mode_bits & required_mode_bits) != required_mode_bits) {
                return error.InsufficientRulesetFdMode;
            }
        }
        if (!request.private_data_present or !request.ruleset_present) {
            return error.MissingRuleset;
        }

        return .{
            .anchor = descriptor().anchor,
            .validates_ruleset_fd = true,
            .obtains_file_from_fd = true,
            .validates_file_operations_binding = true,
            .validates_required_mode_bits = request.required_mode_bits != null,
            .required_mode_bits = request.required_mode_bits,
            .reads_file_private_data = true,
            .validates_ruleset_presence = true,
            .returns_ruleset_handle = true,
        };
    }

    pub fn planLandlockRestrictSelf(request: RestrictSelfRequest) !RestrictSelfPlan {
        if (!request.initialized) {
            return error.BootDisabled;
        }

        const ruleset_fd_lookup_plan = try planGetRulesetFromFd(request.ruleset_fd);
        if (!request.no_new_privs) {
            return error.MissingNoNewPrivileges;
        }
        if ((request.flags & ~(LANDLOCK_RESTRICT_SELF_LOG_NEW_EXEC_ON | LANDLOCK_RESTRICT_SELF_TSYNC)) != 0) {
            return error.UnsupportedRestrictSelfFlags;
        }

        return .{
            .anchor = descriptor().anchor,
            .checks_initialization_gate = true,
            .validates_ruleset_presence = true,
            .validates_no_new_privs = true,
            .validates_flags = true,
            .reuses_ruleset_fd_lookup_planning = true,
            .ruleset_fd_lookup_plan = ruleset_fd_lookup_plan,
            .logs_new_exec_transitions = (request.flags & LANDLOCK_RESTRICT_SELF_LOG_NEW_EXEC_ON) != 0,
            .requests_tsync = (request.flags & LANDLOCK_RESTRICT_SELF_TSYNC) != 0,
            .prepares_new_domain = true,
            .merges_ruleset_into_domain = true,
            .updates_current_cred = false,
        };
    }

    pub fn planAddRule(input: AddRuleInput, ruleset_fd: GetRulesetFromFdRequest) !AddRulePlan {
        const ruleset_fd_lookup_plan = try planGetRulesetFromFd(ruleset_fd);
        if (input.incoming_layers.len == 0) {
            return error.MissingLayers;
        }

        const search_plan = try landlock_ruleset.RulesetHelperLab.planRuleTreeSearch(
            input.key_type,
            input.root_present,
            input.search_key_data,
            input.walker_keys,
            input.current_num_rules,
        );
        const branch_plan = try landlock_ruleset.RulesetHelperLab.planInsertRuleBranch(
            search_plan,
            input.existing_rule,
            input.incoming_layers,
        );

        return .{
            .anchor = descriptor().anchor,
            .validates_ruleset_fd = true,
            .validates_incoming_layers = true,
            .validates_tree_walk = true,
            .performs_copy_from_user = true,
            .reuses_ruleset_fd_lookup_planning = true,
            .delegates_rule_tree_search_planning = true,
            .delegates_rule_insertion_planning = true,
            .ruleset_fd_lookup_plan = ruleset_fd_lookup_plan,
            .search_plan = search_plan,
            .branch_plan = branch_plan,
        };
    }

    pub fn planLandlockAddRule(request: AddRuleSyscallRequest) !AddRuleSyscallPlan {
        if (!request.initialized) {
            return error.BootDisabled;
        }
        if (!request.attr_present) {
            return error.BadUserPointer;
        }
        if (request.flags != 0) {
            return error.UnsupportedAddRuleFlags;
        }

        return .{
            .anchor = descriptor().anchor,
            .checks_initialization_gate = true,
            .checks_attr_presence_before_copy_from_user = true,
            .requires_zero_flags = true,
            .validates_ruleset_fd_write_mode = true,
            .required_ruleset_fd_mode_bits = FMODE_CAN_WRITE,
            .reuses_add_rule_validation = true,
            .add_rule_plan = try planAddRule(request.input, .{
                .ruleset_fd_present = request.ruleset_fd.ruleset_fd_present,
                .file_present = request.ruleset_fd.file_present,
                .ruleset_fops_present = request.ruleset_fd.ruleset_fops_present,
                .private_data_present = request.ruleset_fd.private_data_present,
                .ruleset_present = request.ruleset_fd.ruleset_present,
                .file_mode_bits = request.ruleset_fd_mode_bits,
                .required_mode_bits = FMODE_CAN_WRITE,
            }),
        };
    }

    pub fn planInstallRulesetFd(request: RulesetFdInstallRequest) !RulesetFdInstallPlan {
        if (!request.ruleset_present) {
            return error.MissingRuleset;
        }
        if (!request.ruleset_fops_present) {
            return error.MissingRulesetFileOperations;
        }
        if (!std.mem.eql(u8, request.label, "[landlock-ruleset]")) {
            return error.InvalidAnonInodeLabel;
        }
        if (request.flags != (O_RDWR | O_CLOEXEC)) {
            return error.UnsupportedAnonInodeFlags;
        }

        return .{
            .anchor = descriptor().anchor,
            .label = request.label,
            .validates_label = true,
            .validates_install_flags = true,
            .validates_file_operations_binding = true,
            .performs_anon_inode_getfd = true,
            .returns_new_fd = true,
            .releases_ruleset_on_fd_failure = true,
            .install_flags = request.flags,
        };
    }

    pub fn planRulesetFdStub(request: RulesetFdStubRequest) !RulesetFdStubPlan {
        const expected_mode_bits = switch (request.operation) {
            .read => FMODE_CAN_READ,
            .write => FMODE_CAN_WRITE,
        };

        if (request.mode_bits != expected_mode_bits) {
            return error.UnsupportedRulesetFdMode;
        }

        return switch (request.operation) {
            .read => .{
                .anchor = descriptor().anchor,
                .operation = .read,
                .validates_mode_bits = true,
                .required_mode_bits = expected_mode_bits,
                .enables_read_mode = true,
                .enables_write_mode = false,
                .returns_einval = true,
                .mutates_ruleset_state = false,
            },
            .write => .{
                .anchor = descriptor().anchor,
                .operation = .write,
                .validates_mode_bits = true,
                .required_mode_bits = expected_mode_bits,
                .enables_read_mode = false,
                .enables_write_mode = true,
                .returns_einval = true,
                .mutates_ruleset_state = false,
            },
        };
    }

    pub fn planFopRulesetRelease(request: RulesetReleaseRequest) !RulesetReleasePlan {
        if (!request.file_present) {
            return error.MissingFile;
        }
        if (!request.private_data_present or !request.ruleset_present) {
            return error.MissingRuleset;
        }

        return .{
            .anchor = descriptor().anchor,
            .reads_file_private_data = true,
            .invokes_landlock_put_ruleset = true,
            .returns_zero = true,
        };
    }
};

test "landlock syscalls descriptor stays within create, restrict-self, and add-rule planning boundaries" {
    const descriptor = SyscallsHelperLab.descriptor();

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
    try std.testing.expect(descriptor.validates_handled_access);
    try std.testing.expect(descriptor.validates_attr_size);
    try std.testing.expect(descriptor.validates_flags);
    try std.testing.expect(descriptor.validates_add_rule_layers);
    try std.testing.expect(descriptor.validates_add_rule_tree_walk);
    try std.testing.expect(descriptor.delegates_ruleset_creation_planning);
    try std.testing.expect(descriptor.delegates_rule_tree_search_planning);
    try std.testing.expect(descriptor.delegates_rule_insertion_planning);
    try std.testing.expect(!descriptor.touches_live_fd_installation);
    try std.testing.expect(!descriptor.touches_live_cred_replacement);
}

test "landlock syscalls version query stays before anon inode installation" {
    const plan = try SyscallsHelperLab.planCreateRuleset(.{
        .attr_size = 0,
        .flags = LANDLOCK_CREATE_RULESET_VERSION,
    });

    try std.testing.expectEqualStrings(SyscallsHelperLab.descriptor().anchor, plan.anchor);
    try std.testing.expectEqual(CreateRulesetMode.abi_version_query, plan.mode);
    try std.testing.expect(plan.validates_flags);
    try std.testing.expect(plan.validates_attr_size);
    try std.testing.expect(plan.validates_handled_access);
    try std.testing.expect(!plan.performs_copy_from_user);
    try std.testing.expect(!plan.delegates_ruleset_creation_planning);
    try std.testing.expect(!plan.performs_anon_inode_getfd);
    try std.testing.expect(!plan.returns_new_fd);
    try std.testing.expectEqual(@as(?landlock_ruleset.CreationPlan, null), plan.ruleset_plan);
}

test "landlock syscalls errata query stays before anon inode installation" {
    const plan = try SyscallsHelperLab.planCreateRuleset(.{
        .attr_size = 0,
        .flags = LANDLOCK_CREATE_RULESET_ERRATA,
    });

    try std.testing.expectEqualStrings(SyscallsHelperLab.descriptor().anchor, plan.anchor);
    try std.testing.expectEqual(CreateRulesetMode.abi_errata_query, plan.mode);
    try std.testing.expect(plan.validates_flags);
    try std.testing.expect(plan.validates_attr_size);
    try std.testing.expect(plan.validates_handled_access);
    try std.testing.expect(!plan.performs_copy_from_user);
    try std.testing.expect(!plan.delegates_ruleset_creation_planning);
    try std.testing.expect(!plan.performs_anon_inode_getfd);
    try std.testing.expect(!plan.returns_new_fd);
    try std.testing.expectEqual(@as(?landlock_ruleset.CreationPlan, null), plan.ruleset_plan);
}

test "landlock syscalls version query rejects unexpected attr payload" {
    try std.testing.expectError(error.UnexpectedAttrPayload, SyscallsHelperLab.planCreateRuleset(.{
        .attr = .{ .handled_access_fs = 0x1 },
        .attr_size = @sizeOf(CreateRulesetAttr),
        .flags = LANDLOCK_CREATE_RULESET_VERSION,
    }));
}

test "landlock syscalls errata query rejects unexpected attr payload" {
    try std.testing.expectError(error.UnexpectedAttrPayload, SyscallsHelperLab.planCreateRuleset(.{
        .attr = .{ .handled_access_net = 0x1 },
        .attr_size = @sizeOf(CreateRulesetAttr),
        .flags = LANDLOCK_CREATE_RULESET_ERRATA,
    }));
}

test "landlock syscalls create-ruleset rejects undersized attr copies" {
    try std.testing.expectError(error.AttrTooSmall, SyscallsHelperLab.planCreateRuleset(.{
        .attr = .{ .handled_access_fs = 0x2 },
        .attr_size = @sizeOf(CreateRulesetAttr) - 1,
    }));
}

test "landlock syscalls create-ruleset rejects combined or unknown query flags" {
    try std.testing.expectError(error.UnsupportedCreateRulesetFlags, SyscallsHelperLab.planCreateRuleset(.{
        .attr_size = 0,
        .flags = LANDLOCK_CREATE_RULESET_VERSION | LANDLOCK_CREATE_RULESET_ERRATA,
    }));
    try std.testing.expectError(error.UnsupportedCreateRulesetFlags, SyscallsHelperLab.planCreateRuleset(.{
        .attr_size = 0,
        .flags = 1 << 5,
    }));
}

test "landlock syscalls create-ruleset delegates handled access planning before fd install" {
    const plan = try SyscallsHelperLab.planCreateRuleset(.{
        .attr = .{
            .handled_access_fs = 0x6,
            .handled_access_net = 0x10,
            .scoped = 0x3,
        },
    });
    const ruleset_plan = plan.ruleset_plan orelse unreachable;

    try std.testing.expectEqual(CreateRulesetMode.create_handle, plan.mode);
    try std.testing.expect(plan.performs_copy_from_user);
    try std.testing.expect(plan.delegates_ruleset_creation_planning);
    try std.testing.expect(!plan.performs_anon_inode_getfd);
    try std.testing.expect(!plan.returns_new_fd);
    try std.testing.expectEqualStrings(SyscallsHelperLab.descriptor().anchor, plan.anchor);
    try std.testing.expectEqualStrings(landlock_ruleset.RulesetHelperLab.descriptor().anchor, ruleset_plan.anchor);
    try std.testing.expectEqual(@as(u32, 1), ruleset_plan.num_layers);
    try std.testing.expectEqual(@as(u32, 0x6), ruleset_plan.access_masks.fs);
    try std.testing.expectEqual(@as(u32, 0x10), ruleset_plan.access_masks.net);
    try std.testing.expectEqual(@as(u32, 0x3), ruleset_plan.access_masks.scope);
}

test "landlock syscalls create-ruleset still rejects empty handled access" {
    try std.testing.expectError(error.EmptyRuleset, SyscallsHelperLab.planCreateRuleset(.{}));
}

test "landlock syscalls top-level wrapper keeps version query nullable and explicit" {
    const wrapper = try SyscallsHelperLab.planLandlockCreateRuleset(.{
        .attr_present = false,
        .input = .{
            .attr_size = 0,
            .flags = LANDLOCK_CREATE_RULESET_VERSION,
        },
    });

    try std.testing.expectEqualStrings(SyscallsHelperLab.descriptor().anchor, wrapper.anchor);
    try std.testing.expect(wrapper.checks_initialization_gate);
    try std.testing.expect(!wrapper.checks_attr_presence_before_copy_from_user);
    try std.testing.expect(wrapper.reuses_create_ruleset_validation);
    try std.testing.expectEqual(CreateRulesetMode.abi_version_query, wrapper.create_ruleset_plan.mode);
    try std.testing.expect(!wrapper.create_ruleset_plan.performs_copy_from_user);
}

test "landlock syscalls top-level wrapper keeps errata query nullable and explicit" {
    const wrapper = try SyscallsHelperLab.planLandlockCreateRuleset(.{
        .attr_present = false,
        .input = .{
            .attr_size = 0,
            .flags = LANDLOCK_CREATE_RULESET_ERRATA,
        },
    });

    try std.testing.expectEqualStrings(SyscallsHelperLab.descriptor().anchor, wrapper.anchor);
    try std.testing.expect(wrapper.checks_initialization_gate);
    try std.testing.expect(!wrapper.checks_attr_presence_before_copy_from_user);
    try std.testing.expect(wrapper.reuses_create_ruleset_validation);
    try std.testing.expectEqual(CreateRulesetMode.abi_errata_query, wrapper.create_ruleset_plan.mode);
    try std.testing.expect(!wrapper.create_ruleset_plan.performs_copy_from_user);
}

test "landlock syscalls top-level wrapper keeps version and errata queries install planning nullable and explicit" {
    const version_query = try SyscallsHelperLab.planLandlockCreateRuleset(.{
        .attr_present = false,
        .input = .{
            .attr_size = 0,
            .flags = LANDLOCK_CREATE_RULESET_VERSION,
        },
    });
    const errata_query = try SyscallsHelperLab.planLandlockCreateRuleset(.{
        .attr_present = false,
        .input = .{
            .attr_size = 0,
            .flags = LANDLOCK_CREATE_RULESET_ERRATA,
        },
    });

    try std.testing.expect(!version_query.reuses_ruleset_fd_install_planning);
    try std.testing.expectEqual(@as(?RulesetFdInstallPlan, null), version_query.ruleset_fd_install_plan);
    try std.testing.expect(!errata_query.reuses_ruleset_fd_install_planning);
    try std.testing.expectEqual(@as(?RulesetFdInstallPlan, null), errata_query.ruleset_fd_install_plan);
}

test "landlock syscalls top-level wrapper ignores ruleset_fops for create-ruleset query paths" {
    const version_query = try SyscallsHelperLab.planLandlockCreateRuleset(.{
        .attr_present = false,
        .ruleset_fops_present = false,
        .input = .{
            .attr_size = 0,
            .flags = LANDLOCK_CREATE_RULESET_VERSION,
        },
    });
    const errata_query = try SyscallsHelperLab.planLandlockCreateRuleset(.{
        .attr_present = false,
        .ruleset_fops_present = false,
        .input = .{
            .attr_size = 0,
            .flags = LANDLOCK_CREATE_RULESET_ERRATA,
        },
    });

    try std.testing.expectEqual(CreateRulesetMode.abi_version_query, version_query.create_ruleset_plan.mode);
    try std.testing.expect(!version_query.reuses_ruleset_fd_install_planning);
    try std.testing.expectEqual(@as(?RulesetFdInstallPlan, null), version_query.ruleset_fd_install_plan);
    try std.testing.expectEqual(CreateRulesetMode.abi_errata_query, errata_query.create_ruleset_plan.mode);
    try std.testing.expect(!errata_query.reuses_ruleset_fd_install_planning);
    try std.testing.expectEqual(@as(?RulesetFdInstallPlan, null), errata_query.ruleset_fd_install_plan);
}

test "landlock syscalls top-level wrapper threads ruleset fd install only for create path" {
    const wrapper = try SyscallsHelperLab.planLandlockCreateRuleset(.{
        .input = .{
            .attr = .{ .handled_access_fs = 0x4 },
        },
    });
    const install_plan = wrapper.ruleset_fd_install_plan orelse unreachable;

    try std.testing.expectEqual(CreateRulesetMode.create_handle, wrapper.create_ruleset_plan.mode);
    try std.testing.expect(wrapper.create_ruleset_plan.performs_copy_from_user);
    try std.testing.expect(wrapper.create_ruleset_plan.delegates_ruleset_creation_planning);
    try std.testing.expect(wrapper.reuses_ruleset_fd_install_planning);
    try std.testing.expectEqualStrings(SyscallsHelperLab.descriptor().anchor, install_plan.anchor);
    try std.testing.expectEqualStrings("[landlock-ruleset]", install_plan.label);
    try std.testing.expect(install_plan.validates_label);
    try std.testing.expect(install_plan.validates_install_flags);
    try std.testing.expect(install_plan.validates_file_operations_binding);
    try std.testing.expect(install_plan.performs_anon_inode_getfd);
    try std.testing.expect(install_plan.returns_new_fd);
    try std.testing.expect(install_plan.releases_ruleset_on_fd_failure);
}

test "landlock syscalls top-level wrapper propagates missing ruleset_fops for create path" {
    try std.testing.expectError(error.MissingRulesetFileOperations, SyscallsHelperLab.planLandlockCreateRuleset(.{
        .ruleset_fops_present = false,
        .input = .{
            .attr = .{ .handled_access_fs = 0x4 },
        },
    }));
}

test "landlock syscalls top-level wrapper requires attr presence for create path" {
    try std.testing.expectError(error.BadUserPointer, SyscallsHelperLab.planLandlockCreateRuleset(.{
        .attr_present = false,
        .input = .{
            .attr = .{ .handled_access_fs = 0x4 },
        },
    }));
}

test "landlock syscalls top-level wrapper rejects disabled boot before planning" {
    try std.testing.expectError(error.BootDisabled, SyscallsHelperLab.planLandlockCreateRuleset(.{
        .initialized = false,
        .input = .{
            .attr = .{ .handled_access_fs = 0x4 },
        },
    }));
}

test "landlock syscalls ruleset-fd lookup keeps file, fops, and private-data handoff explicit" {
    const plan = try SyscallsHelperLab.planGetRulesetFromFd(.{});

    try std.testing.expectEqualStrings(SyscallsHelperLab.descriptor().anchor, plan.anchor);
    try std.testing.expect(plan.validates_ruleset_fd);
    try std.testing.expect(plan.obtains_file_from_fd);
    try std.testing.expect(plan.validates_file_operations_binding);
    try std.testing.expect(!plan.validates_required_mode_bits);
    try std.testing.expectEqual(@as(?u32, null), plan.required_mode_bits);
    try std.testing.expect(plan.reads_file_private_data);
    try std.testing.expect(plan.validates_ruleset_presence);
    try std.testing.expect(plan.returns_ruleset_handle);
}

test "landlock syscalls ruleset-fd lookup can require write mode for mutating callers" {
    const plan = try SyscallsHelperLab.planGetRulesetFromFd(.{
        .file_mode_bits = FMODE_CAN_READ | FMODE_CAN_WRITE,
        .required_mode_bits = FMODE_CAN_WRITE,
    });

    try std.testing.expect(plan.validates_required_mode_bits);
    try std.testing.expectEqual(@as(?u32, FMODE_CAN_WRITE), plan.required_mode_bits);
}

test "landlock syscalls ruleset-fd lookup rejects missing fd file fops mode and ruleset state" {
    try std.testing.expectError(error.MissingRulesetFd, SyscallsHelperLab.planGetRulesetFromFd(.{
        .ruleset_fd_present = false,
    }));
    try std.testing.expectError(error.MissingFile, SyscallsHelperLab.planGetRulesetFromFd(.{
        .file_present = false,
    }));
    try std.testing.expectError(error.MissingRulesetFileOperations, SyscallsHelperLab.planGetRulesetFromFd(.{
        .ruleset_fops_present = false,
    }));
    try std.testing.expectError(error.InsufficientRulesetFdMode, SyscallsHelperLab.planGetRulesetFromFd(.{
        .file_mode_bits = FMODE_CAN_READ,
        .required_mode_bits = FMODE_CAN_WRITE,
    }));
    try std.testing.expectError(error.MissingRuleset, SyscallsHelperLab.planGetRulesetFromFd(.{
        .private_data_present = false,
    }));
}

test "landlock syscalls restrict-self keeps ruleset lookup no_new_privs and domain merge planning explicit" {
    const plan = try SyscallsHelperLab.planLandlockRestrictSelf(.{
        .flags = LANDLOCK_RESTRICT_SELF_LOG_NEW_EXEC_ON | LANDLOCK_RESTRICT_SELF_TSYNC,
    });

    try std.testing.expectEqualStrings(SyscallsHelperLab.descriptor().anchor, plan.anchor);
    try std.testing.expect(plan.checks_initialization_gate);
    try std.testing.expect(plan.validates_ruleset_presence);
    try std.testing.expect(plan.validates_no_new_privs);
    try std.testing.expect(plan.validates_flags);
    try std.testing.expect(plan.reuses_ruleset_fd_lookup_planning);
    try std.testing.expect(plan.ruleset_fd_lookup_plan.validates_file_operations_binding);
    try std.testing.expect(plan.ruleset_fd_lookup_plan.reads_file_private_data);
    try std.testing.expect(plan.logs_new_exec_transitions);
    try std.testing.expect(plan.requests_tsync);
    try std.testing.expect(plan.prepares_new_domain);
    try std.testing.expect(plan.merges_ruleset_into_domain);
    try std.testing.expect(!plan.updates_current_cred);
}

test "landlock syscalls restrict-self rejects disabled boot missing lookup preconditions and unknown flags" {
    try std.testing.expectError(error.BootDisabled, SyscallsHelperLab.planLandlockRestrictSelf(.{
        .initialized = false,
    }));
    try std.testing.expectError(error.MissingRulesetFd, SyscallsHelperLab.planLandlockRestrictSelf(.{
        .ruleset_fd = .{ .ruleset_fd_present = false },
    }));
    try std.testing.expectError(error.MissingNoNewPrivileges, SyscallsHelperLab.planLandlockRestrictSelf(.{
        .no_new_privs = false,
    }));
    try std.testing.expectError(error.UnsupportedRestrictSelfFlags, SyscallsHelperLab.planLandlockRestrictSelf(.{
        .flags = 1 << 5,
    }));
}

test "landlock syscalls add-rule plans fresh inode insertion through ruleset lookup search and link helpers" {
    const plan = try SyscallsHelperLab.planAddRule(.{
        .search_key_data = 64,
        .incoming_layers = &.{.{ .level = 0, .access = 0x2 }},
    }, .{});

    try std.testing.expectEqualStrings(SyscallsHelperLab.descriptor().anchor, plan.anchor);
    try std.testing.expect(plan.validates_ruleset_fd);
    try std.testing.expect(plan.validates_incoming_layers);
    try std.testing.expect(plan.validates_tree_walk);
    try std.testing.expect(plan.performs_copy_from_user);
    try std.testing.expect(plan.reuses_ruleset_fd_lookup_planning);
    try std.testing.expect(plan.ruleset_fd_lookup_plan.reads_file_private_data);
    try std.testing.expect(plan.delegates_rule_tree_search_planning);
    try std.testing.expect(plan.delegates_rule_insertion_planning);
    try std.testing.expectEqual(landlock_ruleset.TreeRoot.inode, plan.search_plan.root);
    try std.testing.expectEqual(@as(?landlock_ruleset.InsertionSite, .root), plan.search_plan.insertion_site);
    try std.testing.expect(!plan.search_plan.matched_existing_rule);
    try std.testing.expectEqual(landlock_ruleset.InsertRuleBranchMode.insert_with_link, plan.branch_plan.mode);
    try std.testing.expect(plan.branch_plan.link_plan != null);
    try std.testing.expect(plan.branch_plan.replacement_plan == null);
    try std.testing.expectEqual(@as(u32, 1), plan.branch_plan.resulting_num_rules);
}

test "landlock syscalls add-rule plans matched-rule replacement for layered merges" {
    const existing = landlock_ruleset.RulePlan{
        .num_layers = 2,
        .layers = [_]landlock_ruleset.Layer{
            .{ .level = 1, .access = 0x1 },
            .{ .level = 3, .access = 0x4 },
        } ++ ([_]landlock_ruleset.Layer{.{ .level = 0, .access = 0 }} ** (landlock_ruleset.max_num_layers - 2)),
    };

    const plan = try SyscallsHelperLab.planAddRule(.{
        .root_present = true,
        .search_key_data = 99,
        .walker_keys = &.{ 10, 99, 120 },
        .current_num_rules = 6,
        .existing_rule = existing,
        .incoming_layers = &.{.{ .level = 5, .access = 0x10 }},
    }, .{});

    try std.testing.expect(plan.search_plan.matched_existing_rule);
    try std.testing.expectEqual(landlock_ruleset.InsertRuleBranchMode.replace_existing_rule, plan.branch_plan.mode);
    try std.testing.expect(plan.branch_plan.link_plan == null);
    try std.testing.expect(plan.branch_plan.replacement_plan != null);
    try std.testing.expectEqual(@as(usize, 3), plan.branch_plan.resulting_rule.num_layers);
    try std.testing.expectEqual(@as(u32, 6), plan.branch_plan.resulting_num_rules);
}

test "landlock syscalls add-rule rejects missing ruleset fds before branch planning" {
    try std.testing.expectError(error.MissingRulesetFd, SyscallsHelperLab.planAddRule(.{
        .incoming_layers = &.{.{ .level = 0, .access = 0x1 }},
    }, .{ .ruleset_fd_present = false }));
}

test "landlock syscalls add-rule top-level wrapper keeps zero flags and write mode explicit" {
    const wrapper = try SyscallsHelperLab.planLandlockAddRule(.{
        .ruleset_fd_mode_bits = FMODE_CAN_READ | FMODE_CAN_WRITE,
        .input = .{
            .search_key_data = 41,
            .incoming_layers = &.{.{ .level = 0, .access = 0x8 }},
        },
    });

    try std.testing.expectEqualStrings(SyscallsHelperLab.descriptor().anchor, wrapper.anchor);
    try std.testing.expect(wrapper.checks_initialization_gate);
    try std.testing.expect(wrapper.checks_attr_presence_before_copy_from_user);
    try std.testing.expect(wrapper.requires_zero_flags);
    try std.testing.expect(wrapper.validates_ruleset_fd_write_mode);
    try std.testing.expectEqual(@as(u32, FMODE_CAN_WRITE), wrapper.required_ruleset_fd_mode_bits);
    try std.testing.expect(wrapper.reuses_add_rule_validation);
    try std.testing.expect(wrapper.add_rule_plan.performs_copy_from_user);
    try std.testing.expect(wrapper.add_rule_plan.reuses_ruleset_fd_lookup_planning);
    try std.testing.expect(wrapper.add_rule_plan.ruleset_fd_lookup_plan.validates_required_mode_bits);
    try std.testing.expectEqual(@as(?u32, FMODE_CAN_WRITE), wrapper.add_rule_plan.ruleset_fd_lookup_plan.required_mode_bits);
}

test "landlock syscalls add-rule top-level wrapper propagates missing ruleset_fops from ruleset lookup" {
    try std.testing.expectError(error.MissingRulesetFileOperations, SyscallsHelperLab.planLandlockAddRule(.{
        .ruleset_fd_mode_bits = FMODE_CAN_READ | FMODE_CAN_WRITE,
        .ruleset_fd = .{
            .ruleset_fops_present = false,
        },
        .input = .{
            .incoming_layers = &.{.{ .level = 0, .access = 0x8 }},
        },
    }));
}

test "landlock syscalls add-rule top-level wrapper rejects disabled boot missing attr nonzero flags and non-writable rulesets" {
    try std.testing.expectError(error.BootDisabled, SyscallsHelperLab.planLandlockAddRule(.{
        .initialized = false,
        .input = .{
            .incoming_layers = &.{.{ .level = 0, .access = 0x8 }},
        },
    }));
    try std.testing.expectError(error.BadUserPointer, SyscallsHelperLab.planLandlockAddRule(.{
        .attr_present = false,
        .input = .{
            .incoming_layers = &.{.{ .level = 0, .access = 0x8 }},
        },
    }));
    try std.testing.expectError(error.UnsupportedAddRuleFlags, SyscallsHelperLab.planLandlockAddRule(.{
        .flags = 1,
        .input = .{
            .incoming_layers = &.{.{ .level = 0, .access = 0x8 }},
        },
    }));
    try std.testing.expectError(error.InsufficientRulesetFdMode, SyscallsHelperLab.planLandlockAddRule(.{
        .ruleset_fd_mode_bits = FMODE_CAN_READ,
        .input = .{
            .incoming_layers = &.{.{ .level = 0, .access = 0x8 }},
        },
    }));
}

test "landlock syscalls ruleset fd install keeps anon inode label fops binding and failure release explicit" {
    const plan = try SyscallsHelperLab.planInstallRulesetFd(.{});

    try std.testing.expectEqualStrings(SyscallsHelperLab.descriptor().anchor, plan.anchor);
    try std.testing.expectEqualStrings("[landlock-ruleset]", plan.label);
    try std.testing.expect(plan.validates_label);
    try std.testing.expect(plan.validates_install_flags);
    try std.testing.expect(plan.validates_file_operations_binding);
    try std.testing.expect(plan.performs_anon_inode_getfd);
    try std.testing.expect(plan.returns_new_fd);
    try std.testing.expect(plan.releases_ruleset_on_fd_failure);
    try std.testing.expectEqual(@as(u32, O_RDWR | O_CLOEXEC), plan.install_flags);
}

test "landlock syscalls ruleset fd install rejects missing rulesets fops labels and flags" {
    try std.testing.expectError(error.MissingRuleset, SyscallsHelperLab.planInstallRulesetFd(.{
        .ruleset_present = false,
    }));
    try std.testing.expectError(error.MissingRulesetFileOperations, SyscallsHelperLab.planInstallRulesetFd(.{
        .ruleset_fops_present = false,
    }));
    try std.testing.expectError(error.InvalidAnonInodeLabel, SyscallsHelperLab.planInstallRulesetFd(.{
        .label = "[wrong-label]",
    }));
    try std.testing.expectError(error.UnsupportedAnonInodeFlags, SyscallsHelperLab.planInstallRulesetFd(.{
        .flags = O_RDWR,
    }));
}

test "landlock syscalls ruleset release keeps private-data handoff and zero return explicit" {
    const plan = try SyscallsHelperLab.planFopRulesetRelease(.{});

    try std.testing.expectEqualStrings(SyscallsHelperLab.descriptor().anchor, plan.anchor);
    try std.testing.expect(plan.reads_file_private_data);
    try std.testing.expect(plan.invokes_landlock_put_ruleset);
    try std.testing.expect(plan.returns_zero);
}

test "landlock syscalls ruleset release rejects missing file private-data or ruleset state" {
    try std.testing.expectError(error.MissingFile, SyscallsHelperLab.planFopRulesetRelease(.{
        .file_present = false,
    }));
    try std.testing.expectError(error.MissingRuleset, SyscallsHelperLab.planFopRulesetRelease(.{
        .private_data_present = false,
    }));
    try std.testing.expectError(error.MissingRuleset, SyscallsHelperLab.planFopRulesetRelease(.{
        .ruleset_present = false,
    }));
}

test "landlock syscalls ruleset fd stubs validate exact mode discipline" {
    const read_plan = try SyscallsHelperLab.planRulesetFdStub(.{
        .operation = .read,
        .mode_bits = FMODE_CAN_READ,
    });
    try std.testing.expectEqualStrings(SyscallsHelperLab.descriptor().anchor, read_plan.anchor);
    try std.testing.expectEqual(RulesetFdStubOperation.read, read_plan.operation);
    try std.testing.expect(read_plan.validates_mode_bits);
    try std.testing.expectEqual(@as(u32, FMODE_CAN_READ), read_plan.required_mode_bits);
    try std.testing.expect(read_plan.enables_read_mode);
    try std.testing.expect(!read_plan.enables_write_mode);
    try std.testing.expect(read_plan.returns_einval);
    try std.testing.expect(!read_plan.mutates_ruleset_state);

    const write_plan = try SyscallsHelperLab.planRulesetFdStub(.{
        .operation = .write,
        .mode_bits = FMODE_CAN_WRITE,
    });
    try std.testing.expectEqualStrings(SyscallsHelperLab.descriptor().anchor, write_plan.anchor);
    try std.testing.expectEqual(RulesetFdStubOperation.write, write_plan.operation);
    try std.testing.expect(write_plan.validates_mode_bits);
    try std.testing.expectEqual(@as(u32, FMODE_CAN_WRITE), write_plan.required_mode_bits);
    try std.testing.expect(!write_plan.enables_read_mode);
    try std.testing.expect(write_plan.enables_write_mode);
    try std.testing.expect(write_plan.returns_einval);
    try std.testing.expect(!write_plan.mutates_ruleset_state);
}

test "landlock syscalls ruleset fd stubs reject mismatched or combined mode bits" {
    try std.testing.expectError(error.UnsupportedRulesetFdMode, SyscallsHelperLab.planRulesetFdStub(.{
        .operation = .read,
        .mode_bits = FMODE_CAN_WRITE,
    }));
    try std.testing.expectError(error.UnsupportedRulesetFdMode, SyscallsHelperLab.planRulesetFdStub(.{
        .operation = .write,
        .mode_bits = FMODE_CAN_READ | FMODE_CAN_WRITE,
    }));
}
