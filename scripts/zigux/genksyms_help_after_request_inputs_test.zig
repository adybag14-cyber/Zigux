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
        else => return error.ExpectedCommand,
    }
}

test "genksyms help after delayed positional keeps earlier version side effect" {
    const args = [_][]const u8{
        "leftover.c",
        "--ver",
        "--help",
    };

    try expectHelpVersionCount(&args, 1);
}

test "genksyms help after stdin request input keeps clustered short versions" {
    const args = [_][]const u8{
        "-",
        "-VV",
        "-h",
    };

    try expectHelpVersionCount(&args, 2);
}

test "genksyms help after required-option data ignores option-looking data" {
    const args = [_][]const u8{
        "-r",
        "--version",
        "leftover.c",
        "--he",
    };

    try expectHelpVersionCount(&args, 0);
}
