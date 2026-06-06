const std = @import("std");
const genksyms = @import("genksyms.zig");

const testing = std.testing;

test "interleaved version flags remain request side effects after delayed positionals" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();
    const arena = arena_state.allocator();

    const args = [_][]const u8{
        "--version",
        "early.c",
        "-VV",
        "middle.h",
        "--ver",
        "--debug",
        "-d",
        "--reference",
        "refs.sym",
        "late.c",
        "--dump-types=types.sym",
        "--warnings",
    };
    const rendered_args = [_][]const u8{
        "--version",
        "-VV",
        "--ver",
        "--debug",
        "-d",
        "--reference",
        "refs.sym",
        "--dump-types=types.sym",
        "--warnings",
        "early.c",
        "middle.h",
        "late.c",
    };

    const outcome = try genksyms.parseArgs(arena, &args);
    const request = switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| request,
            else => return error.ExpectedRequestCommand,
        },
        else => return error.ExpectedRequestCommand,
    };

    try testing.expectEqual(@as(usize, 4), request.version_count);
    try testing.expectEqual(@as(usize, 2), request.debug_level);
    try testing.expect(request.warnings);
    try testing.expect(!request.dump_defs);
    try testing.expect(!request.preserve);
    try testing.expectEqual(@as(usize, 1), request.reference_files.len);
    try testing.expectEqualStrings("refs.sym", request.reference_files[0]);
    try testing.expectEqualStrings("types.sym", request.dump_types_file.?);
    try testing.expectEqualSlices([]const u8, &args, request.raw_args);
    try testing.expectEqualSlices([]const u8, &rendered_args, request.rendered_args);

    var output: std.Io.Writer.Allocating = .init(testing.allocator);
    defer output.deinit();
    try genksyms.renderGenksymsBridge(&output.writer, request);

    try testing.expectEqualStrings(
        "{\"tool\":\"scripts/genksyms/genksyms\",\"stdin\":\"cpp-stream\",\"stdout\":\"symversions\",\"argv\":[\"scripts/genksyms/genksyms\",\"--version\",\"-VV\",\"--ver\",\"--debug\",\"-d\",\"--reference\",\"refs.sym\",\"--dump-types=types.sym\",\"--warnings\",\"early.c\",\"middle.h\",\"late.c\"],\"options\":{\"debug_level\":2,\"warnings\":true,\"dump_defs\":false,\"preserve\":false,\"reference_files\":[\"refs.sym\"],\"dump_types_file\":\"types.sym\"}}\n",
        output.written(),
    );
}
