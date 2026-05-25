const std = @import("std");
const fixture_depfile = "zigux/tests/fixtures/fixdep/sample_missing_dep.d";
const fixture_stdout = "zigux/tests/fixtures/fixdep/sample_missing_dep_expected.txt";
const fixture_stderr = "zigux/tests/fixtures/fixdep/sample_missing_dep_expected.stderr.txt";
const stdout_full_stderr = "zigux/tests/fixtures/fixdep/sample_missing_dep_expected.stderr.txt";
const base_target = "sample_missing_dep.o";
const base_cmdline = "clang -c zigux/tests/fixtures/fixdep/sample_missing_dep_source.c -o sample_missing_dep.o";
const target = "sample_missing_dep_stdout_full.o";
const cmdline = "clang -c zigux/tests/fixtures/fixdep/sample_missing_dep_source.c -o sample_missing_dep_stdout_full.o";

fn readFixture(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, allocator, .limited(4096));
}

test "fixdep replays the shipped missing-dependency fixture packet" {
    const allocator = std.testing.allocator;

    const expected_stdout = try readFixture(allocator, fixture_stdout);
    defer allocator.free(expected_stdout);

    const expected_stderr = try readFixture(allocator, fixture_stderr);
    defer allocator.free(expected_stderr);

    const argv: []const []const u8 = &.{
        "zig",
        "run",
        "scripts/zigux/fixdep.zig",
        "--",
        fixture_depfile,
        base_target,
        base_cmdline,
    };
    const result = try std.process.run(allocator, std.testing.io, .{
        .argv = argv,
        .cwd = .{ .path = "." },
        .stdout_limit = .unlimited,
        .stderr_limit = .unlimited,
    });
    defer allocator.free(result.stdout);
    defer allocator.free(result.stderr);

    try std.testing.expectEqual(std.process.Child.Term{ .exited = 2 }, result.term);
    try std.testing.expectEqualStrings(expected_stdout, result.stdout);
    try std.testing.expectEqualStrings(expected_stderr, result.stderr);
}

test "fixdep main preserves the missing-dependency stderr when stdout points at /dev/full" {
    const argv: []const []const u8 = &.{
        "zig",
        "run",
        "scripts/zigux/fixdep.zig",
        "--",
        fixture_depfile,
        target,
        cmdline,
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
    const stderr = try stderr_reader.interface.allocRemaining(std.testing.allocator, .limited(4096));
    defer std.testing.allocator.free(stderr);
    const term = try child.wait(std.testing.io);

    const expected_stderr = try readFixture(std.testing.allocator, stdout_full_stderr);
    defer std.testing.allocator.free(expected_stderr);

    try std.testing.expectEqual(std.process.Child.Term{ .exited = 2 }, term);
    try std.testing.expectEqualStrings(expected_stderr, stderr);
}
