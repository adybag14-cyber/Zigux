const std = @import("std");
const testing = std.testing;

const version_line = "genksyms version 2.5.60\n";
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

fn expectHelpRun(exe_path: []const u8, args: []const []const u8, expected_version_count: usize) !void {
    var argv = std.ArrayList([]const u8).empty;
    defer argv.deinit(testing.allocator);
    try argv.append(testing.allocator, exe_path);
    try argv.appendSlice(testing.allocator, args);

    const result = try std.process.run(testing.allocator, testing.io, .{
        .argv = argv.items,
    });
    defer testing.allocator.free(result.stdout);
    defer testing.allocator.free(result.stderr);

    try testing.expectEqual(std.process.Child.Term{ .exited = 0 }, result.term);
    try testing.expectEqualStrings("", result.stdout);

    var expected = std.ArrayList(u8).empty;
    defer expected.deinit(testing.allocator);
    for (0..expected_version_count) |_| {
        try expected.appendSlice(testing.allocator, version_line);
    }
    try expected.appendSlice(testing.allocator, usage_text);
    try testing.expectEqualStrings(expected.items, result.stderr);
}

test "genksyms executable prints pure help without request JSON" {
    var tmp = testing.tmpDir(.{});
    defer tmp.cleanup();

    const exe_path = try std.fmt.allocPrint(
        testing.allocator,
        ".zig-cache/tmp/{s}/genksyms-help-proof",
        .{tmp.sub_path},
    );
    defer testing.allocator.free(exe_path);

    const emit_arg = try std.fmt.allocPrint(testing.allocator, "-femit-bin={s}", .{exe_path});
    defer testing.allocator.free(emit_arg);

    const build_result = try std.process.run(testing.allocator, testing.io, .{
        .argv = &.{ "zig", "build-exe", "scripts/zigux/genksyms.zig", emit_arg },
    });
    defer testing.allocator.free(build_result.stdout);
    defer testing.allocator.free(build_result.stderr);
    try testing.expectEqual(std.process.Child.Term{ .exited = 0 }, build_result.term);

    try expectHelpRun(exe_path, &.{"--help"}, 0);
    try expectHelpRun(exe_path, &.{"--he"}, 0);
    try expectHelpRun(exe_path, &.{"-h"}, 0);
    try expectHelpRun(exe_path, &.{ "--version", "--ver", "-Vh" }, 3);
}
