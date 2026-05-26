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

test "fixdep keeps bare carriage-return escapes from continuing dependency lines on the public entry path" {
    var tmp = std.testing.tmpDir(.{});
    defer tmp.cleanup();

    const allocator = std.testing.allocator;
    const base_path = try absoluteTmpBasePath(allocator, tmp);
    defer allocator.free(base_path);

    const source_path = try std.fmt.allocPrint(
        allocator,
        "{s}/sample_bare_cr_source.rmeta",
        .{base_path},
    );
    defer allocator.free(source_path);

    const first_dep_path = try std.fmt.allocPrint(
        allocator,
        "{s}/dep-first.so",
        .{base_path},
    );
    defer allocator.free(first_dep_path);

    const ignored_source_path = try std.fmt.allocPrint(
        allocator,
        "{s}/ignored-source.rmeta",
        .{base_path},
    );
    defer allocator.free(ignored_source_path);

    const later_dep_path = try std.fmt.allocPrint(
        allocator,
        "{s}/later-dep.so",
        .{base_path},
    );
    defer allocator.free(later_dep_path);

    const depfile_path = try std.fmt.allocPrint(
        allocator,
        "{s}/sample_bare_cr_public_entry.d",
        .{base_path},
    );
    defer allocator.free(depfile_path);

    const cmdline = try std.fmt.allocPrint(
        allocator,
        "clang -c {s} -o sample_bare_cr_public_entry.o",
        .{source_path},
    );
    defer allocator.free(cmdline);

    const depfile_text = try std.fmt.allocPrint(
        allocator,
        "sample_bare_cr_public_entry.o: {s} {s} \\\rmodule/sample_bare_cr_public_entry.o: {s} {s}\r",
        .{ source_path, first_dep_path, ignored_source_path, later_dep_path },
    );
    defer allocator.free(depfile_text);

    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = "sample_bare_cr_public_entry.d",
        .data = depfile_text,
    });

    const argv: []const []const u8 = &.{
        "/usr/bin/env",
        "zig",
        "run",
        "fixdep.zig",
        "--",
        depfile_path,
        "sample_bare_cr_public_entry.o",
        cmdline,
    };
    const result = try std.process.run(allocator, std.testing.io, .{
        .argv = argv,
        .cwd = .{ .path = "." },
        .stdout_limit = .limited(4 * 1024),
        .stderr_limit = .limited(4 * 1024),
    });
    defer allocator.free(result.stdout);
    defer allocator.free(result.stderr);

    const expected_stdout = try std.fmt.allocPrint(
        allocator,
        "savedcmd_sample_bare_cr_public_entry.o := {s}\n\n" ++
            "source_sample_bare_cr_public_entry.o := {s}\n\n" ++
            "deps_sample_bare_cr_public_entry.o := \\\n" ++
            "  {s} \\\n" ++
            "  {s} \\\n" ++
            "\n" ++
            "sample_bare_cr_public_entry.o: $(deps_sample_bare_cr_public_entry.o)\n\n" ++
            "$(deps_sample_bare_cr_public_entry.o):\n",
        .{ cmdline, source_path, first_dep_path, later_dep_path },
    );
    defer allocator.free(expected_stdout);

    try std.testing.expectEqual(std.process.Child.Term{ .exited = 0 }, result.term);
    try std.testing.expectEqualStrings(expected_stdout, result.stdout);
    try std.testing.expectEqualStrings("", result.stderr);
}
