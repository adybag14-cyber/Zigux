const std = @import("std");

fn runAndCollect(allocator: std.mem.Allocator, argv: []const []const u8) !std.process.RunResult {
    return std.process.run(allocator, std.testing.io, .{
        .argv = argv,
        .stdout_limit = .limited(16 * 1024),
        .stderr_limit = .limited(16 * 1024),
    });
}

fn expectExited(result: std.process.RunResult, code: u8) !void {
    switch (result.term) {
        .exited => |actual| try std.testing.expectEqual(code, actual),
        else => try std.testing.expect(false),
    }
}

test "confdata bridge CLI preserves prior value after malformed quote" {
    const allocator = std.testing.allocator;

    var tmp = std.testing.tmpDir(.{});
    defer tmp.cleanup();

    const exe_path = try std.fmt.allocPrint(
        allocator,
        ".zig-cache/tmp/{s}/confdata-bridge",
        .{tmp.sub_path[0..]},
    );
    defer allocator.free(exe_path);

    const emit_arg = try std.fmt.allocPrint(allocator, "-femit-bin={s}", .{exe_path});
    defer allocator.free(emit_arg);

    const build_result = try runAndCollect(allocator, &.{
        "zig",
        "build-exe",
        "scripts/zigux/kconfig/confdata_bridge.zig",
        emit_arg,
    });
    defer allocator.free(build_result.stdout);
    defer allocator.free(build_result.stderr);
    try expectExited(build_result, 0);
    try std.testing.expectEqualStrings("", build_result.stderr);

    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = "malformed.config",
        .data =
        \\CONFIG_ALPHA="stable"
        \\CONFIG_ALPHA="broken
        \\
        ,
    });

    const config_path = try std.fmt.allocPrint(
        allocator,
        ".zig-cache/tmp/{s}/malformed.config",
        .{tmp.sub_path[0..]},
    );
    defer allocator.free(config_path);

    const run_result = try runAndCollect(allocator, &.{ exe_path, config_path });
    defer allocator.free(run_result.stdout);
    defer allocator.free(run_result.stderr);

    try expectExited(run_result, 0);
    try std.testing.expectEqualStrings("", run_result.stderr);
    try std.testing.expect(std.mem.indexOf(u8, run_result.stdout, "\"set\":1") != null);
    try std.testing.expect(std.mem.indexOf(u8, run_result.stdout, "\"unset\":0") != null);
    try std.testing.expect(std.mem.indexOf(u8, run_result.stdout, "\"name\":\"CONFIG_ALPHA\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, run_result.stdout, "\"kind\":\"string\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, run_result.stdout, "\"value\":\"stable\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, run_result.stdout, "broken") == null);
}
