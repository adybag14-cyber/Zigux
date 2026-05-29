const std = @import("std");
const genksyms = @import("genksyms");

const testing = std.testing;

fn expectRequestWithEmptySeparateLongArgument(
    args: []const []const u8,
    expected_version_count: usize,
    expected_reference_count: usize,
    expected_dump_types_file: ?[]const u8,
) !void {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const outcome = try genksyms.parseArgs(arena_state.allocator(), args);
    switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| {
                try testing.expectEqual(expected_version_count, request.version_count);
                try testing.expectEqual(expected_reference_count, request.reference_files.len);
                for (request.reference_files) |reference_file| {
                    try testing.expectEqualStrings("", reference_file);
                }
                if (expected_dump_types_file) |expected_file| {
                    try testing.expectEqualStrings(expected_file, request.dump_types_file.?);
                } else {
                    try testing.expectEqual(@as(?[]const u8, null), request.dump_types_file);
                }
                try testing.expectEqualSlices([]const u8, args, request.rendered_args);
            },
            else => return error.ExpectedRequestCommand,
        },
        else => return error.ExpectedRequestCommand,
    }
}

test "phase2 genksyms wrapper version-prefixed empty separate long reference argument stays data" {
    try expectRequestWithEmptySeparateLongArgument(&.{
        "--version",
        "--reference",
        "",
    }, 1, 1, null);
    try expectRequestWithEmptySeparateLongArgument(&.{
        "--ver",
        "--reference",
        "",
    }, 1, 1, null);
}

test "phase2 genksyms wrapper repeated version prefixes keep empty separate long arguments" {
    try expectRequestWithEmptySeparateLongArgument(&.{
        "--version",
        "--ver",
        "--reference",
        "",
        "--dump-types",
        "",
    }, 2, 1, "");
}

test "phase2 genksyms wrapper short version prefix keeps empty separate long dump types" {
    try expectRequestWithEmptySeparateLongArgument(&.{
        "-V",
        "--dump-types",
        "",
    }, 1, 0, "");
}
