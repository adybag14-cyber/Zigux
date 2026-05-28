const std = @import("std");

fn tmpBasePath(tmp: anytype) ![]u8 {
    return std.fmt.allocPrint(
        std.testing.allocator,
        ".zig-cache/tmp/{s}",
        .{tmp.sub_path[0..]},
    );
}

test "fixdep deduplicates repeated dependencies on the public entry path" {
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
        "{s}/duplicate_dependency_source.rmeta",
        .{absolute_base_path},
    );
    defer std.testing.allocator.free(source_path);

    const dep_path = try std.fmt.allocPrint(
        std.testing.allocator,
        "{s}/duplicate_dependency_dep.so",
        .{absolute_base_path},
    );
    defer std.testing.allocator.free(dep_path);

    const depfile_path = try std.fmt.allocPrint(
        std.testing.allocator,
        "{s}/sample_duplicate_dependency.d",
        .{absolute_base_path},
    );
    defer std.testing.allocator.free(depfile_path);

    const cmdline = try std.fmt.allocPrint(
        std.testing.allocator,
        "clang -c {s} -o sample_duplicate_dependency.o",
        .{source_path},
    );
    defer std.testing.allocator.free(cmdline);

    const depfile_text = try std.fmt.allocPrint(
        std.testing.allocator,
        "sample_duplicate_dependency.o: {s} {s} {s}\n",
        .{ source_path, dep_path, dep_path },
    );
    defer std.testing.allocator.free(depfile_text);

    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = "sample_duplicate_dependency.d",
        .data = depfile_text,
    });

    const argv: []const []const u8 = &.{
        "/usr/bin/env",
        "zig",
        "run",
        "scripts/zigux/fixdep.zig",
        "--",
        depfile_path,
        "sample_duplicate_dependency.o",
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
        "savedcmd_sample_duplicate_dependency.o := {s}\n\n" ++
            "source_sample_duplicate_dependency.o := {s}\n\n" ++
            "deps_sample_duplicate_dependency.o := \\" ++ "\n" ++
            "  {s} \\" ++ "\n" ++
            "\n" ++
            "sample_duplicate_dependency.o: $(deps_sample_duplicate_dependency.o)\n\n" ++
            "$(deps_sample_duplicate_dependency.o):\n",
        .{ cmdline, source_path, dep_path },
    );
    defer std.testing.allocator.free(expected);

    try std.testing.expectEqual(std.process.Child.Term{ .exited = 0 }, result.term);
    try std.testing.expectEqualStrings(expected, result.stdout);
    try std.testing.expectEqualStrings("", result.stderr);
}
