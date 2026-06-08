const std = @import("std");

const bridge_exe = ".zig-cache/tmp/conf_bridge_olddefconfig_silent";

fn runProcess(argv: []const []const u8) !std.process.RunResult {
    return std.process.run(std.testing.allocator, std.testing.io, .{
        .argv = argv,
    });
}

test "olddefconfig silent CLI emits plain env surface" {
    try std.Io.Dir.cwd().createDirPath(std.testing.io, ".zig-cache/tmp");

    const build_result = try runProcess(&.{
        "zig",
        "build-exe",
        "scripts/zigux/kconfig/conf_bridge.zig",
        "-femit-bin=" ++ bridge_exe,
    });
    defer std.testing.allocator.free(build_result.stdout);
    defer std.testing.allocator.free(build_result.stderr);
    try std.testing.expectEqual(std.process.Child.Term{ .exited = 0 }, build_result.term);
    try std.testing.expectEqualStrings("", build_result.stderr);

    const run_result = try runProcess(&.{
        bridge_exe,
        "olddefconfig",
        "Kconfig",
        "olddef/.config",
        "riscv64",
        "silent",
    });
    defer std.testing.allocator.free(run_result.stdout);
    defer std.testing.allocator.free(run_result.stderr);

    try std.testing.expectEqual(std.process.Child.Term{ .exited = 0 }, run_result.term);
    try std.testing.expectEqualStrings("", run_result.stderr);
    try std.testing.expect(std.mem.indexOf(u8, run_result.stdout, "\"mode\":\"olddefconfig\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, run_result.stdout, "\"argv\":[\"scripts/kconfig/conf\",\"--silent\",\"--olddefconfig\",\"Kconfig\"]") != null);
    try std.testing.expect(std.mem.indexOf(u8, run_result.stdout, "\"ARCH\":\"riscv64\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, run_result.stdout, "\"KCONFIG_CONFIG\":\"olddef/.config\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, run_result.stdout, "KCONFIG_ALLCONFIG") == null);
    try std.testing.expect(std.mem.indexOf(u8, run_result.stdout, "KCONFIG_AUTOCONFIG") == null);
    try std.testing.expect(std.mem.indexOf(u8, run_result.stdout, "KCONFIG_SEED") == null);
    try std.testing.expect(std.mem.indexOf(u8, run_result.stdout, "KCONFIG_PROBABILITY") == null);
    try std.testing.expect(std.mem.indexOf(u8, run_result.stdout, "allconfig_fallbacks") == null);
}
