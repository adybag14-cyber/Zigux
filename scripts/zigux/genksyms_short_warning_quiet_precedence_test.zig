const std = @import("std");
const testing = std.testing;

const genksyms = @import("genksyms.zig");

test "short warnings and quiet remain order-sensitive around delayed positionals" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "input.c",
        "-wq",
        "middle.h",
        "-w",
        "tail.sym",
    };
    const outcome = try genksyms.parseArgs(arena_state.allocator(), &args);
    switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| {
                try testing.expect(request.warnings);
                try testing.expectEqual(@as(usize, 5), request.rendered_args.len);
                try testing.expectEqualStrings("-wq", request.rendered_args[0]);
                try testing.expectEqualStrings("-w", request.rendered_args[1]);
                try testing.expectEqualStrings("input.c", request.rendered_args[2]);
                try testing.expectEqualStrings("middle.h", request.rendered_args[3]);
                try testing.expectEqualStrings("tail.sym", request.rendered_args[4]);
            },
            else => return error.ExpectedRequestCommand,
        },
        else => return error.ExpectedRequestCommand,
    }
}

test "short quiet side effect can be the final state after prior warnings" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "left.c",
        "-w",
        "right.h",
        "-q",
    };
    const outcome = try genksyms.parseArgs(arena_state.allocator(), &args);
    switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| {
                try testing.expect(!request.warnings);
                try testing.expectEqual(@as(usize, 4), request.rendered_args.len);
                try testing.expectEqualStrings("-w", request.rendered_args[0]);
                try testing.expectEqualStrings("-q", request.rendered_args[1]);
                try testing.expectEqualStrings("left.c", request.rendered_args[2]);
                try testing.expectEqualStrings("right.h", request.rendered_args[3]);
            },
            else => return error.ExpectedRequestCommand,
        },
        else => return error.ExpectedRequestCommand,
    }
}

test "terminator tail keeps warning-looking short tokens as data" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "queued.c",
        "-w",
        "--",
        "-q",
        "-w",
    };
    const expected_rendered = [_][]const u8{
        "-w",
        "queued.c",
        "--",
        "-q",
        "-w",
    };
    const outcome = try genksyms.parseArgs(arena_state.allocator(), &args);
    switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| {
                try testing.expect(request.warnings);
                try testing.expectEqualSlices([]const u8, &expected_rendered, request.rendered_args);
            },
            else => return error.ExpectedRequestCommand,
        },
        else => return error.ExpectedRequestCommand,
    }
}
