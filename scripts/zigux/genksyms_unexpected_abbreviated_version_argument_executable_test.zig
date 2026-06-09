const std = @import("std");
const testing = std.testing;

const genksyms_source = "scripts/zigux/genksyms.zig";
const genksyms_binary_name = "zigux-genksyms-unexpected-abbrev-version";

fn buildGenksymsBinary(allocator: std.mem.Allocator) ![]const u8 {
    const binary_path = try std.fs.path.join(allocator, &.{
        genksyms_binary_name,
    });
    errdefer allocator.free(binary_path);
    const emit_bin_arg = try std.fmt.allocPrint(allocator, "-femit-bin={s}", .{binary_path});
    defer allocator.free(emit_bin_arg);

    const build_result = try std.process.run(allocator, testing.io, .{
        .argv = &.{
            "zig",
            "build-exe",
            genksyms_source,
            "-O",
            "Debug",
            "--name",
            genksyms_binary_name,
            "--cache-dir",
            "zig-cache",
            "--global-cache-dir",
            "zig-cache/global",
            emit_bin_arg,
        },
    });
    defer allocator.free(build_result.stdout);
    defer allocator.free(build_result.stderr);

    switch (build_result.term) {
        .exited => |code| try testing.expectEqual(@as(u8, 0), code),
        else => return error.BuildDidNotExit,
    }
    try testing.expectEqualStrings("", build_result.stderr);
    return binary_path;
}

test "executable canonicalizes unexpected abbreviated version argument" {
    const allocator = testing.allocator;
    const binary_path = try buildGenksymsBinary(allocator);
    defer allocator.free(binary_path);
    const binary_argv = try std.fmt.allocPrint(allocator, "./{s}", .{binary_path});
    defer allocator.free(binary_argv);

    const result = try std.process.run(allocator, testing.io, .{
        .argv = &.{
            binary_argv,
            "--ver=extra",
        },
    });
    defer allocator.free(result.stdout);
    defer allocator.free(result.stderr);

    switch (result.term) {
        .exited => |code| try testing.expectEqual(@as(u8, 1), code),
        else => return error.RunDidNotExit,
    }
    try testing.expectEqualStrings("", result.stdout);
    try testing.expectEqualStrings(
        "option '--version' doesn't allow an argument\n" ++
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
            " -V, --version Print the release version\n",
        result.stderr,
    );
}
