const std = @import("std");
const testing = std.testing;
const genksyms = @import("genksyms.zig");

test "genksyms bridge preserves exact long version side effect before long help" {
    const args = [_][]const u8{
        "--version",
        "--help",
    };
    const outcome = try genksyms.parseArgs(testing.allocator, &args);
    switch (outcome) {
        .command => |command| switch (command) {
            .help => |version_count| try testing.expectEqual(@as(usize, 1), version_count),
            else => return error.ExpectedHelpCommand,
        },
        else => return error.ExpectedCommand,
    }
}

test "genksyms bridge preserves abbreviated long version side effect before abbreviated help" {
    const args = [_][]const u8{
        "--ver",
        "--he",
    };
    const outcome = try genksyms.parseArgs(testing.allocator, &args);
    switch (outcome) {
        .command => |command| switch (command) {
            .help => |version_count| try testing.expectEqual(@as(usize, 1), version_count),
            else => return error.ExpectedHelpCommand,
        },
        else => return error.ExpectedCommand,
    }
}

test "genksyms bridge preserves repeated short version side effects before short help" {
    const args = [_][]const u8{
        "-V",
        "-V",
        "-h",
    };
    const outcome = try genksyms.parseArgs(testing.allocator, &args);
    switch (outcome) {
        .command => |command| switch (command) {
            .help => |version_count| try testing.expectEqual(@as(usize, 2), version_count),
            else => return error.ExpectedHelpCommand,
        },
        else => return error.ExpectedCommand,
    }
}

test "genksyms bridge preserves clustered short version side effects before short help" {
    const args = [_][]const u8{"-VVh"};
    const outcome = try genksyms.parseArgs(testing.allocator, &args);
    switch (outcome) {
        .command => |command| switch (command) {
            .help => |version_count| try testing.expectEqual(@as(usize, 2), version_count),
            else => return error.ExpectedHelpCommand,
        },
        else => return error.ExpectedCommand,
    }
}
