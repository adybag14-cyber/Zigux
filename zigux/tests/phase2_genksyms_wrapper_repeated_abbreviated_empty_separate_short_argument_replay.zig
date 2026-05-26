const std = @import("std");
const genksyms = @import("genksyms");

test "phase2 genksyms wrapper replay preserves repeated abbreviated version side effects before empty separate short reference arguments" {
    var arena_state = std.heap.ArenaAllocator.init(std.testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "--ver",
        "--ver",
        "-r",
        "",
        "-T",
        "types.symtypes",
    };
    const outcome = try genksyms.parseArgs(arena_state.allocator(), &args);
    switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| {
                try std.testing.expectEqual(@as(usize, 2), request.version_count);
                try std.testing.expectEqual(@as(usize, 1), request.reference_files.len);
                try std.testing.expectEqualStrings("", request.reference_files[0]);
                try std.testing.expectEqualStrings("types.symtypes", request.dump_types_file.?);
                try std.testing.expectEqualSlices([]const u8, &args, request.rendered_args);
            },
            else => return error.ExpectedRequestCommand,
        },
        else => return error.ExpectedRequestCommand,
    }
}

test "phase2 genksyms wrapper replay preserves repeated abbreviated version side effects before empty separate short dump-types arguments" {
    var arena_state = std.heap.ArenaAllocator.init(std.testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "--ver",
        "--ver",
        "-r",
        "foo.symref",
        "-T",
        "",
        "leftover.c",
    };
    const outcome = try genksyms.parseArgs(arena_state.allocator(), &args);
    switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| {
                try std.testing.expectEqual(@as(usize, 2), request.version_count);
                try std.testing.expectEqual(@as(usize, 1), request.reference_files.len);
                try std.testing.expectEqualStrings("foo.symref", request.reference_files[0]);
                try std.testing.expectEqualStrings("", request.dump_types_file.?);
                try std.testing.expectEqual(@as(usize, 7), request.rendered_args.len);
                try std.testing.expectEqualStrings("--ver", request.rendered_args[0]);
                try std.testing.expectEqualStrings("--ver", request.rendered_args[1]);
                try std.testing.expectEqualStrings("-r", request.rendered_args[2]);
                try std.testing.expectEqualStrings("foo.symref", request.rendered_args[3]);
                try std.testing.expectEqualStrings("-T", request.rendered_args[4]);
                try std.testing.expectEqualStrings("", request.rendered_args[5]);
                try std.testing.expectEqualStrings("leftover.c", request.rendered_args[6]);
            },
            else => return error.ExpectedRequestCommand,
        },
        else => return error.ExpectedRequestCommand,
    }
}
