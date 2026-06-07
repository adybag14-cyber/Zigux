const std = @import("std");

const zig_exe = "/workspace/.toolchains/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2/zig";

fn expectExitZero(result: std.process.RunResult) !void {
    switch (result.term) {
        .exited => |code| try std.testing.expectEqual(@as(u8, 0), code),
        else => return error.UnexpectedChildTermination,
    }
}

test "confdata bridge autoconf header CLI emits tristate defines" {
    var tmp = std.testing.tmpDir(.{});
    defer tmp.cleanup();

    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = "tristate.config",
        .data =
        \\CONFIG_BUILTIN=y
        \\CONFIG_DRIVER=m
        \\CONFIG_DISABLED=n
        \\# CONFIG_UNUSED is not set
        \\CONFIG_COUNT=7
        \\
        ,
    });

    const exe_path = try std.fmt.allocPrint(
        std.testing.allocator,
        ".zig-cache/tmp/{s}/confdata_bridge_tristate",
        .{tmp.sub_path[0..]},
    );
    defer std.testing.allocator.free(exe_path);

    const emit_arg = try std.fmt.allocPrint(
        std.testing.allocator,
        "-femit-bin={s}",
        .{exe_path},
    );
    defer std.testing.allocator.free(emit_arg);

    const build_result = try std.process.run(std.testing.allocator, std.testing.io, .{
        .argv = &.{
            zig_exe,
            "build-exe",
            "scripts/zigux/kconfig/confdata_bridge.zig",
            emit_arg,
            "--cache-dir",
            ".zig-cache-lane20-autoconf-tristate-build",
            "--global-cache-dir",
            ".zig-cache-lane20-autoconf-tristate-build/global",
        },
    });
    defer std.testing.allocator.free(build_result.stdout);
    defer std.testing.allocator.free(build_result.stderr);
    try expectExitZero(build_result);

    const config_path = try std.fmt.allocPrint(
        std.testing.allocator,
        ".zig-cache/tmp/{s}/tristate.config",
        .{tmp.sub_path[0..]},
    );
    defer std.testing.allocator.free(config_path);

    const run_result = try std.process.run(std.testing.allocator, std.testing.io, .{
        .argv = &.{
            exe_path,
            "autoconf.h",
            config_path,
        },
    });
    defer std.testing.allocator.free(run_result.stdout);
    defer std.testing.allocator.free(run_result.stderr);

    try expectExitZero(run_result);
    try std.testing.expectEqualStrings("", run_result.stderr);
    try std.testing.expect(std.mem.indexOf(u8, run_result.stdout, "#define CONFIG_BUILTIN 1\n") != null);
    try std.testing.expect(std.mem.indexOf(u8, run_result.stdout, "#define CONFIG_DRIVER_MODULE 1\n") != null);
    try std.testing.expect(std.mem.indexOf(u8, run_result.stdout, "#define CONFIG_COUNT 7\n") != null);
    try std.testing.expect(std.mem.indexOf(u8, run_result.stdout, "CONFIG_DISABLED") == null);
    try std.testing.expect(std.mem.indexOf(u8, run_result.stdout, "CONFIG_UNUSED") == null);
    try std.testing.expect(std.mem.endsWith(u8, run_result.stdout, "\n"));
}
