const std = @import("std");
const genksyms = @import("genksyms.zig");

test "separated required values before positionals stay option data" {
    var arena_state = std.heap.ArenaAllocator.init(std.testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "--reference",
        "--version",
        "-T",
        "--",
        "left.c",
        "--warnings",
        "right.h",
        "--dump",
    };

    const outcome = try genksyms.parseArgs(arena_state.allocator(), &args);
    switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| {
                const expected_rendered = [_][]const u8{
                    "--reference",
                    "--version",
                    "-T",
                    "--",
                    "--warnings",
                    "--dump",
                    "left.c",
                    "right.h",
                };

                try std.testing.expectEqualSlices([]const u8, &args, request.raw_args);
                try std.testing.expectEqualSlices([]const u8, &expected_rendered, request.rendered_args);
                try std.testing.expectEqual(@as(usize, 0), request.version_count);
                try std.testing.expect(request.warnings);
                try std.testing.expect(request.dump_defs);
                try std.testing.expect(!request.preserve);
                try std.testing.expectEqual(@as(usize, 1), request.reference_files.len);
                try std.testing.expectEqualStrings("--version", request.reference_files[0]);
                try std.testing.expectEqualStrings("--", request.dump_types_file.?);
            },
            else => return error.ExpectedRequestCommand,
        },
        else => return error.ExpectedRequestCommand,
    }
}

test "bridge renders separated required values before delayed positionals" {
    var arena_state = std.heap.ArenaAllocator.init(std.testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "--reference",
        "--version",
        "-T",
        "--",
        "left.c",
        "--warnings",
        "right.h",
        "--dump",
    };

    const outcome = try genksyms.parseArgs(arena_state.allocator(), &args);
    const request = switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| request,
            else => return error.ExpectedRequestCommand,
        },
        else => return error.ExpectedRequestCommand,
    };

    var output: std.Io.Writer.Allocating = .init(std.testing.allocator);
    defer output.deinit();

    try genksyms.renderGenksymsBridge(&output.writer, request);
    try std.testing.expectEqualStrings(
        "{\"tool\":\"scripts/genksyms/genksyms\",\"stdin\":\"cpp-stream\",\"stdout\":\"symversions\",\"argv\":[\"scripts/genksyms/genksyms\",\"--reference\",\"--version\",\"-T\",\"--\",\"--warnings\",\"--dump\",\"left.c\",\"right.h\"],\"options\":{\"debug_level\":0,\"warnings\":true,\"dump_defs\":true,\"preserve\":false,\"reference_files\":[\"--version\"],\"dump_types_file\":\"--\"}}\n",
        output.written(),
    );
}
