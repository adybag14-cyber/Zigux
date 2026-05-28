const std = @import("std");

const depfile_path = "zigux/tests/fixtures/fixdep/sample.d";
const expected_stdout_path = "zigux/tests/fixtures/fixdep/sample_output_write_expected.txt";
const expected_stderr_path = "zigux/tests/fixtures/fixdep/sample_output_write_expected.stderr.txt";
const target = "sample_output_write.o";
const cmdline = "clang -Iinclude -DZIGUX_SAMPLE -c zigux/tests/fixtures/fixdep/sample.c -o sample_output_write.o";

test "fixdep replays the shipped output-write fixture packet" {
    const allocator = std.testing.allocator;

    const expected_stdout = try std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        expected_stdout_path,
        allocator,
        .limited(4 * 1024),
    );
    defer allocator.free(expected_stdout);
    try std.testing.expectEqual(@as(usize, 0), expected_stdout.len);

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

    try std.testing.expectEqual(std.process.Child.Term{ .exited = 1 }, term);
    try std.testing.expectEqualStrings(expected_stderr, stderr);
}
