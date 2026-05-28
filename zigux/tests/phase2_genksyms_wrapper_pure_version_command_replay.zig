const std = @import("std");
const genksyms = @import("genksyms");

const testing = std.testing;

fn expectPureVersionCommand(
    args: []const []const u8,
    expected_version_count: usize,
) !void {
    const outcome = try genksyms.parseArgs(testing.allocator, args);
    switch (outcome) {
        .command => |command| switch (command) {
            .version => |version_count| try testing.expectEqual(expected_version_count, version_count),
            else => return error.ExpectedVersionCommand,
        },
        else => return error.ExpectedCommand,
    }
}

test "phase2 genksyms wrapper exact pure version invocations stay version commands" {
    try expectPureVersionCommand(&.{
        "--version",
    }, 1);
    try expectPureVersionCommand(&.{
        "-V",
    }, 1);
    try expectPureVersionCommand(&.{
        "--version",
        "-V",
    }, 2);
}

test "phase2 genksyms wrapper abbreviated and clustered pure version invocations accumulate count" {
    try expectPureVersionCommand(&.{
        "--ver",
    }, 1);
    try expectPureVersionCommand(&.{
        "-VV",
    }, 2);
    try expectPureVersionCommand(&.{
        "--ver",
        "-VV",
    }, 3);
}
