const std = @import("std");
const testing = std.testing;
const genksyms = @import("genksyms.zig");

test "genksyms bridge preserves repeated version side effects before abbreviated help" {
    const args = [_][]const u8{
        "--version",
        "--ver",
        "--he",
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

test "genksyms bridge preserves mixed repeated version side effects before abbreviated help" {
    const args = [_][]const u8{
        "-V",
        "--version",
        "--he",
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
