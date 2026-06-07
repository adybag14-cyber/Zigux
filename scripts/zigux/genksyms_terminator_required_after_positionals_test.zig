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

test "terminator after positionals keeps required-looking long tokens as data" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "early.c",
        "--version",
        "--reference",
        "pre.symref",
        "middle.c",
        "--",
        "--reference",
        "--dump-types",
        "-r",
        "tail.c",
    };
    const request = try expectRequest(&args);
    defer testing.allocator.free(request.rendered_args);
    defer testing.allocator.free(request.reference_files);

    const expected_rendered = [_][]const u8{
        "--version",
        "--reference",
        "pre.symref",
        "--",
        "early.c",
        "middle.c",
        "--reference",
        "--dump-types",
        "-r",
        "tail.c",
    };

    try testing.expectEqual(@as(usize, 1), request.version_count);
    try testing.expectEqual(@as(usize, 1), request.reference_files.len);
    try testing.expectEqualStrings("pre.symref", request.reference_files[0]);
    try testing.expectEqual(@as(?[]const u8, null), request.dump_types_file);
    try testing.expectEqualSlices([]const u8, &args, request.raw_args);
    try testing.expectEqualSlices([]const u8, &expected_rendered, request.rendered_args);
}

test "terminator preserves required-looking short clusters after delayed positionals" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "left.c",
        "-T",
        "pre.types",
        "-w",
        "right.c",
        "--",
        "-Tpost.types",
        "-rpost.symref",
        "-V",
        "--debug",
    };
    const request = try expectRequest(&args);
    defer testing.allocator.free(request.rendered_args);
    defer testing.allocator.free(request.reference_files);

    const expected_rendered = [_][]const u8{
        "-T",
        "pre.types",
        "-w",
        "--",
        "left.c",
        "right.c",
        "-Tpost.types",
        "-rpost.symref",
        "-V",
        "--debug",
    };

    try testing.expectEqual(@as(usize, 0), request.version_count);
    try testing.expect(request.warnings);
    try testing.expectEqual(@as(usize, 0), request.reference_files.len);
    try testing.expectEqualStrings("pre.types", request.dump_types_file.?);
    try testing.expectEqualSlices([]const u8, &expected_rendered, request.rendered_args);
}

test "terminator-preserved required tokens render through bridge json" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "before.c",
        "--debug",
        "--dump-types=pre.types",
        "--",
        "--reference",
        "post.symref",
        "-Tpost.types",
        "after.c",
    };
    const request = try expectRequest(&args);
    defer testing.allocator.free(request.rendered_args);
    defer testing.allocator.free(request.reference_files);

    const expected_rendered = [_][]const u8{
        "--debug",
        "--dump-types=pre.types",
        "--",
        "before.c",
        "--reference",
        "post.symref",
        "-Tpost.types",
        "after.c",
    };

    try testing.expectEqual(@as(usize, 1), request.debug_level);
    try testing.expectEqualStrings("pre.types", request.dump_types_file.?);
    try testing.expectEqual(@as(usize, 0), request.reference_files.len);
    try testing.expectEqualSlices([]const u8, &expected_rendered, request.rendered_args);

    var bridge: std.Io.Writer.Allocating = .init(testing.allocator);
    defer bridge.deinit();

    try genksyms.renderGenksymsBridge(&bridge.writer, request);
    try testing.expectEqualStrings(
        "{\"tool\":\"scripts/genksyms/genksyms\",\"stdin\":\"cpp-stream\",\"stdout\":\"symversions\",\"argv\":[\"scripts/genksyms/genksyms\",\"--debug\",\"--dump-types=pre.types\",\"--\",\"before.c\",\"--reference\",\"post.symref\",\"-Tpost.types\",\"after.c\"],\"options\":{\"debug_level\":1,\"warnings\":false,\"dump_defs\":false,\"preserve\":false,\"reference_files\":[],\"dump_types_file\":\"pre.types\"}}\n",
        bridge.written(),
    );
}
