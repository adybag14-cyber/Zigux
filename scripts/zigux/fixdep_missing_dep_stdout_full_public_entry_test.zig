const std = @import("std");

test "fixdep keeps missing-dependency stderr aligned when stdout is full on the public entry path" {
    const depfile_path = "zigux/tests/fixtures/fixdep/sample_missing_dep.d";
    const target = "sample_missing_dep_stdout_full.o";
    const cmdline = "clang -c zigux/tests/fixtures/fixdep/sample_missing_dep_source.c -o sample_missing_dep_stdout_full.o";
    const expected_stderr_path = "../../zigux/tests/fixtures/fixdep/sample_missing_dep_expected.stderr.txt";
    const expected_stderr = try std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        expected_stderr_path,
        std.testing.allocator,
        .limited(4 * 1024),
    );
    defer std.testing.allocator.free(expected_stderr);
    const trimmed_expected_stderr = std.mem.trimEnd(u8, expected_stderr, "\n");

    const argv: []const []const u8 = &.{
        "sh",
        "-c",
        "zig run scripts/zigux/fixdep.zig -- \"$1\" \"$2\" \"$3\" >/dev/full",
        "ignored",
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

    try std.testing.expectEqual(std.process.Child.Term{ .exited = 2 }, result.term);
    try std.testing.expectEqualStrings("", result.stdout);
    try std.testing.expectEqualStrings(trimmed_expected_stderr, std.mem.trimEnd(u8, result.stderr, "\n"));
}
