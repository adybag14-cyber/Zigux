const std = @import("std");

fn buildConfBridge(binary_path: []const u8) !void {
    const emit_arg = try std.fmt.allocPrint(std.testing.allocator, "-femit-bin={s}", .{binary_path});
    defer std.testing.allocator.free(emit_arg);

    const result = try std.process.run(std.testing.allocator, std.testing.io, .{
        .argv = &.{ "zig", "build-exe", "scripts/zigux/kconfig/conf_bridge.zig", emit_arg },
        .stdout_limit = .limited(8192),
        .stderr_limit = .limited(8192),
    });
    defer std.testing.allocator.free(result.stdout);
    defer std.testing.allocator.free(result.stderr);

    try std.testing.expectEqual(std.process.Child.Term{ .exited = 0 }, result.term);
    try std.testing.expectEqualStrings("", result.stderr);
}

test "conf bridge CLI escapes accepted defconfig mode argument" {
    var tmp = std.testing.tmpDir(.{});
    defer tmp.cleanup();

    const binary_path = try std.fmt.allocPrint(
        std.testing.allocator,
        ".zig-cache/tmp/{s}/conf_bridge_defconfig_escaped_mode_arg",
        .{tmp.sub_path[0..]},
    );
    defer std.testing.allocator.free(binary_path);

    try buildConfBridge(binary_path);

    const result = try std.process.run(std.testing.allocator, std.testing.io, .{
        .argv = &.{
            binary_path,
            "defconfig",
            "Kconfig",
            "out/.config",
            "x86_64",
            "configs/quoted\"slash\\tab\tline\n.defconfig",
            "silent",
        },
        .stdout_limit = .limited(8192),
        .stderr_limit = .limited(8192),
    });
    defer std.testing.allocator.free(result.stdout);
    defer std.testing.allocator.free(result.stderr);

    try std.testing.expectEqual(std.process.Child.Term{ .exited = 0 }, result.term);
    try std.testing.expectEqualStrings("", result.stderr);
    try std.testing.expect(std.mem.indexOf(u8, result.stdout, "\"mode\":\"defconfig\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, result.stdout, "\"argv\":[\"scripts/kconfig/conf\",\"--silent\",\"--defconfig\",\"configs/quoted\\\"slash\\\\tab\\tline\\n.defconfig\",\"Kconfig\"]") != null);
    try std.testing.expect(std.mem.indexOf(u8, result.stdout, "\"ARCH\":\"x86_64\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, result.stdout, "\"KCONFIG_CONFIG\":\"out/.config\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, result.stdout, "\"allconfig_fallbacks\"") == null);
    try std.testing.expect(std.mem.indexOf(u8, result.stdout, "quoted\"slash") == null);
}
