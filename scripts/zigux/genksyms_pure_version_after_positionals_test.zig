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
        .failure => error.UnexpectedParseFailure,
    };
}

test "pure version options without positional input stay version command" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "-V",
        "-VV",
        "--version",
        "--ver",
    };
    const outcome = try genksyms.parseArgs(arena_state.allocator(), &args);

    switch (outcome) {
        .command => |command| switch (command) {
            .version => |version_count| try testing.expectEqual(@as(usize, 5), version_count),
            else => return error.ExpectedVersionCommand,
        },
        else => return error.ExpectedVersionCommand,
    }
}

test "pure version options after delayed positionals stay request side effects" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();
    const arena = arena_state.allocator();

    const args = [_][]const u8{
        "first.c",
        "-V",
        "middle.h",
        "--version",
        "--ver",
        "-VV",
        "tail.sym",
    };
    const request = try expectRequest(arena, &args);

    try testing.expectEqualSlices([]const u8, &args, request.raw_args);
    try testing.expectEqual(@as(usize, 5), request.version_count);
    try testing.expectEqual(@as(usize, 0), request.debug_level);
    try testing.expect(!request.warnings);
    try testing.expect(!request.dump_defs);
    try testing.expect(!request.preserve);
    try testing.expectEqual(@as(usize, 0), request.reference_files.len);
    try testing.expect(request.dump_types_file == null);

    const expected_rendered = [_][]const u8{
        "-V",
        "--version",
        "--ver",
        "-VV",
        "first.c",
        "middle.h",
        "tail.sym",
    };
    try testing.expectEqualSlices([]const u8, &expected_rendered, request.rendered_args);
}

test "pure version request bridge json keeps positional-only state empty" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();
    const arena = arena_state.allocator();

    const args = [_][]const u8{
        "unit.c",
        "--version",
        "-VV",
        "unit.h",
    };
    const request = try expectRequest(arena, &args);

    try testing.expectEqual(@as(usize, 3), request.version_count);
    const expected_rendered = [_][]const u8{
        "--version",
        "-VV",
        "unit.c",
        "unit.h",
    };
    try testing.expectEqualSlices([]const u8, &expected_rendered, request.rendered_args);

    var output: std.Io.Writer.Allocating = .init(testing.allocator);
    defer output.deinit();
    try genksyms.renderGenksymsBridge(&output.writer, request);

    try testing.expectEqualStrings(
        "{\"tool\":\"scripts/genksyms/genksyms\",\"stdin\":\"cpp-stream\",\"stdout\":\"symversions\",\"argv\":[\"scripts/genksyms/genksyms\",\"--version\",\"-VV\",\"unit.c\",\"unit.h\"],\"options\":{\"debug_level\":0,\"warnings\":false,\"dump_defs\":false,\"preserve\":false,\"reference_files\":[],\"dump_types_file\":null}}\n",
        output.written(),
    );
}
