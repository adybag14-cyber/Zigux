const std = @import("std");

fn expectExitedZero(result: std.process.RunResult) !void {
    try std.testing.expectEqual(std.process.Child.Term{ .exited = 0 }, result.term);
    try std.testing.expectEqualStrings("", result.stderr);
}

fn runAndOwn(allocator: std.mem.Allocator, argv: []const []const u8) !std.process.RunResult {
    return std.process.run(allocator, std.testing.io, .{
        .argv = argv,
        .stdout_limit = .limited(4096),
        .stderr_limit = .limited(4096),
    });
}

test "confdata bridge explicit json CLI matches legacy config path output" {
    const allocator = std.testing.allocator;

    var tmp = std.testing.tmpDir(.{});
    defer tmp.cleanup();

    const exe_path = try std.fmt.allocPrint(
        allocator,
        ".zig-cache/tmp/{s}/confdata_bridge_json_cli",
        .{tmp.sub_path[0..]},
    );
    defer allocator.free(exe_path);

    const config_path = try std.fmt.allocPrint(
        allocator,
        ".zig-cache/tmp/{s}/json-cli.config",
        .{tmp.sub_path[0..]},
    );
    defer allocator.free(config_path);

    const config_text =
        \\CONFIG_ALPHA=y
        \\CONFIG_NAME="zigux\"json\\bridge"
        \\CONFIG_COUNT=7
        \\CONFIG_EMPTY=
        \\CONFIG_EXPLICIT_N=n
        \\# CONFIG_DEBUG is not set
        \\
    ;
    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = "json-cli.config",
        .data = config_text,
    });

    const emit_arg = try std.fmt.allocPrint(allocator, "-femit-bin={s}", .{exe_path});
    defer allocator.free(emit_arg);

    const build_result = try runAndOwn(allocator, &.{
        "zig",
        "build-exe",
        "scripts/zigux/kconfig/confdata_bridge.zig",
        emit_arg,
    });
    defer {
        allocator.free(build_result.stdout);
        allocator.free(build_result.stderr);
    }
    try expectExitedZero(build_result);

    const default_result = try runAndOwn(allocator, &.{ exe_path, config_path });
    defer {
        allocator.free(default_result.stdout);
        allocator.free(default_result.stderr);
    }
    try expectExitedZero(default_result);

    const explicit_json_result = try runAndOwn(allocator, &.{ exe_path, "json", config_path });
    defer {
        allocator.free(explicit_json_result.stdout);
        allocator.free(explicit_json_result.stderr);
    }
    try expectExitedZero(explicit_json_result);

    try std.testing.expectEqualStrings(default_result.stdout, explicit_json_result.stdout);
    try std.testing.expect(std.mem.indexOf(u8, explicit_json_result.stdout, "\"counts\":{\"set\":5,\"unset\":1}") != null);
    try std.testing.expect(std.mem.indexOf(u8, explicit_json_result.stdout, "\"name\":\"CONFIG_NAME\",\"kind\":\"string\",\"value\":\"zigux\\\"json\\\\bridge\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, explicit_json_result.stdout, "\"name\":\"CONFIG_EXPLICIT_N\",\"kind\":\"tristate\",\"value\":\"n\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, explicit_json_result.stdout, "\"name\":\"CONFIG_DEBUG\",\"kind\":\"unset\",\"value\":\"n\"") != null);
}
