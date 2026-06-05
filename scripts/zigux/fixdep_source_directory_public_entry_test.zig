const std = @import("std");

fn publicFixdepArg() []const u8 {
    _ = std.Io.Dir.cwd().openFile(std.testing.io, "scripts/zigux/fixdep.zig", .{}) catch {
        return "fixdep.zig";
    };
    return "scripts/zigux/fixdep.zig";
}

test "source directory reports read error through the public entry path" {
    const allocator = std.testing.allocator;
    var tmp = std.testing.tmpDir(.{});
    defer tmp.cleanup();

    const source_path = try std.fmt.allocPrint(
        allocator,
        ".zig-cache/tmp/{s}/source_dir.c",
        .{tmp.sub_path},
    );
    defer allocator.free(source_path);
    const depfile_path = try std.fmt.allocPrint(
        allocator,
        ".zig-cache/tmp/{s}/source_dir.d",
        .{tmp.sub_path},
    );
    defer allocator.free(depfile_path);

    _ = try tmp.dir.createDirPathStatus(std.testing.io, "source_dir.c", .default_dir);
    const depfile_text = try std.fmt.allocPrint(
        allocator,
        "source_dir.o: {s}\n",
        .{source_path},
    );
    defer allocator.free(depfile_text);
    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = "source_dir.d",
        .data = depfile_text,
    });

    const cmdline = "clang -c source_dir.c -o source_dir.o";
    const result = try std.process.run(allocator, std.testing.io, .{
        .argv = &.{
            "zig",
            "run",
            publicFixdepArg(),
            "--",
            depfile_path,
            "source_dir.o",
            cmdline,
        },
    });
    defer allocator.free(result.stdout);
    defer allocator.free(result.stderr);

    try std.testing.expectEqual(std.process.Child.Term{ .exited = 2 }, result.term);

    const expected_stdout = try std.fmt.allocPrint(
        allocator,
        "savedcmd_source_dir.o := {s}\n\n" ++
            "source_source_dir.o := {s}\n\n" ++
            "deps_source_dir.o := \\\n",
        .{ cmdline, source_path },
    );
    defer allocator.free(expected_stdout);
    try std.testing.expectEqualStrings(expected_stdout, result.stdout);

    try std.testing.expectEqualStrings("fixdep: read: Is a directory\n", result.stderr);
}
