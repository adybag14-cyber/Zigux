const std = @import("std");
const testing = std.testing;
const genksyms = @import("genksyms.zig");

test "genksyms bridge preserves version side effect before option terminator" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "--version",
        "--",
        "--debug",
        "-r",
        "tail.symref",
    };
    const outcome = try genksyms.parseArgs(arena_state.allocator(), &args);
    switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| {
                try testing.expectEqual(@as(usize, 1), request.version_count);
                try testing.expectEqual(@as(usize, 0), request.debug_level);
                try testing.expectEqual(@as(usize, 0), request.reference_files.len);
                try testing.expect(request.dump_types_file == null);
                try testing.expectEqualSlices([]const u8, &args, request.rendered_args);
            },
            else => return error.ExpectedRequestCommand,
        },
        else => return error.ExpectedRequestCommand,
    }
}

test "genksyms bridge renders terminator tail as data after short version" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "-V",
        "--",
        "-d",
        "--reference",
    };
    const outcome = try genksyms.parseArgs(arena_state.allocator(), &args);
    const request = switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| request,
            else => return error.ExpectedRequestCommand,
        },
        else => return error.ExpectedRequestCommand,
    };

    try testing.expectEqual(@as(usize, 1), request.version_count);
    try testing.expectEqual(@as(usize, 0), request.debug_level);
    try testing.expectEqual(@as(usize, 0), request.reference_files.len);
    try testing.expectEqual(@as(usize, 4), request.rendered_args.len);
    try testing.expectEqualStrings("-V", request.rendered_args[0]);
    try testing.expectEqualStrings("--", request.rendered_args[1]);
    try testing.expectEqualStrings("-d", request.rendered_args[2]);
    try testing.expectEqualStrings("--reference", request.rendered_args[3]);

    var output: std.Io.Writer.Allocating = .init(testing.allocator);
    defer output.deinit();

    try genksyms.renderGenksymsBridge(&output.writer, request);
    try testing.expectEqualStrings(
        "{\"tool\":\"scripts/genksyms/genksyms\",\"stdin\":\"cpp-stream\",\"stdout\":\"symversions\",\"argv\":[\"scripts/genksyms/genksyms\",\"-V\",\"--\",\"-d\",\"--reference\"],\"options\":{\"debug_level\":0,\"warnings\":false,\"dump_defs\":false,\"preserve\":false,\"reference_files\":[],\"dump_types_file\":null}}\n",
        output.written(),
    );
}
