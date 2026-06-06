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

test "separated reference value may be a terminator token after positionals" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "delayed.c",
        "--reference",
        "--",
        "--debug",
        "--warnings",
        "tail.c",
    };

    const request = try expectRequest(arena_state.allocator(), &args);

    try testing.expectEqual(@as(usize, 0), request.version_count);
    try testing.expectEqual(@as(usize, 1), request.debug_level);
    try testing.expect(request.warnings);
    try testing.expect(!request.dump_defs);
    try testing.expect(!request.preserve);
    try testing.expectEqual(@as(usize, 1), request.reference_files.len);
    try testing.expectEqualStrings("--", request.reference_files[0]);
    try testing.expect(request.dump_types_file == null);
    try testing.expectEqualSlices([]const u8, &args, request.raw_args);

    const expected_rendered = [_][]const u8{
        "--reference",
        "--",
        "--debug",
        "--warnings",
        "delayed.c",
        "tail.c",
    };
    try testing.expectEqualSlices([]const u8, &expected_rendered, request.rendered_args);
}

test "separated dump-types value may be a terminator token before a real terminator" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "input.c",
        "-T",
        "--",
        "-d",
        "--",
        "--reference",
        "after.symref",
    };

    const request = try expectRequest(arena_state.allocator(), &args);

    try testing.expectEqual(@as(usize, 0), request.version_count);
    try testing.expectEqual(@as(usize, 1), request.debug_level);
    try testing.expectEqual(@as(usize, 0), request.reference_files.len);
    try testing.expectEqualStrings("--", request.dump_types_file.?);

    const expected_rendered = [_][]const u8{
        "-T",
        "--",
        "-d",
        "--",
        "input.c",
        "--reference",
        "after.symref",
    };
    try testing.expectEqualSlices([]const u8, &expected_rendered, request.rendered_args);
}

test "bridge renders consumed terminator values as parsed option data" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "source.c",
        "--reference",
        "--",
        "-T",
        "--",
        "--version",
        "--",
        "--debug",
    };

    const request = try expectRequest(arena_state.allocator(), &args);

    try testing.expectEqual(@as(usize, 1), request.version_count);
    try testing.expectEqual(@as(usize, 0), request.debug_level);
    try testing.expectEqual(@as(usize, 1), request.reference_files.len);
    try testing.expectEqualStrings("--", request.reference_files[0]);
    try testing.expectEqualStrings("--", request.dump_types_file.?);

    var output: std.Io.Writer.Allocating = .init(testing.allocator);
    defer output.deinit();

    try genksyms.renderGenksymsBridge(&output.writer, request);
    try testing.expectEqualStrings(
        "{\"tool\":\"scripts/genksyms/genksyms\",\"stdin\":\"cpp-stream\",\"stdout\":\"symversions\",\"argv\":[\"scripts/genksyms/genksyms\",\"--reference\",\"--\",\"-T\",\"--\",\"--version\",\"--\",\"source.c\",\"--debug\"],\"options\":{\"debug_level\":0,\"warnings\":false,\"dump_defs\":false,\"preserve\":false,\"reference_files\":[\"--\"],\"dump_types_file\":\"--\"}}\n",
        output.written(),
    );
}
