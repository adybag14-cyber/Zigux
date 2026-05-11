const std = @import("std");

pub const ModuleDescriptor = struct {
    name: []const u8,
    anchor: []const u8,
    provides_restrict_self_planning: bool,
    validates_ruleset_fd: bool,
    validates_restrict_self_flags: bool,
    validates_credential_gate: bool,
    touches_live_credentials: bool,
    touches_live_rulesets: bool,
};

pub const CredentialGate = enum {
    no_new_privs,
    cap_sys_admin_override,
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

pub const SyscallsHelperLab = struct {
    pub fn descriptor() ModuleDescriptor {
        return .{
            .name = "landlock_syscalls_helper_lab",
            .anchor = "security/landlock/syscalls.c",
            .provides_restrict_self_planning = true,
            .validates_ruleset_fd = true,
            .validates_restrict_self_flags = true,
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
};

test "landlock syscalls descriptor stays scoped to restrict-self planning" {
    const descriptor = SyscallsHelperLab.descriptor();

    try std.testing.expectEqualStrings("landlock_syscalls_helper_lab", descriptor.name);
    try std.testing.expectEqualStrings("security/landlock/syscalls.c", descriptor.anchor);
    try std.testing.expect(descriptor.provides_restrict_self_planning);
    try std.testing.expect(descriptor.validates_ruleset_fd);
    try std.testing.expect(descriptor.validates_restrict_self_flags);
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
