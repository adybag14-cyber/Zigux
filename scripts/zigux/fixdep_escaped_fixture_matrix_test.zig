const std = @import("std");

const FixtureCase = struct {
    name: []const u8,
    depfile_path: []const u8,
    target: []const u8,
    cmdline: []const u8,
    expected_stdout_path: []const u8,
    expected_stderr_path: ?[]const u8,
    expected_exit_code: u8,
};

const fixture_cases = [_]FixtureCase{
    .{
        .name = "sample_escaped_space",
        .depfile_path = "zigux/tests/fixtures/fixdep/sample_escaped_space.d",
        .target = "sample_escaped_space.o",
        .cmdline = "clang -c zigux/tests/fixtures/fixdep/sample_escaped_space_source.c -o sample_escaped_space.o",
        .expected_stdout_path = "zigux/tests/fixtures/fixdep/sample_escaped_space_expected.txt",
        .expected_stderr_path = null,
        .expected_exit_code = 0,
    },
    .{
        .name = "sample_escaped_colon",
        .depfile_path = "zigux/tests/fixtures/fixdep/sample_escaped_colon.d",
        .target = "sample_escaped_colon.o",
        .cmdline = "clang -c zigux/tests/fixtures/fixdep/sample_escaped_colon_source.c -o sample_escaped_colon.o",
        .expected_stdout_path = "zigux/tests/fixtures/fixdep/sample_escaped_colon_expected.txt",
        .expected_stderr_path = null,
        .expected_exit_code = 0,
    },
    .{
        .name = "sample_double_backslash_comment",
        .depfile_path = "zigux/tests/fixtures/fixdep/sample_double_backslash_comment.d",
        .target = "sample_double_backslash_comment.o",
        .cmdline = "rustc --emit dep-info=sample_double_backslash_comment.d",
        .expected_stdout_path = "zigux/tests/fixtures/fixdep/sample_double_backslash_comment_expected.txt",
        .expected_stderr_path = "zigux/tests/fixtures/fixdep/sample_double_backslash_comment_expected.stderr.txt",
        .expected_exit_code = 2,
    },
};

fn readFixture(allocator: std.mem.Allocator, path: []const u8, max_bytes: usize) ![]u8 {
    return try std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        path,
        allocator,
        .limited(max_bytes),
    );
}

fn runCase(allocator: std.mem.Allocator, fixture_case: FixtureCase) !void {
    const expected_stdout = try readFixture(allocator, fixture_case.expected_stdout_path, 16 * 1024);
    defer allocator.free(expected_stdout);

    const expected_stderr = if (fixture_case.expected_stderr_path) |path|
        try readFixture(allocator, path, 4 * 1024)
    else
        try allocator.dupe(u8, "");
    defer allocator.free(expected_stderr);

    const argv: []const []const u8 = &.{
        "zig",
        "run",
        "scripts/zigux/fixdep.zig",
        "--",
        fixture_case.depfile_path,
        fixture_case.target,
        fixture_case.cmdline,
    };

    const result = try std.process.run(allocator, std.testing.io, .{
        .argv = argv,
        .cwd = .{ .path = "." },
        .stdout_limit = .unlimited,
        .stderr_limit = .unlimited,
    });
    defer allocator.free(result.stdout);
    defer allocator.free(result.stderr);

    try std.testing.expectEqual(
        std.process.Child.Term{ .exited = fixture_case.expected_exit_code },
        result.term,
    );
    try std.testing.expectEqualStrings(expected_stdout, result.stdout);
    try std.testing.expectEqualStrings(expected_stderr, result.stderr);
}

test "fixdep replays the shipped escaped fixture matrix" {
    const allocator = std.testing.allocator;

    inline for (fixture_cases) |fixture_case| {
        try runCase(allocator, fixture_case);
    }
}
