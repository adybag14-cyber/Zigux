const std = @import("std");
const testing = std.testing;
const genksyms = @import("genksyms.zig");

fn expectAmbiguous(
    args: []const []const u8,
    expected_option: []const u8,
    expected_version_count: usize,
) !void {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const outcome = try genksyms.parseArgs(arena_state.allocator(), args);
    switch (outcome) {
        .failure => |parsed_failure| {
            try testing.expectEqual(expected_version_count, parsed_failure.version_count);
            switch (parsed_failure.reason) {
                .ambiguous_option => |option| {
                    try testing.expectEqualStrings(expected_option, option);
                },
                else => return error.ExpectedAmbiguousOption,
            }
        },
        else => return error.ExpectedParseFailure,
    }
}

test "ambiguous long options after positional request inputs stay failures" {
    const args = [_][]const u8{
        "input.sym",
        "--d",
    };

    try expectAmbiguous(&args, "--d", 0);
}

test "ambiguous inline long options after lone dash preserve version side effects" {
    const args = [_][]const u8{
        "-",
        "--version",
        "--du=types.symtypes",
    };

    try expectAmbiguous(&args, "--du", 1);
}

test "required option data that looks ambiguous does not consume later ambiguity" {
    const args = [_][]const u8{
        "-VV",
        "--reference",
        "--d",
        "--du",
    };

    try expectAmbiguous(&args, "--du", 2);
}
