const std = @import("std");
const install = @import("install_zig.zig");

test "local archive copies into staged path" {
    const io = std.testing.io;
    const allocator = std.testing.allocator;
    const root = ".zig-cache/tmp/zigux_install_zig_local_stage_contract";
    std.Io.Dir.cwd().deleteTree(io, root) catch {};
    try std.Io.Dir.cwd().createDirPath(io, root);
    defer std.Io.Dir.cwd().deleteTree(io, root) catch {};

    const local_path = try std.fmt.allocPrint(allocator, "{s}/local.tar.xz", .{root});
    defer allocator.free(local_path);
    const staged_path = try std.fmt.allocPrint(allocator, "{s}/staged.tar.xz", .{root});
    defer allocator.free(staged_path);
    try std.Io.Dir.cwd().writeFile(io, .{ .sub_path = local_path, .data = "local-zig-archive" });

    const source = try install.stageArchive(io, local_path, "https://example.invalid/archive.tar.xz", staged_path, allocator);
    try std.testing.expect(source == .local_archive);
    const staged = try std.Io.Dir.cwd().readFileAlloc(io, staged_path, allocator, .unlimited);
    defer allocator.free(staged);
    try std.testing.expectEqualStrings(staged, "local-zig-archive");
}