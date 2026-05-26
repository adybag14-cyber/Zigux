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

test "fixdep keeps comment-only parse errors aligned when stdout is full on the public entry path" {
    var tmp = std.testing.tmpDir(.{});
    defer tmp.cleanup();

    const allocator = std.testing.allocator;
    const base_path = try absoluteTmpBasePath(allocator, tmp);
    defer allocator.free(base_path);

    const depfile_path = try std.fmt.allocPrint(
        allocator,
        "{s}/sample_comment_only_stdout_full.d",
        .{base_path},
    );
    defer allocator.free(depfile_path);

    const cmdline = "clang -Iinclude -DZIGUX_SAMPLE -c zigux/tests/fixtures/fixdep/sample.c -o sample_comment_only_stdout_full.o";

    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = "sample_comment_only_stdout_full.d",
        .data = "# comment only\\\ncontinued comment\\\nstill no targets\n",
    });

    const argv: []const []const u8 = &.{
        "sh",
        "-c",
        "zig run fixdep.zig -- \"$1\" \"$2\" \"$3\" >/dev/full",
        "ignored",
        depfile_path,
        "sample_comment_only_stdout_full.o",
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

    try std.testing.expectEqual(std.process.Child.Term{ .exited = 1 }, result.term);
    try std.testing.expectEqualStrings("", result.stdout);
    try std.testing.expectEqualStrings(
        "fixdep: parse error; no targets found\n",
        result.stderr,
    );
}
