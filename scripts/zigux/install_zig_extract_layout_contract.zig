const std = @import("std");
const install = @import("install_zig.zig");

test "extract layout helper is exported" {
    _ = install.extractArchive;
    try std.testing.expect(true);
}

test "bin directory resolution supports root and nested layouts" {
    const io = std.testing.io;
    const allocator = std.testing.allocator;
    const layout_root = ".zig-cache/tmp/zigux_install_zig_extract_layout_contract";
    std.Io.Dir.cwd().deleteTree(io, layout_root) catch {};
    try std.Io.Dir.cwd().createDirPath(io, layout_root);
    defer std.Io.Dir.cwd().deleteTree(io, layout_root) catch {};

    const root_layout = try std.fmt.allocPrint(allocator, "{s}/root-layout", .{layout_root});
    defer allocator.free(root_layout);
    try std.Io.Dir.cwd().createDirPath(io, root_layout);
    const zig_path = try std.fmt.allocPrint(allocator, "{s}/zig", .{root_layout});
    defer allocator.free(zig_path);
    try std.Io.Dir.cwd().writeFile(io, .{ .sub_path = zig_path, .data = "" });

    const bin_dir = try install.resolveBinDir(io, allocator, root_layout);
    defer allocator.free(bin_dir);
    try std.testing.expectEqualStrings(bin_dir, root_layout);
}