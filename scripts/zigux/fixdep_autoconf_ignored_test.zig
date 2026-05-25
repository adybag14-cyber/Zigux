const std = @import("std");

fn absoluteTmpBasePath(allocator: std.mem.Allocator, tmp: anytype) ![]u8 {
    const relative_base_path = try std.fmt.allocPrint(
        allocator,
        ".zig-cache/tmp/{s}",
        .{tmp.sub_path[0..]},
    );
    defer allocator.free(relative_base_path);

    return try std.fs.path.resolve(allocator, &.{ ".", relative_base_path });
}

test "fixdep ignores autoconf while keeping recursive config capture on the public entry path" {
    var tmp = std.testing.tmpDir(.{});
    defer tmp.cleanup();

    const allocator = std.testing.allocator;
    const base_path = try absoluteTmpBasePath(allocator, tmp);
    defer allocator.free(base_path);

    _ = try tmp.dir.createDirPathStatus(std.testing.io, "include/generated", .default_dir);

    const source_path = try std.fmt.allocPrint(
        allocator,
        "{s}/sample_autoconf_source.c",
        .{base_path},
    );
    defer allocator.free(source_path);

    const config_path = try std.fmt.allocPrint(
        allocator,
        "{s}/sample-autoconf-config.h",
        .{base_path},
    );
    defer allocator.free(config_path);

    const autoconf_path = try std.fmt.allocPrint(
        allocator,
        "{s}/include/generated/autoconf.h",
        .{base_path},
    );
    defer allocator.free(autoconf_path);

    const tail_path = try std.fmt.allocPrint(
        allocator,
        "{s}/tail.so",
        .{base_path},
    );
    defer allocator.free(tail_path);

    const depfile_path = try std.fmt.allocPrint(
        allocator,
        "{s}/sample_autoconf_ignored.d",
        .{base_path},
    );
    defer allocator.free(depfile_path);

    const cmdline = try std.fmt.allocPrint(
        allocator,
        "clang -c {s} -o sample_autoconf.o",
        .{source_path},
    );
    defer allocator.free(cmdline);

    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = "sample_autoconf_source.c",
        .data = "/* CONFIG_ZIGUX_SRC */\n",
    });
    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = "sample-autoconf-config.h",
        .data = "#define CONFIG_ZIGUX_CFG 1\n#define CONFIG_ZIGUX_SRC 1\n",
    });
    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = "include/generated/autoconf.h",
        .data = "#define CONFIG_AUTOCONF_ONLY 1\n",
    });
    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = "tail.so",
        .data = "placeholder shared object fixture\n",
    });

    const depfile_text = try std.fmt.allocPrint(
        allocator,
        "sample_autoconf.o sample_autoconf.dwo: {s} {s} {s} {s}\n",
        .{ source_path, config_path, autoconf_path, tail_path },
    );
    defer allocator.free(depfile_text);
    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = "sample_autoconf_ignored.d",
        .data = depfile_text,
    });

    const argv: []const []const u8 = &.{
        "zig",
        "run",
        "fixdep.zig",
        "--",
        depfile_path,
        "sample_autoconf.o",
        cmdline,
    };
    const result = try std.process.run(allocator, std.testing.io, .{
        .argv = argv,
        .cwd = .{ .path = "." },
        .stdout_limit = .unlimited,
        .stderr_limit = .unlimited,
    });
    defer allocator.free(result.stdout);
    defer allocator.free(result.stderr);

    try std.testing.expectEqual(std.process.Child.Term{ .exited = 0 }, result.term);
    const expected = try std.fmt.allocPrint(
        allocator,
        "savedcmd_sample_autoconf.o := {s}\n\n" ++
            "source_sample_autoconf.o := {s}\n\n" ++
            "deps_sample_autoconf.o := \\\n" ++
            "    $(wildcard include/config/ZIGUX_SRC) \\\n" ++
            "  {s} \\\n" ++
            "    $(wildcard include/config/ZIGUX_CFG) \\\n" ++
            "  {s} \\\n" ++
            "\n" ++
            "sample_autoconf.o: $(deps_sample_autoconf.o)\n\n" ++
            "$(deps_sample_autoconf.o):\n",
        .{ cmdline, source_path, config_path, tail_path },
    );
    defer allocator.free(expected);

    try std.testing.expectEqualStrings(expected, result.stdout);
    try std.testing.expectEqualStrings("", result.stderr);
    try std.testing.expect(std.mem.indexOf(u8, result.stdout, "include/generated/autoconf.h") == null);
    try std.testing.expect(std.mem.indexOf(u8, result.stdout, "CONFIG_AUTOCONF_ONLY") == null);
}
