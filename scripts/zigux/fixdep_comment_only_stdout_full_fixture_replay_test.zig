const std = @import("std");

fn zigExe(allocator: std.mem.Allocator) ![]const u8 {
    return try allocator.dupe(u8, "zig");
}

test "sample_comment_only stdout-full fixture stays on the output-write path" {
    const allocator = std.testing.allocator;
    const root = try allocator.dupe(u8, ".");
    defer allocator.free(root);

    const zig = try zigExe(allocator);
    defer allocator.free(zig);

    var tmp_dir = std.testing.tmpDir(.{});
    defer tmp_dir.cleanup();

    const exe_path = try std.fmt.allocPrint(
        allocator,
        ".zig-cache/tmp/{s}/fixdep-comment-only-stdout-full",
        .{tmp_dir.sub_path},
    );
    defer allocator.free(exe_path);

    const expected_stdout = try std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        "zigux/tests/fixtures/fixdep/sample_output_write_expected.txt",
        allocator,
        .limited(1024),
    );
    defer allocator.free(expected_stdout);

    const expected_stderr = try std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        "zigux/tests/fixtures/fixdep/sample_comment_only_expected.stderr.txt",
        allocator,
        .limited(1024),
    );
    defer allocator.free(expected_stderr);

    const emit_arg = try std.fmt.allocPrint(allocator, "-femit-bin={s}", .{exe_path});
    defer allocator.free(emit_arg);

    const build = try std.process.run(allocator, std.testing.io, .{
        .argv = &.{ zig, "build-exe", "scripts/zigux/fixdep.zig", emit_arg },
        .cwd = .{ .path = root },
    });
    defer allocator.free(build.stdout);
    defer allocator.free(build.stderr);
    switch (build.term) {
        .exited => |code| try std.testing.expectEqual(@as(u8, 0), code),
        else => return error.UnexpectedChildTermination,
    }

    const command = try std.fmt.allocPrint(
        allocator,
        "'{s}' zigux/tests/fixtures/fixdep/sample_comment_only.d " ++
            "sample_comment_only_stdout_full.o " ++
            "\"clang -Iinclude -DZIGUX_SAMPLE -c zigux/tests/fixtures/fixdep/sample.c -o sample_comment_only_stdout_full.o\" >/dev/full",
        .{exe_path},
    );
    defer allocator.free(command);

    const result = try std.process.run(allocator, std.testing.io, .{
        .argv = &.{ "sh", "-c", command },
        .cwd = .{ .path = root },
    });
    defer allocator.free(result.stdout);
    defer allocator.free(result.stderr);

    switch (result.term) {
        .exited => |code| try std.testing.expectEqual(@as(u8, 1), code),
        else => return error.UnexpectedChildTermination,
    }

    try std.testing.expectEqualStrings(expected_stdout, result.stdout);
    try std.testing.expectEqualStrings(expected_stderr, result.stderr);
}
