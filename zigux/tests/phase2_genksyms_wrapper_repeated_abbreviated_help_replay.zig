const std = @import("std");
const genksyms = @import("genksyms");

const testing = std.testing;

fn expectHelpCommand(
    version_prefixes: []const []const u8,
    help_flag: []const u8,
    expected_version_count: usize,
) !void {
    var args = std.ArrayList([]const u8).empty;
    defer args.deinit(testing.allocator);

    try args.appendSlice(testing.allocator, version_prefixes);
    try args.append(testing.allocator, help_flag);

    const outcome = try genksyms.parseArgs(testing.allocator, args.items);
    switch (outcome) {
        .command => |command| switch (command) {
            .help => |version_count| try testing.expectEqual(expected_version_count, version_count),
            else => return error.ExpectedHelpCommand,
        },
        else => return error.ExpectedCommand,
    }
}

test "phase2 genksyms wrapper preserves repeated abbreviated version counts before help commands" {
    try expectHelpCommand(&.{ "--ver", "--ver" }, "-h", 2);
    try expectHelpCommand(&.{ "--ver", "-V", "--ver" }, "--help", 3);
}
