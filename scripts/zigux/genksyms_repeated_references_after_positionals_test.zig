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
        else => error.ExpectedRequestCommand,
    };
}

test "genksyms accumulates repeated references after delayed positionals" {
    const args = [_][]const u8{
        "first.c",
        "--reference",
        "one.symref",
        "middle.h",
        "-rsecond.symref",
        "--ref=third.symref",
        "-T",
        "types.symtypes",
        "tail.c",
    };
    const request = try expectRequest(&args);
    defer testing.allocator.free(request.rendered_args);
    defer testing.allocator.free(request.reference_files);

    try testing.expectEqualSlices([]const u8, &args, request.raw_args);
    try testing.expectEqual(@as(usize, 3), request.reference_files.len);
    try testing.expectEqualStrings("one.symref", request.reference_files[0]);
    try testing.expectEqualStrings("second.symref", request.reference_files[1]);
    try testing.expectEqualStrings("third.symref", request.reference_files[2]);
    try testing.expectEqualStrings("types.symtypes", request.dump_types_file.?);

    const rendered = [_][]const u8{
        "--reference",
        "one.symref",
        "-rsecond.symref",
        "--ref=third.symref",
        "-T",
        "types.symtypes",
        "first.c",
        "middle.h",
        "tail.c",
    };
    try testing.expectEqualSlices([]const u8, &rendered, request.rendered_args);
}

test "genksyms renders repeated references after positionals in bridge json" {
    const args = [_][]const u8{
        "left.c",
        "-V",
        "-r",
        "first.symref",
        "right.c",
        "--reference=second.symref",
        "--warnings",
    };
    const request = try expectRequest(&args);
    defer testing.allocator.free(request.rendered_args);
    defer testing.allocator.free(request.reference_files);

    try testing.expectEqual(@as(usize, 1), request.version_count);
    try testing.expect(request.warnings);
    try testing.expectEqual(@as(usize, 2), request.reference_files.len);
    try testing.expectEqualStrings("first.symref", request.reference_files[0]);
    try testing.expectEqualStrings("second.symref", request.reference_files[1]);

    var output: std.Io.Writer.Allocating = .init(testing.allocator);
    defer output.deinit();

    try genksyms.renderGenksymsBridge(&output.writer, request);
    try testing.expectEqualStrings(
        "{\"tool\":\"scripts/genksyms/genksyms\",\"stdin\":\"cpp-stream\",\"stdout\":\"symversions\",\"argv\":[\"scripts/genksyms/genksyms\",\"-V\",\"-r\",\"first.symref\",\"--reference=second.symref\",\"--warnings\",\"left.c\",\"right.c\"],\"options\":{\"debug_level\":0,\"warnings\":true,\"dump_defs\":false,\"preserve\":false,\"reference_files\":[\"first.symref\",\"second.symref\"],\"dump_types_file\":null}}\n",
        output.written(),
    );
}
