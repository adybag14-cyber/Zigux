const std = @import("std");

test "fixdep keeps double-backslash hash comments aligned on the public entry path" {
    var tmp = std.testing.tmpDir(.{});
    defer tmp.cleanup();

    const base_path = try std.fmt.allocPrint(
        std.testing.allocator,
        ".zig-cache/tmp/{s}",
        .{tmp.sub_path[0..]},
    );
    defer std.testing.allocator.free(base_path);

    const depfile_path = try std.fmt.allocPrint(
        std.testing.allocator,
        "{s}/sample_double_backslash_comment.d",
        .{base_path},
    );
    defer std.testing.allocator.free(depfile_path);

    const cmdline = "clang -c sample_double_backslash_comment_source.c -o sample_double_backslash_comment.o";

    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = "sample_double_backslash_comment.d",
        .data = "sample_double_backslash_comment.o: sample_double_backslash_comment_source.rmeta missing\\\\#dep.h\n",
    });

    const argv: []const []const u8 = &.{
        "zig",
        "run",
        "fixdep.zig",
        "--",
        depfile_path,
        "sample_double_backslash_comment.o",
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

    try std.testing.expectEqual(std.process.Child.Term{ .exited = 2 }, result.term);
    try std.testing.expectEqualStrings(
        "savedcmd_sample_double_backslash_comment.o := " ++ cmdline ++ "\n\n" ++
            "source_sample_double_backslash_comment.o := sample_double_backslash_comment_source.rmeta\n\n" ++
            "deps_sample_double_backslash_comment.o := \\\n" ++
            "  missing\\\\ \\\n",
        result.stdout,
    );
    try std.testing.expectEqualStrings(
        "fixdep: error opening file: missing\\\\: No such file or directory\n",
        result.stderr,
    );
}
