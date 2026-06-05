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

test "genksyms keeps empty inline reference after delayed positionals" {
    const args = [_][]const u8{
        "leftover.c",
        "--reference=",
        "middle.h",
        "-w",
        "-r",
        "tail.symref",
        "tail.c",
    };
    const request = try expectRequest(&args);
    defer testing.allocator.free(request.rendered_args);
    defer testing.allocator.free(request.reference_files);

    try testing.expectEqualSlices([]const u8, &args, request.raw_args);
    try testing.expect(request.warnings);
    try testing.expectEqual(@as(usize, 2), request.reference_files.len);
    try testing.expectEqualStrings("", request.reference_files[0]);
    try testing.expectEqualStrings("tail.symref", request.reference_files[1]);
    try testing.expect(request.dump_types_file == null);

    const rendered = [_][]const u8{
        "--reference=",
        "-w",
        "-r",
        "tail.symref",
        "leftover.c",
        "middle.h",
        "tail.c",
    };
    try testing.expectEqualSlices([]const u8, &rendered, request.rendered_args);
}

test "genksyms keeps empty inline dump-types after delayed positionals" {
    const args = [_][]const u8{
        "first.c",
        "-V",
        "--dump-t=",
        "second.h",
        "--reference=ref.sym",
        "-D",
    };
    const request = try expectRequest(&args);
    defer testing.allocator.free(request.rendered_args);
    defer testing.allocator.free(request.reference_files);

    try testing.expectEqualSlices([]const u8, &args, request.raw_args);
    try testing.expectEqual(@as(usize, 1), request.version_count);
    try testing.expect(request.dump_defs);
    try testing.expectEqualStrings("", request.dump_types_file.?);
    try testing.expectEqual(@as(usize, 1), request.reference_files.len);
    try testing.expectEqualStrings("ref.sym", request.reference_files[0]);

    const rendered = [_][]const u8{
        "-V",
        "--dump-t=",
        "--reference=ref.sym",
        "-D",
        "first.c",
        "second.h",
    };
    try testing.expectEqualSlices([]const u8, &rendered, request.rendered_args);
}

test "genksyms renders empty inline required args after positionals in bridge json" {
    const args = [_][]const u8{
        "input.c",
        "--reference=",
        "input.h",
        "--dump-types=",
        "--preserve",
    };
    const request = try expectRequest(&args);
    defer testing.allocator.free(request.rendered_args);
    defer testing.allocator.free(request.reference_files);

    try testing.expect(request.preserve);
    try testing.expectEqual(@as(usize, 1), request.reference_files.len);
    try testing.expectEqualStrings("", request.reference_files[0]);
    try testing.expectEqualStrings("", request.dump_types_file.?);

    var output: std.Io.Writer.Allocating = .init(testing.allocator);
    defer output.deinit();

    try genksyms.renderGenksymsBridge(&output.writer, request);
    try testing.expectEqualStrings(
        "{\"tool\":\"scripts/genksyms/genksyms\",\"stdin\":\"cpp-stream\",\"stdout\":\"symversions\",\"argv\":[\"scripts/genksyms/genksyms\",\"--reference=\",\"--dump-types=\",\"--preserve\",\"input.c\",\"input.h\"],\"options\":{\"debug_level\":0,\"warnings\":false,\"dump_defs\":false,\"preserve\":true,\"reference_files\":[\"\"],\"dump_types_file\":\"\"}}\n",
        output.written(),
    );
}
