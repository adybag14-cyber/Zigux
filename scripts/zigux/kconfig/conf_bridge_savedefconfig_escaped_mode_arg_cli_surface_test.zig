const std = @import("std");

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectNotContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

fn expectExited(result: std.process.RunResult, code: u8) !void {
    try std.testing.expectEqual(std.process.Child.Term{ .exited = code }, result.term);
}

test "savedefconfig CLI JSON escapes accepted mode argument" {
    const allocator = std.testing.allocator;

    var tmp = std.testing.tmpDir(.{});
    defer tmp.cleanup();

    const binary_path = try std.fmt.allocPrint(
        allocator,
        ".zig-cache/tmp/{s}/conf_bridge_savedefconfig_escape",
        .{tmp.sub_path[0..]},
    );
    defer allocator.free(binary_path);

    const emit_arg = try std.fmt.allocPrint(allocator, "-femit-bin={s}", .{binary_path});
    defer allocator.free(emit_arg);

    const build = try std.process.run(allocator, std.testing.io, .{
        .argv = &.{
            "zig",
            "build-exe",
            "scripts/zigux/kconfig/conf_bridge.zig",
            emit_arg,
        },
    });
    defer allocator.free(build.stdout);
    defer allocator.free(build.stderr);

    try expectExited(build, 0);
    try std.testing.expectEqualStrings("", build.stderr);

    const mode_arg = "out/saved\"debug\\mini\tlane\nsavedefconfig";
    const run = try std.process.run(allocator, std.testing.io, .{
        .argv = &.{
            binary_path,
            "savedefconfig",
            "Kconfig",
            "out/.config",
            "x86_64",
            mode_arg,
            "silent",
        },
    });
    defer allocator.free(run.stdout);
    defer allocator.free(run.stderr);

    try expectExited(run, 0);
    try std.testing.expectEqualStrings("", run.stderr);
    try expectContains(run.stdout, "\"tool\":\"scripts/kconfig/conf\"");
    try expectContains(run.stdout, "\"mode\":\"savedefconfig\"");
    try expectContains(
        run.stdout,
        "\"argv\":[\"scripts/kconfig/conf\",\"--silent\",\"--savedefconfig\",\"out/saved\\\"debug\\\\mini\\tlane\\nsavedefconfig\",\"Kconfig\"]",
    );
    try expectContains(run.stdout, "\"ARCH\":\"x86_64\"");
    try expectContains(run.stdout, "\"KCONFIG_CONFIG\":\"out/.config\"");
    try expectNotContains(run.stdout, "\"KCONFIG_ALLCONFIG\"");
    try expectNotContains(run.stdout, "out/saved\"debug");
}
