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
        else => error.ExpectedRequestCommand,
    };
}

test "double terminator after delayed positionals keeps tail as argv data" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "-V",
        "alpha.c",
        "-d",
        "--",
        "--",
        "--version",
        "-r",
        "tail.symref",
    };
    const request = try genksyms.parseArgs(arena_state.allocator(), &args);
    switch (request) {
        .command => |command| switch (command) {
            .request => |parsed| {
                try testing.expectEqual(@as(usize, 1), parsed.version_count);
                try testing.expectEqual(@as(usize, 1), parsed.debug_level);
                try testing.expectEqual(@as(usize, 0), parsed.reference_files.len);
                try testing.expect(parsed.dump_types_file == null);
                try testing.expectEqualSlices([]const u8, &args, parsed.raw_args);
                try testing.expectEqual(@as(usize, 8), parsed.rendered_args.len);
                try testing.expectEqualStrings("-V", parsed.rendered_args[0]);
                try testing.expectEqualStrings("-d", parsed.rendered_args[1]);
                try testing.expectEqualStrings("--", parsed.rendered_args[2]);
                try testing.expectEqualStrings("alpha.c", parsed.rendered_args[3]);
                try testing.expectEqualStrings("--", parsed.rendered_args[4]);
                try testing.expectEqualStrings("--version", parsed.rendered_args[5]);
                try testing.expectEqualStrings("-r", parsed.rendered_args[6]);
                try testing.expectEqualStrings("tail.symref", parsed.rendered_args[7]);
            },
            else => return error.ExpectedRequestCommand,
        },
        else => return error.ExpectedRequestCommand,
    }
}

test "second terminator prevents post terminator required value capture" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "input.c",
        "--warnings",
        "--",
        "--",
        "--reference",
        "after.symref",
        "--dump-types=after.types",
    };
    const request = try expectRequest(arena_state.allocator(), &args);
    try testing.expect(request.warnings);
    try testing.expectEqual(@as(usize, 0), request.reference_files.len);
    try testing.expect(request.dump_types_file == null);
    try testing.expectEqualStrings("--reference", request.rendered_args[4]);
    try testing.expectEqualStrings("after.symref", request.rendered_args[5]);
    try testing.expectEqualStrings("--dump-types=after.types", request.rendered_args[6]);
}

test "double terminator bridge JSON preserves normalized argv tail" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "alpha.c",
        "-p",
        "--",
        "--",
        "-V",
        "--quiet",
    };
    const request = try expectRequest(arena_state.allocator(), &args);
    try testing.expect(request.preserve);
    try testing.expectEqual(@as(usize, 0), request.version_count);

    var output: std.Io.Writer.Allocating = .init(testing.allocator);
    defer output.deinit();

    try genksyms.renderGenksymsBridge(&output.writer, request);
    try testing.expectEqualStrings(
        "{\"tool\":\"scripts/genksyms/genksyms\",\"stdin\":\"cpp-stream\",\"stdout\":\"symversions\",\"argv\":[\"scripts/genksyms/genksyms\",\"-p\",\"--\",\"alpha.c\",\"--\",\"-V\",\"--quiet\"],\"options\":{\"debug_level\":0,\"warnings\":false,\"dump_defs\":false,\"preserve\":true,\"reference_files\":[],\"dump_types_file\":null}}\n",
        output.written(),
    );
}
