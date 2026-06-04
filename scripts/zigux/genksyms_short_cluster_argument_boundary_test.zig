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
        .failure => error.UnexpectedParseFailure,
    };
}

test "genksyms short cluster consumes attached reference suffix as data" {
    const args = [_][]const u8{
        "-dwrcluster.symref",
        "-Ttypes.symtypes",
    };
    const request = try expectRequest(&args);
    defer testing.allocator.free(request.rendered_args);
    defer testing.allocator.free(request.reference_files);

    try testing.expectEqual(@as(usize, 1), request.debug_level);
    try testing.expect(request.warnings);
    try testing.expectEqual(@as(usize, 1), request.reference_files.len);
    try testing.expectEqualStrings("cluster.symref", request.reference_files[0]);
    try testing.expectEqualStrings("types.symtypes", request.dump_types_file.?);
    try testing.expectEqualSlices([]const u8, &args, request.rendered_args);
}

test "genksyms short cluster consumes attached dump types suffix as data" {
    const args = [_][]const u8{
        "-DdpTtypes.symtypes",
        "--reference",
        "baseline.symref",
        "tail.c",
    };
    const request = try expectRequest(&args);
    defer testing.allocator.free(request.rendered_args);
    defer testing.allocator.free(request.reference_files);

    try testing.expectEqual(@as(usize, 1), request.debug_level);
    try testing.expect(request.dump_defs);
    try testing.expect(request.preserve);
    try testing.expectEqualStrings("types.symtypes", request.dump_types_file.?);
    try testing.expectEqual(@as(usize, 1), request.reference_files.len);
    try testing.expectEqualStrings("baseline.symref", request.reference_files[0]);
    try testing.expectEqualSlices([]const u8, &args, request.rendered_args);

    var output: std.Io.Writer.Allocating = .init(testing.allocator);
    defer output.deinit();

    try genksyms.renderGenksymsBridge(&output.writer, request);
    try testing.expect(std.mem.containsAtLeast(
        u8,
        output.written(),
        1,
        "\"argv\":[\"scripts/genksyms/genksyms\",\"-DdpTtypes.symtypes\",\"--reference\",\"baseline.symref\",\"tail.c\"]",
    ));
    try testing.expect(std.mem.containsAtLeast(
        u8,
        output.written(),
        1,
        "\"debug_level\":1,\"warnings\":false,\"dump_defs\":true,\"preserve\":true,\"reference_files\":[\"baseline.symref\"],\"dump_types_file\":\"types.symtypes\"",
    ));
}
