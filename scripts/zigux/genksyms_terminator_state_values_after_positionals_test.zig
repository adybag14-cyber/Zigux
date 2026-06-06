const std = @import("std");
const genksyms = @import("genksyms.zig");

const testing = std.testing;

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

test "post-terminator state option values stay positional after delayed input" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "leftover.c",
        "-Vd",
        "--reference",
        "before.symref",
        "--",
        "--debug=late",
        "--warnings=late",
        "--quiet=late",
        "--dump=late",
        "--preserve=late",
        "tail.c",
    };

    const request = try expectRequest(arena_state.allocator(), &args);

    try testing.expectEqual(@as(usize, 1), request.version_count);
    try testing.expectEqual(@as(usize, 1), request.debug_level);
    try testing.expect(!request.warnings);
    try testing.expect(!request.dump_defs);
    try testing.expect(!request.preserve);
    try testing.expectEqual(@as(usize, 1), request.reference_files.len);
    try testing.expectEqualStrings("before.symref", request.reference_files[0]);
    try testing.expect(request.dump_types_file == null);

    const expected_rendered = [_][]const u8{
        "-Vd",
        "--reference",
        "before.symref",
        "leftover.c",
        "--",
        "--debug=late",
        "--warnings=late",
        "--quiet=late",
        "--dump=late",
        "--preserve=late",
        "tail.c",
    };
    try testing.expectEqualSlices([]const u8, &expected_rendered, request.rendered_args);
    try testing.expectEqualSlices([]const u8, &args, request.raw_args);
}

test "abbreviated post-terminator state values do not become failures" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "--warnings",
        "input.c",
        "--",
        "--deb=2",
        "--warn=",
        "--qui=no",
        "--du=ambiguous-before-terminator",
        "--pres=yes",
    };

    const request = try expectRequest(arena_state.allocator(), &args);

    try testing.expectEqual(@as(usize, 0), request.version_count);
    try testing.expectEqual(@as(usize, 0), request.debug_level);
    try testing.expect(request.warnings);
    try testing.expect(!request.dump_defs);
    try testing.expect(!request.preserve);
    try testing.expectEqual(@as(usize, 0), request.reference_files.len);
    try testing.expect(request.dump_types_file == null);

    const expected_rendered = [_][]const u8{
        "--warnings",
        "input.c",
        "--",
        "--deb=2",
        "--warn=",
        "--qui=no",
        "--du=ambiguous-before-terminator",
        "--pres=yes",
    };
    try testing.expectEqualSlices([]const u8, &expected_rendered, request.rendered_args);
}

test "bridge output preserves post-terminator state values as argv data" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "source.c",
        "--",
        "--debug=late",
        "--quiet=late",
    };

    const request = try expectRequest(arena_state.allocator(), &args);

    try testing.expectEqual(@as(usize, 0), request.debug_level);
    try testing.expect(!request.warnings);
    try testing.expect(!request.dump_defs);
    try testing.expect(!request.preserve);

    var output: std.Io.Writer.Allocating = .init(testing.allocator);
    defer output.deinit();

    try genksyms.renderGenksymsBridge(&output.writer, request);
    try testing.expectEqualStrings(
        "{\"tool\":\"scripts/genksyms/genksyms\",\"stdin\":\"cpp-stream\",\"stdout\":\"symversions\",\"argv\":[\"scripts/genksyms/genksyms\",\"source.c\",\"--\",\"--debug=late\",\"--quiet=late\"],\"options\":{\"debug_level\":0,\"warnings\":false,\"dump_defs\":false,\"preserve\":false,\"reference_files\":[],\"dump_types_file\":null}}\n",
        output.written(),
    );
}
