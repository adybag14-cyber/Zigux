const std = @import("std");
const genksyms = @import("genksyms");

test "phase2 genksyms wrapper replay keeps lone dash as passthrough data" {
    var arena_state = std.heap.ArenaAllocator.init(std.testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "-",
        "-d",
        "-r",
        "foo.symref",
    };
    const outcome = try genksyms.parseArgs(arena_state.allocator(), &args);
    switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| {
                try std.testing.expectEqual(@as(usize, 0), request.version_count);
                try std.testing.expectEqual(@as(usize, 1), request.debug_level);
                try std.testing.expectEqual(@as(usize, 1), request.reference_files.len);
                try std.testing.expectEqualStrings("foo.symref", request.reference_files[0]);
                try std.testing.expectEqual(@as(usize, 4), request.rendered_args.len);
                try std.testing.expectEqualStrings("-d", request.rendered_args[0]);
                try std.testing.expectEqualStrings("-r", request.rendered_args[1]);
                try std.testing.expectEqualStrings("foo.symref", request.rendered_args[2]);
                try std.testing.expectEqualStrings("-", request.rendered_args[3]);
            },
            else => return error.ExpectedRequestCommand,
        },
        else => return error.ExpectedRequestCommand,
    }
}

test "phase2 genksyms wrapper replay preserves positional passthrough ordering" {
    var arena_state = std.heap.ArenaAllocator.init(std.testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "leftover.c",
        "-d",
        "rightover.h",
        "-r",
        "foo.symref",
        "--preserve",
    };
    const outcome = try genksyms.parseArgs(arena_state.allocator(), &args);
    switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| {
                try std.testing.expectEqual(@as(usize, 0), request.version_count);
                try std.testing.expectEqual(@as(usize, 1), request.debug_level);
                try std.testing.expect(request.preserve);
                try std.testing.expectEqual(@as(usize, 1), request.reference_files.len);
                try std.testing.expectEqualStrings("foo.symref", request.reference_files[0]);
                try std.testing.expectEqual(@as(usize, 6), request.rendered_args.len);
                try std.testing.expectEqualStrings("-d", request.rendered_args[0]);
                try std.testing.expectEqualStrings("-r", request.rendered_args[1]);
                try std.testing.expectEqualStrings("foo.symref", request.rendered_args[2]);
                try std.testing.expectEqualStrings("--preserve", request.rendered_args[3]);
                try std.testing.expectEqualStrings("leftover.c", request.rendered_args[4]);
                try std.testing.expectEqualStrings("rightover.h", request.rendered_args[5]);
            },
            else => return error.ExpectedRequestCommand,
        },
        else => return error.ExpectedRequestCommand,
    }
}

test "phase2 genksyms wrapper replay keeps version side effects before passthrough shape inputs" {
    var arena_state = std.heap.ArenaAllocator.init(std.testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "--version",
        "leftover.c",
        "-",
        "-d",
    };
    const outcome = try genksyms.parseArgs(arena_state.allocator(), &args);
    switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| {
                try std.testing.expectEqual(@as(usize, 1), request.version_count);
                try std.testing.expectEqual(@as(usize, 1), request.debug_level);
                try std.testing.expectEqual(@as(usize, 4), request.rendered_args.len);
                try std.testing.expectEqualStrings("--version", request.rendered_args[0]);
                try std.testing.expectEqualStrings("-d", request.rendered_args[1]);
                try std.testing.expectEqualStrings("leftover.c", request.rendered_args[2]);
                try std.testing.expectEqualStrings("-", request.rendered_args[3]);
            },
            else => return error.ExpectedRequestCommand,
        },
        else => return error.ExpectedRequestCommand,
    }
}
