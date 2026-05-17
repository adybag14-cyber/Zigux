const std = @import("std");
const landlock_ruleset = @import("ruleset.zig");

pub const LANDLOCK_CREATE_RULESET_VERSION: u32 = 1 << 0;
pub const O_RDWR: u32 = 0x2;
pub const O_CLOEXEC: u32 = 0x80000;

pub const ModuleDescriptor = struct {
    name: []const u8,
    anchor: []const u8,
    provides_create_ruleset_planning: bool,
    provides_abi_version_query_planning: bool,
    provides_ruleset_fd_install_planning: bool,
    provides_ruleset_fd_stub_planning: bool,
    validates_handled_access: bool,
    validates_attr_size: bool,
    validates_flags: bool,
    delegates_ruleset_creation_planning: bool,
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
    input: CreateRulesetInput = .{},
};

pub const CreateRulesetSyscallPlan = struct {
    anchor: []const u8,
    checks_initialization_gate: bool,
    checks_attr_presence_before_copy_from_user: bool,
    reuses_create_ruleset_validation: bool,
    create_ruleset_plan: CreateRulesetPlan,
};

pub const RulesetFdInstallRequest = struct {
    label: []const u8 = "[landlock-ruleset]",
    flags: u32 = O_RDWR | O_CLOEXEC,
    ruleset_present: bool = true,
};

pub const RulesetFdInstallPlan = struct {
    anchor: []const u8,
    label: []const u8,
    validates_label: bool,
    validates_install_flags: bool,
    performs_anon_inode_getfd: bool,
    returns_new_fd: bool,
    releases_ruleset_on_fd_failure: bool,
    install_flags: u32,
};

pub const RulesetFdStubOperation = enum {
    read,
    write,
};

pub const RulesetFdStubPlan = struct {
    anchor: []const u8,
    operation: RulesetFdStubOperation,
    enables_read_mode: bool,
    enables_write_mode: bool,
    returns_einval: bool,
    mutates_ruleset_state: bool,
};

