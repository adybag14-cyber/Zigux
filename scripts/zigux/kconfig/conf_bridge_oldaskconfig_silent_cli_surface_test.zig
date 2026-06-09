const std = @import("std");

test "oldaskconfig silent CLI emits oldaskconfig packet" {
    const allocator = std.testing.allocator;
    const exe_path = ".zig-cache/tmp/conf_bridge_oldaskconfig_silent_cli_surface_test_bin";

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
            "oldaskconfig",
            "Kconfig",
            "old/.config",
            "x86_64",
            "silent",
        },
    });
    defer allocator.free(run_result.stdout);
    defer allocator.free(run_result.stderr);

    try std.testing.expectEqual(std.process.Child.Term{ .exited = 0 }, run_result.term);
    try std.testing.expectEqualStrings("", run_result.stderr);
    try std.testing.expect(std.mem.indexOf(u8, run_result.stdout, "\"mode\":\"oldaskconfig\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, run_result.stdout, "\"argv\":[\"scripts/kconfig/conf\",\"--silent\",\"--oldaskconfig\",\"Kconfig\"]") != null);
    try std.testing.expect(std.mem.indexOf(u8, run_result.stdout, "\"ARCH\":\"x86_64\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, run_result.stdout, "\"KCONFIG_CONFIG\":\"old/.config\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, run_result.stdout, "\"KCONFIG_ALLCONFIG\"") == null);
    try std.testing.expect(std.mem.indexOf(u8, run_result.stdout, "\"KCONFIG_AUTOCONFIG\"") == null);
    try std.testing.expect(std.mem.indexOf(u8, run_result.stdout, "\"KCONFIG_AUTOHEADER\"") == null);
    try std.testing.expect(std.mem.indexOf(u8, run_result.stdout, "\"KCONFIG_NOSILENTUPDATE\"") == null);
    try std.testing.expect(std.mem.indexOf(u8, run_result.stdout, "\"KCONFIG_SEED\"") == null);
    try std.testing.expect(std.mem.indexOf(u8, run_result.stdout, "\"KCONFIG_PROBABILITY\"") == null);
}
