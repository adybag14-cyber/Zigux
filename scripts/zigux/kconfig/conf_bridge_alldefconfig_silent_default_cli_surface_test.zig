const std = @import("std");

fn expectExitCode(result: std.process.RunResult, expected: u8) !void {
    switch (result.term) {
        .exited => |code| try std.testing.expectEqual(expected, code),
        else => return error.UnexpectedChildTermination,
    }
}

fn runBridge(args: []const []const u8) !std.process.RunResult {
    return std.process.run(std.testing.allocator, std.testing.io, .{ .argv = args });
}

test "standalone conf bridge alldefconfig silent default sentinel CLI" {
    const bridge_exe = ".zig-cache/tmp/conf_bridge_alldefconfig_silent_default_test";
    try std.Io.Dir.cwd().createDirPath(std.testing.io, ".zig-cache/tmp");

    const build = try runBridge(&.{
        "zig",
        "build-exe",
        "scripts/zigux/kconfig/conf_bridge.zig",
        "-femit-bin=.zig-cache/tmp/conf_bridge_alldefconfig_silent_default_test",
    });
    defer std.testing.allocator.free(build.stdout);
    defer std.testing.allocator.free(build.stderr);
    try expectExitCode(build, 0);
    try std.testing.expectEqualStrings("", build.stderr);

    const result = try runBridge(&.{
        bridge_exe,
        "alldefconfig",
        "Kconfig",
        "alldef/.config",
        "arm64",
        "silent",
    });
    defer std.testing.allocator.free(result.stdout);
    defer std.testing.allocator.free(result.stderr);

    try expectExitCode(result, 0);
    try std.testing.expectEqualStrings("", result.stderr);
    try std.testing.expect(std.mem.indexOf(u8, result.stdout, "\"mode\":\"alldefconfig\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, result.stdout, "\"argv\":[\"scripts/kconfig/conf\",\"--silent\",\"--alldefconfig\",\"Kconfig\"]") != null);
    try std.testing.expect(std.mem.indexOf(u8, result.stdout, "\"ARCH\":\"arm64\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, result.stdout, "\"KCONFIG_CONFIG\":\"alldef/.config\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, result.stdout, "\"KCONFIG_ALLCONFIG\":\"1\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, result.stdout, "\"KCONFIG_SEED\"") == null);
    try std.testing.expect(std.mem.indexOf(u8, result.stdout, "\"KCONFIG_PROBABILITY\"") == null);
    try std.testing.expect(std.mem.indexOf(u8, result.stdout, "\"KCONFIG_NOSILENTUPDATE\"") == null);
}
