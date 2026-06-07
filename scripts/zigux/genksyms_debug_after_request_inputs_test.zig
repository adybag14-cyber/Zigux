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

test "debug flags after positional request input remain request state" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "unit.c",
        "--debug",
        "-dd",
        "--deb",
        "-V",
    };

    const request = try expectRequest(arena_state.allocator(), &args);

    try testing.expectEqual(@as(usize, 4), request.debug_level);
    try testing.expectEqual(@as(usize, 1), request.version_count);
    try testing.expectEqual(@as(usize, 0), request.reference_files.len);
    try testing.expect(request.dump_types_file == null);

    const expected_rendered = [_][]const u8{
        "--debug",
        "-dd",
        "--deb",
        "-V",
        "unit.c",
    };
    try testing.expectEqualSlices([]const u8, &expected_rendered, request.rendered_args);
}

test "lone dash request input does not stop later debug accumulation" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "-",
        "-d",
        "--debug",
        "source.c",
    };

    const request = try expectRequest(arena_state.allocator(), &args);

    try testing.expectEqual(@as(usize, 2), request.debug_level);
    try testing.expectEqual(@as(usize, 0), request.version_count);

    const expected_rendered = [_][]const u8{
        "-d",
        "--debug",
        "-",
        "source.c",
    };
    try testing.expectEqualSlices([]const u8, &expected_rendered, request.rendered_args);
}

test "required option values that look like debug flags stay data after requests" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "first.c",
        "--reference",
        "--debug",
        "-T",
        "-d",
        "--debug",
    };

    const request = try expectRequest(arena_state.allocator(), &args);

    try testing.expectEqual(@as(usize, 1), request.debug_level);
    try testing.expectEqual(@as(usize, 1), request.reference_files.len);
    try testing.expectEqualStrings("--debug", request.reference_files[0]);
    try testing.expectEqualStrings("-d", request.dump_types_file.?);

    const expected_rendered = [_][]const u8{
        "--reference",
        "--debug",
        "-T",
        "-d",
        "--debug",
        "first.c",
    };
    try testing.expectEqualSlices([]const u8, &expected_rendered, request.rendered_args);

    var rendered: std.Io.Writer.Allocating = .init(testing.allocator);
    defer rendered.deinit();

    try genksyms.renderGenksymsBridge(&rendered.writer, request);
    try testing.expectEqualStrings(
        "{\"tool\":\"scripts/genksyms/genksyms\",\"stdin\":\"cpp-stream\",\"stdout\":\"symversions\",\"argv\":[\"scripts/genksyms/genksyms\",\"--reference\",\"--debug\",\"-T\",\"-d\",\"--debug\",\"first.c\"],\"options\":{\"debug_level\":1,\"warnings\":false,\"dump_defs\":false,\"preserve\":false,\"reference_files\":[\"--debug\"],\"dump_types_file\":\"-d\"}}\n",
        rendered.written(),
    );
}
