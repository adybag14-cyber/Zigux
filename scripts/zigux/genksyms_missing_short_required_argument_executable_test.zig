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

test "genksyms executable reports missing short required argument with usage" {
    const exe_path = ".zig-cache/zigux-genksyms-missing-short-required-argument";
    const build_result = try run(&.{
        "zig",
        "build-exe",
        "scripts/zigux/genksyms.zig",
        "-femit-bin=.zig-cache/zigux-genksyms-missing-short-required-argument",
        "--cache-dir",
        ".zig-cache/lane23-missing-short-required-exe",
        "--global-cache-dir",
        ".zig-cache/lane23-missing-short-required-exe/global",
    });
    defer testing.allocator.free(build_result.stdout);
    defer testing.allocator.free(build_result.stderr);

    try testing.expectEqual(std.process.Child.Term{ .exited = 0 }, build_result.term);
    try testing.expectEqualStrings("", build_result.stdout);
    try testing.expectEqualStrings("", build_result.stderr);

    const run_result = try run(&.{ exe_path, "-T" });
    defer testing.allocator.free(run_result.stdout);
    defer testing.allocator.free(run_result.stderr);

    try testing.expectEqual(std.process.Child.Term{ .exited = 1 }, run_result.term);
    try testing.expectEqualStrings("", run_result.stdout);
    try testing.expectEqualStrings(
        "option requires an argument -- 'T'\n" ++ usage_text,
        run_result.stderr,
    );
}
