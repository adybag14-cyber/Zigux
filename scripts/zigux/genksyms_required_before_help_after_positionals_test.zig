const std = @import("std");
const testing = std.testing;
const genksyms = @import("genksyms.zig");

test "genksyms help after required long values keeps only version side effects" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "delayed.c",
        "-V",
        "--reference",
        "base.symvers",
        "--dump-types=base.types",
        "--help",
        "--reference",
        "ignored.symvers",
    };

    const outcome = try genksyms.parseArgs(arena_state.allocator(), &args);
    switch (outcome) {
        .command => |command| switch (command) {
            .help => |version_count| try testing.expectEqual(@as(usize, 1), version_count),
            else => return error.ExpectedHelpCommand,
        },
        else => return error.ExpectedHelpCommand,
    }
}

test "genksyms abbreviated help after inline required values discards request state" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "first.o",
        "-VV",
        "--ref=first.symvers",
        "--dump-t=first.types",
        "--hel",
        "--dump-types",
        "ignored.types",
    };

    const outcome = try genksyms.parseArgs(arena_state.allocator(), &args);
    switch (outcome) {
        .command => |command| switch (command) {
            .help => |version_count| try testing.expectEqual(@as(usize, 2), version_count),
            else => return error.ExpectedHelpCommand,
        },
        else => return error.ExpectedHelpCommand,
    }
}

test "genksyms short help cluster after required values ignores trailing cluster state" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "source.c",
        "--version",
        "-r",
        "pre.symvers",
        "-Tpre.types",
        "-VhDp",
        "--reference",
        "ignored.symvers",
    };

    const outcome = try genksyms.parseArgs(arena_state.allocator(), &args);
    switch (outcome) {
        .command => |command| switch (command) {
            .help => |version_count| try testing.expectEqual(@as(usize, 2), version_count),
            else => return error.ExpectedHelpCommand,
        },
        else => return error.ExpectedHelpCommand,
    }
}
