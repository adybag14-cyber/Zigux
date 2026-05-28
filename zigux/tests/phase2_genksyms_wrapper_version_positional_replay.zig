const std = @import("std");
const genksyms = @import("genksyms");

const testing = std.testing;

fn expectVersionedRequest(
    args: []const []const u8,
    expected_version_count: usize,
    expected_rendered_args: []const []const u8,
) !void {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const outcome = try genksyms.parseArgs(arena_state.allocator(), args);
    switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| {
                try testing.expectEqual(expected_version_count, request.version_count);
                try testing.expectEqualSlices([]const u8, expected_rendered_args, request.rendered_args);
            },
            else => return error.ExpectedRequestCommand,
        },
        else => return error.ExpectedRequestCommand,
    }
}

test "phase2 genksyms wrapper keeps version side effects when stdin makes request mode" {
    const args = [_][]const u8{
        "--version",
        "-",
    };
    const rendered = [_][]const u8{
        "--version",
        "-",
    };

    try expectVersionedRequest(&args, 1, &rendered);
}

test "phase2 genksyms wrapper keeps clustered versions when positional input makes request mode" {
    const args = [_][]const u8{
        "-VV",
        "input.c",
        "--ver",
    };
    const rendered = [_][]const u8{
        "-VV",
        "--ver",
        "input.c",
    };

    try expectVersionedRequest(&args, 3, &rendered);
}

test "phase2 genksyms wrapper keeps option parsing around versioned positional requests" {
    const args = [_][]const u8{
        "leftover.c",
        "-Vd",
        "rightover.h",
        "--version",
        "-r",
        "base.symref",
    };
    const rendered = [_][]const u8{
        "-Vd",
        "--version",
        "-r",
        "base.symref",
        "leftover.c",
        "rightover.h",
    };

    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const outcome = try genksyms.parseArgs(arena_state.allocator(), &args);
    switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| {
                try testing.expectEqual(@as(usize, 2), request.version_count);
                try testing.expectEqual(@as(usize, 1), request.debug_level);
                try testing.expectEqual(@as(usize, 1), request.reference_files.len);
                try testing.expectEqualStrings("base.symref", request.reference_files[0]);
                try testing.expectEqualSlices([]const u8, &rendered, request.rendered_args);
            },
            else => return error.ExpectedRequestCommand,
        },
        else => return error.ExpectedRequestCommand,
    }
}
