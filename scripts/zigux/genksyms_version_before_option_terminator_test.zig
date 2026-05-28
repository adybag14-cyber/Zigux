const std = @import("std");
const testing = std.testing;

const genksyms = @import("genksyms.zig");

test "version side effect survives before explicit option terminator" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "--version",
        "--",
        "--leftover",
        "-d",
    };
    const outcome = try genksyms.parseArgs(arena_state.allocator(), &args);
    switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| {
                try testing.expectEqual(@as(usize, 1), request.version_count);
                try testing.expectEqual(@as(usize, 0), request.debug_level);
                try testing.expectEqualSlices([]const u8, &args, request.rendered_args);
            },
            else => return error.ExpectedRequestCommand,
        },
        else => return error.ExpectedRequestCommand,
    }
}

test "abbreviated and short versions still count before option terminator" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "--ver",
        "-VV",
        "--",
        "input.c",
    };
    const outcome = try genksyms.parseArgs(arena_state.allocator(), &args);
    switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| {
                try testing.expectEqual(@as(usize, 3), request.version_count);
                try testing.expectEqualSlices([]const u8, &args, request.rendered_args);
            },
            else => return error.ExpectedRequestCommand,
        },
        else => return error.ExpectedRequestCommand,
    }
}
