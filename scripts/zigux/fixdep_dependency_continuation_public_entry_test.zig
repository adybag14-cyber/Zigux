const std = @import("std");

test "fixdep replays the shipped dependency-continuation fixture on the public entry path" {
    const depfile_path = "zigux/tests/fixtures/fixdep/sample_dependency_continuation.d";
    const target = "sample_dependency_continuation.o";
    const cmdline =
        "clang -c zigux/tests/fixtures/fixdep/sample_dependency_continuation_source.c -o sample_dependency_continuation.o";
    const expected_stdout_path =
        "../../zigux/tests/fixtures/fixdep/sample_dependency_continuation_expected.txt";

    const expected_stdout = try std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        expected_stdout_path,
        std.testing.allocator,
        .limited(4 * 1024),
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
        .stdout_limit = .limited(4 * 1024),
        .stderr_limit = .limited(4 * 1024),
    });
    defer std.testing.allocator.free(result.stdout);
    defer std.testing.allocator.free(result.stderr);

    try std.testing.expectEqual(std.process.Child.Term{ .exited = 0 }, result.term);
    try std.testing.expectEqualStrings(expected_stdout, result.stdout);
    try std.testing.expectEqualStrings("", result.stderr);
}
