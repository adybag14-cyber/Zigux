const std = @import("std");

fn buildConfBridge(allocator: std.mem.Allocator, tmp_dir: []const u8) ![]u8 {
    const exe_path = try std.fs.path.join(allocator, &.{ tmp_dir, "conf_bridge_test_exe" });
    errdefer allocator.free(exe_path);

    const result = try std.process.run(allocator, std.testing.io, .{
        .argv = &.{
            "zig",
            "build-exe",
            "scripts/zigux/kconfig/conf_bridge.zig",
            "-femit-bin=zig-cache/conf_bridge_test_exe",
        },
        .stdout_limit = .limited(1024 * 1024),
        .stderr_limit = .limited(1024 * 1024),
    });
    defer allocator.free(result.stdout);
    defer allocator.free(result.stderr);

    try std.testing.expectEqual(std.process.Child.Term{ .exited = 0 }, result.term);
    try std.testing.expectEqualStrings("", result.stdout);

    return exe_path;
}

test "conf bridge syncconfig CLI omits empty nosilentupdate" {
    const allocator = std.testing.allocator;

    const tmp_dir = "zig-cache";
    try std.Io.Dir.cwd().createDirPath(std.testing.io, tmp_dir);

    const exe_path = try buildConfBridge(allocator, tmp_dir);
    defer allocator.free(exe_path);

    const result = try std.process.run(allocator, std.testing.io, .{
        .argv = &.{
            exe_path,
            "syncconfig",
            "Kconfig",
            "out/.config",
            "riscv64",
            "nosilentupdate=",
        },
        .stdout_limit = .limited(1024 * 1024),
        .stderr_limit = .limited(1024 * 1024),
    });
    defer allocator.free(result.stdout);
    defer allocator.free(result.stderr);

    try std.testing.expectEqual(std.process.Child.Term{ .exited = 0 }, result.term);
    try std.testing.expectEqualStrings("", result.stderr);
    try std.testing.expect(std.mem.indexOf(u8, result.stdout, "\"mode\":\"syncconfig\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, result.stdout, "\"--syncconfig\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, result.stdout, "\"KCONFIG_CONFIG\":\"out/.config\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, result.stdout, "\"ARCH\":\"riscv64\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, result.stdout, "\"KCONFIG_AUTOCONFIG\":\"include/config/auto.conf\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, result.stdout, "\"KCONFIG_AUTOHEADER\":\"include/generated/autoconf.h\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, result.stdout, "\"KCONFIG_NOSILENTUPDATE\"") == null);
}
