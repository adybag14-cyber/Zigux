const std = @import("std");
const genksyms = @import("genksyms");

const testing = std.testing;

fn expectEmptySeparateShortArgumentsAsData(
    version_prefixes: []const []const u8,
    expected_version_count: usize,
) !void {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const arena = arena_state.allocator();

    var args = std.ArrayList([]const u8).empty;
    defer args.deinit(arena);

    try args.appendSlice(arena, version_prefixes);
    try args.appendSlice(arena, &.{
        "-r",
        "",
        "-T",
        "",
        "tail.c",
    });

    const outcome = try genksyms.parseArgs(arena, args.items);
    switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| {
                try testing.expectEqual(expected_version_count, request.version_count);
                try testing.expectEqual(@as(usize, 1), request.reference_files.len);
                try testing.expectEqualStrings("", request.reference_files[0]);
                try testing.expectEqualStrings("", request.dump_types_file.?);
                try testing.expectEqualSlices([]const u8, args.items, request.rendered_args);
            },
            else => return error.ExpectedRequestCommand,
        },
        else => return error.ExpectedRequestCommand,
    }
}

test "phase2 genksyms wrapper preserves repeated version counts before empty separate short arguments" {
    try expectEmptySeparateShortArgumentsAsData(&.{ "--version", "--ver", "--version" }, 3);
    try expectEmptySeparateShortArgumentsAsData(
        &.{ "-V", "--version", "--ver", "--version" },
        4,
    );
}
