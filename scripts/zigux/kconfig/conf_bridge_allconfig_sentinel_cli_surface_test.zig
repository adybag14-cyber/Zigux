const std = @import("std");

const Case = struct {
    mode: []const u8,
    config: []const u8,
    arch: []const u8,
    expected_flag: []const u8,
};

fn buildConfBridge(allocator: std.mem.Allocator, tmp_dir: std.testing.TmpDir) ![]u8 {
    const exe_path = try std.fmt.allocPrint(
        allocator,
        ".zig-cache/tmp/{s}/conf-bridge-allconfig-sentinel",
        .{tmp_dir.sub_path[0..]},
    );
    errdefer allocator.free(exe_path);

    const emit_arg = try std.fmt.allocPrint(allocator, "-femit-bin={s}", .{exe_path});
    defer allocator.free(emit_arg);

    const result = try std.process.run(allocator, std.testing.io, .{
        .argv = &.{
            "zig",
            "build-exe",
            "scripts/zigux/kconfig/conf_bridge.zig",
            emit_arg,
        },
    });
    defer allocator.free(result.stdout);
    defer allocator.free(result.stderr);

    try std.testing.expectEqual(std.process.Child.Term{ .exited = 0 }, result.term);
    try std.testing.expectEqualStrings("", result.stderr);
    return exe_path;
}

fn expectAllconfigSentinelCli(exe_path: []const u8, case: Case) !void {
    const result = try std.process.run(std.testing.allocator, std.testing.io, .{
        .argv = &.{
            exe_path,
            case.mode,
            "Kconfig",
            case.config,
            case.arch,
            "allconfig=1",
        },
    });
    defer std.testing.allocator.free(result.stdout);
    defer std.testing.allocator.free(result.stderr);

    try std.testing.expectEqual(std.process.Child.Term{ .exited = 0 }, result.term);
    try std.testing.expectEqualStrings("", result.stderr);
    try std.testing.expect(std.mem.indexOf(u8, result.stdout, "\"KCONFIG_ALLCONFIG\":\"1\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, result.stdout, case.expected_flag) != null);
    try std.testing.expect(std.mem.indexOf(u8, result.stdout, case.config) != null);
    try std.testing.expect(std.mem.indexOf(u8, result.stdout, case.arch) != null);
}

test "conf bridge CLI preserves explicit allconfig sentinel across accepting modes" {
    var tmp = std.testing.tmpDir(.{});
    defer tmp.cleanup();

    const exe_path = try buildConfBridge(std.testing.allocator, tmp);
    defer std.testing.allocator.free(exe_path);

    const cases = [_]Case{
        .{ .mode = "allnoconfig", .config = "none/.config", .arch = "arm64", .expected_flag = "\"--allnoconfig\"" },
        .{ .mode = "allyesconfig", .config = "yes/.config", .arch = "arm64", .expected_flag = "\"--allyesconfig\"" },
        .{ .mode = "allmodconfig", .config = "mod/.config", .arch = "arm", .expected_flag = "\"--allmodconfig\"" },
        .{ .mode = "alldefconfig", .config = "build/.config", .arch = "riscv64", .expected_flag = "\"--alldefconfig\"" },
        .{ .mode = "randconfig", .config = "rand/.config", .arch = "x86_64", .expected_flag = "\"--randconfig\"" },
    };

    for (cases) |case| {
        try expectAllconfigSentinelCli(exe_path, case);
    }
}
