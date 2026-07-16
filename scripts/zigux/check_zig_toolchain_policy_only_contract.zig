const std = @import("std");
const checker = @import("check_zig_toolchain.zig");
const policy = @import("toolchain_policy.zig");

test "policy-only summary keeps machine-readable phase route and pin fields" {
    const json = @embedFile("zig-toolchain-policy.json");
    var loaded = try policy.loadPolicyFromJson(std.testing.allocator, json);
    defer policy.freePolicy(std.testing.allocator, &loaded);

    try std.testing.expectEqualStrings("Phase 2", loaded.phase);
    try std.testing.expectEqualStrings("0.17.0-dev.1415+64dfaa568", loaded.channel);
    try std.testing.expectEqualStrings("0.17.0-dev.1415+64dfaa568", loaded.minimum_version);
    try std.testing.expect(loaded.upgrade_policy.channel_minimum_lockstep);
    try std.testing.expectEqual(@as(usize, 2), loaded.upgrade_policy.archive_target_scope.len);
    try std.testing.expectEqual(@as(usize, 7), loaded.upgrade_policy.required_make_routes.len);
    try std.testing.expectEqualStrings("x86_64-linux", loaded.upgrade_policy.archive_target_scope[0]);
    try std.testing.expectEqualStrings("x86_64-windows", loaded.upgrade_policy.archive_target_scope[1]);
}

test "policy-only CLI path validates policy before archive or zig probing" {
    try std.testing.expectEqualStrings("scripts/zigux/zig-toolchain-policy.json", checker.default_policy_path);
}

test "pinned Phase 2 policy names the complete toolchain route handoff" {
    const json = @embedFile("zig-toolchain-policy.json");
    try std.testing.expect(std.mem.indexOf(u8, json, "\"phase2-toolchain\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, json, "\"phase2-tools\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, json, "\"phase2-kconfig\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, json, "\"phase2-cross\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, json, "\"phase2-genksyms\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, json, "\"phase2-fixdep\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, json, "\"phase2-validate\"") != null);
}
