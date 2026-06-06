const std = @import("std");

const fixture_dir = "zigux/tests/fixtures/fixdep";

test "sample_multi_target fixture reports output write failure on dev_full stdout" {
    const allocator = std.testing.allocator;

    const exe_path = "/tmp/zigux_fixdep_sample_multi_target_stdout_full_fixture_replay";

    const build_result = try std.process.run(allocator, std.testing.io, .{
        .argv = &.{
            "zig",
            "build-exe",
            "scripts/zigux/fixdep.zig",
            "-femit-bin=" ++ exe_path,
        },
        .cwd = .{ .path = "." },
    });
    defer allocator.free(build_result.stdout);
    defer allocator.free(build_result.stderr);
    try std.testing.expectEqual(std.process.Child.Term{ .exited = 0 }, build_result.term);
    try std.testing.expectEqualStrings("", build_result.stderr);

    const replay_cmd = try std.fmt.allocPrint(
        allocator,
        "{s} {s}/sample_multi_target.d module/sample2_stdout_full.o 'clang -Iinclude -DZIGUX_MULTI -c {s}/sample2.c -o module/sample2_stdout_full.o' > /dev/full",
        .{ exe_path, fixture_dir, fixture_dir },
    );
    defer allocator.free(replay_cmd);

    const replay_result = try std.process.run(allocator, std.testing.io, .{
        .argv = &.{ "sh", "-c", replay_cmd },
        .cwd = .{ .path = "." },
    });
    defer allocator.free(replay_result.stdout);
    defer allocator.free(replay_result.stderr);

    try std.testing.expectEqual(std.process.Child.Term{ .exited = 1 }, replay_result.term);
    try std.testing.expectEqualStrings("", replay_result.stdout);
    try std.testing.expectEqualStrings(
        "fixdep: not all data was written to the output\n",
        replay_result.stderr,
    );
}
