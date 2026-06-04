const std = @import("std");
const genksyms = @import("genksyms.zig");

const testing = std.testing;

test "genksyms bridge renders explicit empty option arguments" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "--reference=",
        "--ref=",
        "-r",
        "",
        "--dump-types=",
        "--dump-t=",
        "-T",
        "",
    };

    const outcome = try genksyms.parseArgs(arena_state.allocator(), &args);
    const request = switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| request,
            else => return error.ExpectedRequestCommand,
        },
        else => return error.ExpectedRequestCommand,
    };

    try testing.expectEqual(@as(usize, 0), request.version_count);
    try testing.expectEqual(@as(usize, 0), request.debug_level);
    try testing.expect(!request.warnings);
    try testing.expect(!request.dump_defs);
    try testing.expect(!request.preserve);
    try testing.expectEqual(@as(usize, 3), request.reference_files.len);
    try testing.expectEqualStrings("", request.reference_files[0]);
    try testing.expectEqualStrings("", request.reference_files[1]);
    try testing.expectEqualStrings("", request.reference_files[2]);
    try testing.expect(request.dump_types_file != null);
    try testing.expectEqualStrings("", request.dump_types_file.?);
    try testing.expectEqualSlices([]const u8, &args, request.rendered_args);

    var output: std.Io.Writer.Allocating = .init(testing.allocator);
    defer output.deinit();

    try genksyms.renderGenksymsBridge(&output.writer, request);
    try testing.expectEqualStrings(
        "{\"tool\":\"scripts/genksyms/genksyms\",\"stdin\":\"cpp-stream\",\"stdout\":\"symversions\",\"argv\":[\"scripts/genksyms/genksyms\",\"--reference=\",\"--ref=\",\"-r\",\"\",\"--dump-types=\",\"--dump-t=\",\"-T\",\"\"],\"options\":{\"debug_level\":0,\"warnings\":false,\"dump_defs\":false,\"preserve\":false,\"reference_files\":[\"\",\"\",\"\"],\"dump_types_file\":\"\"}}\n",
        output.written(),
    );
}
