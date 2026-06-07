const std = @import("std");

const helper_source = "scripts/zigux/kconfig/conf_bridge.zig";
const build_dir = ".zig-cache-lane20-mode-arg-path";
const helper_bin = build_dir ++ "/conf_bridge_mode_arg_path_helper";

const Case = struct {
    mode: []const u8,
    config: []const u8,
    arch: []const u8,
    mode_arg: []const u8,
    expected_flag: []const u8,
};

fn run(argv: []const []const u8) !std.process.RunResult {
    return try std.process.run(std.testing.allocator, std.testing.io, .{
        .argv = argv,
        .stdout_limit = .limited(4096),
        .stderr_limit = .limited(4096),
    });
}

fn expectSuccessfulModeArg(case: Case) !void {
    const result = try run(&.{
        helper_bin,
        case.mode,
        "Kconfig",
        case.config,
        case.arch,
        case.mode_arg,
    });
    defer std.testing.allocator.free(result.stdout);
    defer std.testing.allocator.free(result.stderr);

    try std.testing.expectEqual(std.process.Child.Term{ .exited = 0 }, result.term);
    try std.testing.expectEqualStrings("", result.stderr);
    try std.testing.expect(std.mem.endsWith(u8, result.stdout, "\n"));
    try std.testing.expect(std.mem.indexOf(u8, result.stdout, case.expected_flag) != null);
    try std.testing.expect(std.mem.indexOf(u8, result.stdout, case.mode_arg) != null);
    try std.testing.expect(std.mem.indexOf(u8, result.stdout, "\"KCONFIG_CONFIG\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, result.stdout, case.config) != null);
    try std.testing.expect(std.mem.indexOf(u8, result.stdout, case.arch) != null);
    try std.testing.expect(std.mem.indexOf(u8, result.stdout, "\"KCONFIG_ALLCONFIG\"") == null);
    try std.testing.expect(std.mem.indexOf(u8, result.stdout, "\"KCONFIG_SEED\"") == null);
    try std.testing.expect(std.mem.indexOf(u8, result.stdout, "\"KCONFIG_NOSILENTUPDATE\"") == null);
}

test "mode argument paths that only resemble bridge options stay data through CLI" {
    var cwd = std.Io.Dir.cwd();
    cwd.deleteTree(std.testing.io, build_dir) catch {};
    try cwd.createDirPath(std.testing.io, build_dir);
    defer cwd.deleteTree(std.testing.io, build_dir) catch {};

    const build = try run(&.{
        "zig",
        "build-exe",
        helper_source,
        "-femit-bin=" ++ helper_bin,
    });
    defer std.testing.allocator.free(build.stdout);
    defer std.testing.allocator.free(build.stderr);

    try std.testing.expectEqual(std.process.Child.Term{ .exited = 0 }, build.term);
    try std.testing.expectEqualStrings("", build.stderr);

    const cases = [_]Case{
        .{
            .mode = "defconfig",
            .config = "out/.config",
            .arch = "arm64",
            .mode_arg = "arch/arm64/configs/silent-debug_defconfig",
            .expected_flag = "\"--defconfig\"",
        },
        .{
            .mode = "defconfig",
            .config = "debug/.config",
            .arch = "x86_64",
            .mode_arg = "arch/x86/configs/debug=1_defconfig",
            .expected_flag = "\"--defconfig\"",
        },
        .{
            .mode = "savedefconfig",
            .config = ".config",
            .arch = "riscv64",
            .mode_arg = "out/silent.save",
            .expected_flag = "\"--savedefconfig\"",
        },
    };

    for (cases) |case| {
        try expectSuccessfulModeArg(case);
    }
}
