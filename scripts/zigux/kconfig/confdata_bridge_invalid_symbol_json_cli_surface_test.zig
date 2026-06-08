const std = @import("std");

fn buildBridgeExecutable(allocator: std.mem.Allocator, exe_path: []const u8) !void {
    try std.Io.Dir.cwd().createDirPath(std.testing.io, ".zig-cache/tmp");
    const emit_arg = try std.fmt.allocPrint(allocator, "-femit-bin={s}", .{exe_path});
    defer allocator.free(emit_arg);

    const result = try std.process.run(allocator, std.testing.io, .{
        .argv = &.{
            "zig",
            "build-exe",
            "scripts/zigux/kconfig/confdata_bridge.zig",
            emit_arg,
        },
    });
    defer allocator.free(result.stdout);
    defer allocator.free(result.stderr);

    try std.testing.expectEqual(std.process.Child.Term{ .exited = 0 }, result.term);
    try std.testing.expectEqualStrings("", result.stderr);
}

fn runBridge(allocator: std.mem.Allocator, exe_path: []const u8, config_path: []const u8) !std.process.RunResult {
    return std.process.run(allocator, std.testing.io, .{
        .argv = &.{ exe_path, config_path },
    });
}

test "confdata bridge JSON CLI ignores invalid CONFIG symbol names" {
    const allocator = std.testing.allocator;

    var tmp = std.testing.tmpDir(.{});
    defer tmp.cleanup();

    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = "invalid-symbols.config",
        .data = "CONFIG_ALPHA=y\n" ++
            "CONFIG_=m\n" ++
            "CONFIG_BAD-DASH=y\n" ++
            "CONFIG.BAD=m\n" ++
            "NOT_CONFIG=y\n" ++
            "# CONFIG_DEBUG is not set\n" ++
            "CONFIG_WORD=yes\n",
    });

    const config_path = try std.fmt.allocPrint(
        allocator,
        ".zig-cache/tmp/{s}/invalid-symbols.config",
        .{tmp.sub_path[0..]},
    );
    defer allocator.free(config_path);

    const exe_path = try std.fmt.allocPrint(
        allocator,
        ".zig-cache/tmp/{s}/confdata_bridge_invalid_symbol_cli",
        .{tmp.sub_path[0..]},
    );
    defer allocator.free(exe_path);

    try buildBridgeExecutable(allocator, exe_path);

    const result = try runBridge(allocator, exe_path, config_path);
    defer allocator.free(result.stdout);
    defer allocator.free(result.stderr);

    try std.testing.expectEqual(std.process.Child.Term{ .exited = 0 }, result.term);
    try std.testing.expectEqualStrings("", result.stderr);
    try std.testing.expect(std.mem.endsWith(u8, result.stdout, "\n"));
    try std.testing.expect(std.mem.indexOf(u8, result.stdout, "\"counts\":{\"set\":2,\"unset\":1}") != null);
    try std.testing.expect(std.mem.indexOf(u8, result.stdout, "\"name\":\"CONFIG_ALPHA\",\"kind\":\"tristate\",\"value\":\"y\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, result.stdout, "\"name\":\"CONFIG_DEBUG\",\"kind\":\"unset\",\"value\":\"n\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, result.stdout, "\"name\":\"CONFIG_WORD\",\"kind\":\"value\",\"value\":\"yes\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, result.stdout, "CONFIG_\\\"") == null);
    try std.testing.expect(std.mem.indexOf(u8, result.stdout, "CONFIG_BAD-DASH") == null);
    try std.testing.expect(std.mem.indexOf(u8, result.stdout, "CONFIG.BAD") == null);
    try std.testing.expect(std.mem.indexOf(u8, result.stdout, "NOT_CONFIG") == null);
}
