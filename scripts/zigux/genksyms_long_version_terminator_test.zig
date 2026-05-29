const std = @import("std");
const testing = std.testing;

const genksyms = @import("genksyms.zig");

fn expectVersionTerminatorRequest(
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
                try testing.expectEqualSlices([]const u8, args, request.rendered_args);
            },
            else => return error.ExpectedRequestCommand,
        },
        else => return error.ExpectedRequestCommand,
    }
}

test "long version before terminator forces request mode" {
    const args = [_][]const u8{
        "--version",
        "--",
        "--help",
        "input.c",
    };

    try expectVersionTerminatorRequest(&args, 1);
}

test "abbreviated long version before terminator forces request mode" {
    const args = [_][]const u8{
        "--ver",
        "--",
        "--dump",
        "object.o",
    };

    try expectVersionTerminatorRequest(&args, 1);
}

test "repeated long versions before terminator preserve side effects" {
    const args = [_][]const u8{
        "--version",
        "--ver",
        "--",
        "--reference",
        "symbols.ref",
    };

    try expectVersionTerminatorRequest(&args, 2);
}
