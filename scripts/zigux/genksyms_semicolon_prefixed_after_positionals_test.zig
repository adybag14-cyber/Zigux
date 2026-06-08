const std = @import("std");
const testing = std.testing;
const genksyms = @import("genksyms.zig");

test "semicolon-prefixed tokens after positionals remain request argv data" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "-V",
        ";unit.c",
        "--debug",
        ";next-input.h",
        "--warnings",
    };

    const outcome = try genksyms.parseArgs(arena_state.allocator(), &args);
    switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| {
                try testing.expectEqual(@as(usize, 1), request.version_count);
                try testing.expectEqual(@as(usize, 1), request.debug_level);
                try testing.expect(request.warnings);
                try testing.expectEqual(@as(usize, 0), request.reference_files.len);
                try testing.expectEqual(@as(?[]const u8, null), request.dump_types_file);
                try testing.expectEqualSlices([]const u8, &args, request.raw_args);
                try testing.expectEqualSlices([]const u8, &.{
                    "-V",
                    "--debug",
                    "--warnings",
                    ";unit.c",
                    ";next-input.h",
                }, request.rendered_args);
            },
            else => return error.ExpectedRequestCommand,
        },
        else => return error.ExpectedRequestCommand,
    }
}

test "semicolon-prefixed required option values after positionals remain data" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "alpha.c",
        "--reference",
        ";ref.sym",
        "-T",
        ";types.out",
        "--version",
    };

    const outcome = try genksyms.parseArgs(arena_state.allocator(), &args);
    switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| {
                try testing.expectEqual(@as(usize, 1), request.version_count);
                try testing.expectEqual(@as(usize, 1), request.reference_files.len);
                try testing.expectEqualStrings(";ref.sym", request.reference_files[0]);
                try testing.expectEqualStrings(";types.out", request.dump_types_file.?);
                try testing.expectEqualSlices([]const u8, &.{
                    "--reference",
                    ";ref.sym",
                    "-T",
                    ";types.out",
                    "--version",
                    "alpha.c",
                }, request.rendered_args);
            },
            else => return error.ExpectedRequestCommand,
        },
        else => return error.ExpectedRequestCommand,
    }
}

test "semicolon-prefixed terminator tails stay out of parser state" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "--debug",
        ";pre.c",
        "--",
        ";tail.c",
        "--reference",
        ";not-ref.sym",
    };

    const outcome = try genksyms.parseArgs(arena_state.allocator(), &args);
    switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| {
                try testing.expectEqual(@as(usize, 1), request.debug_level);
                try testing.expectEqual(@as(usize, 0), request.version_count);
                try testing.expectEqual(@as(usize, 0), request.reference_files.len);
                try testing.expectEqual(@as(?[]const u8, null), request.dump_types_file);
                try testing.expectEqualSlices([]const u8, &.{
                    "--debug",
                    "--",
                    ";pre.c",
                    ";tail.c",
                    "--reference",
                    ";not-ref.sym",
                }, request.rendered_args);
            },
            else => return error.ExpectedRequestCommand,
        },
        else => return error.ExpectedRequestCommand,
    }
}
