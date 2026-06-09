const std = @import("std");

const allocator = std.testing.allocator;

fn run(argv: []const []const u8) !std.process.RunResult {
    return std.process.run(allocator, std.testing.io, .{ .argv = argv });
}

fn expectSuccess(result: std.process.RunResult) !void {
    try std.testing.expectEqual(std.process.Child.Term{ .exited = 0 }, result.term);
    try std.testing.expectEqualStrings("", result.stderr);
}

test "conf bridge syncconfig CLI combines silent and nosilentupdate env" {
    var tmp = std.testing.tmpDir(.{});
    defer tmp.cleanup();

    const exe_path = try std.fmt.allocPrint(
        allocator,
        ".zig-cache/tmp/{s}/conf_bridge_syncconfig_silent_nosilentupdate",
        .{tmp.sub_path[0..]},
    );
    defer allocator.free(exe_path);

    const emit_arg = try std.fmt.allocPrint(allocator, "-femit-bin={s}", .{exe_path});
    defer allocator.free(emit_arg);

    const build_result = try run(&.{
        "zig",
        "build-exe",
        "scripts/zigux/kconfig/conf_bridge.zig",
        emit_arg,
    });
    defer allocator.free(build_result.stdout);
    defer allocator.free(build_result.stderr);
    try expectSuccess(build_result);

    const result = try run(&.{
        exe_path,
        "syncconfig",
        "Kconfig",
        "out/.config",
        "x86_64",
        "silent",
        "nosilentupdate=1",
    });
    defer allocator.free(result.stdout);
    defer allocator.free(result.stderr);
    try expectSuccess(result);

    try std.testing.expect(std.mem.indexOf(u8, result.stdout, "\"argv\":[\"scripts/kconfig/conf\",\"--silent\",\"--syncconfig\",\"Kconfig\"]") != null);
    try std.testing.expect(std.mem.indexOf(u8, result.stdout, "\"mode\":\"syncconfig\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, result.stdout, "\"ARCH\":\"x86_64\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, result.stdout, "\"KCONFIG_CONFIG\":\"out/.config\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, result.stdout, "\"KCONFIG_AUTOCONFIG\":\"include/config/auto.conf\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, result.stdout, "\"KCONFIG_AUTOHEADER\":\"include/generated/autoconf.h\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, result.stdout, "\"KCONFIG_NOSILENTUPDATE\":\"1\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, result.stdout, "\"allconfig_fallbacks\"") == null);
    try std.testing.expect(std.mem.endsWith(u8, result.stdout, "}}\n"));
}
