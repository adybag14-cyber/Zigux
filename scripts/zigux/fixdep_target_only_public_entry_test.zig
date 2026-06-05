const std = @import("std");

test "target-only depfile preserves savedcmd before no-target parse error" {
    const allocator = std.testing.allocator;

    var temp_dir = std.testing.tmpDir(.{});
    defer temp_dir.cleanup();

    try temp_dir.dir.writeFile(std.testing.io, .{
        .sub_path = "target_only.d",
        .data = "target_only.o:\n",
    });

    const depfile_path = try std.fmt.allocPrint(
        allocator,
        ".zig-cache/tmp/{s}/target_only.d",
        .{temp_dir.sub_path},
    );
    defer allocator.free(depfile_path);

    const result = try std.process.run(allocator, std.testing.io, .{
        .argv = &.{
            "zig",
            "run",
            "scripts/zigux/fixdep.zig",
            "--",
            depfile_path,
            "target_only.o",
            "cc -c target_only.c -o target_only.o",
        },
    });
    defer allocator.free(result.stdout);
    defer allocator.free(result.stderr);

    try std.testing.expectEqual(
        std.process.Child.Term{ .exited = 1 },
        result.term,
    );
    try std.testing.expectEqualStrings(
        "savedcmd_target_only.o := cc -c target_only.c -o target_only.o\n\n",
        result.stdout,
    );
    try std.testing.expectEqualStrings(
        "fixdep: parse error; no targets found\n",
        result.stderr,
    );
}
