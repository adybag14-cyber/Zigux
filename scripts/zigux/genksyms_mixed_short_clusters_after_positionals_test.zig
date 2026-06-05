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

test "genksyms parses mixed short clusters after delayed positionals" {
    const args = [_][]const u8{
        "leftover.c",
        "-dDwpqV",
        "rightover.h",
        "-Vd",
    };
    const request = try expectRequest(&args);
    defer testing.allocator.free(request.rendered_args);
    defer testing.allocator.free(request.reference_files);

    try testing.expectEqualSlices([]const u8, &args, request.raw_args);
    try testing.expectEqual(@as(usize, 2), request.debug_level);
    try testing.expectEqual(@as(usize, 2), request.version_count);
    try testing.expect(!request.warnings);
    try testing.expect(request.dump_defs);
    try testing.expect(request.preserve);
    try testing.expectEqual(@as(usize, 0), request.reference_files.len);
    try testing.expect(request.dump_types_file == null);

    const rendered = [_][]const u8{
        "-dDwpqV",
        "-Vd",
        "leftover.c",
        "rightover.h",
    };
    try testing.expectEqualSlices([]const u8, &rendered, request.rendered_args);
}

test "genksyms short cluster state resumes parsing after delayed positionals" {
    const args = [_][]const u8{
        "first.sym",
        "-Vdw",
        "-qDp",
        "--reference",
        "ref.sym",
        "second.sym",
        "--dump-types",
        "types.sym",
    };
    const request = try expectRequest(&args);
    defer testing.allocator.free(request.rendered_args);
    defer testing.allocator.free(request.reference_files);

    try testing.expectEqual(@as(usize, 1), request.debug_level);
    try testing.expectEqual(@as(usize, 1), request.version_count);
    try testing.expect(!request.warnings);
    try testing.expect(request.dump_defs);
    try testing.expect(request.preserve);
    try testing.expectEqual(@as(usize, 1), request.reference_files.len);
    try testing.expectEqualStrings("ref.sym", request.reference_files[0]);
    try testing.expectEqualStrings("types.sym", request.dump_types_file.?);

    const rendered = [_][]const u8{
        "-Vdw",
        "-qDp",
        "--reference",
        "ref.sym",
        "--dump-types",
        "types.sym",
        "first.sym",
        "second.sym",
    };
    try testing.expectEqualSlices([]const u8, &rendered, request.rendered_args);
}

test "genksyms renders mixed short clusters after positionals in bridge json" {
    const args = [_][]const u8{
        "input.sym",
        "-dDwpqV",
        "-Vd",
    };
    const request = try expectRequest(&args);
    defer testing.allocator.free(request.rendered_args);
    defer testing.allocator.free(request.reference_files);

    var output: std.Io.Writer.Allocating = .init(testing.allocator);
    defer output.deinit();

    try genksyms.renderGenksymsBridge(&output.writer, request);
    try testing.expectEqualStrings(
        "{\"tool\":\"scripts/genksyms/genksyms\",\"stdin\":\"cpp-stream\",\"stdout\":\"symversions\",\"argv\":[\"scripts/genksyms/genksyms\",\"-dDwpqV\",\"-Vd\",\"input.sym\"],\"options\":{\"debug_level\":2,\"warnings\":false,\"dump_defs\":true,\"preserve\":true,\"reference_files\":[],\"dump_types_file\":null}}\n",
        output.written(),
    );
}
