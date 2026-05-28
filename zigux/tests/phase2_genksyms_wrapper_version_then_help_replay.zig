const std = @import("std");
const genksyms = @import("genksyms");

const testing = std.testing;

fn expectHelpVersionCount(
    args: []const []const u8,
    expected_version_count: usize,
) !void {
    const outcome = try genksyms.parseArgs(testing.allocator, args);
    switch (outcome) {
        .command => |command| switch (command) {
            .help => |version_count| try testing.expectEqual(expected_version_count, version_count),
            else => return error.ExpectedHelpCommand,
        },
        else => return error.ExpectedCommand,
    }
}

test "phase2 genksyms wrapper exact version prefixes preserve help command version count" {
    try expectHelpVersionCount(&.{
        "--version",
        "--help",
    }, 1);
    try expectHelpVersionCount(&.{
        "-V",
        "-h",
    }, 1);
}

test "phase2 genksyms wrapper abbreviated version prefixes preserve help command version count" {
    try expectHelpVersionCount(&.{
        "--ver",
        "--help",
    }, 1);
    try expectHelpVersionCount(&.{
        "--ver",
        "-h",
    }, 1);
}
