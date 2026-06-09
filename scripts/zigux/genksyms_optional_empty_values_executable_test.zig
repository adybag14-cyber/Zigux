const std = @import("std");
const testing = std.testing;

const version_text = "genksyms version 2.5.60\n";

fn run(allocator: std.mem.Allocator, argv: []const []const u8) !std.process.RunResult {
    return std.process.run(allocator, testing.io, .{
        .argv = argv,
        .stdout_limit = .limited(8192),
        .stderr_limit = .limited(8192),
    });
}

fn expectExited(term: std.process.Child.Term, expected_code: u8) !void {
    switch (term) {
        .exited => |code| try testing.expectEqual(expected_code, code),
        else => return error.UnexpectedProcessTermination,
    }
}

test "genksyms executable rejects empty inline values for optional long options" {
    const allocator = testing.allocator;
    const exe_path = try std.fs.path.join(allocator, &.{ ".zig-cache", "lane23-optional-empty-exe", "genksyms-optional-empty" });
    defer allocator.free(exe_path);

    const mkdir_result = try run(allocator, &.{ "mkdir", "-p", std.fs.path.dirname(exe_path).? });
    defer allocator.free(mkdir_result.stdout);
    defer allocator.free(mkdir_result.stderr);
    try expectExited(mkdir_result.term, 0);
    try testing.expectEqualStrings("", mkdir_result.stdout);
    try testing.expectEqualStrings("", mkdir_result.stderr);

    const build_result = try run(allocator, &.{
        "zig",
        "build-exe",
        "scripts/zigux/genksyms.zig",
        "-femit-bin=.zig-cache/lane23-optional-empty-exe/genksyms-optional-empty",
        "--cache-dir",
        ".zig-cache/lane23-optional-empty-build",
        "--global-cache-dir",
        ".zig-cache/lane23-optional-empty-build/global",
    });
    defer allocator.free(build_result.stdout);
    defer allocator.free(build_result.stderr);
    try expectExited(build_result.term, 0);
    try testing.expectEqualStrings("", build_result.stdout);
    try testing.expectEqualStrings("", build_result.stderr);

    const warnings_empty = try run(allocator, &.{
        exe_path,
        "--warnings=",
        "unit.c",
    });
    defer allocator.free(warnings_empty.stdout);
    defer allocator.free(warnings_empty.stderr);
    try expectExited(warnings_empty.term, 1);
    try testing.expectEqualStrings("", warnings_empty.stdout);
    try testing.expect(std.mem.startsWith(
        u8,
        warnings_empty.stderr,
        "option '--warnings' doesn't allow an argument\n",
    ));

    const debug_empty_after_version = try run(allocator, &.{
        exe_path,
        "--version",
        "--debug=",
        "--warnings",
        "unit.c",
    });
    defer allocator.free(debug_empty_after_version.stdout);
    defer allocator.free(debug_empty_after_version.stderr);
    try expectExited(debug_empty_after_version.term, 1);
    try testing.expectEqualStrings("", debug_empty_after_version.stdout);
    try testing.expect(std.mem.startsWith(
        u8,
        debug_empty_after_version.stderr,
        version_text ++ "option '--debug' doesn't allow an argument\n",
    ));
}
