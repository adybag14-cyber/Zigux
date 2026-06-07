const std = @import("std");
const testing = std.testing;

fn expectExitedZero(term: std.process.Child.Term) !void {
    switch (term) {
        .exited => |code| try testing.expectEqual(@as(u8, 0), code),
        else => return error.UnexpectedProcessTermination,
    }
}

fn run(allocator: std.mem.Allocator, argv: []const []const u8) !std.process.RunResult {
    return std.process.run(allocator, testing.io, .{
        .argv = argv,
        .stdout_limit = .limited(16 * 1024),
        .stderr_limit = .limited(16 * 1024),
    });
}

test "genksyms executable preserves separated empty required arguments" {
    const allocator = testing.allocator;

    const binary_dir = ".zig-cache/lane23-separated-empty-required-exe";
    const binary_path = binary_dir ++ "/genksyms-separated-empty-required";

    const mkdir = try run(allocator, &.{ "mkdir", "-p", binary_dir });
    defer allocator.free(mkdir.stdout);
    defer allocator.free(mkdir.stderr);
    try expectExitedZero(mkdir.term);
    try testing.expectEqualStrings("", mkdir.stdout);
    try testing.expectEqualStrings("", mkdir.stderr);

    const build = try run(allocator, &.{
        "zig",
        "build-exe",
        "scripts/zigux/genksyms.zig",
        "-femit-bin=" ++ binary_path,
        "--cache-dir",
        ".zig-cache/lane23-separated-empty-required-build",
        "--global-cache-dir",
        ".zig-cache/lane23-separated-empty-required-build/global",
    });
    defer allocator.free(build.stdout);
    defer allocator.free(build.stderr);
    try expectExitedZero(build.term);
    try testing.expectEqualStrings("", build.stdout);
    try testing.expectEqualStrings("", build.stderr);

    const child = try run(allocator, &.{
        binary_path,
        "--reference",
        "",
        "-T",
        "",
        "--warnings",
        "unit.c",
    });
    defer allocator.free(child.stdout);
    defer allocator.free(child.stderr);

    try expectExitedZero(child.term);
    try testing.expectEqualStrings("", child.stderr);
    try testing.expectEqualStrings(
        "{\"tool\":\"scripts/genksyms/genksyms\",\"stdin\":\"cpp-stream\",\"stdout\":\"symversions\",\"argv\":[\"scripts/genksyms/genksyms\",\"--reference\",\"\",\"-T\",\"\",\"--warnings\",\"unit.c\"],\"options\":{\"debug_level\":0,\"warnings\":true,\"dump_defs\":false,\"preserve\":false,\"reference_files\":[\"\"],\"dump_types_file\":\"\"}}\n",
        child.stdout,
    );
}
