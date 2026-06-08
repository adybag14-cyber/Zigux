const std = @import("std");
const Io = std.Io;

const Case = struct {
    name: []const u8,
    argv: []const []const u8,
};

fn buildConfdataBridge(allocator: std.mem.Allocator) ![]const u8 {
    try Io.Dir.cwd().createDirPath(std.testing.io, ".zig-cache/tmp");
    const exe_path = ".zig-cache/tmp/confdata_bridge_usage_cli_test";
    const build_args = [_][]const u8{
        "zig",
        "build-exe",
        "scripts/zigux/kconfig/confdata_bridge.zig",
        "-femit-bin=.zig-cache/tmp/confdata_bridge_usage_cli_test",
    };

    const result = try std.process.run(allocator, std.testing.io, .{
        .argv = &build_args,
    });
    defer allocator.free(result.stdout);
    defer allocator.free(result.stderr);

    try std.testing.expectEqual(std.process.Child.Term{ .exited = 0 }, result.term);
    return exe_path;
}

fn expectUsageFailure(allocator: std.mem.Allocator, case: Case) !void {
    const result = try std.process.run(allocator, std.testing.io, .{
        .argv = case.argv,
    });
    defer allocator.free(result.stdout);
    defer allocator.free(result.stderr);

    try std.testing.expectEqual(std.process.Child.Term{ .exited = 1 }, result.term);
    try std.testing.expectEqualStrings("", result.stdout);
    try std.testing.expectEqualStrings("Usage: confdata_bridge [json|auto.conf|autoconf.h] <config>\n", result.stderr);
}

test "confdata bridge usage errors stay on the public CLI boundary" {
    const allocator = std.testing.allocator;
    const exe_path = try buildConfdataBridge(allocator);

    const too_few_args = [_][]const u8{exe_path};
    const invalid_mode_args = [_][]const u8{ exe_path, "toml", "zigux/tests/fixtures/kconfig_bridge/sample.config" };
    const too_many_args = [_][]const u8{ exe_path, "json", "zigux/tests/fixtures/kconfig_bridge/sample.config", "extra" };

    const cases = [_]Case{
        .{ .name = "too few args", .argv = &too_few_args },
        .{ .name = "invalid output mode", .argv = &invalid_mode_args },
        .{ .name = "too many args", .argv = &too_many_args },
    };

    for (cases) |case| {
        errdefer std.debug.print("case failed: {s}\n", .{case.name});
        try expectUsageFailure(allocator, case);
    }
}
