const std = @import("std");
const genksyms = @import("genksyms");

test "phase2 genksyms wrapper replay keeps option terminator after earlier positional input" {
    var arena_state = std.heap.ArenaAllocator.init(std.testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "-d",
        "leftover.c",
        "--",
        "--leftover",
        "positional",
    };
    const outcome = try genksyms.parseArgs(arena_state.allocator(), &args);
    switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| {
                try std.testing.expectEqual(@as(usize, 1), request.debug_level);
                try std.testing.expectEqual(@as(usize, 5), request.rendered_args.len);
                try std.testing.expectEqualStrings("-d", request.rendered_args[0]);
                try std.testing.expectEqualStrings("leftover.c", request.rendered_args[1]);
                try std.testing.expectEqualStrings("--", request.rendered_args[2]);
                try std.testing.expectEqualStrings("--leftover", request.rendered_args[3]);
                try std.testing.expectEqualStrings("positional", request.rendered_args[4]);
            },
            else => return error.ExpectedRequestCommand,
        },
        else => return error.ExpectedRequestCommand,
    }
}

test "phase2 genksyms wrapper replay keeps dash-prefixed arguments as data across terminator boundaries" {
    var arena_state = std.heap.ArenaAllocator.init(std.testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "leftover.c",
        "--reference",
        "--debug",
        "--dump-types",
        "--types",
        "--",
        "-V",
        "tail.symref",
    };
    const outcome = try genksyms.parseArgs(arena_state.allocator(), &args);
    switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| {
                try std.testing.expectEqual(@as(usize, 0), request.debug_level);
                try std.testing.expectEqual(@as(usize, 1), request.reference_files.len);
                try std.testing.expectEqualStrings("--debug", request.reference_files[0]);
                try std.testing.expectEqualStrings("--types", request.dump_types_file.?);
                try std.testing.expectEqual(@as(usize, 8), request.rendered_args.len);
                try std.testing.expectEqualStrings("--reference", request.rendered_args[0]);
                try std.testing.expectEqualStrings("--debug", request.rendered_args[1]);
                try std.testing.expectEqualStrings("--dump-types", request.rendered_args[2]);
                try std.testing.expectEqualStrings("--types", request.rendered_args[3]);
                try std.testing.expectEqualStrings("leftover.c", request.rendered_args[4]);
                try std.testing.expectEqualStrings("--", request.rendered_args[5]);
                try std.testing.expectEqualStrings("-V", request.rendered_args[6]);
                try std.testing.expectEqualStrings("tail.symref", request.rendered_args[7]);
            },
            else => return error.ExpectedRequestCommand,
        },
        else => return error.ExpectedRequestCommand,
    }
}
