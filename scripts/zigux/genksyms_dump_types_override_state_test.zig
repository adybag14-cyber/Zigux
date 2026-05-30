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

test "dump types options use last write precedence across long and short forms" {
    const args = [_][]const u8{
        "input.c",
        "--dump-types=first.symtypes",
        "-Tsecond.symtypes",
        "--dump-types",
        "third.symtypes",
    };
    const expected_rendered = [_][]const u8{
        "--dump-types=first.symtypes",
        "-Tsecond.symtypes",
        "--dump-types",
        "third.symtypes",
        "input.c",
    };

    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const request = try expectRequest(arena_state.allocator(), &args);

    try testing.expectEqualStrings("third.symtypes", request.dump_types_file.?);
    try testing.expectEqualSlices([]const u8, &expected_rendered, request.rendered_args);
}

test "dump types option-like arguments stay data before parsing resumes" {
    const args = [_][]const u8{
        "--dump-types",
        "--version",
        "-V",
        "-T--help",
        "-d",
    };

    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const request = try expectRequest(arena_state.allocator(), &args);

    try testing.expectEqualStrings("--help", request.dump_types_file.?);
    try testing.expectEqual(@as(usize, 1), request.version_count);
    try testing.expectEqual(@as(usize, 1), request.debug_level);
    try testing.expectEqualSlices([]const u8, &args, request.rendered_args);
}

test "dump types state survives terminator tails" {
    const args = [_][]const u8{
        "pre.c",
        "-T",
        "types.symtypes",
        "--",
        "--dump-types",
        "tail.symtypes",
    };
    const expected_rendered = [_][]const u8{
        "-T",
        "types.symtypes",
        "--",
        "pre.c",
        "--dump-types",
        "tail.symtypes",
    };

    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const request = try expectRequest(arena_state.allocator(), &args);

    try testing.expectEqualStrings("types.symtypes", request.dump_types_file.?);
    try testing.expectEqualSlices([]const u8, &expected_rendered, request.rendered_args);
}
