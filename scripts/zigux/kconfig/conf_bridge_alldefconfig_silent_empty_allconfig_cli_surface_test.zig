const std = @import("std");

test "alldefconfig silent empty allconfig CLI emits explicit override packet" {
    const allocator = std.testing.allocator;
    const exe_path = ".zig-cache/tmp/conf_bridge_alldefconfig_silent_empty_allconfig_cli_surface_test_bin";

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
            "alldefconfig",
            "Kconfig",
            "defs/.config",
            "riscv64",
            "silent",
            "allconfig=",
        },
    });
    defer allocator.free(run_result.stdout);
    defer allocator.free(run_result.stderr);

    try std.testing.expectEqual(std.process.Child.Term{ .exited = 0 }, run_result.term);
    try std.testing.expectEqualStrings("", run_result.stderr);
    try std.testing.expect(std.mem.indexOf(u8, run_result.stdout, "\"mode\":\"alldefconfig\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, run_result.stdout, "\"argv\":[\"scripts/kconfig/conf\",\"--silent\",\"--alldefconfig\",\"Kconfig\"]") != null);
    try std.testing.expect(std.mem.indexOf(u8, run_result.stdout, "\"ARCH\":\"riscv64\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, run_result.stdout, "\"KCONFIG_CONFIG\":\"defs/.config\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, run_result.stdout, "\"KCONFIG_ALLCONFIG\":\"\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, run_result.stdout, "\"KCONFIG_ALLCONFIG\":\"1\"") == null);
    try std.testing.expect(std.mem.indexOf(u8, run_result.stdout, "\"KCONFIG_AUTOCONFIG\"") == null);
    try std.testing.expect(std.mem.indexOf(u8, run_result.stdout, "\"KCONFIG_AUTOHEADER\"") == null);
    try std.testing.expect(std.mem.indexOf(u8, run_result.stdout, "\"KCONFIG_NOSILENTUPDATE\"") == null);
    try std.testing.expect(std.mem.indexOf(u8, run_result.stdout, "\"KCONFIG_SEED\"") == null);
    try std.testing.expect(std.mem.indexOf(u8, run_result.stdout, "\"KCONFIG_PROBABILITY\"") == null);
}
