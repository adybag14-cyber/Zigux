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
        else => error.ExpectedRequestCommand,
    };
}

test "genksyms bridge treats hash-prefixed values after positionals as request input" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "-V",
        "#module.sym",
        "--debug",
        "##type-stream",
        "--warnings",
    };
    const request = try parseRequest(arena_state.allocator(), &args);

    try testing.expectEqual(@as(usize, 1), request.version_count);
    try testing.expectEqual(@as(usize, 1), request.debug_level);
    try testing.expect(request.warnings);
    try testing.expectEqual(@as(usize, 0), request.reference_files.len);
    try testing.expectEqual(@as(?[]const u8, null), request.dump_types_file);
    try testing.expectEqualSlices([]const u8, &args, request.raw_args);
    try testing.expectEqualSlices([]const u8, &.{
        "-V",
        "--debug",
        "--warnings",
        "#module.sym",
        "##type-stream",
    }, request.rendered_args);
}

test "genksyms bridge accepts hash-prefixed required option arguments after positionals" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "alpha.c",
        "--reference",
        "#refs.sym",
        "-T",
        "##types.out",
        "--version",
    };
    const request = try parseRequest(arena_state.allocator(), &args);

    try testing.expectEqual(@as(usize, 1), request.version_count);
    try testing.expectEqual(@as(usize, 1), request.reference_files.len);
    try testing.expectEqualStrings("#refs.sym", request.reference_files[0]);
    try testing.expectEqualStrings("##types.out", request.dump_types_file.?);
    try testing.expectEqualSlices([]const u8, &.{
        "--reference",
        "#refs.sym",
        "-T",
        "##types.out",
        "--version",
        "alpha.c",
    }, request.rendered_args);
}

test "genksyms bridge keeps hash-prefixed terminator tails out of parser state" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "--debug",
        "#pre.c",
        "--",
        "#tail.c",
        "--reference",
        "#not-ref.sym",
    };
    const request = try parseRequest(arena_state.allocator(), &args);

    try testing.expectEqual(@as(usize, 1), request.debug_level);
    try testing.expectEqual(@as(usize, 0), request.version_count);
    try testing.expectEqual(@as(usize, 0), request.reference_files.len);
    try testing.expectEqual(@as(?[]const u8, null), request.dump_types_file);
    try testing.expectEqualSlices([]const u8, &.{
        "--debug",
        "--",
        "#pre.c",
        "#tail.c",
        "--reference",
        "#not-ref.sym",
    }, request.rendered_args);
}

test "genksyms bridge renders hash-prefixed terminator tail in bridge json" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "input.c",
        "-p",
        "--",
        "#tail.sym",
        "-V",
    };
    const request = try parseRequest(arena_state.allocator(), &args);

    var output: std.Io.Writer.Allocating = .init(testing.allocator);
    defer output.deinit();

    try genksyms.renderGenksymsBridge(&output.writer, request);
    try testing.expectEqualStrings(
        "{\"tool\":\"scripts/genksyms/genksyms\",\"stdin\":\"cpp-stream\",\"stdout\":\"symversions\",\"argv\":[\"scripts/genksyms/genksyms\",\"-p\",\"--\",\"input.c\",\"#tail.sym\",\"-V\"],\"options\":{\"debug_level\":0,\"warnings\":false,\"dump_defs\":false,\"preserve\":true,\"reference_files\":[],\"dump_types_file\":null}}\n",
        output.written(),
    );
}
