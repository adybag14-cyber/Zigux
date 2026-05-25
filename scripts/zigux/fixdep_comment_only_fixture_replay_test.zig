const std = @import("std");

const depfile_path = "zigux/tests/fixtures/fixdep/sample_comment_only.d";
const expected_stdout_path = "zigux/tests/fixtures/fixdep/sample_comment_only_expected.txt";
const expected_stderr_path = "zigux/tests/fixtures/fixdep/sample_comment_only_expected.stderr.txt";
const target = "sample_comment_only.o";
const cmdline = "clang -Iinclude -DZIGUX_SAMPLE -c zigux/tests/fixtures/fixdep/sample.c -o sample_comment_only.o";

test "fixdep replays the shipped comment-only fixture packet" {
    const allocator = std.testing.allocator;

    const expected_stdout = try std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        expected_stdout_path,
        allocator,
        .limited(16 * 1024),
    );
    defer allocator.free(expected_stdout);

    const expected_stderr = try std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        expected_stderr_path,
        allocator,
        .limited(4 * 1024),
    );
    defer allocator.free(expected_stderr);

    const argv: []const []const u8 = &.{
        "zig",
        "run",
        "scripts/zigux/fixdep.zig",
        "--",
        depfile_path,
        target,
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
    try std.testing.expectEqualStrings(expected_stdout, result.stdout);
    try std.testing.expectEqualStrings(expected_stderr, result.stderr);
}
