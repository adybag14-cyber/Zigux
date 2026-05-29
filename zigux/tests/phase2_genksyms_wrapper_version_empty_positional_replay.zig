const std = @import("std");
const testing = std.testing;
const genksyms = @import("genksyms");

test "version side effects survive empty positional request input" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "--version",
        "",
        "--ver",
        "-d",
    };

    const outcome = try genksyms.parseArgs(arena_state.allocator(), &args);
    switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| {
                try testing.expectEqual(@as(usize, 2), request.version_count);
                try testing.expectEqual(@as(usize, 1), request.debug_level);
                try testing.expectEqualSlices([]const u8, &args, request.raw_args);
                try testing.expectEqual(@as(usize, 4), request.rendered_args.len);
                try testing.expectEqualStrings("--version", request.rendered_args[0]);
                try testing.expectEqualStrings("--ver", request.rendered_args[1]);
                try testing.expectEqualStrings("-d", request.rendered_args[2]);
                try testing.expectEqualStrings("", request.rendered_args[3]);
            },
            else => return error.ExpectedRequestCommand,
        },
        else => return error.ExpectedRequestCommand,
    }
}

test "clustered short version flags survive empty positional request input" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "-VV",
        "",
        "-wq",
        "-T",
        "types.symtypes",
    };

    const outcome = try genksyms.parseArgs(arena_state.allocator(), &args);
    switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| {
                try testing.expectEqual(@as(usize, 2), request.version_count);
                try testing.expect(!request.warnings);
                try testing.expectEqualStrings("types.symtypes", request.dump_types_file.?);
                try testing.expectEqualSlices([]const u8, &args, request.raw_args);
                try testing.expectEqual(@as(usize, 5), request.rendered_args.len);
                try testing.expectEqualStrings("-VV", request.rendered_args[0]);
                try testing.expectEqualStrings("-wq", request.rendered_args[1]);
                try testing.expectEqualStrings("-T", request.rendered_args[2]);
                try testing.expectEqualStrings("types.symtypes", request.rendered_args[3]);
                try testing.expectEqualStrings("", request.rendered_args[4]);
            },
            else => return error.ExpectedRequestCommand,
        },
        else => return error.ExpectedRequestCommand,
    }
}
