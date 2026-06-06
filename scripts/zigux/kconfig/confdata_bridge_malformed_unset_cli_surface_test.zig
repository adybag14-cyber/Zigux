const std = @import("std");

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectNotContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

fn buildConfdataBridge(allocator: std.mem.Allocator, tmp_sub_path: []const u8) ![]u8 {
    const exe_path = try std.fmt.allocPrint(
        allocator,
        ".zig-cache/tmp/{s}/confdata_bridge_malformed_unset",
        .{tmp_sub_path},
    );
    errdefer allocator.free(exe_path);

    const emit_arg = try std.fmt.allocPrint(allocator, "-femit-bin={s}", .{exe_path});
    defer allocator.free(emit_arg);

    const build_result = try std.process.run(allocator, std.testing.io, .{
        .argv = &.{
            "zig",
            "build-exe",
            "scripts/zigux/kconfig/confdata_bridge.zig",
            emit_arg,
        },
    });
    defer allocator.free(build_result.stdout);
    defer allocator.free(build_result.stderr);

    try std.testing.expectEqual(std.process.Child.Term{ .exited = 0 }, build_result.term);
    try std.testing.expectEqual(@as(usize, 0), build_result.stderr.len);

    return exe_path;
}

test "confdata bridge CLI ignores malformed unset comments with extra tokens" {
    var tmp = std.testing.tmpDir(.{});
    defer tmp.cleanup();

    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = "malformed-unset.config",
        .data = "CONFIG_ALPHA=y\n" ++
            "# CONFIG_ALPHA is not set today\n" ++
            "# CONFIG_BETA is not set\n" ++
            "CONFIG_GAMMA=\"stable\"\n" ++
            "# CONFIG_GAMMA is not set\t\n" ++
            "CONFIG_DELTA=7\n",
    });

    const allocator = std.testing.allocator;
    const exe_path = try buildConfdataBridge(allocator, tmp.sub_path[0..]);
    defer allocator.free(exe_path);

    const config_path = try std.fmt.allocPrint(
        allocator,
        ".zig-cache/tmp/{s}/malformed-unset.config",
        .{tmp.sub_path[0..]},
    );
    defer allocator.free(config_path);

    const run_result = try std.process.run(allocator, std.testing.io, .{
        .argv = &.{ exe_path, config_path },
    });
    defer allocator.free(run_result.stdout);
    defer allocator.free(run_result.stderr);

    try std.testing.expectEqual(std.process.Child.Term{ .exited = 0 }, run_result.term);
    try std.testing.expectEqual(@as(usize, 0), run_result.stderr.len);
    try expectContains(run_result.stdout, "\"counts\":{\"set\":3,\"unset\":1}");
    try expectContains(run_result.stdout, "\"name\":\"CONFIG_ALPHA\",\"kind\":\"tristate\",\"value\":\"y\"");
    try expectContains(run_result.stdout, "\"name\":\"CONFIG_BETA\",\"kind\":\"unset\",\"value\":\"n\"");
    try expectContains(run_result.stdout, "\"name\":\"CONFIG_GAMMA\",\"kind\":\"string\",\"value\":\"stable\"");
    try expectContains(run_result.stdout, "\"name\":\"CONFIG_DELTA\",\"kind\":\"value\",\"value\":\"7\"");
    try expectNotContains(run_result.stdout, "today");
    try expectNotContains(run_result.stdout, "\"counts\":{\"set\":2,\"unset\":2}");
}
