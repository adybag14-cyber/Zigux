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

test "genksyms executable honors short help inside a version cluster" {
    const allocator = testing.allocator;
    const exe_path = try std.fs.path.join(allocator, &.{ ".zig-cache", "lane23-short-help-cluster-exe", "genksyms-short-help-cluster" });
    defer allocator.free(exe_path);

    const mkdir_result = try run(allocator, &.{ "mkdir", "-p", std.fs.path.dirname(exe_path).? });
    defer allocator.free(mkdir_result.stdout);
    defer allocator.free(mkdir_result.stderr);
    try testing.expectEqual(std.process.Child.Term{ .exited = 0 }, mkdir_result.term);

    const build_result = try run(allocator, &.{
        "zig",
        "build-exe",
        "scripts/zigux/genksyms.zig",
        "-femit-bin=.zig-cache/lane23-short-help-cluster-exe/genksyms-short-help-cluster",
        "--cache-dir",
        ".zig-cache/lane23-short-help-cluster-build",
        "--global-cache-dir",
        ".zig-cache/lane23-short-help-cluster-build/global",
    });
    defer allocator.free(build_result.stdout);
    defer allocator.free(build_result.stderr);
    try testing.expectEqual(std.process.Child.Term{ .exited = 0 }, build_result.term);
    try testing.expectEqualStrings("", build_result.stdout);
    try testing.expectEqualStrings("", build_result.stderr);

    const short_help = try run(allocator, &.{
        exe_path,
        "-Vh",
        "-d",
        "--reference",
        "ignored.symref",
        "unit.c",
    });
    defer allocator.free(short_help.stdout);
    defer allocator.free(short_help.stderr);
    try testing.expectEqual(std.process.Child.Term{ .exited = 0 }, short_help.term);
    try testing.expectEqualStrings("", short_help.stdout);
    try testing.expectEqualStrings(version_text ++ usage_text, short_help.stderr);
}
