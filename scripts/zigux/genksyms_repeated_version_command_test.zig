const std = @import("std");
const testing = std.testing;
const genksyms = @import("genksyms.zig");

test "genksyms repeated pure version command keeps accumulated long-form count" {
    const args = [_][]const u8{
        "--version",
        "--ver",
    };
    const outcome = try genksyms.parseArgs(testing.allocator, &args);
    switch (outcome) {
        .command => |command| switch (command) {
            .version => |count| try testing.expectEqual(@as(usize, 2), count),
            else => return error.ExpectedVersionCommand,
        },
        else => return error.ExpectedVersionCommand,
    }
}

test "genksyms repeated pure version command keeps accumulated mixed-form count" {
    const args = [_][]const u8{
        "-V",
        "--version",
        "--ver",
    };
    const outcome = try genksyms.parseArgs(testing.allocator, &args);
    switch (outcome) {
        .command => |command| switch (command) {
            .version => |count| try testing.expectEqual(@as(usize, 3), count),
            else => return error.ExpectedVersionCommand,
        },
        else => return error.ExpectedVersionCommand,
    }
}
