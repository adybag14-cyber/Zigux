const std = @import("std");

fn readFixture(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, allocator, .limited(16 * 1024));
}

test "sample_comment_only fixture replay preserves CLI stdout stderr and exit code" {
    const allocator = std.testing.allocator;

    const expected_stdout = try readFixture(allocator, "zigux/tests/fixtures/fixdep/sample_comment_only_expected.txt");
    defer allocator.free(expected_stdout);
    const expected_stderr = try readFixture(allocator, "zigux/tests/fixtures/fixdep/sample_comment_only_expected.stderr.txt");
    defer allocator.free(expected_stderr);

    var tmp = std.testing.tmpDir(.{});
    defer tmp.cleanup();

    const binary_path = try std.fmt.allocPrint(
        allocator,
        ".zig-cache/tmp/{s}/fixdep-sample-comment-only-replay",
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

    const replay_result = try std.process.run(allocator, std.testing.io, .{
        .argv = &.{
            binary_path,
            "zigux/tests/fixtures/fixdep/sample_comment_only.d",
            "sample_comment_only.o",
            "clang -Iinclude -DZIGUX_SAMPLE -c zigux/tests/fixtures/fixdep/sample.c -o sample_comment_only.o",
        },
        .stdout_limit = .limited(16 * 1024),
        .stderr_limit = .limited(16 * 1024),
    });
    defer allocator.free(replay_result.stdout);
    defer allocator.free(replay_result.stderr);

    try std.testing.expectEqual(std.process.Child.Term{ .exited = 1 }, replay_result.term);
    try std.testing.expectEqualStrings(expected_stdout, replay_result.stdout);
    try std.testing.expectEqualStrings(expected_stderr, replay_result.stderr);
    try std.testing.expect(std.mem.indexOf(u8, replay_result.stdout, "savedcmd_sample_comment_only.o") != null);
    try std.testing.expect(std.mem.indexOf(u8, replay_result.stderr, "no targets found") != null);
}
