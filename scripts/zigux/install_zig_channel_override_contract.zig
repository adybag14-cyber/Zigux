const std = @import("std");
const install = @import("install_zig.zig");

test "policy channel loader falls back when policy is missing" {
    const io = std.testing.io;
    const allocator = std.testing.allocator;
    const channel = try install.loadPolicyChannel(io, allocator, ".zig-cache/tmp/zigux-missing-policy.json", "0.15.0");
    defer allocator.free(channel);
    try std.testing.expectEqualStrings(channel, "0.15.0");
}

test "policy channel loader reads pinned channel when present" {
    const io = std.testing.io;
    const allocator = std.testing.allocator;
    const policy_root = ".zig-cache/tmp/zigux_install_zig_channel_override_contract";
    std.Io.Dir.cwd().deleteTree(io, policy_root) catch {};
    try std.Io.Dir.cwd().createDirPath(io, policy_root);
    defer std.Io.Dir.cwd().deleteTree(io, policy_root) catch {};
    const policy_path = try std.fmt.allocPrint(allocator, "{s}/policy.json", .{policy_root});
    defer allocator.free(policy_path);
    try std.Io.Dir.cwd().writeFile(io, .{ .sub_path = policy_path, .data = "{\"channel\":\"0.17.0-dev.877+a3ae499dc\"}\n" });
    const channel = try install.loadPolicyChannel(io, allocator, policy_path, "0.15.0");
    defer allocator.free(channel);
    try std.testing.expectEqualStrings(channel, install.canonical_release_channel);
}