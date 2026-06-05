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

test "confdata bridge CLI strips only the first-line UTF-8 BOM" {
    const allocator = std.testing.allocator;

    var tmp = std.testing.tmpDir(.{});
    defer tmp.cleanup();

    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = "sample.config",
        .data = "\xef\xbb\xbfCONFIG_BOOT=y\n" ++
            "CONFIG_VISIBLE=m\n" ++
            "\xef\xbb\xbfCONFIG_HIDDEN=y\n" ++
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
        "{\"counts\":{\"set\":2,\"unset\":1},\"entries\":[{\"name\":\"CONFIG_BOOT\",\"kind\":\"tristate\",\"value\":\"y\"},{\"name\":\"CONFIG_VISIBLE\",\"kind\":\"tristate\",\"value\":\"m\"},{\"name\":\"CONFIG_DEBUG\",\"kind\":\"unset\",\"value\":\"n\"}]}\n",
        result.stdout,
    );
    try std.testing.expect(std.mem.indexOf(u8, result.stdout, "CONFIG_HIDDEN") == null);
    try std.testing.expect(std.mem.indexOf(u8, result.stdout, "\xef\xbb\xbf") == null);
}
