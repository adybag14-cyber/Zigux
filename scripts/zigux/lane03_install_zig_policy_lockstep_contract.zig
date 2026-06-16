const std = @import("std");
const install = @import("install_zig.zig");
const policy_source = @embedFile("zig-toolchain-policy.json");

const canonical_channel = install.canonical_release_channel;
const canonical_target = "x86_64-linux";
const canonical_digest = "c1fd3190ab9e03ba2ec339aff9f1371780dc0727dacd0b0edb7ae6ba936501d8";

test "install-zig keeps the canonical release route pinned" {
    try std.testing.expectEqualStrings(install.default_canonical_release_repo, "adybag14-cyber/zig");
    try std.testing.expectEqualStrings(install.default_canonical_release_tag, "upstream-a3ae499dc297");
    try std.testing.expectEqualStrings(install.canonical_release_channel, canonical_channel);
}

test "installer policy helpers reject ambiguous policy data" {
    const io = std.testing.io;
    const allocator = std.testing.allocator;
    const policy_root = ".zig-cache/tmp/zigux_lane03_policy_lockstep";
    std.Io.Dir.cwd().deleteTree(io, policy_root) catch {};
    try std.Io.Dir.cwd().createDirPath(io, policy_root);
    defer std.Io.Dir.cwd().deleteTree(io, policy_root) catch {};
    const policy_path = try std.fmt.allocPrint(allocator, "{s}/policy.json", .{policy_root});
    defer allocator.free(policy_path);
    try std.Io.Dir.cwd().writeFile(io, .{ .sub_path = policy_path, .data = "{not-json}\n" });
    try std.testing.expectError(error.InvalidPolicyJson, install.loadPolicyChannel(io, allocator, policy_path, "master"));
}

test "toolchain policy stays lockstep with one trusted Linux archive target" {
    try std.testing.expect(std.mem.indexOf(u8, policy_source, "\"channel\": \"" ++ canonical_channel ++ "\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, policy_source, "\"minimum_version\": \"" ++ canonical_channel ++ "\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, policy_source, "\"" ++ canonical_target ++ "\": \"" ++ canonical_digest ++ "\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, policy_source, "\"channel_minimum_lockstep\": true") != null);
}