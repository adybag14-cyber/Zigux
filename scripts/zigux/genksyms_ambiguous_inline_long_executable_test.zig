const std = @import("std");
const testing = std.testing;

const expected_usage =
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

fn runChild(allocator: std.mem.Allocator, argv: []const []const u8) !std.process.RunResult {
    return std.process.run(allocator, testing.io, .{
        .argv = argv,
    });
}

test "genksyms executable reports inline ambiguous long option with usage" {
    const allocator = testing.allocator;
    var tmp = testing.tmpDir(.{});
    defer tmp.cleanup();

    const exe_name = "genksyms-ambiguous-inline-long";
    const build_result = try runChild(allocator, &.{
        "zig",
        "build-exe",
        "scripts/zigux/genksyms.zig",
        "-fno-emit-bin",
        "-femit-bin=genksyms-ambiguous-inline-long",
    });
    defer allocator.free(build_result.stdout);
    defer allocator.free(build_result.stderr);

    try testing.expectEqual(std.process.Child.Term{ .exited = 0 }, build_result.term);
    try testing.expectEqualStrings("", build_result.stdout);
    try testing.expectEqualStrings("", build_result.stderr);

    const run_result = try runChild(allocator, &.{
        "./" ++ exe_name,
        "--du=foo",
    });
    defer allocator.free(run_result.stdout);
    defer allocator.free(run_result.stderr);

    try testing.expectEqual(std.process.Child.Term{ .exited = 1 }, run_result.term);
    try testing.expectEqualStrings("", run_result.stdout);
    try testing.expectEqualStrings(
        "option '--du' is ambiguous; possibilities: '--dump' '--dump-types'\n" ++ expected_usage,
        run_result.stderr,
    );
}
