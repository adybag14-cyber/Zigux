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

fn expectExited(term: std.process.Child.Term, expected_code: u8) !void {
    switch (term) {
        .exited => |code| try testing.expectEqual(expected_code, code),
        else => return error.ExpectedProcessExit,
    }
}

test "unexpected inline long arguments fail after version side effects at executable boundary" {
    var tmp = testing.tmpDir(.{});
    defer tmp.cleanup();

    var exe_path_buffer: [256]u8 = undefined;
    const exe_path = try std.fmt.bufPrint(
        &exe_path_buffer,
        ".zig-cache/tmp/{s}/genksyms-unexpected-inline-long",
        .{tmp.sub_path},
    );
    const emit_arg = try std.fmt.allocPrint(testing.allocator, "-femit-bin={s}", .{exe_path});
    defer testing.allocator.free(emit_arg);

    const build_result = try std.process.run(testing.allocator, testing.io, .{
        .argv = &.{
            "zig",
            "build-exe",
            "scripts/zigux/genksyms.zig",
            emit_arg,
        },
        .stdout_limit = .limited(4096),
        .stderr_limit = .limited(4096),
    });
    defer testing.allocator.free(build_result.stdout);
    defer testing.allocator.free(build_result.stderr);

    try expectExited(build_result.term, 0);
    try testing.expectEqualStrings("", build_result.stdout);
    try testing.expectEqualStrings("", build_result.stderr);

    const cases = [_]struct {
        argv: []const []const u8,
        unexpected_option: []const u8,
        version_count: usize,
    }{
        .{
            .argv = &.{ exe_path, "-VV", "--debug=extra" },
            .unexpected_option = "--debug",
            .version_count = 2,
        },
        .{
            .argv = &.{ exe_path, "--version", "--quiet=nope" },
            .unexpected_option = "--quiet",
            .version_count = 1,
        },
    };

    for (cases) |case| {
        const run_result = try std.process.run(testing.allocator, testing.io, .{
            .argv = case.argv,
            .stdout_limit = .limited(16 * 1024),
            .stderr_limit = .limited(16 * 1024),
        });
        defer testing.allocator.free(run_result.stdout);
        defer testing.allocator.free(run_result.stderr);

        try expectExited(run_result.term, 1);
        try testing.expectEqualStrings("", run_result.stdout);

        var expected_stderr: std.Io.Writer.Allocating = .init(testing.allocator);
        defer expected_stderr.deinit();

        for (0..case.version_count) |_| {
            try expected_stderr.writer.writeAll("genksyms version 2.5.60\n");
        }
        try expected_stderr.writer.print("option '{s}' doesn't allow an argument\n", .{case.unexpected_option});
        try expected_stderr.writer.writeAll(usage_text);

        try testing.expectEqualStrings(expected_stderr.written(), run_result.stderr);
    }
}
