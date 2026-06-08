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

test "negative numeric token after delayed positionals remains an option failure" {
    const args = [_][]const u8{
        "-V",
        "input.c",
        "-1",
    };
    const outcome = try genksyms.parseArgs(testing.allocator, &args);
    switch (outcome) {
        .failure => |failure| {
            try testing.expectEqual(@as(usize, 1), failure.version_count);
            switch (failure.reason) {
                .invalid_option => |option| try testing.expectEqualStrings("1", option),
                else => return error.UnexpectedParseFailure,
            }
        },
        else => return error.ExpectedFailure,
    }
}

test "negative numeric required values after delayed positionals stay data" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "input.c",
        "--version",
        "-r",
        "-1",
        "--dump-types",
        "-2",
        "-d",
    };
    const request = try expectRequest(arena_state.allocator(), &args);
    try testing.expectEqual(@as(usize, 1), request.version_count);
    try testing.expectEqual(@as(usize, 1), request.debug_level);
    try testing.expectEqual(@as(usize, 1), request.reference_files.len);
    try testing.expectEqualStrings("-1", request.reference_files[0]);
    try testing.expectEqualStrings("-2", request.dump_types_file.?);
    try testing.expectEqual(@as(usize, 7), request.rendered_args.len);
    try testing.expectEqualStrings("--version", request.rendered_args[0]);
    try testing.expectEqualStrings("-r", request.rendered_args[1]);
    try testing.expectEqualStrings("-1", request.rendered_args[2]);
    try testing.expectEqualStrings("--dump-types", request.rendered_args[3]);
    try testing.expectEqualStrings("-2", request.rendered_args[4]);
    try testing.expectEqualStrings("-d", request.rendered_args[5]);
    try testing.expectEqualStrings("input.c", request.rendered_args[6]);
}

test "terminator keeps negative numeric tail values in rendered argv" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "-V",
        "input.c",
        "--",
        "-1",
        "-2",
        "--reference",
        "-3",
    };
    const request = try expectRequest(arena_state.allocator(), &args);
    try testing.expectEqual(@as(usize, 1), request.version_count);
    try testing.expectEqual(@as(usize, 0), request.reference_files.len);
    try testing.expect(request.dump_types_file == null);
    try testing.expectEqual(@as(usize, 7), request.rendered_args.len);
    try testing.expectEqualStrings("-V", request.rendered_args[0]);
    try testing.expectEqualStrings("--", request.rendered_args[1]);
    try testing.expectEqualStrings("input.c", request.rendered_args[2]);
    try testing.expectEqualStrings("-1", request.rendered_args[3]);
    try testing.expectEqualStrings("-2", request.rendered_args[4]);
    try testing.expectEqualStrings("--reference", request.rendered_args[5]);
    try testing.expectEqualStrings("-3", request.rendered_args[6]);
}

test "negative numeric terminator bridge JSON preserves argv data" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "input.c",
        "-p",
        "--",
        "-1",
        "-V",
    };
    const request = try expectRequest(arena_state.allocator(), &args);
    try testing.expect(request.preserve);
    try testing.expectEqual(@as(usize, 0), request.version_count);

    var output: std.Io.Writer.Allocating = .init(testing.allocator);
    defer output.deinit();

    try genksyms.renderGenksymsBridge(&output.writer, request);
    try testing.expectEqualStrings(
        "{\"tool\":\"scripts/genksyms/genksyms\",\"stdin\":\"cpp-stream\",\"stdout\":\"symversions\",\"argv\":[\"scripts/genksyms/genksyms\",\"-p\",\"--\",\"input.c\",\"-1\",\"-V\"],\"options\":{\"debug_level\":0,\"warnings\":false,\"dump_defs\":false,\"preserve\":true,\"reference_files\":[],\"dump_types_file\":null}}\n",
        output.written(),
    );
}
