const std = @import("std");
const testing = std.testing;
const genksyms = @import("genksyms.zig");

test "positional arguments keep short version side effect in normalized request argv" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "leftover.c",
        "-V",
        "-d",
        "rightover.h",
        "--reference",
        "baseline.symref",
    };
    const outcome = try genksyms.parseArgs(arena_state.allocator(), &args);
    switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| {
                try testing.expectEqual(@as(usize, 1), request.version_count);
                try testing.expectEqual(@as(usize, 1), request.debug_level);
                try testing.expectEqual(@as(usize, 1), request.reference_files.len);
                try testing.expectEqualStrings("baseline.symref", request.reference_files[0]);
                try testing.expectEqualSlices([]const u8, &[_][]const u8{
                    "-V",
                    "-d",
                    "--reference",
                    "baseline.symref",
                    "leftover.c",
                    "rightover.h",
                }, request.rendered_args);
            },
            else => return error.ExpectedRequestCommand,
        },
        else => return error.ExpectedRequestCommand,
    }
}

test "positional arguments keep abbreviated long version side effect before later options" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "first.c",
        "--ver",
        "--dump-types=types.out",
        "last.c",
        "-p",
    };
    const outcome = try genksyms.parseArgs(arena_state.allocator(), &args);
    switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| {
                try testing.expectEqual(@as(usize, 1), request.version_count);
                try testing.expectEqualStrings("types.out", request.dump_types_file.?);
                try testing.expect(request.preserve);
                try testing.expectEqualSlices([]const u8, &[_][]const u8{
                    "--ver",
                    "--dump-types=types.out",
                    "-p",
                    "first.c",
                    "last.c",
                }, request.rendered_args);
            },
            else => return error.ExpectedRequestCommand,
        },
        else => return error.ExpectedRequestCommand,
    }
}
