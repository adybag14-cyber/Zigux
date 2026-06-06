const std = @import("std");

const conf_bridge_source = "scripts/zigux/kconfig/conf_bridge.zig";
const conf_bridge_exe = ".zig-cache/tmp/conf_bridge_listnewconfig_silent_cli_surface_test_bin";

fn expectExitedZero(result: std.process.RunResult) !void {
    switch (result.term) {
        .exited => |code| try std.testing.expectEqual(@as(u8, 0), code),
        else => return error.ChildProcessDidNotExit,
    }
}

fn buildConfBridge(allocator: std.mem.Allocator) !void {
    try std.Io.Dir.cwd().createDirPath(std.testing.io, ".zig-cache/tmp");

    const emit_arg = "-femit-bin=" ++ conf_bridge_exe;
    const result = try std.process.run(allocator, std.testing.io, .{
        .argv = &.{ "zig", "build-exe", conf_bridge_source, emit_arg },
    });
    defer allocator.free(result.stdout);
    defer allocator.free(result.stderr);

    try expectExitedZero(result);
    try std.testing.expectEqual(@as(usize, 0), result.stderr.len);
}

test "listnewconfig silent CLI emits stable bridge packet" {
    const allocator = std.testing.allocator;
    try buildConfBridge(allocator);

    const result = try std.process.run(allocator, std.testing.io, .{
        .argv = &.{
            conf_bridge_exe,
            "listnewconfig",
            "Kconfig",
            "out/list/.config",
            "loongarch",
            "silent",
        },
    });
    defer allocator.free(result.stdout);
    defer allocator.free(result.stderr);

    try expectExitedZero(result);
    try std.testing.expectEqual(@as(usize, 0), result.stderr.len);
    try std.testing.expect(std.mem.indexOf(u8, result.stdout, "\"mode\":\"listnewconfig\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, result.stdout, "\"argv\":[\"scripts/kconfig/conf\",\"--silent\",\"--listnewconfig\",\"Kconfig\"]") != null);
    try std.testing.expect(std.mem.indexOf(u8, result.stdout, "\"ARCH\":\"loongarch\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, result.stdout, "\"KCONFIG_CONFIG\":\"out/list/.config\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, result.stdout, "\"KCONFIG_ALLCONFIG\"") == null);
    try std.testing.expect(std.mem.indexOf(u8, result.stdout, "\"KCONFIG_AUTOCONFIG\"") == null);
    try std.testing.expect(std.mem.indexOf(u8, result.stdout, "\"allconfig_fallbacks\"") == null);
}
