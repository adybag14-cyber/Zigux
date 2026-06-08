const std = @import("std");

fn runConfBridge(args: []const []const u8) !std.process.RunResult {
    return std.process.run(std.testing.allocator, std.testing.io, .{ .argv = args });
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectNotContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

fn buildBridge(binary_path: []const u8) !void {
    const emit_arg = try std.fmt.allocPrint(std.testing.allocator, "-femit-bin={s}", .{binary_path});
    defer std.testing.allocator.free(emit_arg);

    const result = try runConfBridge(&.{
        "zig",
        "build-exe",
        "scripts/zigux/kconfig/conf_bridge.zig",
        emit_arg,
    });
    defer std.testing.allocator.free(result.stdout);
    defer std.testing.allocator.free(result.stderr);

    try std.testing.expectEqual(std.process.Child.Term{ .exited = 0 }, result.term);
    try std.testing.expectEqualStrings("", result.stderr);
}

test "randconfig silent default CLI emits no implicit tunables or allconfig override" {
    try std.Io.Dir.cwd().createDirPath(std.testing.io, ".zig-cache/tmp/lane20-randconfig-silent");
    const binary_path = ".zig-cache/tmp/lane20-randconfig-silent/conf_bridge";
    try buildBridge(binary_path);

    const result = try runConfBridge(&.{
        binary_path,
        "randconfig",
        "Kconfig",
        "rand/.config",
        "x86_64",
        "silent",
    });
    defer std.testing.allocator.free(result.stdout);
    defer std.testing.allocator.free(result.stderr);

    try std.testing.expectEqual(std.process.Child.Term{ .exited = 0 }, result.term);
    try std.testing.expectEqualStrings("", result.stderr);
    try expectContains(result.stdout, "\"tool\":\"scripts/kconfig/conf\"");
    try expectContains(result.stdout, "\"mode\":\"randconfig\"");
    try expectContains(result.stdout, "\"argv\":[\"scripts/kconfig/conf\",\"--silent\",\"--randconfig\",\"Kconfig\"]");
    try expectContains(result.stdout, "\"ARCH\":\"x86_64\"");
    try expectContains(result.stdout, "\"KCONFIG_CONFIG\":\"rand/.config\"");
    try expectNotContains(result.stdout, "\"KCONFIG_ALLCONFIG\"");
    try expectNotContains(result.stdout, "\"allconfig_fallbacks\"");
    try expectNotContains(result.stdout, "\"KCONFIG_SEED\"");
    try expectNotContains(result.stdout, "\"KCONFIG_PROBABILITY\"");
    try expectNotContains(result.stdout, "\"KCONFIG_AUTOCONFIG\"");
    try expectNotContains(result.stdout, "\"KCONFIG_AUTOHEADER\"");
    try std.testing.expect(std.mem.endsWith(u8, result.stdout, "\n"));
}
