const std = @import("std");
const landlock_ruleset = @import("ruleset.zig");

pub const LANDLOCK_CREATE_RULESET_VERSION: u32 = 1 << 0;

pub const ModuleDescriptor = struct {
    name: []const u8,
    anchor: []const u8,
    provides_create_ruleset_planning: bool,
    provides_abi_version_query_planning: bool,
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

pub const SyscallsHelperLab = struct {
    pub fn descriptor() ModuleDescriptor {
        return .{
            .name = "landlock_syscalls_helper_lab",
            .anchor = "security/landlock/syscalls.c",
            .provides_create_ruleset_planning = true,
            .provides_abi_version_query_planning = true,
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
};

test "landlock syscalls descriptor stays within create-ruleset planning boundaries" {
    const descriptor = SyscallsHelperLab.descriptor();

    try std.testing.expectEqualStrings("landlock_syscalls_helper_lab", descriptor.name);
    try std.testing.expectEqualStrings("security/landlock/syscalls.c", descriptor.anchor);
    try std.testing.expect(descriptor.provides_create_ruleset_planning);
    try std.testing.expect(descriptor.provides_abi_version_query_planning);
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
