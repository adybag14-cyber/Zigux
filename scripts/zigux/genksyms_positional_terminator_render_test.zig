const std = @import("std");
const genksyms = @import("genksyms.zig");

const testing = std.testing;

test "genksyms bridge renders delayed positional args before explicit terminator tail" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "leftover.c",
        "--version",
        "-d",
        "middle.h",
        "-r",
        "live.symref",
        "--",
        "--reference=tail.symref",
        "-Ttail.symtypes",
    };
    const expected_rendered = [_][]const u8{
        "--version",
        "-d",
        "-r",
        "live.symref",
        "leftover.c",
        "middle.h",
        "--",
        "--reference=tail.symref",
        "-Ttail.symtypes",
    };

    const outcome = try genksyms.parseArgs(arena_state.allocator(), &args);
    const request = switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| request,
            else => return error.ExpectedRequestCommand,
        },
        else => return error.ExpectedRequestCommand,
    };

    try testing.expectEqual(@as(usize, 1), request.version_count);
    try testing.expectEqual(@as(usize, 1), request.debug_level);
    try testing.expectEqual(@as(usize, 1), request.reference_files.len);
    try testing.expectEqualStrings("live.symref", request.reference_files[0]);
    try testing.expect(request.dump_types_file == null);
    try testing.expectEqualSlices([]const u8, &expected_rendered, request.rendered_args);

    var output: std.Io.Writer.Allocating = .init(testing.allocator);
    defer output.deinit();

    try genksyms.renderGenksymsBridge(&output.writer, request);
    try testing.expectEqualStrings(
        "{\"tool\":\"scripts/genksyms/genksyms\",\"stdin\":\"cpp-stream\",\"stdout\":\"symversions\",\"argv\":[\"scripts/genksyms/genksyms\",\"--version\",\"-d\",\"-r\",\"live.symref\",\"leftover.c\",\"middle.h\",\"--\",\"--reference=tail.symref\",\"-Ttail.symtypes\"],\"options\":{\"debug_level\":1,\"warnings\":false,\"dump_defs\":false,\"preserve\":false,\"reference_files\":[\"live.symref\"],\"dump_types_file\":null}}\n",
        output.written(),
    );
}
