const std = @import("std");
const install = @import("install_zig.zig");

test "policy channel rejects duplicate keys" {
    const io = std.testing.io;
    const allocator = std.testing.allocator;
    const policy_root = ".zig-cache/tmp/zigux_install_zig_policy_dup_contract";
    std.Io.Dir.cwd().deleteTree(io, policy_root) catch {};
    try std.Io.Dir.cwd().createDirPath(io, policy_root);
    defer std.Io.Dir.cwd().deleteTree(io, policy_root) catch {};

    const policy_path = try std.fmt.allocPrint(allocator, "{s}/policy.json", .{policy_root});
    defer allocator.free(policy_path);
    try std.Io.Dir.cwd().writeFile(io, .{ .sub_path = policy_path, .data = "{\"channel\":\"0.17.0-dev.877+a3ae499dc\",\"channel\":\"0.17.0-dev.90+abcdef\"}\n" });
    try std.testing.expectError(error.DuplicatePolicyKey, install.loadPolicyChannel(io, allocator, policy_path, "master"));
}

test "policy archive digest rejects duplicate targets" {
    const io = std.testing.io;
    const allocator = std.testing.allocator;
    const policy_root = ".zig-cache/tmp/zigux_install_zig_archive_dup_contract";
    std.Io.Dir.cwd().deleteTree(io, policy_root) catch {};
    try std.Io.Dir.cwd().createDirPath(io, policy_root);
    defer std.Io.Dir.cwd().deleteTree(io, policy_root) catch {};

    const policy_path = try std.fmt.allocPrint(allocator, "{s}/policy.json", .{policy_root});
    defer allocator.free(policy_path);
    try std.Io.Dir.cwd().writeFile(io, .{ .sub_path = policy_path, .data = "{\"channel\":\"0.17.0-dev.877+a3ae499dc\",\"archive_sha256\":{\"x86_64-linux\":\"c1fd3190ab9e03ba2ec339aff9f1371780dc0727dacd0b0edb7ae6ba936501d8\",\"x86_64-linux\":\"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\"}}\n" });
    try std.testing.expectError(error.DuplicatePolicyKey, install.loadPolicyArchiveSha256(io, allocator, policy_path, "x86_64-linux"));
}

test "invalid archive digest is rejected" {
    const io = std.testing.io;
    const allocator = std.testing.allocator;
    const policy_root = ".zig-cache/tmp/zigux_install_zig_archive_short_contract";
    std.Io.Dir.cwd().deleteTree(io, policy_root) catch {};
    try std.Io.Dir.cwd().createDirPath(io, policy_root);
    defer std.Io.Dir.cwd().deleteTree(io, policy_root) catch {};

    const policy_path = try std.fmt.allocPrint(allocator, "{s}/policy.json", .{policy_root});
    defer allocator.free(policy_path);
    try std.Io.Dir.cwd().writeFile(io, .{ .sub_path = policy_path, .data = "{\"channel\":\"0.17.0-dev.877+a3ae499dc\",\"archive_sha256\":{\"x86_64-linux\":\"short\"}}\n" });
    try std.testing.expectError(error.InvalidArchiveDigest, install.loadPolicyArchiveSha256(io, allocator, policy_path, "x86_64-linux"));
}