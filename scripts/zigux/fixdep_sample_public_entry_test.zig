const std = @import("std");

test "fixdep replays the baseline sample fixture on the public entry path" {
    const depfile_path = "zigux/tests/fixtures/fixdep/sample.d";
    const target = "sample.o";
    const cmdline = "clang -Iinclude -DZIGUX_SAMPLE -c zigux/tests/fixtures/fixdep/sample.c -o sample.o";
    const expected_stdout_path = "../../zigux/tests/fixtures/fixdep/sample_expected.txt";

    const expected_stdout = try std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        expected_stdout_path,
        std.testing.allocator,
        .limited(16 * 1024),
    );
    defer std.testing.allocator.free(expected_stdout);

    const argv: []const []const u8 = &.{
        "/usr/bin/env",
        "zig",
        "run",
        "scripts/zigux/fixdep.zig",
        "--",
        depfile_path,
        target,
        cmdline,
    };

    const result = try std.process.run(std.testing.allocator, std.testing.io, .{
        .argv = argv,
        .cwd = .{ .path = "../.." },
        .stdout_limit = .unlimited,
        .stderr_limit = .unlimited,
    });
    defer std.testing.allocator.free(result.stdout);
    defer std.testing.allocator.free(result.stderr);

    try std.testing.expectEqual(std.process.Child.Term{ .exited = 0 }, result.term);
    try std.testing.expectEqualStrings(expected_stdout, result.stdout);
    try std.testing.expectEqualStrings("", result.stderr);
}
