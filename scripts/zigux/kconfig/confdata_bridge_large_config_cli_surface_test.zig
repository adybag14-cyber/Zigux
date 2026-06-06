const std = @import("std");

fn expectExitedZero(result: std.process.RunResult) !void {
    try std.testing.expectEqual(std.process.Child.Term{ .exited = 0 }, result.term);
    try std.testing.expectEqualStrings("", result.stderr);
}

fn runAndOwn(allocator: std.mem.Allocator, argv: []const []const u8, stdout_limit: usize) !std.process.RunResult {
    return std.process.run(allocator, std.testing.io, .{
        .argv = argv,
        .stdout_limit = .limited(stdout_limit),
        .stderr_limit = .limited(4096),
    });
}

test "confdata bridge CLI reads config inputs beyond one mebibyte" {
    const allocator = std.testing.allocator;

    var tmp = std.testing.tmpDir(.{});
    defer tmp.cleanup();

    const exe_path = try std.fmt.allocPrint(
        allocator,
        ".zig-cache/tmp/{s}/confdata_bridge_large_config_cli",
        .{tmp.sub_path[0..]},
    );
    defer allocator.free(exe_path);

    const config_path = try std.fmt.allocPrint(
        allocator,
        ".zig-cache/tmp/{s}/large-cli.config",
        .{tmp.sub_path[0..]},
    );
    defer allocator.free(config_path);

    const padding_len = (1024 * 1024) + 128;
    var config_text = try std.ArrayList(u8).initCapacity(allocator, padding_len + 96);
    defer config_text.deinit(allocator);
    try config_text.appendSlice(allocator, "CONFIG_BIG=value\n# ");
    try config_text.appendNTimes(allocator, 'a', padding_len);
    try config_text.appendSlice(allocator, "\nCONFIG_AFTER_BIG=m\n# CONFIG_DISABLED is not set\n");

    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = "large-cli.config",
        .data = config_text.items,
    });

    const emit_arg = try std.fmt.allocPrint(allocator, "-femit-bin={s}", .{exe_path});
    defer allocator.free(emit_arg);

    const build_result = try runAndOwn(allocator, &.{
        "zig",
        "build-exe",
        "scripts/zigux/kconfig/confdata_bridge.zig",
        emit_arg,
    }, 4096);
    defer {
        allocator.free(build_result.stdout);
        allocator.free(build_result.stderr);
    }
    try expectExitedZero(build_result);

    const run_result = try runAndOwn(allocator, &.{ exe_path, config_path }, 4096);
    defer {
        allocator.free(run_result.stdout);
        allocator.free(run_result.stderr);
    }
    try expectExitedZero(run_result);

    try std.testing.expect(config_text.items.len > 1024 * 1024);
    try std.testing.expect(std.mem.indexOf(u8, run_result.stdout, "\"counts\":{\"set\":2,\"unset\":1}") != null);
    try std.testing.expect(std.mem.indexOf(u8, run_result.stdout, "\"name\":\"CONFIG_BIG\",\"kind\":\"value\",\"value\":\"value\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, run_result.stdout, "\"name\":\"CONFIG_AFTER_BIG\",\"kind\":\"tristate\",\"value\":\"m\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, run_result.stdout, "\"name\":\"CONFIG_DISABLED\",\"kind\":\"unset\",\"value\":\"n\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, run_result.stdout, "\"aaaaaaaa") == null);
}
