const std = @import("std");

const testing = std.testing;

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

fn run(argv: []const []const u8) !std.process.RunResult {
    return try std.process.run(testing.allocator, testing.io, .{
        .argv = argv,
        .stdout_limit = .limited(4096),
        .stderr_limit = .limited(4096),
    });
}

test "genksyms executable reports unexpected long option arguments with usage" {
    const exe_path = ".zig-cache/zigux-genksyms-unexpected-long-argument";
    const build_result = try run(&.{
        "zig",
        "build-exe",
        "scripts/zigux/genksyms.zig",
        "-femit-bin=.zig-cache/zigux-genksyms-unexpected-long-argument",
        "--cache-dir",
        ".zig-cache/lane23-unexpected-long-exe",
        "--global-cache-dir",
        ".zig-cache/lane23-unexpected-long-exe/global",
    });
    defer testing.allocator.free(build_result.stdout);
    defer testing.allocator.free(build_result.stderr);

    try testing.expectEqual(std.process.Child.Term{ .exited = 0 }, build_result.term);
    try testing.expectEqualStrings("", build_result.stdout);
    try testing.expectEqualStrings("", build_result.stderr);

    const help_result = try run(&.{ exe_path, "--help=extra" });
    defer testing.allocator.free(help_result.stdout);
    defer testing.allocator.free(help_result.stderr);

    try testing.expectEqual(std.process.Child.Term{ .exited = 1 }, help_result.term);
    try testing.expectEqualStrings("", help_result.stdout);
    try testing.expectEqualStrings(
        "option '--help' doesn't allow an argument\n" ++ usage_text,
        help_result.stderr,
    );

    const debug_result = try run(&.{ exe_path, "-V", "--debug=2" });
    defer testing.allocator.free(debug_result.stdout);
    defer testing.allocator.free(debug_result.stderr);

    try testing.expectEqual(std.process.Child.Term{ .exited = 1 }, debug_result.term);
    try testing.expectEqualStrings("", debug_result.stdout);
    try testing.expectEqualStrings(
        "genksyms version 2.5.60\n" ++
            "option '--debug' doesn't allow an argument\n" ++
            usage_text,
        debug_result.stderr,
    );
}
