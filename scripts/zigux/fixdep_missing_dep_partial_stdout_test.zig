const std = @import("std");

fn tmpBasePath(tmp: anytype) ![]u8 {
    return std.fmt.allocPrint(
        std.testing.allocator,
        ".zig-cache/tmp/{s}",
        .{tmp.sub_path[0..]},
    );
}

test "fixdep keeps partial stdout before missing dependency failures on the public entry path" {
    var tmp = std.testing.tmpDir(.{});
    defer tmp.cleanup();

    const allocator = std.testing.allocator;
    const base_path = try tmpBasePath(tmp);
    defer allocator.free(base_path);

    const depfile_path = try std.fmt.allocPrint(allocator, "{s}/sample_missing_dep.d", .{base_path});
    defer allocator.free(depfile_path);
    const source_path = try std.fmt.allocPrint(allocator, "{s}/sample_missing_dep_source.c", .{base_path});
    defer allocator.free(source_path);
    const missing_dep_path = try std.fmt.allocPrint(allocator, "{s}/sample_missing_dep.h", .{base_path});
    defer allocator.free(missing_dep_path);

    const cmdline = try std.fmt.allocPrint(
        allocator,
        "clang -c {s} -o sample_missing_dep.o",
        .{source_path},
    );
    defer allocator.free(cmdline);

    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = "sample_missing_dep_source.c",
        .data = "/* CONFIG_MISSING_SOURCE */\n",
    });

    const depfile_text = try std.fmt.allocPrint(
        allocator,
        "sample_missing_dep.o: {s} {s}\n",
        .{ source_path, missing_dep_path },
    );
    defer allocator.free(depfile_text);
    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = "sample_missing_dep.d",
        .data = depfile_text,
    });

    const argv: []const []const u8 = &.{
        "zig",
        "run",
        "fixdep.zig",
        "--",
        depfile_path,
        "sample_missing_dep.o",
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

    try std.testing.expectEqual(std.process.Child.Term{ .exited = 2 }, result.term);

    const expected = try std.fmt.allocPrint(
        allocator,
        "savedcmd_sample_missing_dep.o := {s}\n\n" ++
            "source_sample_missing_dep.o := {s}\n\n" ++
            "deps_sample_missing_dep.o := \\\n" ++
            "    $(wildcard include/config/MISSING_SOURCE) \\\n" ++
            "  {s} \\\n",
        .{ cmdline, source_path, missing_dep_path },
    );
    defer allocator.free(expected);

    const expected_stderr = try std.fmt.allocPrint(
        allocator,
        "fixdep: error opening file: {s}: No such file or directory\n",
        .{missing_dep_path},
    );
    defer allocator.free(expected_stderr);

    try std.testing.expectEqualStrings(expected, result.stdout);
    try std.testing.expectEqualStrings(expected_stderr, result.stderr);
}
