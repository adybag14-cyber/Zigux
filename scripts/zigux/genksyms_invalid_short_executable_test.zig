const std = @import("std");
const testing = std.testing;

const version_text = "genksyms version 2.5.60\n";
const usage_text =
    "Usage:\n" ++
    "genksyms [-dDpwqhV] [-r file] [-T file] > /path/to/.tmp_obj.ver\n" ++
    "\n" ++
    " -d, --debug Increment the debug level (repeatable)\n" ++
    " -D, --dump Dump expanded symbol defs (for debugging only)\n" ++
    " -r, --reference file Read reference symbols from a file\n" ++
    " -T, --dump-types file Dump expanded types into file\n" ++
    " -p, --preserve Preserve reference modversions or fail\n" ++
    " -w, --warnings Enable warnings\n" ++
    " -q, --quiet Disable warnings (default)\n" ++
    " -h, --help Print this message\n" ++
    " -V, --version Print the release version\n";

fn run(allocator: std.mem.Allocator, argv: []const []const u8) !std.process.RunResult {
    return std.process.run(allocator, testing.io, .{
        .argv = argv,
        .stdout_limit = .limited(8192),
        .stderr_limit = .limited(8192),
    });
}

test "genksyms executable reports invalid short options with prior version side effects" {
    const allocator = testing.allocator;
    const exe_path = try std.fs.path.join(allocator, &.{ ".zig-cache", "lane23-invalid-short-exe", "genksyms-invalid-short" });
    defer allocator.free(exe_path);

    const mkdir_result = try run(allocator, &.{ "mkdir", "-p", std.fs.path.dirname(exe_path).? });
    defer allocator.free(mkdir_result.stdout);
    defer allocator.free(mkdir_result.stderr);
    try testing.expectEqual(std.process.Child.Term{ .exited = 0 }, mkdir_result.term);

    const build_result = try run(allocator, &.{
        "zig",
        "build-exe",
        "scripts/zigux/genksyms.zig",
        "-femit-bin=.zig-cache/lane23-invalid-short-exe/genksyms-invalid-short",
        "--cache-dir",
        ".zig-cache/lane23-invalid-short-build",
        "--global-cache-dir",
        ".zig-cache/lane23-invalid-short-build/global",
    });
    defer allocator.free(build_result.stdout);
    defer allocator.free(build_result.stderr);
    try testing.expectEqual(std.process.Child.Term{ .exited = 0 }, build_result.term);
    try testing.expectEqualStrings("", build_result.stdout);
    try testing.expectEqualStrings("", build_result.stderr);

    const bare_invalid = try run(allocator, &.{ exe_path, "-x" });
    defer allocator.free(bare_invalid.stdout);
    defer allocator.free(bare_invalid.stderr);
    try testing.expectEqual(std.process.Child.Term{ .exited = 1 }, bare_invalid.term);
    try testing.expectEqualStrings("", bare_invalid.stdout);
    try testing.expectEqualStrings("invalid option -- 'x'\n" ++ usage_text, bare_invalid.stderr);

    const versioned_invalid = try run(allocator, &.{ exe_path, "-VVx" });
    defer allocator.free(versioned_invalid.stdout);
    defer allocator.free(versioned_invalid.stderr);
    try testing.expectEqual(std.process.Child.Term{ .exited = 1 }, versioned_invalid.term);
    try testing.expectEqualStrings("", versioned_invalid.stdout);
    try testing.expectEqualStrings(version_text ++ version_text ++ "invalid option -- 'x'\n" ++ usage_text, versioned_invalid.stderr);
}
