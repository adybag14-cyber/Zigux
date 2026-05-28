const std = @import("std");

const FixtureCase = struct {
    name: []const u8,
    depfile_path: []const u8,
    target: []const u8,
    cmdline: []const u8,
    expected_stderr_path: []const u8,
    expected_exit_code: u8,
};

const fixture_cases = [_]FixtureCase{
    .{
        .name = "sample_comment_only_stdout_full",
        .depfile_path = "zigux/tests/fixtures/fixdep/sample_comment_only.d",
        .target = "sample_comment_only_stdout_full.o",
        .cmdline = "clang -Iinclude -DZIGUX_SAMPLE -c zigux/tests/fixtures/fixdep/sample.c -o sample_comment_only_stdout_full.o",
        .expected_stderr_path = "zigux/tests/fixtures/fixdep/sample_comment_only_expected.stderr.txt",
        .expected_exit_code = 1,
    },
    .{
        .name = "sample_missing_dep_stdout_full",
        .depfile_path = "zigux/tests/fixtures/fixdep/sample_missing_dep.d",
        .target = "sample_missing_dep_stdout_full.o",
        .cmdline = "clang -c zigux/tests/fixtures/fixdep/sample_missing_dep_source.c -o sample_missing_dep_stdout_full.o",
        .expected_stderr_path = "zigux/tests/fixtures/fixdep/sample_missing_dep_expected.stderr.txt",
        .expected_exit_code = 2,
    },
    .{
        .name = "sample_output_write",
        .depfile_path = "zigux/tests/fixtures/fixdep/sample.d",
        .target = "sample_output_write.o",
        .cmdline = "clang -Iinclude -DZIGUX_SAMPLE -c zigux/tests/fixtures/fixdep/sample.c -o sample_output_write.o",
        .expected_stderr_path = "zigux/tests/fixtures/fixdep/sample_output_write_expected.stderr.txt",
        .expected_exit_code = 1,
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

fn runStdoutFullCase(allocator: std.mem.Allocator, fixture_case: FixtureCase) !void {
    const expected_stdout = try readFixture(
        allocator,
        "zigux/tests/fixtures/fixdep/sample_output_write_expected.txt",
        4 * 1024,
    );
    defer allocator.free(expected_stdout);
    try std.testing.expectEqual(@as(usize, 0), expected_stdout.len);

    const expected_stderr = try readFixture(allocator, fixture_case.expected_stderr_path, 4 * 1024);
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

    const dev_full = try std.Io.Dir.openFileAbsolute(std.testing.io, "/dev/full", .{ .mode = .write_only });
    defer dev_full.close(std.testing.io);

    var child = try std.process.spawn(std.testing.io, .{
        .argv = argv,
        .cwd = .{ .path = "." },
        .stdin = .ignore,
        .stdout = .{ .file = dev_full },
        .stderr = .pipe,
    });
    defer child.kill(std.testing.io);

    var stderr_reader = child.stderr.?.reader(std.testing.io, &.{});
    const stderr = try stderr_reader.interface.allocRemaining(allocator, .limited(4 * 1024));
    defer allocator.free(stderr);
    const term = try child.wait(std.testing.io);

    try std.testing.expectEqual(
        std.process.Child.Term{ .exited = fixture_case.expected_exit_code },
        term,
    );
    try std.testing.expectEqualStrings(expected_stderr, stderr);
}

test "fixdep replays the shipped stdout-full fixture matrix" {
    const allocator = std.testing.allocator;

    inline for (fixture_cases) |fixture_case| {
        try runStdoutFullCase(allocator, fixture_case);
    }
}
