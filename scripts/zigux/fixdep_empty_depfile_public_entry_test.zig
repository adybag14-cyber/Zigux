const std = @import("std");

test "empty depfile preserves savedcmd before no-target parse error" {
    const allocator = std.testing.allocator;

    var temp_dir = std.testing.tmpDir(.{});
    defer temp_dir.cleanup();

    {
        const file = try temp_dir.dir.createFile(std.testing.io, "empty.d", .{});
        file.close(std.testing.io);
    }

    const depfile_path = try std.fmt.allocPrint(
        allocator,
        ".zig-cache/tmp/{s}/empty.d",
        .{temp_dir.sub_path},
    );
    defer allocator.free(depfile_path);

    const result = try std.process.run(allocator, std.testing.io, .{
        .argv = &.{
            "zig",
            "run",
            "fixdep.zig",
            "--",
            depfile_path,
            "empty.o",
            "cc -c empty.c -o empty.o",
        },
    });
    defer allocator.free(result.stdout);
    defer allocator.free(result.stderr);

    try std.testing.expectEqual(
        std.process.Child.Term{ .exited = 1 },
        result.term,
    );
    try std.testing.expectEqualStrings(
        "savedcmd_empty.o := cc -c empty.c -o empty.o\n\n",
        result.stdout,
    );
    try std.testing.expectEqualStrings(
        "fixdep: parse error; no targets found\n",
        result.stderr,
    );
}
