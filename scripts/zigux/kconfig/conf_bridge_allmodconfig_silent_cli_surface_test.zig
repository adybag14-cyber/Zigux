const std = @import("std");

fn buildBridgeExecutable(allocator: std.mem.Allocator) ![]const u8 {
    try std.Io.Dir.cwd().createDirPath(std.testing.io, ".zig-cache/tmp/lane20-allmodconfig-silent");
    const exe_path = ".zig-cache/tmp/lane20-allmodconfig-silent/conf_bridge";
    const args = [_][]const u8{
        "zig",
        "build-exe",
        "scripts/zigux/kconfig/conf_bridge.zig",
        "-femit-bin=.zig-cache/tmp/lane20-allmodconfig-silent/conf_bridge",
    };
    const result = try std.process.run(allocator, std.testing.io, .{ .argv = &args });
    defer allocator.free(result.stdout);
    defer allocator.free(result.stderr);

    try std.testing.expectEqual(std.process.Child.Term{ .exited = 0 }, result.term);
    try std.testing.expectEqualStrings("", result.stderr);
    return exe_path;
}

test "allmodconfig silent CLI emits no implicit allconfig fallback" {
    const allocator = std.testing.allocator;
    const exe_path = try buildBridgeExecutable(allocator);
    const args = [_][]const u8{
        exe_path,
        "allmodconfig",
        "Kconfig",
        "mod/.config",
        "riscv64",
        "silent",
    };
    const result = try std.process.run(allocator, std.testing.io, .{ .argv = &args });
    defer allocator.free(result.stdout);
    defer allocator.free(result.stderr);

    try std.testing.expectEqual(std.process.Child.Term{ .exited = 0 }, result.term);
    try std.testing.expectEqualStrings("", result.stderr);
    try std.testing.expect(std.mem.indexOf(u8, result.stdout, "\"mode\":\"allmodconfig\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, result.stdout, "\"argv\":[\"scripts/kconfig/conf\",\"--silent\",\"--allmodconfig\",\"Kconfig\"]") != null);
    try std.testing.expect(std.mem.indexOf(u8, result.stdout, "\"ARCH\":\"riscv64\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, result.stdout, "\"KCONFIG_CONFIG\":\"mod/.config\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, result.stdout, "\"KCONFIG_ALLCONFIG\"") == null);
    try std.testing.expect(std.mem.indexOf(u8, result.stdout, "\"allconfig_fallbacks\"") == null);
    try std.testing.expect(std.mem.indexOf(u8, result.stdout, "\"KCONFIG_AUTOCONFIG\"") == null);
    try std.testing.expect(std.mem.indexOf(u8, result.stdout, "\"KCONFIG_SEED\"") == null);
    try std.testing.expect(std.mem.endsWith(u8, result.stdout, "\n"));
}