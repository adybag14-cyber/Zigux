const std = @import("std");

const bridge_source = "scripts/zigux/kconfig/confdata_bridge.zig";

fn tmpPath(allocator: std.mem.Allocator, tmp_sub_path: []const u8, leaf: []const u8) ![]u8 {
    return std.fmt.allocPrint(
        allocator,
        ".zig-cache/tmp/{s}/{s}",
        .{ tmp_sub_path, leaf },
    );
}

fn buildBridgeExe(allocator: std.mem.Allocator, tmp_sub_path: []const u8) ![]u8 {
    const exe_path = try tmpPath(allocator, tmp_sub_path, "confdata_bridge_test_exe");
    errdefer allocator.free(exe_path);

    const emit_arg = try std.fmt.allocPrint(allocator, "-femit-bin={s}", .{exe_path});
    defer allocator.free(emit_arg);

    const result = try std.process.run(allocator, std.testing.io, .{
        .argv = &.{ "zig", "build-exe", bridge_source, emit_arg },
        .stderr_limit = .limited(32 * 1024),
        .stdout_limit = .limited(32 * 1024),
    });
    defer allocator.free(result.stdout);
    defer allocator.free(result.stderr);

    try std.testing.expectEqual(std.process.Child.Term{ .exited = 0 }, result.term);
    try std.testing.expectEqualStrings("", result.stdout);
    try std.testing.expectEqualStrings("", result.stderr);

    return exe_path;
}

test "confdata bridge CLI keeps final state across set unset transitions" {
    var tmp = std.testing.tmpDir(.{});
    defer tmp.cleanup();

    const config_text =
        \\# CONFIG_ALPHA is not set
        \\CONFIG_ALPHA="enabled"
        \\CONFIG_BETA=m
        \\# CONFIG_BETA is not set
        \\CONFIG_BETA=7
        \\# CONFIG_GAMMA is not set
        \\
    ;

    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = "transition.config",
        .data = config_text,
    });

    const allocator = std.testing.allocator;
    const config_path = try tmpPath(allocator, tmp.sub_path[0..], "transition.config");
    defer allocator.free(config_path);

    const exe_path = try buildBridgeExe(allocator, tmp.sub_path[0..]);
    defer allocator.free(exe_path);

    const result = try std.process.run(allocator, std.testing.io, .{
        .argv = &.{ exe_path, config_path },
        .stderr_limit = .limited(32 * 1024),
        .stdout_limit = .limited(32 * 1024),
    });
    defer allocator.free(result.stdout);
    defer allocator.free(result.stderr);

    try std.testing.expectEqual(std.process.Child.Term{ .exited = 0 }, result.term);
    try std.testing.expectEqualStrings("", result.stderr);
    try std.testing.expectEqualStrings(
        "{\"counts\":{\"set\":2,\"unset\":1},\"entries\":[{\"name\":\"CONFIG_ALPHA\",\"kind\":\"string\",\"value\":\"enabled\"},{\"name\":\"CONFIG_BETA\",\"kind\":\"value\",\"value\":\"7\"},{\"name\":\"CONFIG_GAMMA\",\"kind\":\"unset\",\"value\":\"n\"}]}\n",
        result.stdout,
    );
    try std.testing.expect(std.mem.indexOf(u8, result.stdout, "\"value\":\"m\"") == null);
    try std.testing.expect(std.mem.indexOf(u8, result.stdout, "\"CONFIG_ALPHA\",\"kind\":\"unset\"") == null);
}