pub const SyscallsHelperLab = struct {
    pub fn descriptor() ModuleDescriptor {
        return .{
            .name = "landlock_syscalls_helper_lab",
            .anchor = "security/landlock/syscalls.c",
            .provides_create_ruleset_planning = true,
            .provides_abi_version_query_planning = true,
            .provides_ruleset_fd_install_planning = true,
            .provides_ruleset_fd_stub_planning = true,
            .validates_handled_access = true,
            .validates_attr_size = true,
            .validates_flags = true,
            .delegates_ruleset_creation_planning = true,
            .touches_live_fd_installation = false,
            .touches_live_cred_replacement = false,
        };
    }

    pub fn planCreateRuleset(input: CreateRulesetInput) !CreateRulesetPlan {
        if ((input.flags & ~LANDLOCK_CREATE_RULESET_VERSION) != 0) {
            return error.UnsupportedCreateRulesetFlags;
        }

        if ((input.flags & LANDLOCK_CREATE_RULESET_VERSION) != 0) {
            if (input.attr_size != 0) {
                return error.UnexpectedAttrPayload;
            }
            if (input.attr.handled_access_fs != 0 or input.attr.handled_access_net != 0 or input.attr.scoped != 0) {
                return error.UnexpectedAttrPayload;
            }

            return .{
                .anchor = descriptor().anchor,
                .mode = .abi_version_query,
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
            .fs_access_mask = input.attr.handled_access_fs,
            .net_access_mask = input.attr.handled_access_net,
            .scope_mask = input.attr.scoped,
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
        if (create_ruleset_plan.mode == .create_handle and !request.attr_present) {
            return error.BadUserPointer;
        }

        return .{
            .anchor = descriptor().anchor,
            .checks_initialization_gate = true,
            .checks_attr_presence_before_copy_from_user = true,
            .reuses_create_ruleset_validation = true,
            .create_ruleset_plan = create_ruleset_plan,
        };
    }

    pub fn planInstallRulesetFd(request: RulesetFdInstallRequest) !RulesetFdInstallPlan {
        if (!request.ruleset_present) {
            return error.MissingRuleset;
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
            .performs_anon_inode_getfd = true,
            .returns_new_fd = true,
            .releases_ruleset_on_fd_failure = true,
            .install_flags = request.flags,
        };
    }

    pub fn planRulesetFdStub(operation: RulesetFdStubOperation) RulesetFdStubPlan {
        return switch (operation) {
            .read => .{
                .anchor = descriptor().anchor,
                .operation = .read,
                .enables_read_mode = true,
                .enables_write_mode = false,
                .returns_einval = true,
                .mutates_ruleset_state = false,
            },
            .write => .{
                .anchor = descriptor().anchor,
                .operation = .write,
                .enables_read_mode = false,
                .enables_write_mode = true,
                .returns_einval = true,
                .mutates_ruleset_state = false,
            },
        };
    }
};

test "landlock syscalls descriptor stays within create-ruleset planning boundaries" {
    const descriptor = SyscallsHelperLab.descriptor();

    try std.testing.expectEqualStrings("landlock_syscalls_helper_lab", descriptor.name);
    try std.testing.expectEqualStrings("security/landlock/syscalls.c", descriptor.anchor);
    try std.testing.expect(descriptor.provides_create_ruleset_planning);
    try std.testing.expect(descriptor.provides_abi_version_query_planning);
    try std.testing.expect(descriptor.provides_ruleset_fd_install_planning);
    try std.testing.expect(descriptor.provides_ruleset_fd_stub_planning);
    try std.testing.expect(descriptor.validates_handled_access);
    try std.testing.expect(descriptor.validates_attr_size);
    try std.testing.expect(descriptor.validates_flags);
    try std.testing.expect(descriptor.delegates_ruleset_creation_planning);
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

test "landlock syscalls version query rejects unexpected attr payload" {
    try std.testing.expectError(error.UnexpectedAttrPayload, SyscallsHelperLab.planCreateRuleset(.{
        .attr = .{ .handled_access_fs = 0x1 },
        .attr_size = @sizeOf(CreateRulesetAttr),
        .flags = LANDLOCK_CREATE_RULESET_VERSION,
    }));
}

test "landlock syscalls create-ruleset rejects undersized attr copies" {
    try std.testing.expectError(error.AttrTooSmall, SyscallsHelperLab.planCreateRuleset(.{
        .attr = .{ .handled_access_fs = 0x2 },
        .attr_size = @sizeOf(CreateRulesetAttr) - 1,
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
    try std.testing.expect(wrapper.checks_attr_presence_before_copy_from_user);
    try std.testing.expect(wrapper.reuses_create_ruleset_validation);
    try std.testing.expectEqual(CreateRulesetMode.abi_version_query, wrapper.create_ruleset_plan.mode);
    try std.testing.expect(!wrapper.create_ruleset_plan.performs_copy_from_user);
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

test "landlock syscalls ruleset fd install keeps anon inode label and failure release explicit" {
    const plan = try SyscallsHelperLab.planInstallRulesetFd(.{});

    try std.testing.expectEqualStrings(SyscallsHelperLab.descriptor().anchor, plan.anchor);
    try std.testing.expectEqualStrings("[landlock-ruleset]", plan.label);
    try std.testing.expect(plan.validates_label);
    try std.testing.expect(plan.validates_install_flags);
    try std.testing.expect(plan.performs_anon_inode_getfd);
    try std.testing.expect(plan.returns_new_fd);
    try std.testing.expect(plan.releases_ruleset_on_fd_failure);
    try std.testing.expectEqual(@as(u32, O_RDWR | O_CLOEXEC), plan.install_flags);
}

test "landlock syscalls ruleset fd install rejects missing rulesets labels and flags" {
    try std.testing.expectError(error.MissingRuleset, SyscallsHelperLab.planInstallRulesetFd(.{
        .ruleset_present = false,
    }));
    try std.testing.expectError(error.InvalidAnonInodeLabel, SyscallsHelperLab.planInstallRulesetFd(.{
        .label = "[wrong-label]",
    }));
    try std.testing.expectError(error.UnsupportedAnonInodeFlags, SyscallsHelperLab.planInstallRulesetFd(.{
        .flags = O_RDWR,
    }));
}

test "landlock syscalls ruleset fd stubs keep dummy operation discipline explicit" {
    const read_plan = SyscallsHelperLab.planRulesetFdStub(.read);
    try std.testing.expectEqualStrings(SyscallsHelperLab.descriptor().anchor, read_plan.anchor);
    try std.testing.expectEqual(RulesetFdStubOperation.read, read_plan.operation);
    try std.testing.expect(read_plan.enables_read_mode);
    try std.testing.expect(!read_plan.enables_write_mode);
    try std.testing.expect(read_plan.returns_einval);
    try std.testing.expect(!read_plan.mutates_ruleset_state);

    const write_plan = SyscallsHelperLab.planRulesetFdStub(.write);
    try std.testing.expectEqualStrings(SyscallsHelperLab.descriptor().anchor, write_plan.anchor);
    try std.testing.expectEqual(RulesetFdStubOperation.write, write_plan.operation);
    try std.testing.expect(!write_plan.enables_read_mode);
    try std.testing.expect(write_plan.enables_write_mode);
    try std.testing.expect(write_plan.returns_einval);
    try std.testing.expect(!write_plan.mutates_ruleset_state);
}
