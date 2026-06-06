const std = @import("std");

fn run(allocator: std.mem.Allocator, argv: []const []const u8) !std.process.RunResult {
    return std.process.run(allocator, std.testing.io, .{
        .argv = argv,
        .stdout_limit = .limited(4096),
        .stderr_limit = .limited(4096),
    });
}

test "defconfig mode argument remains before later bridge options" {
    const allocator = std.testing.allocator;

    var tmp = std.testing.tmpDir(.{});
    defer tmp.cleanup();

    const exe_path = try std.fmt.allocPrint(
        allocator,
        ".zig-cache/tmp/{s}/conf_bridge_defconfig_options",
        .{tmp.sub_path[0..]},
    );
    defer allocator.free(exe_path);
    const emit_bin_arg = try std.fmt.allocPrint(allocator, "-femit-bin={s}", .{exe_path});
    defer allocator.free(emit_bin_arg);

    const build = try run(allocator, &.{
        "zig",
        "build-exe",
        "scripts/zigux/kconfig/conf_bridge.zig",
        emit_bin_arg,
    });
    defer allocator.free(build.stdout);
    defer allocator.free(build.stderr);
    try std.testing.expectEqual(std.process.Child.Term{ .exited = 0 }, build.term);
    try std.testing.expectEqualStrings("", build.stdout);
    try std.testing.expectEqualStrings("", build.stderr);

    const result = try run(allocator, &.{
        exe_path,
        "defconfig",
        "Kconfig",
        "out/.config",
        "arm64",
        "arch/arm64/configs/defconfig",
        "silent",
    });
    defer allocator.free(result.stdout);
    defer allocator.free(result.stderr);

    try std.testing.expectEqual(std.process.Child.Term{ .exited = 0 }, result.term);
    try std.testing.expectEqualStrings("", result.stderr);
    try std.testing.expect(std.mem.indexOf(
        u8,
        result.stdout,
        "\"argv\":[\"scripts/kconfig/conf\",\"--silent\",\"--defconfig\",\"arch/arm64/configs/defconfig\",\"Kconfig\"]",
    ) != null);
    try std.testing.expect(std.mem.indexOf(u8, result.stdout, "\"mode\":\"defconfig\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, result.stdout, "\"ARCH\":\"arm64\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, result.stdout, "\"KCONFIG_CONFIG\":\"out/.config\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, result.stdout, "allconfig_fallbacks") == null);
}
