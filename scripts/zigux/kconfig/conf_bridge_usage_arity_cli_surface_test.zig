const std = @import("std");

const usage =
    "Usage: conf_bridge <mode> <Kconfig> <.config> <arch> [mode-arg] [silent] [allconfig=<value>] [seed=<value>] [probability=<value>] [nosilentupdate=<value>]\n";

fn expectExited(term: std.process.Child.Term, expected_code: u8) !void {
    switch (term) {
        .exited => |code| try std.testing.expectEqual(expected_code, code),
        else => return error.UnexpectedChildTermination,
    }
}

fn runAndExpectUsage(exe_path: []const u8, argv: []const []const u8) !void {
    const allocator = std.testing.allocator;
    const result = try std.process.run(allocator, std.testing.io, .{
        .argv = argv,
        .stdout_limit = .limited(1024),
        .stderr_limit = .limited(1024),
    });
    defer allocator.free(result.stdout);
    defer allocator.free(result.stderr);

    try expectExited(result.term, 1);
    try std.testing.expectEqualStrings("", result.stdout);
    try std.testing.expectEqualStrings(usage, result.stderr);
    try std.testing.expectEqualStrings(exe_path, argv[0]);
}

test "conf bridge executable rejects arity outside supported CLI surface" {
    const allocator = std.testing.allocator;
    var tmp = std.testing.tmpDir(.{});
    defer tmp.cleanup();

    const exe_path = try std.fmt.allocPrint(
        allocator,
        ".zig-cache/tmp/{s}/conf_bridge_arity",
        .{tmp.sub_path[0..]},
    );
    defer allocator.free(exe_path);
    const emit_arg = try std.fmt.allocPrint(allocator, "-femit-bin={s}", .{exe_path});
    defer allocator.free(emit_arg);

    const build = try std.process.run(allocator, std.testing.io, .{
        .argv = &.{
            "zig",
            "build-exe",
            "scripts/zigux/kconfig/conf_bridge.zig",
            emit_arg,
        },
        .stdout_limit = .limited(2048),
        .stderr_limit = .limited(2048),
    });
    defer allocator.free(build.stdout);
    defer allocator.free(build.stderr);
    try expectExited(build.term, 0);
    try std.testing.expectEqualStrings("", build.stdout);
    try std.testing.expectEqualStrings("", build.stderr);

    try runAndExpectUsage(exe_path, &.{exe_path});
    try runAndExpectUsage(exe_path, &.{ exe_path, "olddefconfig", "Kconfig", ".config" });
    try runAndExpectUsage(exe_path, &.{
        exe_path,
        "randconfig",
        "Kconfig",
        ".config",
        "x86_64",
        "silent",
        "allconfig=allrandom.config",
        "seed=123",
        "probability=10",
        "nosilentupdate=1",
    });
}
