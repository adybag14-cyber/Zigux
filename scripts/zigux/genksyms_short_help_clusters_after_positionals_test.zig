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

test "genksyms short help cluster after positionals keeps preceding version side effect" {
    const args = [_][]const u8{
        "leftover.c",
        "-Vh",
        "rightover.h",
        "-d",
    };

    try expectHelpVersionCount(&args, 1);
}

test "genksyms short help cluster after positionals ignores flags after help" {
    const args = [_][]const u8{
        "leftover.c",
        "-dhV",
        "--reference",
        "ignored.symref",
    };

    try expectHelpVersionCount(&args, 0);
}

test "genksyms repeated short versions before help after positionals are counted" {
    const args = [_][]const u8{
        "leftover.c",
        "-VVhD",
        "rightover.h",
        "--dump",
    };

    try expectHelpVersionCount(&args, 2);
}
