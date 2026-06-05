const std = @import("std");

const helper_source = "scripts/zigux/kconfig/confdata_bridge.zig";

test "confdata bridge autoconf header CLI escapes string bytes" {
    const allocator = std.testing.allocator;

    var tmp = std.testing.tmpDir(.{});
    defer tmp.cleanup();

    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = "escape.config",
        .data = "CONFIG_ALPHA=y\n" ++
            "CONFIG_BETA=m\n" ++
            "CONFIG_ESCAPED=\"quote\\\"slash\\\\tab\\tcr\\rend\"\n" ++
            "CONFIG_COUNT=0x2a\n" ++
            "CONFIG_EXPLICIT_N=n\n" ++
            "# CONFIG_OMITTED is not set\n",
    });

    const exe_path = try std.fmt.allocPrint(allocator, ".zig-cache/tmp/{s}/confdata_bridge", .{tmp.sub_path[0..]});
    defer allocator.free(exe_path);
    const config_path = try std.fmt.allocPrint(allocator, ".zig-cache/tmp/{s}/escape.config", .{tmp.sub_path[0..]});
    defer allocator.free(config_path);

    const emit_arg = try std.fmt.allocPrint(allocator, "-femit-bin={s}", .{exe_path});
    defer allocator.free(emit_arg);

    const build = try std.process.run(allocator, std.testing.io, .{
        .argv = &.{ "zig", "build-exe", helper_source, emit_arg },
        .cwd = .{ .path = "." },
    });
    defer allocator.free(build.stdout);
    defer allocator.free(build.stderr);
    try std.testing.expectEqual(@as(u8, 0), build.term.exited);
    try std.testing.expectEqualStrings("", build.stderr);

    const run = try std.process.run(allocator, std.testing.io, .{
        .argv = &.{ exe_path, "autoconf.h", config_path },
        .cwd = .{ .path = "." },
    });
    defer allocator.free(run.stdout);
    defer allocator.free(run.stderr);
    try std.testing.expectEqual(@as(u8, 0), run.term.exited);
    try std.testing.expectEqualStrings("", run.stderr);
    try std.testing.expectEqualStrings(
        "#define CONFIG_ALPHA 1\n" ++
            "#define CONFIG_BETA_MODULE 1\n" ++
            "#define CONFIG_ESCAPED \"quote\\\"slash\\\\tabtcrrend\"\n" ++
            "#define CONFIG_COUNT 0x2a\n",
        run.stdout,
    );
    try std.testing.expect(std.mem.indexOf(u8, run.stdout, "CONFIG_EXPLICIT_N") == null);
    try std.testing.expect(std.mem.indexOf(u8, run.stdout, "CONFIG_OMITTED") == null);
}
