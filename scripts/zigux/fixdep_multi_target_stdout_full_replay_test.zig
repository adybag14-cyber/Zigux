const std = @import("std");

const fixture_depfile = "zigux/tests/fixtures/fixdep/sample_multi_target.d";
const fixture_stdout = "zigux/tests/fixtures/fixdep/sample_multi_target_expected.txt";
const stdout_full_stdout = "zigux/tests/fixtures/fixdep/sample_output_write_expected.txt";
const stdout_full_stderr = "zigux/tests/fixtures/fixdep/sample_output_write_expected.stderr.txt";
const base_target = "module/sample2.o";
const base_cmdline = "clang -Iinclude -DZIGUX_MULTI -c zigux/tests/fixtures/fixdep/sample2.c -o module/sample2.o";
const target = "module/sample2_stdout_full.o";
const cmdline = "clang -Iinclude -DZIGUX_MULTI -c zigux/tests/fixtures/fixdep/sample2.c -o module/sample2_stdout_full.o";

fn readFixture(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, allocator, .limited(4096));
}

test "fixdep replays the shipped multi-target fixture packet" {
    const allocator = std.testing.allocator;

    const expected_stdout = try readFixture(allocator, fixture_stdout);
    defer allocator.free(expected_stdout);

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

    try std.testing.expectEqual(std.process.Child.Term{ .exited = 0 }, result.term);
    try std.testing.expectEqualStrings(expected_stdout, result.stdout);
    try std.testing.expectEqualStrings("", result.stderr);
}

test "fixdep main reports the output-write path when multi-target stdout points at /dev/full" {
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

    const expected_stdout = try readFixture(std.testing.allocator, stdout_full_stdout);
    defer std.testing.allocator.free(expected_stdout);
    const expected_stderr = try readFixture(std.testing.allocator, stdout_full_stderr);
    defer std.testing.allocator.free(expected_stderr);

    try std.testing.expectEqual(std.process.Child.Term{ .exited = 1 }, term);
    try std.testing.expectEqualStrings("", expected_stdout);
    try std.testing.expectEqualStrings(expected_stderr, stderr);
}
