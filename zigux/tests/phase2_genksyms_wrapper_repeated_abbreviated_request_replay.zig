const std = @import("std");
const genksyms = @import("genksyms");

const testing = std.testing;

fn expectRequestCommand(
    args: []const []const u8,
    expected_version_count: usize,
    expected_debug_level: usize,
    expected_reference_file: ?[]const u8,
) !void {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const outcome = try genksyms.parseArgs(arena_state.allocator(), args);
    switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| {
                try testing.expectEqual(expected_version_count, request.version_count);
                try testing.expectEqual(expected_debug_level, request.debug_level);
                if (expected_reference_file) |reference_file| {
                    try testing.expectEqual(@as(usize, 1), request.reference_files.len);
                    try testing.expectEqualStrings(reference_file, request.reference_files[0]);
                } else {
                    try testing.expectEqual(@as(usize, 0), request.reference_files.len);
                }
                try testing.expectEqualSlices([]const u8, args, request.rendered_args);
            },
            else => return error.ExpectedRequestCommand,
        },
        else => return error.ExpectedCommand,
    }
}

test "phase2 genksyms wrapper preserves repeated abbreviated version counts before request parsing" {
    try expectRequestCommand(&.{ "--ver", "--ver", "-d" }, 2, 1, null);
    try expectRequestCommand(&.{ "--ver", "-V", "--reference", "foo.symref" }, 2, 0, "foo.symref");
    try expectRequestCommand(&.{ "--ver", "--version", "--ver", "--debug" }, 3, 1, null);
}
