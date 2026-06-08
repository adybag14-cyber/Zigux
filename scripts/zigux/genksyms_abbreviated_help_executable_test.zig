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

fn expectExitedZero(term: std.process.Child.Term) !void {
    switch (term) {
        .exited => |code| try testing.expectEqual(@as(u8, 0), code),
        else => return error.UnexpectedProcessTermination,
    }
}

test "genksyms executable accepts abbreviated long help before later request input" {
    const allocator = testing.allocator;

    const binary_path = ".zig-cache/lane23-abbreviated-help/genksyms";
    const build_args = [_][]const u8{
        "zig",
        "build-exe",
        "scripts/zigux/genksyms.zig",
        "-femit-bin=" ++ binary_path,
        "--cache-dir",
        ".zig-cache/lane23-abbreviated-help/build",
        "--global-cache-dir",
        ".zig-cache/lane23-abbreviated-help/global",
    };
    const build = try std.process.run(allocator, testing.io, .{
        .argv = &build_args,
        .stderr_limit = .limited(16 * 1024),
        .stdout_limit = .limited(16 * 1024),
    });
    defer allocator.free(build.stdout);
    defer allocator.free(build.stderr);
    try expectExitedZero(build.term);
    try testing.expectEqualStrings("", build.stdout);
    try testing.expectEqualStrings("", build.stderr);

    const run_args = [_][]const u8{
        binary_path,
        "-V",
        "--hel",
        "-d",
        "--reference",
        "ignored.symref",
        "unit.c",
    };
    const run = try std.process.run(allocator, testing.io, .{
        .argv = &run_args,
        .stderr_limit = .limited(16 * 1024),
        .stdout_limit = .limited(16 * 1024),
    });
    defer allocator.free(run.stdout);
    defer allocator.free(run.stderr);

    try expectExitedZero(run.term);
    try testing.expectEqualStrings("", run.stdout);
    try testing.expectEqualStrings(
        "genksyms version 2.5.60\n" ++ usage_text,
        run.stderr,
    );
}
