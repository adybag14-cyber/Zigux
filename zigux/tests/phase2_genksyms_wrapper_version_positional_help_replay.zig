const std = @import("std");

const genksyms = @import("genksyms");

fn expectHelpVersionCount(arena: std.mem.Allocator, args: []const []const u8, expected_count: usize) !void {
    const outcome = try genksyms.parseArgs(arena, args);
    switch (outcome) {
        .command => |command| switch (command) {
            .help => |version_count| try std.testing.expectEqual(expected_count, version_count),
            else => return error.ExpectedGenksymsHelp,
        },
        .failure => return error.UnexpectedGenksymsFailure,
    }
}

test "version side effects survive buffered positional args before long help" {
    var arena_state = std.heap.ArenaAllocator.init(std.testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "--version",
        "leftover-input.c",
        "--debug",
        "rightover-input.h",
        "--help",
    };

    try expectHelpVersionCount(arena_state.allocator(), &args, 1);
}

test "clustered short help keeps prior version side effects after positional data" {
    var arena_state = std.heap.ArenaAllocator.init(std.testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "-V",
        "buffered-before-help.c",
        "-VVh",
        "ignored-after-help.h",
    };

    try expectHelpVersionCount(arena_state.allocator(), &args, 3);
}
