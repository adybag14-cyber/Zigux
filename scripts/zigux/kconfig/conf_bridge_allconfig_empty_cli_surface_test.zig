const std = @import("std");

const Case = struct {
    mode: []const u8,
    config: []const u8,
    arch: []const u8,
    expected_flag: []const u8,
};

fn expectExited(term: std.process.Child.Term, code: u8) !void {
    switch (term) {
        .exited => |actual| try std.testing.expectEqual(code, actual),
        else => return error.UnexpectedChildTermination,
    }
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn buildConfBridge(allocator: std.mem.Allocator, tmp_dir: std.testing.TmpDir) ![]u8 {
    const exe_path = try std.fmt.allocPrint(
        allocator,
        ".zig-cache/tmp/{s}/conf-bridge-allconfig-empty",
        .{tmp_dir.sub_path[0..]},
    );
    errdefer allocator.free(exe_path);

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
    return exe_path;
}

fn expectEmptyAllconfigCli(exe_path: []const u8, case: Case) !void {
    const run = try std.process.run(std.testing.allocator, std.testing.io, .{
        .argv = &.{
            exe_path,
            case.mode,
            "Kconfig",
            case.config,
            case.arch,
            "allconfig=",
        },
    });
    defer std.testing.allocator.free(run.stdout);
    defer std.testing.allocator.free(run.stderr);

    try expectExited(run.term, 0);
    try std.testing.expectEqual(@as(usize, 0), run.stderr.len);
    try expectContains(run.stdout, "\"tool\":\"scripts/kconfig/conf\"");
    try expectContains(run.stdout, "\"mode\":\"");
    try expectContains(run.stdout, case.mode);
    try expectContains(run.stdout, case.expected_flag);
    try expectContains(run.stdout, case.config);
    try expectContains(run.stdout, case.arch);
    try expectContains(run.stdout, "\"KCONFIG_ALLCONFIG\":\"\"");
}

test "conf bridge CLI preserves explicit empty allconfig override across accepting modes" {
    var tmp = std.testing.tmpDir(.{});
    defer tmp.cleanup();

    const exe_path = try buildConfBridge(std.testing.allocator, tmp);
    defer std.testing.allocator.free(exe_path);

    const cases = [_]Case{
        .{
            .mode = "allnoconfig",
            .config = "none/.config",
            .arch = "arm64",
            .expected_flag = "\"--allnoconfig\"",
        },
        .{
            .mode = "allyesconfig",
            .config = "yes/.config",
            .arch = "arm64",
            .expected_flag = "\"--allyesconfig\"",
        },
        .{
            .mode = "allmodconfig",
            .config = "mod/.config",
            .arch = "arm",
            .expected_flag = "\"--allmodconfig\"",
        },
        .{
            .mode = "alldefconfig",
            .config = "build/.config",
            .arch = "riscv64",
            .expected_flag = "\"--alldefconfig\"",
        },
        .{
            .mode = "randconfig",
            .config = "rand/.config",
            .arch = "x86_64",
            .expected_flag = "\"--randconfig\"",
        },
    };

    for (cases) |case| {
        try expectEmptyAllconfigCli(exe_path, case);
    }
}
