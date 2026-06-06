const std = @import("std");

fn buildConfBridge(allocator: std.mem.Allocator) !void {
    const result = try std.process.run(allocator, std.testing.io, .{
        .argv = &.{
            "zig",
            "build-exe",
            "scripts/zigux/kconfig/conf_bridge.zig",
            "-femit-bin=./conf_bridge_mode_arg_guard_test_bin",
            "--cache-dir",
            ".zig-cache-lane20-mode-arg-guard-build",
            "--global-cache-dir",
            ".zig-cache-lane20-mode-arg-guard-build/global",
        },
    });
    defer allocator.free(result.stdout);
    defer allocator.free(result.stderr);

    try std.testing.expectEqual(std.process.Child.Term{ .exited = 0 }, result.term);
    try std.testing.expectEqualStrings("", result.stderr);
}

fn expectMissingModeArg(bin_path: []const u8, mode: []const u8, bridge_like_arg: []const u8, expected_stderr: []const u8) !void {
    const allocator = std.testing.allocator;
    const result = try std.process.run(allocator, std.testing.io, .{
        .argv = &.{ bin_path, mode, "Kconfig", "build/.config", "x86_64", bridge_like_arg },
    });
    defer allocator.free(result.stdout);
    defer allocator.free(result.stderr);

    try std.testing.expectEqual(std.process.Child.Term{ .exited = 1 }, result.term);
    try std.testing.expectEqualStrings("", result.stdout);
    try std.testing.expectEqualStrings(expected_stderr, result.stderr);
}

test "required mode args reject bridge-option-looking values at CLI boundary" {
    const allocator = std.testing.allocator;
    const bin_path = "./conf_bridge_mode_arg_guard_test_bin";
    defer std.Io.Dir.cwd().deleteFile(std.testing.io, "conf_bridge_mode_arg_guard_test_bin") catch {};

    try buildConfBridge(allocator);

    const cases = [_]struct {
        mode: []const u8,
        arg: []const u8,
        stderr: []const u8,
    }{
        .{ .mode = "defconfig", .arg = "silent", .stderr = "Error: defconfig mode requires <defconfig>\n" },
        .{ .mode = "defconfig", .arg = "allconfig=boards/min.config", .stderr = "Error: defconfig mode requires <defconfig>\n" },
        .{ .mode = "defconfig", .arg = "seed=0x5eed", .stderr = "Error: defconfig mode requires <defconfig>\n" },
        .{ .mode = "defconfig", .arg = "probability=10:20", .stderr = "Error: defconfig mode requires <defconfig>\n" },
        .{ .mode = "savedefconfig", .arg = "nosilentupdate=1", .stderr = "Error: savedefconfig mode requires <path>\n" },
        .{ .mode = "savedefconfig", .arg = "allconfig=", .stderr = "Error: savedefconfig mode requires <path>\n" },
    };

    for (cases) |case| {
        try expectMissingModeArg(bin_path, case.mode, case.arg, case.stderr);
    }
}
