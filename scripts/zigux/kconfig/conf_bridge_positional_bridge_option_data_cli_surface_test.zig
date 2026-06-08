const std = @import("std");

fn run(args: []const []const u8) !std.process.RunResult {
    return std.process.run(std.testing.allocator, std.testing.io, .{
        .argv = args,
        .stdout_limit = .limited(4096),
        .stderr_limit = .limited(4096),
    });
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectNotContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

fn buildConfBridge(binary_path: []const u8) !void {
    const emit_arg = try std.fmt.allocPrint(std.testing.allocator, "-femit-bin={s}", .{binary_path});
    defer std.testing.allocator.free(emit_arg);

    const result = try run(&.{
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

test "conf bridge CLI keeps option-shaped positional fields as request data" {
    try std.Io.Dir.cwd().createDirPath(std.testing.io, ".zig-cache/tmp/lane20-positional-data");
    const binary_path = ".zig-cache/tmp/lane20-positional-data/conf_bridge";
    try buildConfBridge(binary_path);

    const result = try run(&.{
        binary_path,
        "syncconfig",
        "allconfig=Kconfig",
        "seed=.config",
        "silent",
        "nosilentupdate=keep-existing-auto",
    });
    defer std.testing.allocator.free(result.stdout);
    defer std.testing.allocator.free(result.stderr);

    try std.testing.expectEqual(std.process.Child.Term{ .exited = 0 }, result.term);
    try std.testing.expectEqualStrings("", result.stderr);
    try expectContains(result.stdout, "\"tool\":\"scripts/kconfig/conf\"");
    try expectContains(result.stdout, "\"mode\":\"syncconfig\"");
    try expectContains(result.stdout, "\"argv\":[\"scripts/kconfig/conf\",\"--syncconfig\",\"allconfig=Kconfig\"]");
    try expectContains(result.stdout, "\"ARCH\":\"silent\"");
    try expectContains(result.stdout, "\"KCONFIG_CONFIG\":\"seed=.config\"");
    try expectContains(result.stdout, "\"KCONFIG_AUTOCONFIG\":\"include/config/auto.conf\"");
    try expectContains(result.stdout, "\"KCONFIG_AUTOHEADER\":\"include/generated/autoconf.h\"");
    try expectContains(result.stdout, "\"KCONFIG_NOSILENTUPDATE\":\"keep-existing-auto\"");
    try expectNotContains(result.stdout, "\"KCONFIG_ALLCONFIG\"");
    try expectNotContains(result.stdout, "\"KCONFIG_SEED\"");
    try expectNotContains(result.stdout, "\"KCONFIG_PROBABILITY\"");
    try std.testing.expect(std.mem.endsWith(u8, result.stdout, "\n"));
}
