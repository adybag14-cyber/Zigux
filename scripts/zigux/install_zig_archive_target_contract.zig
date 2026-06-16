const std = @import("std");
const install = @import("install_zig.zig");

test "policy archive digest lookup is target keyed" {
    const io = std.testing.io;
    const allocator = std.testing.allocator;
    const policy_root = ".zig-cache/tmp/zigux_install_zig_archive_target_contract";
    std.Io.Dir.cwd().deleteTree(io, policy_root) catch {};
    try std.Io.Dir.cwd().createDirPath(io, policy_root);
    defer std.Io.Dir.cwd().deleteTree(io, policy_root) catch {};
    const policy_path = try std.fmt.allocPrint(allocator, "{s}/policy.json", .{policy_root});
    defer allocator.free(policy_path);
    try std.Io.Dir.cwd().writeFile(io, .{ .sub_path = policy_path, .data = "{\"channel\":\"0.17.0-dev.877+a3ae499dc\",\"archive_sha256\":{\"x86_64-linux\":\"c1fd3190ab9e03ba2ec339aff9f1371780dc0727dacd0b0edb7ae6ba936501d8\"}}\n" });

    const digest = (try install.loadPolicyArchiveSha256(io, allocator, policy_path, "x86_64-linux")).?;
    defer allocator.free(digest);
    try std.testing.expectEqualStrings(digest, "c1fd3190ab9e03ba2ec339aff9f1371780dc0727dacd0b0edb7ae6ba936501d8");
    try std.testing.expect((try install.loadPolicyArchiveSha256(io, allocator, policy_path, "aarch64-linux")) == null);
}