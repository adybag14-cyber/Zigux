const std = @import("std");
const testing = std.testing;
const genksyms = @import("genksyms.zig");

fn expectVersionRequest(
    args: []const []const u8,
    expected_version_count: usize,
    expected_rendered_args: []const []const u8,
    expected_raw_args: []const []const u8,
) !void {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const outcome = try genksyms.parseArgs(arena_state.allocator(), args);
    switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| {
                try testing.expectEqual(expected_version_count, request.version_count);
                try testing.expectEqual(@as(usize, 0), request.debug_level);
                try testing.expect(!request.warnings);
                try testing.expect(!request.dump_defs);
                try testing.expect(!request.preserve);
                try testing.expectEqual(@as(usize, 0), request.reference_files.len);
                try testing.expect(request.dump_types_file == null);
                try testing.expectEqualSlices([]const u8, expected_rendered_args, request.rendered_args);
                try testing.expectEqualSlices([]const u8, expected_raw_args, request.raw_args);
            },
            .version => return error.ExpectedRequestNotVersionCommand,
            else => return error.ExpectedRequestCommand,
        },
        else => return error.ExpectedRequestCommand,
    }
}

test "pure long version after delayed positionals remains request state" {
    const args = [_][]const u8{
        "leftover.c",
        "--version",
        "rightover.h",
        "--ver",
    };
    const expected_rendered = [_][]const u8{
        "--version",
        "--ver",
        "leftover.c",
        "rightover.h",
    };

    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const outcome = try genksyms.parseArgs(arena_state.allocator(), &args);
    const request = switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| request,
            .version => return error.ExpectedRequestNotVersionCommand,
            else => return error.ExpectedRequestCommand,
        },
        else => return error.ExpectedRequestCommand,
    };

    try testing.expectEqual(@as(usize, 2), request.version_count);
    try testing.expectEqualSlices([]const u8, &expected_rendered, request.rendered_args);
    try testing.expectEqualSlices([]const u8, &args, request.raw_args);

    var output: std.Io.Writer.Allocating = .init(testing.allocator);
    defer output.deinit();

    try genksyms.renderGenksymsBridge(&output.writer, request);
    try testing.expectEqualStrings(
        "{\"tool\":\"scripts/genksyms/genksyms\",\"stdin\":\"cpp-stream\",\"stdout\":\"symversions\",\"argv\":[\"scripts/genksyms/genksyms\",\"--version\",\"--ver\",\"leftover.c\",\"rightover.h\"],\"options\":{\"debug_level\":0,\"warnings\":false,\"dump_defs\":false,\"preserve\":false,\"reference_files\":[],\"dump_types_file\":null}}\n",
        output.written(),
    );
}

test "pure short version clusters after delayed positionals remain request state" {
    const args = [_][]const u8{
        "before.sym",
        "-VV",
        "after.sym",
        "-V",
    };
    const expected_rendered = [_][]const u8{
        "-VV",
        "-V",
        "before.sym",
        "after.sym",
    };

    try expectVersionRequest(&args, 3, &expected_rendered, &args);
}

test "mixed pure version forms after option-looking positionals stay side effects" {
    const args = [_][]const u8{
        "-",
        "--version",
        "literal--version",
        "-VV",
    };
    const expected_rendered = [_][]const u8{
        "--version",
        "-VV",
        "-",
        "literal--version",
    };

    try expectVersionRequest(&args, 3, &expected_rendered, &args);
}
