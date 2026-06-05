const std = @import("std");

fn repoRelativePath(allocator: std.mem.Allocator, comptime leaf: []const u8) ![]u8 {
    return std.fs.path.join(allocator, &.{ "scripts", "zigux", "kconfig", leaf });
}

fn tmpPath(allocator: std.mem.Allocator, tmp_sub_path: []const u8, leaf: []const u8) ![]u8 {
    return std.fs.path.join(allocator, &.{ ".zig-cache", "tmp", tmp_sub_path, leaf });
}

fn buildConfdataBridge(allocator: std.mem.Allocator, exe_path: []const u8) !void {
    const bridge_source = try repoRelativePath(allocator, "confdata_bridge.zig");
    defer allocator.free(bridge_source);

    const emit_arg = try std.fmt.allocPrint(allocator, "-femit-bin={s}", .{exe_path});
    defer allocator.free(emit_arg);

    const result = try std.process.run(allocator, std.testing.io, .{
        .argv = &.{ "zig", "build-exe", bridge_source, emit_arg },
    });
    defer allocator.free(result.stdout);
    defer allocator.free(result.stderr);

    try std.testing.expectEqual(std.process.Child.Term{ .exited = 0 }, result.term);
    try std.testing.expectEqualStrings("", result.stdout);
    try std.testing.expectEqualStrings("", result.stderr);
}

test "confdata bridge CLI truncates config lines at embedded NUL before JSON output" {
    const allocator = std.testing.allocator;

    var tmp = std.testing.tmpDir(.{});
    defer tmp.cleanup();

    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = "sample.config",
        .data = "CONFIG_ALPHA=y\x00CONFIG_SHADOW=m\n" ++
            "CONFIG_BETA=m\n" ++
            "CONFIG_TAIL=\"kept\"\x00CONFIG_TRAILER=y\n" ++
            "# CONFIG_DEBUG is not set\n",
    });

    const exe_path = try tmpPath(allocator, tmp.sub_path[0..], "confdata-bridge");
    defer allocator.free(exe_path);
    try buildConfdataBridge(allocator, exe_path);

    const config_path = try tmpPath(allocator, tmp.sub_path[0..], "sample.config");
    defer allocator.free(config_path);

    const result = try std.process.run(allocator, std.testing.io, .{
        .argv = &.{ exe_path, config_path },
    });
    defer allocator.free(result.stdout);
    defer allocator.free(result.stderr);

    try std.testing.expectEqual(std.process.Child.Term{ .exited = 0 }, result.term);
    try std.testing.expectEqualStrings("", result.stderr);
    try std.testing.expectEqualStrings(
        "{\"counts\":{\"set\":3,\"unset\":1},\"entries\":[{\"name\":\"CONFIG_ALPHA\",\"kind\":\"tristate\",\"value\":\"y\"},{\"name\":\"CONFIG_BETA\",\"kind\":\"tristate\",\"value\":\"m\"},{\"name\":\"CONFIG_TAIL\",\"kind\":\"string\",\"value\":\"kept\"},{\"name\":\"CONFIG_DEBUG\",\"kind\":\"unset\",\"value\":\"n\"}]}\n",
        result.stdout,
    );
    try std.testing.expect(std.mem.indexOf(u8, result.stdout, "CONFIG_SHADOW") == null);
    try std.testing.expect(std.mem.indexOf(u8, result.stdout, "CONFIG_TRAILER") == null);
    try std.testing.expect(std.mem.indexOfScalar(u8, result.stdout, 0) == null);
}
