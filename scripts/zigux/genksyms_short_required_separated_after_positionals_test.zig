const std = @import("std");
const testing = std.testing;

const genksyms = @import("genksyms.zig");

test "short required separated values stay data after delayed positionals" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "alpha.c",
        "-r",
        "--reference-looking-value",
        "beta.c",
        "-T",
        "-Vd",
        "-r",
        "--",
    };

    const outcome = try genksyms.parseArgs(arena_state.allocator(), &args);
    switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| {
                try testing.expectEqual(@as(usize, 2), request.reference_files.len);
                try testing.expectEqualStrings("--reference-looking-value", request.reference_files[0]);
                try testing.expectEqualStrings("--", request.reference_files[1]);
                try testing.expectEqualStrings("-Vd", request.dump_types_file.?);
                try testing.expectEqual(@as(usize, 0), request.debug_level);
                try testing.expect(!request.warnings);
                try testing.expect(!request.dump_defs);
                try testing.expect(!request.preserve);
                try testing.expectEqual(@as(usize, 0), request.version_count);

                const expected_rendered = [_][]const u8{
                    "-r",
                    "--reference-looking-value",
                    "-T",
                    "-Vd",
                    "-r",
                    "--",
                    "alpha.c",
                    "beta.c",
                };
                try testing.expectEqualSlices([]const u8, &args, request.raw_args);
                try testing.expectEqualSlices([]const u8, &expected_rendered, request.rendered_args);
            },
            else => return error.ExpectedRequestCommand,
        },
        .failure => return error.ExpectedRequestCommand,
    }
}

test "short required separated bridge renders option-looking payloads as data" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "input.sym",
        "-r",
        "--version",
        "-T",
        "--debug",
        "-r",
        "-q",
        "--warnings",
    };

    const outcome = try genksyms.parseArgs(arena_state.allocator(), &args);
    const request = switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| request,
            else => return error.ExpectedRequestCommand,
        },
        .failure => return error.ExpectedRequestCommand,
    };

    try testing.expectEqual(@as(usize, 0), request.version_count);
    try testing.expectEqual(@as(usize, 0), request.debug_level);
    try testing.expect(request.warnings);
    try testing.expectEqual(@as(usize, 2), request.reference_files.len);
    try testing.expectEqualStrings("--version", request.reference_files[0]);
    try testing.expectEqualStrings("-q", request.reference_files[1]);
    try testing.expectEqualStrings("--debug", request.dump_types_file.?);

    var output: std.Io.Writer.Allocating = .init(testing.allocator);
    defer output.deinit();
    try genksyms.renderGenksymsBridge(&output.writer, request);

    try testing.expectEqualStrings(
        "{\"tool\":\"scripts/genksyms/genksyms\",\"stdin\":\"cpp-stream\",\"stdout\":\"symversions\",\"argv\":[\"scripts/genksyms/genksyms\",\"-r\",\"--version\",\"-T\",\"--debug\",\"-r\",\"-q\",\"--warnings\",\"input.sym\"],\"options\":{\"debug_level\":0,\"warnings\":true,\"dump_defs\":false,\"preserve\":false,\"reference_files\":[\"--version\",\"-q\"],\"dump_types_file\":\"--debug\"}}\n",
        output.written(),
    );
}
