const std = @import("std");
const testing = std.testing;
const genksyms = @import("genksyms.zig");

test "genksyms bridge keeps repeated version side effects before lone dash positional passthrough" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "--version",
        "--ver",
        "-",
        "-d",
    };
    const outcome = try genksyms.parseArgs(arena_state.allocator(), &args);
    switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| {
                try testing.expectEqual(@as(usize, 2), request.version_count);
                try testing.expectEqual(@as(usize, 1), request.debug_level);
                try testing.expectEqual(@as(usize, 4), request.rendered_args.len);
                try testing.expectEqualStrings("--version", request.rendered_args[0]);
                try testing.expectEqualStrings("--ver", request.rendered_args[1]);
                try testing.expectEqualStrings("-d", request.rendered_args[2]);
                try testing.expectEqualStrings("-", request.rendered_args[3]);
            },
            else => return error.ExpectedRequestCommand,
        },
        else => return error.ExpectedRequestCommand,
    }
}

test "genksyms bridge keeps repeated version side effects before later positional request inputs" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "-V",
        "--version",
        "leftover.c",
        "--reference",
        "foo.symref",
    };
    const outcome = try genksyms.parseArgs(arena_state.allocator(), &args);
    switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| {
                try testing.expectEqual(@as(usize, 2), request.version_count);
                try testing.expectEqual(@as(usize, 1), request.reference_files.len);
                try testing.expectEqualStrings("foo.symref", request.reference_files[0]);
                try testing.expectEqual(@as(usize, 5), request.rendered_args.len);
                try testing.expectEqualStrings("-V", request.rendered_args[0]);
                try testing.expectEqualStrings("--version", request.rendered_args[1]);
                try testing.expectEqualStrings("--reference", request.rendered_args[2]);
                try testing.expectEqualStrings("foo.symref", request.rendered_args[3]);
                try testing.expectEqualStrings("leftover.c", request.rendered_args[4]);
            },
            else => return error.ExpectedRequestCommand,
        },
        else => return error.ExpectedRequestCommand,
    }
}
