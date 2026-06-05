const std = @import("std");
const testing = std.testing;
const genksyms = @import("genksyms.zig");

fn expectRequest(args: []const []const u8) !genksyms.Request {
    const outcome = try genksyms.parseArgs(testing.allocator, args);
    switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| return request,
            else => return error.ExpectedRequestCommand,
        },
        else => return error.ExpectedRequestCommand,
    }
}

test "empty inline required values allow later non-empty replacements" {
    const args = [_][]const u8{
        "--reference=",
        "--dump-types=",
        "--version",
        "--reference=final.symref",
        "--dump-types=final.symtypes",
        "-d",
    };
    const request = try expectRequest(&args);
    defer testing.allocator.free(request.rendered_args);
    defer testing.allocator.free(request.reference_files);

    try testing.expectEqual(@as(usize, 1), request.version_count);
    try testing.expectEqual(@as(usize, 1), request.debug_level);
    try testing.expectEqual(@as(usize, 2), request.reference_files.len);
    try testing.expectEqualStrings("", request.reference_files[0]);
    try testing.expectEqualStrings("final.symref", request.reference_files[1]);
    try testing.expectEqualStrings("final.symtypes", request.dump_types_file.?);
    try testing.expectEqualSlices([]const u8, &args, request.raw_args);
    try testing.expectEqualSlices([]const u8, &args, request.rendered_args);

    var output: std.Io.Writer.Allocating = .init(testing.allocator);
    defer output.deinit();
    try genksyms.renderGenksymsBridge(&output.writer, request);
    try testing.expectEqualStrings(
        "{\"tool\":\"scripts/genksyms/genksyms\",\"stdin\":\"cpp-stream\",\"stdout\":\"symversions\",\"argv\":[\"scripts/genksyms/genksyms\",\"--reference=\",\"--dump-types=\",\"--version\",\"--reference=final.symref\",\"--dump-types=final.symtypes\",\"-d\"],\"options\":{\"debug_level\":1,\"warnings\":false,\"dump_defs\":false,\"preserve\":false,\"reference_files\":[\"\",\"final.symref\"],\"dump_types_file\":\"final.symtypes\"}}\n",
        output.written(),
    );
}

test "later empty inline required values stay data instead of missing arguments" {
    const args = [_][]const u8{
        "--reference=initial.symref",
        "--dump-types=initial.symtypes",
        "--reference=",
        "--dump-types=",
        "--preserve",
    };
    const request = try expectRequest(&args);
    defer testing.allocator.free(request.rendered_args);
    defer testing.allocator.free(request.reference_files);

    try testing.expectEqual(@as(usize, 0), request.version_count);
    try testing.expect(request.preserve);
    try testing.expectEqual(@as(usize, 2), request.reference_files.len);
    try testing.expectEqualStrings("initial.symref", request.reference_files[0]);
    try testing.expectEqualStrings("", request.reference_files[1]);
    try testing.expect(request.dump_types_file != null);
    try testing.expectEqualStrings("", request.dump_types_file.?);
    try testing.expectEqualSlices([]const u8, &args, request.raw_args);
    try testing.expectEqualSlices([]const u8, &args, request.rendered_args);
}
