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

test "genksyms bridge treats plus numeric values after positionals as request input" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "-V",
        "+1",
        "--version",
    };
    const request = try parseRequest(arena_state.allocator(), &args);

    try testing.expectEqual(@as(usize, 2), request.version_count);
    try testing.expectEqual(@as(usize, 3), request.rendered_args.len);
    try testing.expectEqualStrings("-V", request.rendered_args[0]);
    try testing.expectEqualStrings("--version", request.rendered_args[1]);
    try testing.expectEqualStrings("+1", request.rendered_args[2]);
}

test "genksyms bridge accepts plus numeric required option arguments after positionals" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "input.c",
        "--version",
        "-r",
        "+1",
        "--dump-types",
        "+2",
        "-d",
    };
    const request = try parseRequest(arena_state.allocator(), &args);

    try testing.expectEqual(@as(usize, 1), request.version_count);
    try testing.expectEqual(@as(usize, 1), request.debug_level);
    try testing.expectEqual(@as(usize, 1), request.reference_files.len);
    try testing.expectEqualStrings("+1", request.reference_files[0]);
    try testing.expectEqualStrings("+2", request.dump_types_file.?);
    try testing.expectEqual(@as(usize, 7), request.rendered_args.len);
    try testing.expectEqualStrings("--version", request.rendered_args[0]);
    try testing.expectEqualStrings("-r", request.rendered_args[1]);
    try testing.expectEqualStrings("+1", request.rendered_args[2]);
    try testing.expectEqualStrings("--dump-types", request.rendered_args[3]);
    try testing.expectEqualStrings("+2", request.rendered_args[4]);
    try testing.expectEqualStrings("-d", request.rendered_args[5]);
    try testing.expectEqualStrings("input.c", request.rendered_args[6]);
}

test "genksyms bridge keeps plus numeric terminator tail out of option parsing" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "-V",
        "input.c",
        "--",
        "+1",
        "+2",
        "--reference",
        "+3",
    };
    const request = try parseRequest(arena_state.allocator(), &args);

    try testing.expectEqual(@as(usize, 1), request.version_count);
    try testing.expectEqual(@as(usize, 0), request.reference_files.len);
    try testing.expectEqual(@as(usize, 7), request.rendered_args.len);
    try testing.expectEqualStrings("-V", request.rendered_args[0]);
    try testing.expectEqualStrings("--", request.rendered_args[1]);
    try testing.expectEqualStrings("input.c", request.rendered_args[2]);
    try testing.expectEqualStrings("+1", request.rendered_args[3]);
    try testing.expectEqualStrings("+2", request.rendered_args[4]);
    try testing.expectEqualStrings("--reference", request.rendered_args[5]);
    try testing.expectEqualStrings("+3", request.rendered_args[6]);
}

test "genksyms bridge renders plus numeric terminator tail in bridge json" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "input.c",
        "-p",
        "--",
        "+1",
        "-V",
    };
    const request = try parseRequest(arena_state.allocator(), &args);

    var output: std.Io.Writer.Allocating = .init(testing.allocator);
    defer output.deinit();

    try genksyms.renderGenksymsBridge(&output.writer, request);
    try testing.expectEqualStrings(
        "{\"tool\":\"scripts/genksyms/genksyms\",\"stdin\":\"cpp-stream\",\"stdout\":\"symversions\",\"argv\":[\"scripts/genksyms/genksyms\",\"-p\",\"--\",\"input.c\",\"+1\",\"-V\"],\"options\":{\"debug_level\":0,\"warnings\":false,\"dump_defs\":false,\"preserve\":true,\"reference_files\":[],\"dump_types_file\":null}}\n",
        output.written(),
    );
}
