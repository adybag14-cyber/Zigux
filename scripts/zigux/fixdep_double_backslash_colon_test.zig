const std = @import("std");

test "fixdep keeps double-backslash colon splits aligned on the public entry path" {
    var tmp = std.testing.tmpDir(.{});
    defer tmp.cleanup();

    const base_path = try std.fmt.allocPrint(
        std.testing.allocator,
        ".zig-cache/tmp/{s}",
        .{tmp.sub_path[0..]},
    );
    defer std.testing.allocator.free(base_path);

    const source_path = try std.fmt.allocPrint(
        std.testing.allocator,
        "{s}/sample_double_backslash_colon_source.rmeta",
        .{base_path},
    );
    defer std.testing.allocator.free(source_path);

    const dep_path = try std.fmt.allocPrint(
        std.testing.allocator,
        "{s}/missing\\\\",
        .{base_path},
    );
    defer std.testing.allocator.free(dep_path);

    const depfile_path = try std.fmt.allocPrint(
        std.testing.allocator,
        "{s}/sample_double_backslash_colon.d",
        .{base_path},
    );
    defer std.testing.allocator.free(depfile_path);

    const cmdline = try std.fmt.allocPrint(
        std.testing.allocator,
        "clang -c {s} -o sample_double_backslash_colon.o",
        .{source_path},
    );
    defer std.testing.allocator.free(cmdline);

    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = "sample_double_backslash_colon_source.rmeta",
        .data = "",
    });
    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = "missing\\\\",
        .data = "#define CONFIG_ZIGUX_DOUBLE_BACKSLASH_COLON 1\n",
    });
    const depfile_text = try std.fmt.allocPrint(
        std.testing.allocator,
        "sample_double_backslash_colon.o: {s} {s}:ignored_second_source.rmeta\n",
        .{ source_path, dep_path },
    );
    defer std.testing.allocator.free(depfile_text);
    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = "sample_double_backslash_colon.d",
        .data = depfile_text,
    });

    const argv: []const []const u8 = &.{
        "zig",
        "run",
        "fixdep.zig",
        "--",
        depfile_path,
        "sample_double_backslash_colon.o",
        cmdline,
    };
    const result = try std.process.run(std.testing.allocator, std.testing.io, .{
        .argv = argv,
        .cwd = .{ .path = "." },
        .stdout_limit = .unlimited,
        .stderr_limit = .unlimited,
    });
    defer std.testing.allocator.free(result.stdout);
    defer std.testing.allocator.free(result.stderr);

    try std.testing.expectEqual(std.process.Child.Term{ .exited = 0 }, result.term);
    const expected = try std.fmt.allocPrint(
        std.testing.allocator,
        "savedcmd_sample_double_backslash_colon.o := {s}\n\n" ++
            "source_sample_double_backslash_colon.o := {s}\n\n" ++
            "deps_sample_double_backslash_colon.o := \\\n" ++
            "  {s} \\\n" ++
            "    $(wildcard include/config/ZIGUX_DOUBLE_BACKSLASH_COLON) \\\n" ++
            "\n" ++
            "sample_double_backslash_colon.o: $(deps_sample_double_backslash_colon.o)\n\n" ++
            "$(deps_sample_double_backslash_colon.o):\n",
        .{ cmdline, source_path, dep_path },
    );
    defer std.testing.allocator.free(expected);

    try std.testing.expectEqualStrings(expected, result.stdout);
    try std.testing.expectEqualStrings("", result.stderr);
}
