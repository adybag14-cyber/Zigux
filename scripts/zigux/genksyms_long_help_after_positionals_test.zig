const std = @import("std");
const testing = std.testing;
const genksyms = @import("genksyms.zig");

fn expectHelpVersionCount(args: []const []const u8, expected_version_count: usize) !void {
    const outcome = try genksyms.parseArgs(testing.allocator, args);
    switch (outcome) {
        .command => |command| switch (command) {
            .help => |version_count| try testing.expectEqual(expected_version_count, version_count),
            else => return error.ExpectedHelpCommand,
        },
        else => return error.ExpectedHelpCommand,
    }
}

test "genksyms long help after positionals preserves earlier version side effect" {
    const args = [_][]const u8{
        "leftover.c",
        "--version",
        "rightover.h",
        "--help",
        "--reference",
        "ignored.symref",
    };

    try expectHelpVersionCount(&args, 1);
}

test "genksyms abbreviated long help after positionals returns help immediately" {
    const args = [_][]const u8{
        "leftover.c",
        "--he",
        "--version",
        "--dump",
    };

    try expectHelpVersionCount(&args, 0);
}

test "genksyms repeated long versions before long help after positionals are counted" {
    const args = [_][]const u8{
        "leftover.c",
        "--version",
        "--ver",
        "rightover.h",
        "--help",
        "--dump-types",
        "ignored.symtypes",
    };

    try expectHelpVersionCount(&args, 2);
}
