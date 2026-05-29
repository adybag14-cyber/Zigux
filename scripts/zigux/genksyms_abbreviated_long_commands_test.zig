const std = @import("std");
const testing = std.testing;

const genksyms = @import("genksyms.zig");

fn expectVersionCommand(args: []const []const u8, expected_version_count: usize) !void {
    const outcome = try genksyms.parseArgs(testing.allocator, args);
    switch (outcome) {
        .command => |command| switch (command) {
            .version => |version_count| try testing.expectEqual(expected_version_count, version_count),
            else => return error.ExpectedVersionCommand,
        },
        else => return error.ExpectedVersionCommand,
    }
}

fn expectHelpCommand(args: []const []const u8, expected_version_count: usize) !void {
    const outcome = try genksyms.parseArgs(testing.allocator, args);
    switch (outcome) {
        .command => |command| switch (command) {
            .help => |version_count| try testing.expectEqual(expected_version_count, version_count),
            else => return error.ExpectedHelpCommand,
        },
        else => return error.ExpectedHelpCommand,
    }
}

test "genksyms bridge accepts abbreviated long version as a pure version command" {
    const single = [_][]const u8{"--ver"};
    try expectVersionCommand(&single, 1);

    const repeated = [_][]const u8{
        "--ver",
        "--version",
        "--ver",
    };
    try expectVersionCommand(&repeated, 3);
}

test "genksyms bridge carries abbreviated long version side effects into help" {
    const abbreviated_help = [_][]const u8{
        "--ver",
        "--hel",
    };
    try expectHelpCommand(&abbreviated_help, 1);

    const repeated_versions = [_][]const u8{
        "--version",
        "--ver",
        "--hel",
    };
    try expectHelpCommand(&repeated_versions, 2);
}
