const std = @import("std");

fn publicFixdepArg() []const u8 {
    _ = std.Io.Dir.cwd().openFile(std.testing.io, "scripts/zigux/fixdep.zig", .{}) catch {
        return "fixdep.zig";
    };
    return "scripts/zigux/fixdep.zig";
}

test "directory dependency reports read error through the public entry path" {
    const allocator = std.testing.allocator;
    var tmp = std.testing.tmpDir(.{});
    defer tmp.cleanup();

    const source_path = try std.fmt.allocPrint(
        allocator,
        ".zig-cache/tmp/{s}/directory_source.c",
        .{tmp.sub_path},
    );
    defer allocator.free(source_path);
    const directory_dep_path = try std.fmt.allocPrint(
        allocator,
        ".zig-cache/tmp/{s}/directory_dep.h",
        .{tmp.sub_path},
    );
    defer allocator.free(directory_dep_path);
    const depfile_path = try std.fmt.allocPrint(
        allocator,
        ".zig-cache/tmp/{s}/directory_dep.d",
        .{tmp.sub_path},
    );
    defer allocator.free(depfile_path);

    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = "directory_source.c",
        .data = "#define CONFIG_ZIGUX_DIRECTORY_SOURCE 1\n",
    });
    _ = try tmp.dir.createDirPathStatus(std.testing.io, "directory_dep.h", .default_dir);
    const depfile_text = try std.fmt.allocPrint(
        allocator,
        "directory_dep.o: {s} {s}\n",
        .{ source_path, directory_dep_path },
    );
    defer allocator.free(depfile_text);
    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = "directory_dep.d",
        .data = depfile_text,
    });

    const cmdline = "clang -c directory_source.c -o directory_dep.o";
    const result = try std.process.run(allocator, std.testing.io, .{
        .argv = &.{
            "zig",
            "run",
            publicFixdepArg(),
            "--",
            depfile_path,
            "directory_dep.o",
            cmdline,
        },
    });
    defer allocator.free(result.stdout);
    defer allocator.free(result.stderr);

    try std.testing.expectEqual(std.process.Child.Term{ .exited = 2 }, result.term);

    const expected_stdout = try std.fmt.allocPrint(
        allocator,
        "savedcmd_directory_dep.o := {s}\n\n" ++
            "source_directory_dep.o := {s}\n\n" ++
            "deps_directory_dep.o := \\\n" ++
            "    $(wildcard include/config/ZIGUX_DIRECTORY_SOURCE) \\\n" ++
            "  {s} \\\n",
        .{ cmdline, source_path, directory_dep_path },
    );
    defer allocator.free(expected_stdout);
    try std.testing.expectEqualStrings(expected_stdout, result.stdout);

    const expected_stderr = try std.fmt.allocPrint(
        allocator,
        "fixdep: read: Is a directory\n",
        .{},
    );
    defer allocator.free(expected_stderr);
    try std.testing.expectEqualStrings(expected_stderr, result.stderr);
}
