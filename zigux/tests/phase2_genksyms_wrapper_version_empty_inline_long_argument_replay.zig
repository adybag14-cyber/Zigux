const std = @import("std");
const testing = std.testing;

const genksyms = @import("genksyms");

fn expectVersionedRequestWithEmptyInlineArguments(
    args: []const []const u8,
    expected_version_count: usize,
) !void {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const outcome = try genksyms.parseArgs(arena_state.allocator(), args);
    switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| {
                try testing.expectEqual(expected_version_count, request.version_count);
                try testing.expectEqual(@as(usize, 1), request.reference_files.len);
                try testing.expectEqualStrings("", request.reference_files[0]);
                try testing.expectEqualStrings("", request.dump_types_file.?);
                try testing.expectEqualSlices([]const u8, args, request.rendered_args);
            },
            else => return error.ExpectedRequestCommand,
        },
        else => return error.ExpectedRequestCommand,
    }
}

test "exact version survives before empty inline long arguments" {
    const args = [_][]const u8{
        "--version",
        "--reference=",
        "--dump-types=",
    };
    try expectVersionedRequestWithEmptyInlineArguments(&args, 1);
}

test "abbreviated version survives before abbreviated empty inline long arguments" {
    const args = [_][]const u8{
        "--ver",
        "--ref=",
        "--dump-t=",
    };
    try expectVersionedRequestWithEmptyInlineArguments(&args, 1);
}
