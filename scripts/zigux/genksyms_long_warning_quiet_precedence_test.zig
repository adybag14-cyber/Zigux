const std = @import("std");
const testing = std.testing;
const genksyms = @import("genksyms.zig");

fn expectRequest(allocator: std.mem.Allocator, args: []const []const u8) !genksyms.Request {
    const outcome = try genksyms.parseArgs(allocator, args);
    return switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| request,
            else => error.ExpectedRequestCommand,
        },
        .failure => error.ExpectedRequestCommand,
    };
}

test "exact long warning and quiet options use last write precedence" {
    const args = [_][]const u8{
        "--quiet",
        "--warnings",
        "--quiet",
        "--debug",
        "input.c",
    };

    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const request = try expectRequest(arena_state.allocator(), &args);

    try testing.expect(!request.warnings);
    try testing.expectEqual(@as(usize, 1), request.debug_level);
    try testing.expectEqualSlices([]const u8, &args, request.rendered_args);
}

test "exact long warning toggles do not flush delayed positionals early" {
    const args = [_][]const u8{
        "first.c",
        "--warnings",
        "--quiet",
        "second.c",
    };
    const expected_rendered = [_][]const u8{
        "--warnings",
        "--quiet",
        "first.c",
        "second.c",
    };

    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const request = try expectRequest(arena_state.allocator(), &args);

    try testing.expect(!request.warnings);
    try testing.expectEqualSlices([]const u8, &expected_rendered, request.rendered_args);
}

test "exact long warning state survives terminator tails" {
    const args = [_][]const u8{
        "pre.c",
        "--warnings",
        "--",
        "--quiet",
        "post.c",
    };
    const expected_rendered = [_][]const u8{
        "--warnings",
        "--",
        "pre.c",
        "--quiet",
        "post.c",
    };

    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const request = try expectRequest(arena_state.allocator(), &args);

    try testing.expect(request.warnings);
    try testing.expectEqualSlices([]const u8, &expected_rendered, request.rendered_args);
}
