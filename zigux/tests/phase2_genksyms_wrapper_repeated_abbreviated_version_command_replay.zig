const std = @import("std");
const testing = std.testing;
const genksyms = @import("genksyms_wrapper");

test "phase2 genksyms wrapper replay preserves repeated abbreviated pure-version command count" {
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

test "phase2 genksyms wrapper replay preserves mixed repeated abbreviated pure-version command count" {
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
