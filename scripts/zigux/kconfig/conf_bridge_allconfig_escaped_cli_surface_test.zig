const std = @import("std");

const helper_path = ".zig-cache/lane20-conf-bridge-allconfig-escaped";

fn buildHelper() !void {
    try std.Io.Dir.cwd().createDirPath(std.testing.io, ".zig-cache");
    const result = try std.process.run(std.testing.allocator, std.testing.io, .{
        .argv = &.{
            "zig",
            "build-exe",
            "scripts/zigux/kconfig/conf_bridge.zig",
            "-femit-bin=" ++ helper_path,
        },
    });
    defer std.testing.allocator.free(result.stdout);
    defer std.testing.allocator.free(result.stderr);

    try std.testing.expectEqual(@as(std.process.Child.Term, .{ .exited = 0 }), result.term);
    try std.testing.expectEqualStrings("", result.stderr);
}

test "conf bridge CLI escapes explicit allconfig path override" {
    try buildHelper();
    defer std.Io.Dir.cwd().deleteFile(std.testing.io, helper_path) catch {};

    const allconfig_arg = "allconfig=overrides/quoted \"mini\"\\all.config";
    const result = try std.process.run(std.testing.allocator, std.testing.io, .{
        .argv = &.{
            helper_path,
            "allmodconfig",
            "Kconfig",
            "build/.config",
            "x86_64",
            "silent",
            allconfig_arg,
        },
    });
    defer std.testing.allocator.free(result.stdout);
    defer std.testing.allocator.free(result.stderr);

    try std.testing.expectEqual(@as(std.process.Child.Term, .{ .exited = 0 }), result.term);
    try std.testing.expectEqualStrings("", result.stderr);
    try std.testing.expect(std.mem.endsWith(u8, result.stdout, "\n"));
    try std.testing.expect(std.mem.indexOf(u8, result.stdout, "\"mode\":\"allmodconfig\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, result.stdout, "\"argv\":[\"scripts/kconfig/conf\",\"--silent\",\"--allmodconfig\",\"Kconfig\"]") != null);
    try std.testing.expect(std.mem.indexOf(u8, result.stdout, "\"ARCH\":\"x86_64\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, result.stdout, "\"KCONFIG_CONFIG\":\"build/.config\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, result.stdout, "\"KCONFIG_ALLCONFIG\":\"overrides/quoted \\\"mini\\\"\\\\all.config\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, result.stdout, "\"KCONFIG_ALLCONFIG\":\"1\"") == null);
    try std.testing.expect(std.mem.indexOf(u8, result.stdout, "\"allconfig_fallbacks\"") == null);
}
