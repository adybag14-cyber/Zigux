const std = @import("std");

const helper_source = "scripts/zigux/kconfig/conf_bridge.zig";
const build_dir = ".zig-cache-lane20-randconfig-option-order";
const helper_bin = build_dir ++ "/conf_bridge_randconfig_option_order_helper";

const Case = struct {
    name: []const u8,
    argv: []const []const u8,
    expected_allconfig: []const u8,
    expected_seed: []const u8,
    expected_probability: []const u8,
};

fn run(argv: []const []const u8) !std.process.RunResult {
    return try std.process.run(std.testing.allocator, std.testing.io, .{
        .argv = argv,
        .stdout_limit = .limited(4096),
        .stderr_limit = .limited(4096),
    });
}

fn expectSuccessfulRandconfig(case: Case) !void {
    const result = try run(case.argv);
    defer std.testing.allocator.free(result.stdout);
    defer std.testing.allocator.free(result.stderr);

    errdefer std.debug.print("case failed: {s}\nstdout:\n{s}\nstderr:\n{s}\n", .{ case.name, result.stdout, result.stderr });

    try std.testing.expectEqual(std.process.Child.Term{ .exited = 0 }, result.term);
    try std.testing.expectEqualStrings("", result.stderr);
    try std.testing.expect(std.mem.endsWith(u8, result.stdout, "\n"));
    try std.testing.expect(std.mem.indexOf(u8, result.stdout, "\"mode\":\"randconfig\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, result.stdout, "\"argv\":[\"scripts/kconfig/conf\",\"--silent\",\"--randconfig\",\"Kconfig\"]") != null);
    try std.testing.expect(std.mem.indexOf(u8, result.stdout, "\"ARCH\":\"riscv64\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, result.stdout, "\"KCONFIG_CONFIG\":\"rand/.config\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, result.stdout, case.expected_allconfig) != null);
    try std.testing.expect(std.mem.indexOf(u8, result.stdout, case.expected_seed) != null);
    try std.testing.expect(std.mem.indexOf(u8, result.stdout, case.expected_probability) != null);
    try std.testing.expect(std.mem.indexOf(u8, result.stdout, "\"KCONFIG_AUTOCONFIG\"") == null);
    try std.testing.expect(std.mem.indexOf(u8, result.stdout, "\"KCONFIG_NOSILENTUPDATE\"") == null);
}

test "randconfig bridge options keep their meaning when CLI order varies" {
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

    const probability_first = [_][]const u8{
        helper_bin,
        "randconfig",
        "Kconfig",
        "rand/.config",
        "riscv64",
        "probability=15:25",
        "silent",
        "allconfig=1",
        "seed=0xC0FFEE",
    };
    const empty_allconfig_first = [_][]const u8{
        helper_bin,
        "randconfig",
        "Kconfig",
        "rand/.config",
        "riscv64",
        "allconfig=",
        "seed=0x1234",
        "silent",
        "probability=40",
    };

    const cases = [_]Case{
        .{
            .name = "probability before silent and seed",
            .argv = &probability_first,
            .expected_allconfig = "\"KCONFIG_ALLCONFIG\":\"1\"",
            .expected_seed = "\"KCONFIG_SEED\":\"0xC0FFEE\"",
            .expected_probability = "\"KCONFIG_PROBABILITY\":\"15:25\"",
        },
        .{
            .name = "empty allconfig before silent and probability",
            .argv = &empty_allconfig_first,
            .expected_allconfig = "\"KCONFIG_ALLCONFIG\":\"\"",
            .expected_seed = "\"KCONFIG_SEED\":\"0x1234\"",
            .expected_probability = "\"KCONFIG_PROBABILITY\":\"40\"",
        },
    };

    for (cases) |case| {
        try expectSuccessfulRandconfig(case);
    }
}
