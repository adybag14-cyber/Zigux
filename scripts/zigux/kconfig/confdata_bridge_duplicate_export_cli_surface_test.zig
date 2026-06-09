const std = @import("std");

const zig_exe = "zig";
const helper_source = "scripts/zigux/kconfig/confdata_bridge.zig";
const helper_exe = ".zig-cache/tmp/confdata-duplicate-export/confdata_bridge";
const config_path = ".zig-cache/tmp/confdata-duplicate-export/duplicate.config";

fn expectExitZero(result: std.process.RunResult) !void {
    switch (result.term) {
        .exited => |code| try std.testing.expectEqual(@as(u8, 0), code),
        else => return error.UnexpectedChildTermination,
    }
}

fn expectNoNeedle(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

fn run(argv: []const []const u8) !std.process.RunResult {
    return std.process.run(std.testing.allocator, std.testing.io, .{
        .argv = argv,
        .stdout_limit = .limited(16 * 1024),
        .stderr_limit = .limited(16 * 1024),
    });
}

test "confdata bridge export CLI keeps last duplicate state" {
    try std.Io.Dir.cwd().createDirPath(std.testing.io, ".zig-cache/tmp/confdata-duplicate-export");
    try std.Io.Dir.cwd().writeFile(std.testing.io, .{
        .sub_path = config_path,
        .data =
        \\CONFIG_ALPHA=y
        \\CONFIG_ALPHA=m
        \\CONFIG_BETA="first"
        \\# CONFIG_BETA is not set
        \\CONFIG_BETA=7
        \\CONFIG_GAMMA="stable"
        \\CONFIG_GAMMA="broken
        \\CONFIG_DELTA=m
        \\# CONFIG_DELTA is not set
        \\
        ,
    });

    const build = try run(&.{ zig_exe, "build-exe", helper_source, "-femit-bin=" ++ helper_exe });
    defer std.testing.allocator.free(build.stdout);
    defer std.testing.allocator.free(build.stderr);
    try expectExitZero(build);
    try std.testing.expectEqualStrings("", build.stderr);

    const auto_conf = try run(&.{ helper_exe, "auto.conf", config_path });
    defer std.testing.allocator.free(auto_conf.stdout);
    defer std.testing.allocator.free(auto_conf.stderr);
    try expectExitZero(auto_conf);
    try std.testing.expectEqualStrings("", auto_conf.stderr);
    try std.testing.expectEqualStrings(
        "CONFIG_ALPHA=m\n" ++
            "CONFIG_BETA=7\n" ++
            "CONFIG_GAMMA=\"stable\"\n",
        auto_conf.stdout,
    );
    try expectNoNeedle(auto_conf.stdout, "CONFIG_ALPHA=y");
    try expectNoNeedle(auto_conf.stdout, "CONFIG_BETA=\"first\"");
    try expectNoNeedle(auto_conf.stdout, "CONFIG_DELTA");

    const autoconf_header = try run(&.{ helper_exe, "autoconf.h", config_path });
    defer std.testing.allocator.free(autoconf_header.stdout);
    defer std.testing.allocator.free(autoconf_header.stderr);
    try expectExitZero(autoconf_header);
    try std.testing.expectEqualStrings("", autoconf_header.stderr);
    try std.testing.expectEqualStrings(
        "#define CONFIG_ALPHA_MODULE 1\n" ++
            "#define CONFIG_BETA 7\n" ++
            "#define CONFIG_GAMMA \"stable\"\n",
        autoconf_header.stdout,
    );
    try expectNoNeedle(autoconf_header.stdout, "CONFIG_ALPHA 1");
    try expectNoNeedle(autoconf_header.stdout, "CONFIG_BETA \"first\"");
    try expectNoNeedle(autoconf_header.stdout, "CONFIG_DELTA");
}
