const std = @import("std");
const testing = std.testing;

const bridge_source = "scripts/zigux/kconfig/conf_bridge.zig";
const exe_path = ".zig-cache/tmp/conf-bridge-oldaskconfig-silent-test";

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectNotContains(haystack: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

test "oldaskconfig CLI accepts generic silent bridge option" {
    const allocator = testing.allocator;

    try std.Io.Dir.cwd().createDirPath(testing.io, ".zig-cache/tmp");
    _ = std.Io.Dir.cwd().deleteFile(testing.io, exe_path) catch {};

    const build_result = try std.process.run(allocator, testing.io, .{
        .argv = &.{
            "zig",
            "build-exe",
            bridge_source,
            "-femit-bin=" ++ exe_path,
        },
        .stderr_limit = .limited(64 * 1024),
        .stdout_limit = .limited(64 * 1024),
    });
    defer allocator.free(build_result.stdout);
    defer allocator.free(build_result.stderr);

    try testing.expectEqual(std.process.Child.Term{ .exited = 0 }, build_result.term);
    try testing.expectEqualStrings("", build_result.stderr);

    const run_result = try std.process.run(allocator, testing.io, .{
        .argv = &.{
            exe_path,
            "oldaskconfig",
            "Kconfig",
            "ask/.config",
            "x86_64",
            "silent",
        },
        .stderr_limit = .limited(64 * 1024),
        .stdout_limit = .limited(64 * 1024),
    });
    defer allocator.free(run_result.stdout);
    defer allocator.free(run_result.stderr);

    try testing.expectEqual(std.process.Child.Term{ .exited = 0 }, run_result.term);
    try testing.expectEqualStrings("", run_result.stderr);
    try expectContains(run_result.stdout, "\"mode\":\"oldaskconfig\"");
    try expectContains(run_result.stdout, "\"argv\":[\"scripts/kconfig/conf\",\"--silent\",\"--oldaskconfig\",\"Kconfig\"]");
    try expectContains(run_result.stdout, "\"ARCH\":\"x86_64\"");
    try expectContains(run_result.stdout, "\"KCONFIG_CONFIG\":\"ask/.config\"");
    try expectNotContains(run_result.stdout, "\"KCONFIG_ALLCONFIG\"");
    try expectNotContains(run_result.stdout, "\"allconfig_fallbacks\"");
}
