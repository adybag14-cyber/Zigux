const std = @import("std");
const testing = std.testing;
const genksyms = @import("genksyms.zig");

fn expectHelpAfterFullReferenceSet(args: []const []const u8, expected_version_count: usize) !void {
    const outcome = try genksyms.parseArgs(testing.allocator, args);
    switch (outcome) {
        .command => |command| switch (command) {
            .help => |version_count| try testing.expectEqual(expected_version_count, version_count),
            else => return error.ExpectedHelpCommand,
        },
        else => return error.ExpectedHelpCommand,
    }
}

test "long help short-circuits after full reference set" {
    const args = [_][]const u8{
        "-r",        "01.symref",
        "-r",        "02.symref",
        "-r",        "03.symref",
        "-r",        "04.symref",
        "-r",        "05.symref",
        "-r",        "06.symref",
        "-r",        "07.symref",
        "-r",        "08.symref",
        "-r",        "09.symref",
        "-r",        "10.symref",
        "-r",        "11.symref",
        "-r",        "12.symref",
        "-r",        "13.symref",
        "-r",        "14.symref",
        "-r",        "15.symref",
        "-r",        "16.symref",
        "--help",    "--reference",
        "17.symref",
    };

    try expectHelpAfterFullReferenceSet(&args, 0);
}

test "short help preserves versions after full reference set" {
    const args = [_][]const u8{
        "--version",
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
        "-h",
        "-r",
        "17.symref",
    };

    try expectHelpAfterFullReferenceSet(&args, 1);
}
