const std = @import("std");

const fixture_dir = "zigux/tests/fixtures/fixdep";
const depfile_path = fixture_dir ++ "/sample_comment_only.d";
const expected_stdout_path = fixture_dir ++ "/sample_output_write_expected.txt";
const expected_stderr_path = fixture_dir ++ "/sample_comment_only_expected.stderr.txt";
const target = "sample_comment_only_stdout_full.o";
const cmdline = "clang -Iinclude -DZIGUX_SAMPLE -c zigux/tests/fixtures/fixdep/sample.c -o sample_comment_only_stdout_full.o";

fn readFixture(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return try std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, allocator, .limited(4096));
}

fn expectExited(term: std.process.Child.Term, code: u8) !void {
    switch (term) {
        .exited => |actual| try std.testing.expectEqual(code, actual),
        else => try std.testing.expect(false),
    }
}

test "fixdep comment-only stdout-full fixture replay preserves parse-error stderr" {
    const allocator = std.testing.allocator;

    const expected_stdout = try readFixture(allocator, expected_stdout_path);
    defer allocator.free(expected_stdout);

    const expected_stderr = try readFixture(allocator, expected_stderr_path);
    defer allocator.free(expected_stderr);

    var tmp = std.testing.tmpDir(.{});
    defer tmp.cleanup();

    const exe_name = if (@import("builtin").os.tag == .windows)
        "fixdep-comment-only-stdout-full.exe"
    else
        "fixdep-comment-only-stdout-full";

    const exe_path = try std.fs.path.join(allocator, &.{
        ".zig-cache",
        "tmp",
        tmp.sub_path[0..],
        exe_name,
    });
    defer allocator.free(exe_path);

    const emit_bin_arg = try std.mem.concat(allocator, u8, &.{ "-femit-bin=", exe_path });
    defer allocator.free(emit_bin_arg);

    const build = try std.process.run(allocator, std.testing.io, .{
        .argv = &.{
            "zig",
            "build-exe",
            "scripts/zigux/fixdep.zig",
            emit_bin_arg,
        },
        .stdout_limit = .limited(8192),
        .stderr_limit = .limited(8192),
    });
    defer {
        allocator.free(build.stdout);
        allocator.free(build.stderr);
    }
    try expectExited(build.term, 0);

    const replay = try std.process.run(allocator, std.testing.io, .{
        .argv = &.{
            "sh",
            "-c",
            "exec \"$1\" \"$2\" \"$3\" \"$4\" > /dev/full",
            "sh",
            exe_path,
            depfile_path,
            target,
            cmdline,
        },
        .stdout_limit = .limited(8192),
        .stderr_limit = .limited(8192),
    });
    defer {
        allocator.free(replay.stdout);
        allocator.free(replay.stderr);
    }

    try expectExited(replay.term, 1);
    try std.testing.expectEqualStrings(expected_stdout, replay.stdout);
    try std.testing.expectEqualStrings(expected_stderr, replay.stderr);
}
