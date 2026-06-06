const std = @import("std");
const testing = std.testing;

const genksyms = @import("genksyms.zig");

test "pure version flags become request side effects after delayed positionals" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "first-pos.c",
        "-V",
        "--version",
        "second-pos.c",
        "--ver",
        "-VV",
    };

    const outcome = try genksyms.parseArgs(arena_state.allocator(), &args);
    switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| {
                try testing.expectEqual(@as(usize, 5), request.version_count);
                try testing.expectEqual(@as(usize, 0), request.debug_level);
                try testing.expect(!request.warnings);
                try testing.expect(!request.dump_defs);
                try testing.expect(!request.preserve);
                try testing.expectEqual(@as(usize, 0), request.reference_files.len);
                try testing.expect(request.dump_types_file == null);

                const expected_rendered = [_][]const u8{
                    "-V",
                    "--version",
                    "--ver",
                    "-VV",
                    "first-pos.c",
                    "second-pos.c",
                };
                try testing.expectEqualSlices([]const u8, &expected_rendered, request.rendered_args);
                try testing.expectEqualSlices([]const u8, &args, request.raw_args);
            },
            else => return error.ExpectedRequestCommand,
        },
        .failure => return error.ExpectedRequestCommand,
    }
}

test "version after positionals bridge keeps versions out of argv options" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "-VV",
        "input.c",
        "--ver",
        "tail.h",
    };

    const outcome = try genksyms.parseArgs(arena_state.allocator(), &args);
    const request = switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| request,
            else => return error.ExpectedRequestCommand,
        },
        .failure => return error.ExpectedRequestCommand,
    };

    try testing.expectEqual(@as(usize, 3), request.version_count);

    var output: std.Io.Writer.Allocating = .init(testing.allocator);
    defer output.deinit();
    try genksyms.renderGenksymsBridge(&output.writer, request);

    try testing.expectEqualStrings(
        "{\"tool\":\"scripts/genksyms/genksyms\",\"stdin\":\"cpp-stream\",\"stdout\":\"symversions\",\"argv\":[\"scripts/genksyms/genksyms\",\"-VV\",\"--ver\",\"input.c\",\"tail.h\"],\"options\":{\"debug_level\":0,\"warnings\":false,\"dump_defs\":false,\"preserve\":false,\"reference_files\":[],\"dump_types_file\":null}}\n",
        output.written(),
    );
}
