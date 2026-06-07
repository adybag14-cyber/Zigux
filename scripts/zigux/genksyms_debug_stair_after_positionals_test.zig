const std = @import("std");
const testing = std.testing;
const genksyms = @import("genksyms.zig");

fn parseRequest(allocator: std.mem.Allocator, args: []const []const u8) !genksyms.Request {
    const outcome = try genksyms.parseArgs(allocator, args);
    return switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| request,
            else => error.ExpectedRequestCommand,
        },
        .failure => error.UnexpectedParseFailure,
    };
}

test "debug flags after delayed positionals climb in normalized order" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();
    const arena = arena_state.allocator();

    const args = [_][]const u8{
        "first.c",
        "-d",
        "middle.h",
        "--debug",
        "--deb",
        "-dd",
        "tail.sym",
    };
    const request = try parseRequest(arena, &args);

    try testing.expectEqual(@as(usize, 5), request.debug_level);
    try testing.expectEqual(@as(usize, 0), request.version_count);
    try testing.expect(!request.warnings);
    try testing.expect(!request.dump_defs);
    try testing.expect(!request.preserve);
    try testing.expectEqual(@as(usize, 0), request.reference_files.len);
    try testing.expect(request.dump_types_file == null);

    const expected_rendered = [_][]const u8{
        "-d",
        "--debug",
        "--deb",
        "-dd",
        "first.c",
        "middle.h",
        "tail.sym",
    };
    try testing.expectEqualSlices([]const u8, &args, request.raw_args);
    try testing.expectEqualSlices([]const u8, &expected_rendered, request.rendered_args);
}

test "debug stair keeps version side effects without pure version promotion" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();
    const arena = arena_state.allocator();

    const args = [_][]const u8{
        "unit.c",
        "-Vd",
        "--debug",
        "-Vdd",
        "--deb",
    };
    const request = try parseRequest(arena, &args);

    try testing.expectEqual(@as(usize, 5), request.debug_level);
    try testing.expectEqual(@as(usize, 2), request.version_count);
    try testing.expectEqual(@as(usize, 0), request.reference_files.len);

    const expected_rendered = [_][]const u8{
        "-Vd",
        "--debug",
        "-Vdd",
        "--deb",
        "unit.c",
    };
    try testing.expectEqualSlices([]const u8, &expected_rendered, request.rendered_args);
}

test "debug stair bridge json preserves normalized argv and state" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();
    const arena = arena_state.allocator();

    const args = [_][]const u8{
        "left.c",
        "--debug",
        "-d",
        "right.c",
        "-dd",
        "--deb",
    };
    const request = try parseRequest(arena, &args);

    try testing.expectEqual(@as(usize, 5), request.debug_level);

    var output: std.Io.Writer.Allocating = .init(testing.allocator);
    defer output.deinit();
    try genksyms.renderGenksymsBridge(&output.writer, request);

    try testing.expectEqualStrings(
        "{\"tool\":\"scripts/genksyms/genksyms\",\"stdin\":\"cpp-stream\",\"stdout\":\"symversions\",\"argv\":[\"scripts/genksyms/genksyms\",\"--debug\",\"-d\",\"-dd\",\"--deb\",\"left.c\",\"right.c\"],\"options\":{\"debug_level\":5,\"warnings\":false,\"dump_defs\":false,\"preserve\":false,\"reference_files\":[],\"dump_types_file\":null}}\n",
        output.written(),
    );
}
