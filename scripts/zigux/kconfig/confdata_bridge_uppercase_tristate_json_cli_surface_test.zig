const std = @import("std");

const bridge_source = "scripts/zigux/kconfig/confdata_bridge.zig";

fn runProcess(allocator: std.mem.Allocator, argv: []const []const u8) !std.process.RunResult {
    return std.process.run(allocator, std.testing.io, .{
        .argv = argv,
        .stdout_limit = .limited(16 * 1024),
        .stderr_limit = .limited(16 * 1024),
    });
}

fn expectExited(result: std.process.RunResult, code: u8) !void {
    try std.testing.expectEqual(std.process.Child.Term{ .exited = code }, result.term);
}

test "confdata bridge JSON CLI canonicalizes uppercase tristates and explicit n" {
    const allocator = std.testing.allocator;
    var tmp = std.testing.tmpDir(.{});
    defer tmp.cleanup();

    const exe_path = try std.fmt.allocPrint(allocator, ".zig-cache/tmp/{s}/confdata_bridge_uppercase_tristate", .{tmp.sub_path});
    defer allocator.free(exe_path);
    const emit_arg = try std.fmt.allocPrint(allocator, "-femit-bin={s}", .{exe_path});
    defer allocator.free(emit_arg);

    const build_result = try runProcess(allocator, &.{
        "zig",
        "build-exe",
        bridge_source,
        emit_arg,
    });
    defer allocator.free(build_result.stdout);
    defer allocator.free(build_result.stderr);
    try expectExited(build_result, 0);
    try std.testing.expectEqualStrings("", build_result.stderr);

    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = "sample.config",
        .data =
        \\CONFIG_ALPHA=Y
        \\CONFIG_BETA=M
        \\CONFIG_GAMMA=N
        \\CONFIG_COUNT=7
        \\# CONFIG_DELTA is not set
        \\
        ,
    });

    const config_path = try std.fmt.allocPrint(allocator, ".zig-cache/tmp/{s}/sample.config", .{tmp.sub_path});
    defer allocator.free(config_path);

    const result = try runProcess(allocator, &.{
        exe_path,
        config_path,
    });
    defer allocator.free(result.stdout);
    defer allocator.free(result.stderr);

    try expectExited(result, 0);
    try std.testing.expectEqualStrings("", result.stderr);
    try std.testing.expect(std.mem.indexOf(u8, result.stdout, "\"set\":4") != null);
    try std.testing.expect(std.mem.indexOf(u8, result.stdout, "\"unset\":1") != null);
    try std.testing.expect(std.mem.indexOf(u8, result.stdout, "\"name\":\"CONFIG_ALPHA\",\"kind\":\"tristate\",\"value\":\"y\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, result.stdout, "\"name\":\"CONFIG_BETA\",\"kind\":\"tristate\",\"value\":\"m\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, result.stdout, "\"name\":\"CONFIG_GAMMA\",\"kind\":\"tristate\",\"value\":\"n\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, result.stdout, "\"name\":\"CONFIG_COUNT\",\"kind\":\"value\",\"value\":\"7\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, result.stdout, "\"name\":\"CONFIG_DELTA\",\"kind\":\"unset\",\"value\":\"n\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, result.stdout, "\"value\":\"Y\"") == null);
    try std.testing.expect(std.mem.indexOf(u8, result.stdout, "\"value\":\"M\"") == null);
    try std.testing.expect(std.mem.indexOf(u8, result.stdout, "\"value\":\"N\"") == null);
}
