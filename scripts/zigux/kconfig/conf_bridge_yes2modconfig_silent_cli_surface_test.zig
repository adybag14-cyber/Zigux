const std = @import("std");

fn contains(haystack: []const u8, needle: []const u8) bool {
    return std.mem.indexOf(u8, haystack, needle) != null;
}

test "conf bridge yes2modconfig accepts generic silent option through cli" {
    const allocator = std.testing.allocator;
    const cwd = std.Io.Dir.cwd();
    try cwd.createDirPath(std.testing.io, ".zig-cache/tmp");

    const exe_path = ".zig-cache/tmp/conf_bridge_yes2modconfig_silent_test";
    const build_args = [_][]const u8{
        "zig",
        "build-exe",
        "scripts/zigux/kconfig/conf_bridge.zig",
        "-femit-bin=" ++ exe_path,
        "--cache-dir",
        ".zig-cache/conf-bridge-yes2modconfig-silent-build",
        "--global-cache-dir",
        ".zig-cache/conf-bridge-yes2modconfig-silent-build/global",
    };
    const build_result = try std.process.run(allocator, std.testing.io, .{
        .argv = &build_args,
    });
    defer allocator.free(build_result.stdout);
    defer allocator.free(build_result.stderr);
    try std.testing.expectEqual(std.process.Child.Term{ .exited = 0 }, build_result.term);
    try std.testing.expectEqualStrings("", build_result.stderr);

    const run_args = [_][]const u8{
        exe_path,
        "yes2modconfig",
        "Kconfig",
        "rewrite/.config",
        "x86",
        "silent",
    };
    const run_result = try std.process.run(allocator, std.testing.io, .{
        .argv = &run_args,
    });
    defer allocator.free(run_result.stdout);
    defer allocator.free(run_result.stderr);

    try std.testing.expectEqual(std.process.Child.Term{ .exited = 0 }, run_result.term);
    try std.testing.expectEqualStrings("", run_result.stderr);
    try std.testing.expect(contains(run_result.stdout, "\"mode\":\"yes2modconfig\""));
    try std.testing.expect(contains(run_result.stdout, "\"argv\":[\"scripts/kconfig/conf\",\"--silent\",\"--yes2modconfig\",\"Kconfig\"]"));
    try std.testing.expect(contains(run_result.stdout, "\"ARCH\":\"x86\""));
    try std.testing.expect(contains(run_result.stdout, "\"KCONFIG_CONFIG\":\"rewrite/.config\""));
    try std.testing.expect(!contains(run_result.stdout, "KCONFIG_ALLCONFIG"));
    try std.testing.expect(!contains(run_result.stdout, "KCONFIG_AUTOCONFIG"));
    try std.testing.expect(!contains(run_result.stdout, "KCONFIG_SEED"));
}
