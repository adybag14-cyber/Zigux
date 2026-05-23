const std = @import("std");
const testing = std.testing;
const genksyms = @import("genksyms.zig");

test "genksyms bridge preserves repeated abbreviated version side effects before long quiet override" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "--ver",
        "--ver",
        "--warnings",
        "--quiet",
    };
    const outcome = try genksyms.parseArgs(arena_state.allocator(), &args);
    switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| {
                try testing.expectEqual(@as(usize, 2), request.version_count);
                try testing.expect(!request.warnings);
                try testing.expectEqual(@as(usize, 4), request.rendered_args.len);
                try testing.expectEqualStrings("--ver", request.rendered_args[0]);
                try testing.expectEqualStrings("--ver", request.rendered_args[1]);
                try testing.expectEqualStrings("--warnings", request.rendered_args[2]);
                try testing.expectEqualStrings("--quiet", request.rendered_args[3]);
            },
            else => return error.ExpectedRequestCommand,
        },
        else => return error.ExpectedRequestCommand,
    }
}

test "genksyms bridge preserves repeated abbreviated version side effects before short quiet override" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "--ver",
        "-V",
        "-w",
        "-q",
    };
    const outcome = try genksyms.parseArgs(arena_state.allocator(), &args);
    switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| {
                try testing.expectEqual(@as(usize, 2), request.version_count);
                try testing.expect(!request.warnings);
                try testing.expectEqual(@as(usize, 4), request.rendered_args.len);
                try testing.expectEqualStrings("--ver", request.rendered_args[0]);
                try testing.expectEqualStrings("-V", request.rendered_args[1]);
                try testing.expectEqualStrings("-w", request.rendered_args[2]);
                try testing.expectEqualStrings("-q", request.rendered_args[3]);
            },
            else => return error.ExpectedRequestCommand,
        },
        else => return error.ExpectedRequestCommand,
    }
}
