const std = @import("std");
const testing = std.testing;

const genksyms = @import("genksyms.zig");

fn expectHelpVersionCount(args: []const []const u8, expected_count: usize) !void {
    const outcome = try genksyms.parseArgs(testing.allocator, args);
    switch (outcome) {
        .command => |command| switch (command) {
            .help => |version_count| try testing.expectEqual(expected_count, version_count),
            .request => return error.ExpectedHelpCommandBeforeRequest,
            .version => return error.ExpectedHelpCommandBeforeVersion,
        },
        .failure => return error.ExpectedHelpCommandBeforeFailure,
    }
}

test "short help keeps prior version count before later option terminator" {
    const args = [_][]const u8{
        "-V",
        "-h",
        "--",
        "--reference",
        "ignored.symref",
        "-d",
    };

    try expectHelpVersionCount(&args, 1);
}

test "long help keeps mixed prior version count before terminator tail" {
    const args = [_][]const u8{
        "--version",
        "-VV",
        "--help",
        "--",
        "--dump-types=ignored.symtypes",
        "--version",
    };

    try expectHelpVersionCount(&args, 3);
}

test "abbreviated help wins after deferred positional and before terminator" {
    const args = [_][]const u8{
        "first.sym",
        "--ver",
        "--hel",
        "--",
        "--not-an-option",
    };

    try expectHelpVersionCount(&args, 1);
}
