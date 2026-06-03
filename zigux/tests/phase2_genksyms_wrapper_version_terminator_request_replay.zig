const std = @import("std");
const testing = std.testing;
const genksyms = @import("genksyms");

fn expectRequest(allocator: std.mem.Allocator, args: []const []const u8) !genksyms.Request {
    const outcome = try genksyms.parseArgs(allocator, args);
    switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| return request,
            else => return error.ExpectedRequestCommand,
        },
        else => return error.ExpectedRequestCommand,
    }
}

test "version before terminator keeps later long and short options as request data" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "--version",
        "--",
        "--help",
        "-d",
        "source.c",
    };
    const request = try expectRequest(arena_state.allocator(), &args);

    try testing.expectEqual(@as(usize, 1), request.version_count);
    try testing.expectEqual(@as(usize, 0), request.debug_level);
    try testing.expectEqual(@as(usize, 0), request.reference_files.len);
    try testing.expect(request.dump_types_file == null);
    try testing.expectEqualSlices([]const u8, &args, request.rendered_args);
}

test "short version cluster before terminator keeps reference-looking tail positional" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "-VV",
        "--",
        "--reference",
        "ignored.symref",
    };
    const request = try expectRequest(arena_state.allocator(), &args);

    try testing.expectEqual(@as(usize, 2), request.version_count);
    try testing.expectEqual(@as(usize, 0), request.reference_files.len);
    try testing.expectEqualSlices([]const u8, &args, request.rendered_args);
}

test "abbreviated version before positional terminator tail does not consume later version" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "--ver",
        "--",
        "--version",
    };
    const request = try expectRequest(arena_state.allocator(), &args);

    try testing.expectEqual(@as(usize, 1), request.version_count);
    try testing.expectEqual(@as(usize, 3), request.rendered_args.len);
    try testing.expectEqualSlices([]const u8, &args, request.rendered_args);
}
