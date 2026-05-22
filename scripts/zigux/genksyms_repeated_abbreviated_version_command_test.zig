const std = @import("std");
const testing = std.testing;
const genksyms = @import("genksyms.zig");

test "genksyms bridge keeps repeated abbreviated version requests as a version command" {
    const args = [_][]const u8{
        "--ver",
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

test "genksyms bridge keeps mixed repeated abbreviated version requests as a version command" {
    const args = [_][]const u8{
        "--ver",
        "-V",
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
