const std = @import("std");

const bridge_source = "scripts/zigux/kconfig/conf_bridge.zig";

fn buildBridge(allocator: std.mem.Allocator, tmp_dir: std.testing.TmpDir) ![]u8 {
    const exe_path = try std.fmt.allocPrint(allocator, ".zig-cache/tmp/{s}/conf_bridge_bin", .{tmp_dir.sub_path});
    errdefer allocator.free(exe_path);

    const emit_arg = try std.fmt.allocPrint(allocator, "-femit-bin={s}", .{exe_path});
    defer allocator.free(emit_arg);

    const result = try std.process.run(allocator, std.testing.io, .{
        .argv = &.{ "zig", "build-exe", bridge_source, emit_arg },
    });
    defer allocator.free(result.stdout);
    defer allocator.free(result.stderr);

    try std.testing.expectEqual(std.process.Child.Term{ .exited = 0 }, result.term);
    try std.testing.expectEqualStrings("", result.stderr);
    return exe_path;
}

fn runBridge(allocator: std.mem.Allocator, exe_path: []const u8, args: []const []const u8) !std.process.RunResult {
    var argv = try std.ArrayList([]const u8).initCapacity(allocator, args.len + 1);
    defer argv.deinit(allocator);

    try argv.append(allocator, exe_path);
    try argv.appendSlice(allocator, args);

    return std.process.run(allocator, std.testing.io, .{
        .argv = argv.items,
    });
}

test "allmodconfig CLI keeps explicit allconfig path out of fallback search" {
    const allocator = std.testing.allocator;
    var tmp_dir = std.testing.tmpDir(.{});
    defer tmp_dir.cleanup();

    const exe_path = try buildBridge(allocator, tmp_dir);
    defer allocator.free(exe_path);

    const result = try runBridge(allocator, exe_path, &.{
        "allmodconfig",
        "Kconfig",
        "out/mod/.config",
        "arm64",
        "allconfig=arch/arm64/configs/tiny-mod.config",
    });
    defer allocator.free(result.stdout);
    defer allocator.free(result.stderr);

    try std.testing.expectEqual(std.process.Child.Term{ .exited = 0 }, result.term);
    try std.testing.expectEqualStrings("", result.stderr);
    try std.testing.expect(std.mem.indexOf(u8, result.stdout, "\"mode\":\"allmodconfig\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, result.stdout, "\"--allmodconfig\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, result.stdout, "\"ARCH\":\"arm64\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, result.stdout, "\"KCONFIG_CONFIG\":\"out/mod/.config\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, result.stdout, "\"KCONFIG_ALLCONFIG\":\"arch/arm64/configs/tiny-mod.config\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, result.stdout, "\"KCONFIG_ALLCONFIG\":\"1\"") == null);
    try std.testing.expect(std.mem.indexOf(u8, result.stdout, "\"allconfig_fallbacks\"") == null);
}
