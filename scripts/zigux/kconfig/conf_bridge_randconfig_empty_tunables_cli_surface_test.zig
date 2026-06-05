const std = @import("std");

fn expectExited(term: std.process.Child.Term, code: u8) !void {
    switch (term) {
        .exited => |actual| try std.testing.expectEqual(code, actual),
        else => return error.UnexpectedChildTermination,
    }
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectOmits(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

test "conf bridge CLI keeps empty randconfig tunables unset" {
    var tmp = std.testing.tmpDir(.{});
    defer tmp.cleanup();

    const allocator = std.testing.allocator;
    const exe_path = try std.fmt.allocPrint(
        allocator,
        ".zig-cache/tmp/{s}/conf-bridge-randconfig-empty-tunables",
        .{tmp.sub_path[0..]},
    );
    defer allocator.free(exe_path);
    const emit_arg = try std.fmt.allocPrint(allocator, "-femit-bin={s}", .{exe_path});
    defer allocator.free(emit_arg);

    const build = try std.process.run(allocator, std.testing.io, .{
        .argv = &.{
            "zig",
            "build-exe",
            "scripts/zigux/kconfig/conf_bridge.zig",
            emit_arg,
        },
    });
    defer allocator.free(build.stdout);
    defer allocator.free(build.stderr);
    try expectExited(build.term, 0);
    try std.testing.expectEqual(@as(usize, 0), build.stderr.len);

    const run = try std.process.run(allocator, std.testing.io, .{
        .argv = &.{
            exe_path,
            "randconfig",
            "Kconfig",
            "rand/.config",
            "x86_64",
            "seed=",
            "probability=",
        },
    });
    defer allocator.free(run.stdout);
    defer allocator.free(run.stderr);
    try expectExited(run.term, 0);
    try std.testing.expectEqual(@as(usize, 0), run.stderr.len);

    try expectContains(run.stdout, "\"tool\":\"scripts/kconfig/conf\"");
    try expectContains(run.stdout, "\"mode\":\"randconfig\"");
    try expectContains(run.stdout, "\"--randconfig\"");
    try expectContains(run.stdout, "\"KCONFIG_CONFIG\":\"rand/.config\"");
    try expectContains(run.stdout, "\"ARCH\":\"x86_64\"");
    try expectOmits(run.stdout, "\"KCONFIG_SEED\"");
    try expectOmits(run.stdout, "\"KCONFIG_PROBABILITY\"");
}
