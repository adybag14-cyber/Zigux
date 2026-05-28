const std = @import("std");

const Case = struct {
    name: []const u8,
    depfile: []const u8,
    target: []const u8,
    cmdline: []const u8,
    expected: []const u8,
};

const cases = [_]Case{
    .{
        .name = "sample",
        .depfile = "zigux/tests/fixtures/fixdep/sample.d",
        .target = "sample.o",
        .cmdline = "clang -Iinclude -DZIGUX_SAMPLE -c zigux/tests/fixtures/fixdep/sample.c -o sample.o",
        .expected = "zigux/tests/fixtures/fixdep/sample_expected.txt",
    },
    .{
        .name = "sample_multi_target",
        .depfile = "zigux/tests/fixtures/fixdep/sample_multi_target.d",
        .target = "module/sample2.o",
        .cmdline = "clang -Iinclude -DZIGUX_MULTI -c zigux/tests/fixtures/fixdep/sample2.c -o module/sample2.o",
        .expected = "zigux/tests/fixtures/fixdep/sample_multi_target_expected.txt",
    },
    .{
        .name = "sample_escaped_space",
        .depfile = "zigux/tests/fixtures/fixdep/sample_escaped_space.d",
        .target = "sample_escaped_space.o",
        .cmdline = "clang -c zigux/tests/fixtures/fixdep/sample_escaped_space_source.c -o sample_escaped_space.o",
        .expected = "zigux/tests/fixtures/fixdep/sample_escaped_space_expected.txt",
    },
    .{
        .name = "sample_escaped_colon",
        .depfile = "zigux/tests/fixtures/fixdep/sample_escaped_colon.d",
        .target = "sample_escaped_colon.o",
        .cmdline = "clang -c zigux/tests/fixtures/fixdep/sample_escaped_colon_source.c -o sample_escaped_colon.o",
        .expected = "zigux/tests/fixtures/fixdep/sample_escaped_colon_expected.txt",
    },
};

fn expectPublicEntryCase(allocator: std.mem.Allocator, repo_root: []const u8, case: Case) !void {
    const expected_path = try std.fs.path.join(allocator, &.{ repo_root, case.expected });
    defer allocator.free(expected_path);

    const expected = try std.Io.Dir.cwd().readFileAlloc(std.testing.io, expected_path, allocator, .unlimited);
    defer allocator.free(expected);

    const result = try std.process.run(allocator, std.testing.io, .{
        .argv = &.{
            "zig",
            "run",
            "scripts/zigux/fixdep.zig",
            "--",
            case.depfile,
            case.target,
            case.cmdline,
        },
        .cwd = .{ .path = repo_root },
    });
    defer allocator.free(result.stdout);
    defer allocator.free(result.stderr);

    try std.testing.expectEqual(@as(std.process.Child.Term, .{ .exited = 0 }), result.term);
    try std.testing.expectEqualStrings(expected, result.stdout);
    try std.testing.expectEqualStrings("", result.stderr);
}

test "public entry success matrix matches shipped fixdep outputs" {
    const repo_root = try std.Io.Dir.cwd().realPathFileAlloc(std.testing.io, "../..", std.testing.allocator);
    defer std.testing.allocator.free(repo_root);

    inline for (cases) |case| {
        try expectPublicEntryCase(std.testing.allocator, repo_root, case);
    }
}
