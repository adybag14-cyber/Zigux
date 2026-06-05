const std = @import("std");
const genksyms = @import("genksyms.zig");

const testing = std.testing;

test "genksyms bridge keeps warning quiet state after delayed positionals" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "leftover.c",
        "--warnings",
        "--reference",
        "--debug",
        "middle.h",
        "--dump-types",
        "--types-file",
        "--quiet",
    };
    const expected_rendered = [_][]const u8{
        "--warnings",
        "--reference",
        "--debug",
        "--dump-types",
        "--types-file",
        "--quiet",
        "leftover.c",
        "middle.h",
    };

    const outcome = try genksyms.parseArgs(arena_state.allocator(), &args);
    const request = switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| request,
            else => return error.ExpectedRequestCommand,
        },
        else => return error.ExpectedRequestCommand,
    };

    try testing.expectEqual(@as(usize, 0), request.debug_level);
    try testing.expect(!request.warnings);
    try testing.expect(!request.dump_defs);
    try testing.expect(!request.preserve);
    try testing.expectEqual(@as(usize, 0), request.version_count);
    try testing.expectEqual(@as(usize, 1), request.reference_files.len);
    try testing.expectEqualStrings("--debug", request.reference_files[0]);
    try testing.expectEqualStrings("--types-file", request.dump_types_file.?);
    try testing.expectEqualSlices([]const u8, &args, request.raw_args);
    try testing.expectEqualSlices([]const u8, &expected_rendered, request.rendered_args);

    var output: std.Io.Writer.Allocating = .init(testing.allocator);
    defer output.deinit();

    try genksyms.renderGenksymsBridge(&output.writer, request);
    try testing.expectEqualStrings(
        "{\"tool\":\"scripts/genksyms/genksyms\",\"stdin\":\"cpp-stream\",\"stdout\":\"symversions\",\"argv\":[\"scripts/genksyms/genksyms\",\"--warnings\",\"--reference\",\"--debug\",\"--dump-types\",\"--types-file\",\"--quiet\",\"leftover.c\",\"middle.h\"],\"options\":{\"debug_level\":0,\"warnings\":false,\"dump_defs\":false,\"preserve\":false,\"reference_files\":[\"--debug\"],\"dump_types_file\":\"--types-file\"}}\n",
        output.written(),
    );
}
