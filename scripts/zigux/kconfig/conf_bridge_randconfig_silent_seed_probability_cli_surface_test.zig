const std = @import("std");

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectNotContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

fn expectCleanExit(result: std.process.RunResult) !void {
    try std.testing.expectEqualStrings("", result.stderr);
    switch (result.term) {
        .exited => |code| try std.testing.expectEqual(@as(u8, 0), code),
        else => return error.UnexpectedChildExit,
    }
}

test "conf bridge randconfig CLI preserves silent seed probability and explicit allconfig path" {
    var tmp = std.testing.tmpDir(.{});
    defer tmp.cleanup();

    const emitted_bin = try std.fmt.allocPrint(
        std.testing.allocator,
        ".zig-cache/tmp/{s}/conf_bridge_randconfig_cli",
        .{tmp.sub_path[0..]},
    );
    defer std.testing.allocator.free(emitted_bin);
    const emit_arg = try std.fmt.allocPrint(std.testing.allocator, "-femit-bin={s}", .{emitted_bin});
    defer std.testing.allocator.free(emit_arg);

    const build_result = try std.process.run(std.testing.allocator, std.testing.io, .{
        .argv = &.{
            "zig",
            "build-exe",
            "scripts/zigux/kconfig/conf_bridge.zig",
            emit_arg,
        },
    });
    defer std.testing.allocator.free(build_result.stdout);
    defer std.testing.allocator.free(build_result.stderr);
    try expectCleanExit(build_result);

    const run_result = try std.process.run(std.testing.allocator, std.testing.io, .{
        .argv = &.{
            emitted_bin,
            "randconfig",
            "Kconfig",
            "rand/.config",
            "x86_64",
            "silent",
            "allconfig=boards/x86/rand-mini.config",
            "seed=0xC0FFEE",
            "probability=15:25",
        },
    });
    defer std.testing.allocator.free(run_result.stdout);
    defer std.testing.allocator.free(run_result.stderr);
    try expectCleanExit(run_result);

    try expectContains(run_result.stdout, "\"mode\":\"randconfig\"");
    try expectContains(run_result.stdout, "\"argv\":[\"scripts/kconfig/conf\",\"--silent\",\"--randconfig\",\"Kconfig\"]");
    try expectContains(run_result.stdout, "\"ARCH\":\"x86_64\"");
    try expectContains(run_result.stdout, "\"KCONFIG_CONFIG\":\"rand/.config\"");
    try expectContains(run_result.stdout, "\"KCONFIG_ALLCONFIG\":\"boards/x86/rand-mini.config\"");
    try expectContains(run_result.stdout, "\"KCONFIG_SEED\":\"0xC0FFEE\"");
    try expectContains(run_result.stdout, "\"KCONFIG_PROBABILITY\":\"15:25\"");
    try expectNotContains(run_result.stdout, "\"KCONFIG_ALLCONFIG\":\"1\"");
    try expectNotContains(run_result.stdout, "\"allconfig_fallbacks\"");
}
