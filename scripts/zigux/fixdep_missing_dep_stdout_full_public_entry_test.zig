const std = @import("std");

test "fixdep preserves the shipped missing-dependency stderr when stdout is forced to /dev/full on the public entry path" {
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

    const dev_full = try std.Io.Dir.openFileAbsolute(std.testing.io, "/dev/full", .{ .mode = .write_only });
    defer dev_full.close(std.testing.io);

    var child = try std.process.spawn(std.testing.io, .{
        .argv = argv,
        .cwd = .{ .path = "../.." },
        .stdin = .ignore,
        .stdout = .{ .file = dev_full },
        .stderr = .pipe,
    });
    defer child.kill(std.testing.io);

    var stderr_reader = child.stderr.?.reader(std.testing.io, &.{});
    const stderr = try stderr_reader.interface.allocRemaining(std.testing.allocator, .limited(4 * 1024));
    defer std.testing.allocator.free(stderr);
    const term = try child.wait(std.testing.io);

    try std.testing.expectEqual(std.process.Child.Term{ .exited = 2 }, term);
    try std.testing.expectEqualStrings(expected_stderr, stderr);
}
