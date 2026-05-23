const std = @import("std");

test "fixdep reads depfiles larger than the legacy one mebibyte ceiling on the public entry path" {
    var tmp = std.testing.tmpDir(.{});
    defer tmp.cleanup();

    const relative_base_path = try std.fmt.allocPrint(
        std.testing.allocator,
        ".zig-cache/tmp/{s}",
        .{tmp.sub_path[0..]},
    );
    defer std.testing.allocator.free(relative_base_path);

    const base_path = try std.Io.Dir.cwd().realPathFileAlloc(std.testing.io, relative_base_path, std.testing.allocator);
    defer std.testing.allocator.free(base_path);

    const source_path = try std.fmt.allocPrint(
        std.testing.allocator,
        "{s}/sample_large_depfile_public_source.rmeta",
        .{base_path},
    );
    defer std.testing.allocator.free(source_path);

    const config_dep_path = try std.fmt.allocPrint(
        std.testing.allocator,
        "{s}/sample_large_depfile_public-config.h",
        .{base_path},
    );
    defer std.testing.allocator.free(config_dep_path);

    const depfile_path = try std.fmt.allocPrint(
        std.testing.allocator,
        "{s}/sample_large_depfile_public.d",
        .{base_path},
    );
    defer std.testing.allocator.free(depfile_path);

    const cmdline = try std.fmt.allocPrint(
        std.testing.allocator,
        "clang -c {s} -o sample_large_depfile_public.o",
        .{source_path},
    );
    defer std.testing.allocator.free(cmdline);

    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = "sample_large_depfile_public_source.rmeta",
        .data = "",
    });
    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = "sample_large_depfile_public-config.h",
        .data = "#define CONFIG_ZIGUX_LARGE_DEPFILE_PUBLIC 1\n",
    });

    const padding_len = (1024 * 1024) + 64;
    var depfile_text = try std.ArrayList(u8).initCapacity(
        std.testing.allocator,
        source_path.len + config_dep_path.len + padding_len + 160,
    );
    defer depfile_text.deinit(std.testing.allocator);

    const depfile_header = try std.fmt.allocPrint(
        std.testing.allocator,
        "sample_large_depfile_public.o: {s} {s}\n# ",
        .{ source_path, config_dep_path },
    );
    defer std.testing.allocator.free(depfile_header);

    try depfile_text.appendSlice(std.testing.allocator, depfile_header);
    try depfile_text.appendNTimes(std.testing.allocator, 'a', padding_len);
    try depfile_text.append(std.testing.allocator, '\n');

    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = "sample_large_depfile_public.d",
        .data = depfile_text.items,
    });

    const argv: []const []const u8 = &.{
        "zig",
        "run",
        "fixdep.zig",
        "--",
        depfile_path,
        "sample_large_depfile_public.o",
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
        "savedcmd_sample_large_depfile_public.o := {s}\n\n" ++
            "source_sample_large_depfile_public.o := {s}\n\n" ++
            "deps_sample_large_depfile_public.o := \\\n" ++
            "  {s} \\\n" ++
            "    $(wildcard include/config/ZIGUX_LARGE_DEPFILE_PUBLIC) \\\n" ++
            "\n" ++
            "sample_large_depfile_public.o: $(deps_sample_large_depfile_public.o)\n\n" ++
            "$(deps_sample_large_depfile_public.o):\n",
        .{ cmdline, source_path, config_dep_path },
    );
    defer std.testing.allocator.free(expected);

    try std.testing.expectEqualStrings(expected, result.stdout);
    try std.testing.expectEqualStrings("", result.stderr);
}
