const std = @import("std");

fn tmpBasePath(tmp: anytype) ![]u8 {
    return std.fmt.allocPrint(
        std.testing.allocator,
        ".zig-cache/tmp/{s}",
        .{tmp.sub_path[0..]},
    );
}

test "fixdep ignores trailing comment lines on the public entry path" {
    var tmp = std.testing.tmpDir(.{});
    defer tmp.cleanup();

    const base_path = try tmpBasePath(tmp);
    defer std.testing.allocator.free(base_path);

    const cwd = try std.process.currentPathAlloc(std.testing.io, std.testing.allocator);
    defer std.testing.allocator.free(cwd);

    const absolute_base_path = try std.fmt.allocPrint(
        std.testing.allocator,
        "{s}/{s}",
        .{ cwd, base_path },
    );
    defer std.testing.allocator.free(absolute_base_path);

    const source_path = try std.fmt.allocPrint(
        std.testing.allocator,
        "{s}/trailing_comment_source.rmeta",
        .{absolute_base_path},
    );
    defer std.testing.allocator.free(source_path);

    const dep_path = try std.fmt.allocPrint(
        std.testing.allocator,
        "{s}/trailing_comment_dep.so",
        .{absolute_base_path},
    );
    defer std.testing.allocator.free(dep_path);

    const depfile_path = try std.fmt.allocPrint(
        std.testing.allocator,
        "{s}/sample_trailing_comment.d",
        .{absolute_base_path},
    );
    defer std.testing.allocator.free(depfile_path);

    const cmdline = try std.fmt.allocPrint(
        std.testing.allocator,
        "clang -c {s} -o sample_trailing_comment.o",
        .{source_path},
    );
    defer std.testing.allocator.free(cmdline);

    const depfile_text = try std.fmt.allocPrint(
        std.testing.allocator,
        "sample_trailing_comment.o: {s} {s}\n# generated trailer\n# still no second rule\n",
        .{ source_path, dep_path },
    );
    defer std.testing.allocator.free(depfile_text);

    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = "sample_trailing_comment.d",
        .data = depfile_text,
    });

    const argv: []const []const u8 = &.{
        "/usr/bin/env",
        "zig",
        "run",
        "scripts/zigux/fixdep.zig",
        "--",
        depfile_path,
        "sample_trailing_comment.o",
        cmdline,
    };
    const result = try std.process.run(std.testing.allocator, std.testing.io, .{
        .argv = argv,
        .cwd = .{ .path = "../.." },
        .stdout_limit = .unlimited,
        .stderr_limit = .unlimited,
    });
    defer std.testing.allocator.free(result.stdout);
    defer std.testing.allocator.free(result.stderr);

    const expected = try std.fmt.allocPrint(
        std.testing.allocator,
        "savedcmd_sample_trailing_comment.o := {s}\n\n" ++
            "source_sample_trailing_comment.o := {s}\n\n" ++
            "deps_sample_trailing_comment.o := \\\n" ++
            "  {s} \\\n" ++
            "\n" ++
            "sample_trailing_comment.o: $(deps_sample_trailing_comment.o)\n\n" ++
            "$(deps_sample_trailing_comment.o):\n",
        .{ cmdline, source_path, dep_path },
    );
    defer std.testing.allocator.free(expected);

    try std.testing.expectEqual(std.process.Child.Term{ .exited = 0 }, result.term);
    try std.testing.expectEqualStrings(expected, result.stdout);
    try std.testing.expectEqualStrings("", result.stderr);
}
