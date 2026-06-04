const std = @import("std");
const genksyms = @import("genksyms");

const testing = std.testing;

fn expectHelpVersionCount(args: []const []const u8, expected: usize) !void {
    const outcome = try genksyms.parseArgs(testing.allocator, args);
    switch (outcome) {
        .command => |command| switch (command) {
            .help => |version_count| try testing.expectEqual(expected, version_count),
            else => return error.ExpectedHelpCommand,
        },
        .failure => return error.ExpectedHelpCommand,
    }
}

test "long version side effects reach long and abbreviated help" {
    try expectHelpVersionCount(&[_][]const u8{
        "--version",
        "--help",
    }, 1);

    try expectHelpVersionCount(&[_][]const u8{
        "--version",
        "--hel",
    }, 1);
}

test "abbreviated version side effects reach short help" {
    try expectHelpVersionCount(&[_][]const u8{
        "--ver",
        "-h",
    }, 1);

    try expectHelpVersionCount(&[_][]const u8{
        "--ver",
        "--help",
    }, 1);
}

test "clustered short versions accumulate before help exits" {
    try expectHelpVersionCount(&[_][]const u8{
        "-VV",
        "-h",
    }, 2);

    try expectHelpVersionCount(&[_][]const u8{
        "-Vh",
    }, 1);
}
