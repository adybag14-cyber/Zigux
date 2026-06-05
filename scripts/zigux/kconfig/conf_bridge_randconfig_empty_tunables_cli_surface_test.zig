const std = @import("std");

const allocator = std.testing.allocator;
const io = std.testing.io;

const RunResult = struct {
    stdout: []u8,
    stderr: []u8,
    term: std.process.Child.Term,

    fn deinit(self: RunResult) void {
        allocator.free(self.stdout);
        allocator.free(self.stderr);
    }
};

fn run(argv: []const []const u8) !RunResult {
    const result = try std.process.run(allocator, io, .{
        .argv = argv,
        .stdout_limit = .limited(4096),
        .stderr_limit = .limited(4096),
    });
    return .{
        .stdout = result.stdout,
        .stderr = result.stderr,
        .term = result.term,
    };
}

fn expectExitedZero(result: RunResult) !void {
    switch (result.term) {
        .exited => |code| try std.testing.expectEqual(@as(u8, 0), code),
        else => return error.UnexpectedChildTermination,
    }
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectNotContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

fn buildConfBridge(binary_path: []const u8) !void {
    const emit_arg = try std.fmt.allocPrint(allocator, "-femit-bin={s}", .{binary_path});
    defer allocator.free(emit_arg);

    const result = try run(&.{
        "zig",
        "build-exe",
        "scripts/zigux/kconfig/conf_bridge.zig",
        emit_arg,
    });
    defer result.deinit();

    try expectExitedZero(result);
    try std.testing.expectEqualStrings("", result.stderr);
}

test "standalone conf bridge CLI accepts empty randconfig tunables as omitted env" {
    const binary_path = "/tmp/zigux-conf-bridge-randconfig-empty-test";
    std.Io.Dir.deleteFileAbsolute(io, binary_path) catch {};
    defer std.Io.Dir.deleteFileAbsolute(io, binary_path) catch {};

    try buildConfBridge(binary_path);

    const result = try run(&.{
        binary_path,
        "randconfig",
        "Kconfig",
        "rand/.config",
        "x86_64",
        "silent",
        "seed=",
        "probability=",
    });
    defer result.deinit();

    try expectExitedZero(result);
    try std.testing.expectEqualStrings("", result.stderr);
    try expectContains(result.stdout, "\"mode\":\"randconfig\"");
    try expectContains(result.stdout, "\"argv\":[\"scripts/kconfig/conf\",\"--silent\",\"--randconfig\",\"Kconfig\"]");
    try expectContains(result.stdout, "\"KCONFIG_CONFIG\":\"rand/.config\"");
    try expectContains(result.stdout, "\"ARCH\":\"x86_64\"");
    try expectNotContains(result.stdout, "\"KCONFIG_SEED\"");
    try expectNotContains(result.stdout, "\"KCONFIG_PROBABILITY\"");
}
