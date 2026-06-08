const std = @import("std");

const usage_line = "Usage: conf_bridge <mode> <Kconfig> <.config> <arch> [mode-arg] [silent] [allconfig=<value>] [seed=<value>] [probability=<value>] [nosilentupdate=<value>]\n";
const exe_path = ".zig-cache/lane20-conf-bridge-usage-bin";

fn expectExit(result: std.process.RunResult, code: u8) !void {
    try std.testing.expectEqual(std.process.Child.Term{ .exited = code }, result.term);
}

fn runAndCheckUsage(allocator: std.mem.Allocator, argv: []const []const u8, stderr: []const u8) !void {
    const result = try std.process.run(allocator, std.testing.io, .{
        .argv = argv,
        .stdout_limit = .limited(1024),
        .stderr_limit = .limited(1024),
    });
    defer allocator.free(result.stdout);
    defer allocator.free(result.stderr);

    try expectExit(result, 1);
    try std.testing.expectEqualStrings("", result.stdout);
    try std.testing.expectEqualStrings(stderr, result.stderr);
}

test "conf bridge public CLI reports usage and mode errors" {
    const allocator = std.testing.allocator;

    const build = try std.process.run(allocator, std.testing.io, .{
        .argv = &.{
            "zig",
            "build-exe",
            "scripts/zigux/kconfig/conf_bridge.zig",
            "-femit-bin=" ++ exe_path,
            "--cache-dir",
            ".zig-cache/lane20-conf-bridge-usage-build",
            "--global-cache-dir",
            ".zig-cache/lane20-conf-bridge-usage-build/global",
        },
        .stdout_limit = .limited(1024),
        .stderr_limit = .limited(4096),
    });
    defer allocator.free(build.stdout);
    defer allocator.free(build.stderr);

    try expectExit(build, 0);
    try std.testing.expectEqualStrings("", build.stdout);
    try std.testing.expectEqualStrings("", build.stderr);

    try runAndCheckUsage(allocator, &.{exe_path}, usage_line);
    try runAndCheckUsage(allocator, &.{
        exe_path,
        "notamode",
        "Kconfig",
        ".config",
        "x86_64",
    }, "Error: unsupported kconfig mode\n");
    try runAndCheckUsage(allocator, &.{
        exe_path,
        "oldconfig",
        "Kconfig",
        ".config",
        "x86_64",
        "silent",
        "allconfig=mini.config",
        "seed=1",
        "probability=10",
        "nosilentupdate=1",
    }, usage_line);
}
