const std = @import("std");
const testing = std.testing;
const genksyms = @import("genksyms.zig");

test "genksyms abbreviated version keeps version side effect before long help" {
    const args = [_][]const u8{
        "--ver",
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

test "genksyms long version keeps version side effect before long help" {
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
