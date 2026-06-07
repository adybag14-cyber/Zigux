const std = @import("std");
const testing = std.testing;
const genksyms = @import("genksyms.zig");

fn expectRequest(args: []const []const u8) !genksyms.Request {
    const outcome = try genksyms.parseArgs(testing.allocator, args);
    return switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| request,
            else => error.ExpectedRequestCommand,
        },
        else => error.ExpectedRequestCommand,
    };
}

test "dash-prefixed long required values after positionals stay data" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "left.c",
        "--version",
        "--debug",
        "--reference",
        "--not-an-option.symref",
        "-T",
        "--types-output",
        "--preserve",
        "right.c",
    };
    const request = try expectRequest(&args);
    defer testing.allocator.free(request.rendered_args);
    defer testing.allocator.free(request.reference_files);

    const expected_rendered = [_][]const u8{
        "--version",
        "--debug",
        "--reference",
        "--not-an-option.symref",
        "-T",
        "--types-output",
        "--preserve",
        "left.c",
        "right.c",
    };

    try testing.expectEqual(@as(usize, 1), request.version_count);
    try testing.expectEqual(@as(usize, 1), request.debug_level);
    try testing.expect(request.preserve);
    try testing.expectEqual(@as(usize, 1), request.reference_files.len);
    try testing.expectEqualStrings("--not-an-option.symref", request.reference_files[0]);
    try testing.expectEqualStrings("--types-output", request.dump_types_file.?);
    try testing.expectEqualSlices([]const u8, &args, request.raw_args);
    try testing.expectEqualSlices([]const u8, &expected_rendered, request.rendered_args);

    var bridge: std.Io.Writer.Allocating = .init(testing.allocator);
    defer bridge.deinit();

    try genksyms.renderGenksymsBridge(&bridge.writer, request);
    try testing.expectEqualStrings(
        "{\"tool\":\"scripts/genksyms/genksyms\",\"stdin\":\"cpp-stream\",\"stdout\":\"symversions\",\"argv\":[\"scripts/genksyms/genksyms\",\"--version\",\"--debug\",\"--reference\",\"--not-an-option.symref\",\"-T\",\"--types-output\",\"--preserve\",\"left.c\",\"right.c\"],\"options\":{\"debug_level\":1,\"warnings\":false,\"dump_defs\":false,\"preserve\":true,\"reference_files\":[\"--not-an-option.symref\"],\"dump_types_file\":\"--types-output\"}}\n",
        bridge.written(),
    );
}

test "dash-prefixed short required values after positionals do not become flags" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "input.c",
        "-r",
        "-Vd.symref",
        "-T-dash.types",
        "-D",
        "-p",
        "tail.c",
    };
    const request = try expectRequest(&args);
    defer testing.allocator.free(request.rendered_args);
    defer testing.allocator.free(request.reference_files);

    const expected_rendered = [_][]const u8{
        "-r",
        "-Vd.symref",
        "-T-dash.types",
        "-D",
        "-p",
        "input.c",
        "tail.c",
    };

    try testing.expectEqual(@as(usize, 0), request.version_count);
    try testing.expectEqual(@as(usize, 0), request.debug_level);
    try testing.expect(request.dump_defs);
    try testing.expect(request.preserve);
    try testing.expectEqual(@as(usize, 1), request.reference_files.len);
    try testing.expectEqualStrings("-Vd.symref", request.reference_files[0]);
    try testing.expectEqualStrings("-dash.types", request.dump_types_file.?);
    try testing.expectEqualSlices([]const u8, &expected_rendered, request.rendered_args);
}

test "dash-prefixed required values preserve later real version side effects" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "before.c",
        "--reference",
        "-V",
        "--dump-types",
        "--debug",
        "--version",
        "after.c",
    };
    const request = try expectRequest(&args);
    defer testing.allocator.free(request.rendered_args);
    defer testing.allocator.free(request.reference_files);

    const expected_rendered = [_][]const u8{
        "--reference",
        "-V",
        "--dump-types",
        "--debug",
        "--version",
        "before.c",
        "after.c",
    };

    try testing.expectEqual(@as(usize, 1), request.version_count);
    try testing.expectEqual(@as(usize, 0), request.debug_level);
    try testing.expectEqual(@as(usize, 1), request.reference_files.len);
    try testing.expectEqualStrings("-V", request.reference_files[0]);
    try testing.expectEqualStrings("--debug", request.dump_types_file.?);
    try testing.expectEqualSlices([]const u8, &expected_rendered, request.rendered_args);
}
