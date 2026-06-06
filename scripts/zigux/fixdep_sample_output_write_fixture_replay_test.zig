const std = @import("std");

fn readFixture(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, allocator, .limited(16 * 1024));
}

test "sample_output_write fixture replay preserves CLI stderr and exit code" {
    const allocator = std.testing.allocator;

    const expected_stderr = try readFixture(allocator, "zigux/tests/fixtures/fixdep/sample_output_write_expected.stderr.txt");
    defer allocator.free(expected_stderr);

    var tmp = std.testing.tmpDir(.{});
    defer tmp.cleanup();

    const binary_path = try std.fmt.allocPrint(
        allocator,
        ".zig-cache/tmp/{s}/fixdep-sample-output-write-replay",
        .{tmp.sub_path[0..]},
    );
    defer allocator.free(binary_path);
    const emit_bin_arg = try std.fmt.allocPrint(allocator, "-femit-bin={s}", .{binary_path});
    defer allocator.free(emit_bin_arg);

    const build_result = try std.process.run(allocator, std.testing.io, .{
        .argv = &.{
            "zig",
            "build-exe",
            "scripts/zigux/fixdep.zig",
            emit_bin_arg,
        },
        .stdout_limit = .limited(16 * 1024),
        .stderr_limit = .limited(64 * 1024),
    });
    defer allocator.free(build_result.stdout);
    defer allocator.free(build_result.stderr);
    try std.testing.expectEqual(std.process.Child.Term{ .exited = 0 }, build_result.term);

    const dev_full = try std.Io.Dir.openFileAbsolute(std.testing.io, "/dev/full", .{ .mode = .write_only });
    defer dev_full.close(std.testing.io);

    var child = try std.process.spawn(std.testing.io, .{
        .argv = &.{
            binary_path,
            "zigux/tests/fixtures/fixdep/sample.d",
            "sample_output_write.o",
            "clang -Iinclude -DZIGUX_SAMPLE -c zigux/tests/fixtures/fixdep/sample.c -o sample_output_write.o",
        },
        .stdin = .ignore,
        .stdout = .{ .file = dev_full },
        .stderr = .pipe,
    });
    defer child.kill(std.testing.io);

    var stderr_buffer: [1024]u8 = undefined;
    var stderr_reader = child.stderr.?.reader(std.testing.io, &stderr_buffer);
    const replay_stderr = try stderr_reader.interface.allocRemaining(allocator, .limited(16 * 1024));
    defer allocator.free(replay_stderr);

    const replay_term = try child.wait(std.testing.io);
    try std.testing.expectEqual(std.process.Child.Term{ .exited = 1 }, replay_term);
    try std.testing.expectEqualStrings(expected_stderr, replay_stderr);
    try std.testing.expect(std.mem.indexOf(u8, replay_stderr, "not all data was written") != null);
}
