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

fn expectExit(result: std.process.RunResult, expected_code: u8) !void {
    switch (result.term) {
        .exited => |code| try testing.expectEqual(expected_code, code),
        else => return error.UnexpectedProcessTermination,
    }
}

fn runAndCapture(argv: []const []const u8) !std.process.RunResult {
    return try std.process.run(testing.allocator, testing.io, .{
        .argv = argv,
        .stdout_limit = .limited(8192),
        .stderr_limit = .limited(8192),
    });
}

test "genksyms executable reports ambiguous long options with version side effects" {
    const exe_path = ".zig-cache/genksyms-ambiguous-long-executable";
    const build_result = try runAndCapture(&.{
        "zig",
        "build-exe",
        "scripts/zigux/genksyms.zig",
        "-femit-bin=.zig-cache/genksyms-ambiguous-long-executable",
        "--cache-dir",
        ".zig-cache/lane23-ambiguous-long-executable",
        "--global-cache-dir",
        ".zig-cache/lane23-ambiguous-long-executable/global",
    });
    defer testing.allocator.free(build_result.stdout);
    defer testing.allocator.free(build_result.stderr);

    try expectExit(build_result, 0);
    try testing.expectEqualStrings("", build_result.stdout);
    try testing.expectEqualStrings("", build_result.stderr);

    const inline_result = try runAndCapture(&.{ exe_path, "--du=payload", "unit.c" });
    defer testing.allocator.free(inline_result.stdout);
    defer testing.allocator.free(inline_result.stderr);

    try expectExit(inline_result, 1);
    try testing.expectEqualStrings("", inline_result.stdout);
    try testing.expectEqualStrings(
        "option '--du' is ambiguous; possibilities: '--dump' '--dump-types'\n" ++ usage_text,
        inline_result.stderr,
    );

    const version_result = try runAndCapture(&.{ exe_path, "-V", "--d" });
    defer testing.allocator.free(version_result.stdout);
    defer testing.allocator.free(version_result.stderr);

    try expectExit(version_result, 1);
    try testing.expectEqualStrings("", version_result.stdout);
    try testing.expectEqualStrings(
        "genksyms version 2.5.60\n" ++
            "option '--d' is ambiguous; possibilities: '--debug' '--dump' '--dump-types'\n" ++
            usage_text,
        version_result.stderr,
    );
}
