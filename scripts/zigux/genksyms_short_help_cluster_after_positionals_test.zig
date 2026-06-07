const std = @import("std");
const testing = std.testing;
const genksyms = @import("genksyms.zig");

fn expectHelpVersionCount(args: []const []const u8, expected_count: usize) !void {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const outcome = try genksyms.parseArgs(arena_state.allocator(), args);
    switch (outcome) {
        .command => |command| switch (command) {
            .help => |count| try testing.expectEqual(expected_count, count),
            else => return error.ExpectedHelpCommand,
        },
        else => return error.ExpectedHelpCommand,
    }
}

test "short help cluster after positional preserves earlier version side effect" {
    const args = [_][]const u8{
        "unit.c",
        "-Vh",
        "-d",
        "--reference",
        "ignored.symref",
    };

    try expectHelpVersionCount(&args, 1);
}

test "short help cluster after positional preserves repeated earlier versions" {
    const args = [_][]const u8{
        "unit.c",
        "-VVh",
        "--dump-types",
        "ignored.types",
        "-x",
    };

    try expectHelpVersionCount(&args, 2);
}

test "short help cluster after positional discards earlier request state" {
    const args = [_][]const u8{
        "unit.c",
        "-dDph",
        "--warnings",
        "--reference",
        "ignored.symref",
    };

    try expectHelpVersionCount(&args, 0);
}

test "short help cluster after positional ignores later cluster bytes" {
    const args = [_][]const u8{
        "unit.c",
        "-hVVdD",
        "--reference",
        "ignored.symref",
    };

    try expectHelpVersionCount(&args, 0);
}

test "short help cluster after positional keeps versions before help and ignores versions after help" {
    const args = [_][]const u8{
        "unit.c",
        "-VVhVV",
        "--debug",
        "--dump",
    };

    try expectHelpVersionCount(&args, 2);
}
