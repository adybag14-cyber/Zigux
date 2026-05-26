const std = @import("std");

const StdoutMode = enum {
    capture,
    dev_full,
};

const Case = struct {
    name: []const u8,
    depfile: []const u8,
    target: []const u8,
    cmdline: []const u8,
    expected_stdout: ?[]const u8 = null,
    expected_stderr: []const u8,
    expected_exit_code: u8,
    stdout_mode: StdoutMode = .capture,
};

const cases = [_]Case{
    .{
        .name = "sample_comment_only",
        .depfile = "zigux/tests/fixtures/fixdep/sample_comment_only.d",
        .target = "sample_comment_only.o",
        .cmdline = "clang -Iinclude -DZIGUX_SAMPLE -c zigux/tests/fixtures/fixdep/sample.c -o sample_comment_only.o",
        .expected_stdout = "zigux/tests/fixtures/fixdep/sample_comment_only_expected.txt",
        .expected_stderr = "zigux/tests/fixtures/fixdep/sample_comment_only_expected.stderr.txt",
        .expected_exit_code = 1,
    },
    .{
        .name = "sample_comment_only_stdout_full",
        .depfile = "zigux/tests/fixtures/fixdep/sample_comment_only.d",
        .target = "sample_comment_only_stdout_full.o",
        .cmdline = "clang -Iinclude -DZIGUX_SAMPLE -c zigux/tests/fixtures/fixdep/sample.c -o sample_comment_only_stdout_full.o",
        .expected_stderr = "zigux/tests/fixtures/fixdep/sample_comment_only_expected.stderr.txt",
        .expected_exit_code = 1,
        .stdout_mode = .dev_full,
    },
    .{
        .name = "sample_missing_dep",
        .depfile = "zigux/tests/fixtures/fixdep/sample_missing_dep.d",
        .target = "sample_missing_dep.o",
        .cmdline = "clang -c zigux/tests/fixtures/fixdep/sample_missing_dep_source.c -o sample_missing_dep.o",
        .expected_stdout = "zigux/tests/fixtures/fixdep/sample_missing_dep_expected.txt",
        .expected_stderr = "zigux/tests/fixtures/fixdep/sample_missing_dep_expected.stderr.txt",
        .expected_exit_code = 2,
    },
    .{
        .name = "sample_missing_dep_stdout_full",
        .depfile = "zigux/tests/fixtures/fixdep/sample_missing_dep.d",
        .target = "sample_missing_dep_stdout_full.o",
        .cmdline = "clang -c zigux/tests/fixtures/fixdep/sample_missing_dep_source.c -o sample_missing_dep_stdout_full.o",
        .expected_stderr = "zigux/tests/fixtures/fixdep/sample_missing_dep_expected.stderr.txt",
        .expected_exit_code = 2,
        .stdout_mode = .dev_full,
    },
    .{
        .name = "sample_output_write",
        .depfile = "zigux/tests/fixtures/fixdep/sample.d",
        .target = "sample_output_write.o",
        .cmdline = "clang -Iinclude -DZIGUX_SAMPLE -c zigux/tests/fixtures/fixdep/sample.c -o sample_output_write.o",
        .expected_stderr = "zigux/tests/fixtures/fixdep/sample_output_write_expected.stderr.txt",
        .expected_exit_code = 1,
        .stdout_mode = .dev_full,
    },
};

fn loadFixture(allocator: std.mem.Allocator, repo_root: []const u8, relative_path: []const u8) ![]u8 {
    const full_path = try std.fs.path.join(allocator, &.{ repo_root, relative_path });
    defer allocator.free(full_path);

    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, full_path, allocator, .limited(16 * 1024));
}

fn expectCaptureCase(allocator: std.mem.Allocator, repo_root: []const u8, case: Case) !void {
    const expected_stdout = try loadFixture(allocator, repo_root, case.expected_stdout.?);
    defer allocator.free(expected_stdout);

    const expected_stderr = try loadFixture(allocator, repo_root, case.expected_stderr);
    defer allocator.free(expected_stderr);

    const result = try std.process.run(allocator, std.testing.io, .{
        .argv = &.{
            "/usr/bin/env",
            "zig",
            "run",
            "scripts/zigux/fixdep.zig",
            "--",
            case.depfile,
            case.target,
            case.cmdline,
        },
        .cwd = .{ .path = repo_root },
        .stdout_limit = .limited(16 * 1024),
        .stderr_limit = .limited(16 * 1024),
    });
    defer allocator.free(result.stdout);
    defer allocator.free(result.stderr);

    try std.testing.expectEqual(std.process.Child.Term{ .exited = case.expected_exit_code }, result.term);
    try std.testing.expectEqualStrings(expected_stdout, result.stdout);
    try std.testing.expectEqualStrings(expected_stderr, result.stderr);
}

fn expectStdoutFullCase(allocator: std.mem.Allocator, repo_root: []const u8, case: Case) !void {
    const expected_stderr = try loadFixture(allocator, repo_root, case.expected_stderr);
    defer allocator.free(expected_stderr);

    const dev_full = try std.Io.Dir.openFileAbsolute(std.testing.io, "/dev/full", .{ .mode = .write_only });
    defer dev_full.close(std.testing.io);

    var child = try std.process.spawn(std.testing.io, .{
        .argv = &.{
            "/usr/bin/env",
            "zig",
            "run",
            "scripts/zigux/fixdep.zig",
            "--",
            case.depfile,
            case.target,
            case.cmdline,
        },
        .cwd = .{ .path = repo_root },
        .stdin = .ignore,
        .stdout = .{ .file = dev_full },
        .stderr = .pipe,
    });
    defer child.kill(std.testing.io);

    var stderr_reader = child.stderr.?.reader(std.testing.io, &.{});
    const stderr = try stderr_reader.interface.allocRemaining(allocator, .limited(16 * 1024));
    defer allocator.free(stderr);

    const term = try child.wait(std.testing.io);

    try std.testing.expectEqual(std.process.Child.Term{ .exited = case.expected_exit_code }, term);
    try std.testing.expectEqualStrings(expected_stderr, stderr);
}

fn expectFailureCase(allocator: std.mem.Allocator, repo_root: []const u8, case: Case) !void {
    switch (case.stdout_mode) {
        .capture => try expectCaptureCase(allocator, repo_root, case),
        .dev_full => try expectStdoutFullCase(allocator, repo_root, case),
    }
}

test "public entry failure matrix matches shipped fixdep outputs" {
    const repo_root = try std.Io.Dir.cwd().realPathFileAlloc(std.testing.io, "../..", std.testing.allocator);
    defer std.testing.allocator.free(repo_root);

    inline for (cases) |case| {
        try expectFailureCase(std.testing.allocator, repo_root, case);
    }
}
