const std = @import("std");

test "allyesconfig silent default CLI emits sentinel packet" {
    const allocator = std.testing.allocator;
    const exe_path = ".zig-cache/tmp/conf_bridge_allyesconfig_silent_default_cli_surface_test_bin";

    try std.Io.Dir.cwd().createDirPath(std.testing.io, ".zig-cache/tmp");

    const build_result = try std.process.run(allocator, std.testing.io, .{
        .argv = &.{
            "zig",
            "build-exe",
            "scripts/zigux/kconfig/conf_bridge.zig",
            "-femit-bin=" ++ exe_path,
        },
    });
    defer allocator.free(build_result.stdout);
    defer allocator.free(build_result.stderr);

    try std.testing.expectEqual(std.process.Child.Term{ .exited = 0 }, build_result.term);
    try std.testing.expectEqualStrings("", build_result.stdout);
    try std.testing.expectEqualStrings("", build_result.stderr);

    const run_result = try std.process.run(allocator, std.testing.io, .{
        .argv = &.{
            exe_path,
            "allyesconfig",
            "Kconfig",
            "yes/.config",
            "arm64",
            "silent",
        },
    });
    defer allocator.free(run_result.stdout);
    defer allocator.free(run_result.stderr);

    try std.testing.expectEqual(std.process.Child.Term{ .exited = 0 }, run_result.term);
    try std.testing.expectEqualStrings("", run_result.stderr);
    try std.testing.expect(std.mem.indexOf(u8, run_result.stdout, "\"mode\":\"allyesconfig\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, run_result.stdout, "\"argv\":[\"scripts/kconfig/conf\",\"--silent\",\"--allyesconfig\",\"Kconfig\"]") != null);
    try std.testing.expect(std.mem.indexOf(u8, run_result.stdout, "\"ARCH\":\"arm64\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, run_result.stdout, "\"KCONFIG_CONFIG\":\"yes/.config\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, run_result.stdout, "\"KCONFIG_ALLCONFIG\":\"1\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, run_result.stdout, "\"KCONFIG_AUTOCONFIG\"") == null);
    try std.testing.expect(std.mem.indexOf(u8, run_result.stdout, "\"KCONFIG_AUTOHEADER\"") == null);
    try std.testing.expect(std.mem.indexOf(u8, run_result.stdout, "\"KCONFIG_NOSILENTUPDATE\"") == null);
    try std.testing.expect(std.mem.indexOf(u8, run_result.stdout, "\"KCONFIG_SEED\"") == null);
    try std.testing.expect(std.mem.indexOf(u8, run_result.stdout, "\"KCONFIG_PROBABILITY\"") == null);
}
