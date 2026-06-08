const std = @import("std");
const testing = std.testing;

const genksyms = @import("genksyms.zig");

test "empty argv remains an empty request" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{};
    const outcome = try genksyms.parseArgs(arena_state.allocator(), &args);
    switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| {
                try testing.expectEqual(@as(usize, 0), request.raw_args.len);
                try testing.expectEqual(@as(usize, 0), request.rendered_args.len);
                try testing.expectEqual(@as(usize, 0), request.version_count);
                try testing.expectEqual(@as(usize, 0), request.debug_level);
                try testing.expect(!request.warnings);
                try testing.expect(!request.dump_defs);
                try testing.expect(!request.preserve);
                try testing.expectEqual(@as(usize, 0), request.reference_files.len);
                try testing.expect(request.dump_types_file == null);
            },
            else => return error.ExpectedRequestCommand,
        },
        else => return error.ExpectedRequestCommand,
    }
}

test "empty positional suppresses pure version promotion" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "--version",
        "",
        "--ver",
    };
    const outcome = try genksyms.parseArgs(arena_state.allocator(), &args);
    switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| {
                try testing.expectEqual(@as(usize, 2), request.version_count);
                try testing.expectEqualSlices([]const u8, &args, request.raw_args);
                try testing.expectEqual(@as(usize, 3), request.rendered_args.len);
                try testing.expectEqualStrings("--version", request.rendered_args[0]);
                try testing.expectEqualStrings("--ver", request.rendered_args[1]);
                try testing.expectEqualStrings("", request.rendered_args[2]);
            },
            else => return error.ExpectedRequestCommand,
        },
        else => return error.ExpectedRequestCommand,
    }
}

test "pure version without request input remains version command" {
    const args = [_][]const u8{
        "--version",
        "--ver",
        "-VV",
    };
    const outcome = try genksyms.parseArgs(testing.allocator, &args);
    switch (outcome) {
        .command => |command| switch (command) {
            .version => |count| try testing.expectEqual(@as(usize, 4), count),
            else => return error.ExpectedVersionCommand,
        },
        else => return error.ExpectedVersionCommand,
    }
}
