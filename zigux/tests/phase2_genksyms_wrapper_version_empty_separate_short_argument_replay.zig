const std = @import("std");
const genksyms = @import("genksyms");

const testing = std.testing;

fn expectRequestWithEmptySeparateShortArgument(
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

test "phase2 genksyms wrapper version-prefixed empty separate short reference argument stays data" {
    try expectRequestWithEmptySeparateShortArgument(&.{
        "--version",
        "-r",
        "",
    }, 1, 1, null);
    try expectRequestWithEmptySeparateShortArgument(&.{
        "--ver",
        "-r",
        "",
    }, 1, 1, null);
}

test "phase2 genksyms wrapper clustered version prefixes keep empty separate short arguments" {
    try expectRequestWithEmptySeparateShortArgument(&.{
        "-Vr",
        "",
    }, 1, 1, null);
    try expectRequestWithEmptySeparateShortArgument(&.{
        "-VT",
        "",
    }, 1, 0, "");
}

test "phase2 genksyms wrapper repeated version prefixes keep paired empty short arguments" {
    try expectRequestWithEmptySeparateShortArgument(&.{
        "-VV",
        "-r",
        "",
        "-T",
        "",
    }, 2, 1, "");
}
