const std = @import("std");

fn runBridge(allocator: std.mem.Allocator, bridge_path: []const u8) !std.process.RunResult {
    return std.process.run(allocator, std.testing.io, .{
        .argv = &.{
            bridge_path,
            "mod2noconfig",
            "Kconfig",
            "demote/.config",
            "riscv64",
            "silent",
        },
    });
}

test "conf bridge executable emits mod2noconfig silent packet" {
    const allocator = std.testing.allocator;

    var tmp = std.testing.tmpDir(.{});
    defer tmp.cleanup();

    const bridge_path = try std.fmt.allocPrint(
        allocator,
        ".zig-cache/tmp/{s}/conf_bridge_test_bin",
        .{tmp.sub_path[0..]},
    );
    defer allocator.free(bridge_path);

    const emit_arg = try std.fmt.allocPrint(allocator, "-femit-bin={s}", .{bridge_path});
    defer allocator.free(emit_arg);

    const build_result = try std.process.run(allocator, std.testing.io, .{
        .argv = &.{
            "zig",
            "build-exe",
            "scripts/zigux/kconfig/conf_bridge.zig",
            emit_arg,
        },
    });
    defer allocator.free(build_result.stdout);
    defer allocator.free(build_result.stderr);

    try std.testing.expectEqual(std.process.Child.Term{ .exited = 0 }, build_result.term);
    try std.testing.expectEqualStrings("", build_result.stderr);

    const run_result = try runBridge(allocator, bridge_path);
    defer allocator.free(run_result.stdout);
    defer allocator.free(run_result.stderr);

    try std.testing.expectEqual(std.process.Child.Term{ .exited = 0 }, run_result.term);
    try std.testing.expectEqualStrings("", run_result.stderr);
    try std.testing.expect(std.mem.endsWith(u8, run_result.stdout, "\n"));

    try std.testing.expect(std.mem.indexOf(u8, run_result.stdout, "\"mode\":\"mod2noconfig\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, run_result.stdout, "\"argv\":[\"scripts/kconfig/conf\",\"--silent\",\"--mod2noconfig\",\"Kconfig\"]") != null);
    try std.testing.expect(std.mem.indexOf(u8, run_result.stdout, "\"ARCH\":\"riscv64\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, run_result.stdout, "\"KCONFIG_CONFIG\":\"demote/.config\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, run_result.stdout, "KCONFIG_ALLCONFIG") == null);
    try std.testing.expect(std.mem.indexOf(u8, run_result.stdout, "KCONFIG_AUTOCONFIG") == null);
    try std.testing.expect(std.mem.indexOf(u8, run_result.stdout, "KCONFIG_SEED") == null);
    try std.testing.expect(std.mem.indexOf(u8, run_result.stdout, "allconfig_fallbacks") == null);
}
