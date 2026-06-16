const std = @import("std");
const install = @import("install_zig.zig");

test "resolve-only markers are part of the installer CLI surface" {
    _ = install.resolveTarget;
    _ = install.loadPolicyChannel;
    try std.testing.expectEqualStrings(install.fallback_channel, "master");
}

test "archive target override remains part of resolution metadata" {
    try std.testing.expectEqualStrings(install.default_toolchain_policy_rel, "scripts/zigux/zig-toolchain-policy.json");
}