const std = @import("std");
const genksyms = @import("genksyms");

test "phase2 genksyms wrapper replay preserves version side effects before later positional passthrough" {
    var arena_state = std.heap.ArenaAllocator.init(std.testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "--ver",
        "leftover.c",
        "-r",
        "foo.symref",
    };
    const outcome = try genksyms.parseArgs(arena_state.allocator(), &args);
    switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| {
                try std.testing.expectEqual(@as(usize, 1), request.version_count);
                try std.testing.expectEqual(@as(usize, 1), request.reference_files.len);
                try std.testing.expectEqualStrings("foo.symref", request.reference_files[0]);
                try std.testing.expectEqual(@as(usize, 4), request.rendered_args.len);
                try std.testing.expectEqualStrings("--ver", request.rendered_args[0]);
                try std.testing.expectEqualStrings("-r", request.rendered_args[1]);
                try std.testing.expectEqualStrings("foo.symref", request.rendered_args[2]);
                try std.testing.expectEqualStrings("leftover.c", request.rendered_args[3]);
            },
            else => return error.ExpectedRequestCommand,
        },
        else => return error.ExpectedRequestCommand,
    }
}

test "phase2 genksyms wrapper replay preserves version side effects before explicit option terminator" {
    var arena_state = std.heap.ArenaAllocator.init(std.testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "-V",
        "--",
        "--debug",
        "tail.symref",
    };
    const outcome = try genksyms.parseArgs(arena_state.allocator(), &args);
    switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| {
                try std.testing.expectEqual(@as(usize, 1), request.version_count);
                try std.testing.expectEqual(@as(usize, 0), request.reference_files.len);
                try std.testing.expect(request.dump_types_file == null);
                try std.testing.expectEqual(@as(usize, 4), request.rendered_args.len);
                try std.testing.expectEqualStrings("-V", request.rendered_args[0]);
                try std.testing.expectEqualStrings("--", request.rendered_args[1]);
                try std.testing.expectEqualStrings("--debug", request.rendered_args[2]);
                try std.testing.expectEqualStrings("tail.symref", request.rendered_args[3]);
            },
            else => return error.ExpectedRequestCommand,
        },
        else => return error.ExpectedRequestCommand,
    }
}

test "phase2 genksyms wrapper replay keeps dash-prefixed option arguments as data after version side effects" {
    var arena_state = std.heap.ArenaAllocator.init(std.testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "--version",
        "--reference",
        "--debug",
        "leftover.c",
    };
    const outcome = try genksyms.parseArgs(arena_state.allocator(), &args);
    switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| {
                try std.testing.expectEqual(@as(usize, 1), request.version_count);
                try std.testing.expectEqual(@as(usize, 1), request.reference_files.len);
                try std.testing.expectEqualStrings("--debug", request.reference_files[0]);
                try std.testing.expectEqual(@as(usize, 4), request.rendered_args.len);
                try std.testing.expectEqualStrings("--version", request.rendered_args[0]);
                try std.testing.expectEqualStrings("--reference", request.rendered_args[1]);
                try std.testing.expectEqualStrings("--debug", request.rendered_args[2]);
                try std.testing.expectEqualStrings("leftover.c", request.rendered_args[3]);
            },
            else => return error.ExpectedRequestCommand,
        },
        else => return error.ExpectedRequestCommand,
    }
}
