const std = @import("std");
const genksyms = @import("genksyms.zig");

const testing = std.testing;

fn expectHelpCount(args: []const []const u8, expected_version_count: usize) !void {
    const outcome = try genksyms.parseArgs(testing.allocator, args);
    switch (outcome) {
        .command => |command| switch (command) {
            .help => |version_count| try testing.expectEqual(expected_version_count, version_count),
            else => return error.ExpectedHelpCommand,
        },
        .failure => return error.ExpectedHelpCommand,
    }
}

test "genksyms help command short-circuits invalid tail tokens" {
    const long_args = [_][]const u8{
        "--version",
        "--help",
        "--unknown",
    };
    try expectHelpCount(&long_args, 1);

    const short_args = [_][]const u8{
        "-Vh",
        "-x",
    };
    try expectHelpCount(&short_args, 1);
}

test "genksyms help command short-circuits missing-argument tails" {
    const long_args = [_][]const u8{
        "--ver",
        "--hel",
        "--reference",
    };
    try expectHelpCount(&long_args, 1);

    const short_args = [_][]const u8{
        "-V",
        "-h",
        "-T",
    };
    try expectHelpCount(&short_args, 1);
}

test "genksyms help command short-circuits reference-limit tails" {
    const args = [_][]const u8{
        "-V",
        "--help",
        "-r",
        "01.symref",
        "-r",
        "02.symref",
        "-r",
        "03.symref",
        "-r",
        "04.symref",
        "-r",
        "05.symref",
        "-r",
        "06.symref",
        "-r",
        "07.symref",
        "-r",
        "08.symref",
        "-r",
        "09.symref",
        "-r",
        "10.symref",
        "-r",
        "11.symref",
        "-r",
        "12.symref",
        "-r",
        "13.symref",
        "-r",
        "14.symref",
        "-r",
        "15.symref",
        "-r",
        "16.symref",
        "-r",
        "17.symref",
    };
    try expectHelpCount(&args, 1);
}
