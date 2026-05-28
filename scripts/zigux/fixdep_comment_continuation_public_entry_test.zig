const std = @import("std");

test "fixdep replays the comment-continuation fixture on the public entry path" {
    const depfile_path = "zigux/tests/fixtures/fixdep/sample_comment_continuation.d";
    const target = "sample_comment_continuation.o";
    const cmdline = "clang -c zigux/tests/fixtures/fixdep/sample_comment_continuation_source.c -o sample_comment_continuation.o";
    const expected_path = "../../zigux/tests/fixtures/fixdep/sample_comment_continuation_expected.txt";
    const expected = try std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        expected_path,
        std.testing.allocator,
        .limited(16 * 1024),
    );
    defer std.testing.allocator.free(expected);

    const argv: []const []const u8 = &.{
        "/usr/bin/env",
        "zig",
        "run",
        "scripts/zigux/fixdep.zig",
        "--",
        depfile_path,
        target,
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

    try std.testing.expectEqual(std.process.Child.Term{ .exited = 0 }, result.term);
    try std.testing.expectEqualStrings(expected, result.stdout);
    try std.testing.expectEqualStrings("", result.stderr);
}
