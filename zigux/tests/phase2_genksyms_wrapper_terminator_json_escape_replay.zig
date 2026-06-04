const std = @import("std");
const testing = std.testing;
const genksyms = @import("genksyms");

fn expectRequest(args: []const []const u8) !genksyms.Request {
    const outcome = try genksyms.parseArgs(testing.allocator, args);
    return switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| request,
            else => error.ExpectedRequestCommand,
        },
        .failure => error.ExpectedRequestCommand,
    };
}

test "terminator tail preserves escaped rendered argv data" {
    const args = [_][]const u8{
        "-d",
        "--",
        "--tail=\"quoted\"",
        "path\\name",
        "line\nnext",
        "carriage\rnext",
        "tab\tnext",
    };

    const request = try expectRequest(&args);
    defer testing.allocator.free(request.rendered_args);
    defer testing.allocator.free(request.reference_files);

    try testing.expectEqual(@as(usize, 1), request.debug_level);
    try testing.expectEqual(@as(usize, 0), request.version_count);
    try testing.expectEqual(@as(usize, 0), request.reference_files.len);
    try testing.expect(request.dump_types_file == null);
    try testing.expectEqualSlices([]const u8, &args, request.rendered_args);

    var output: std.Io.Writer.Allocating = .init(testing.allocator);
    defer output.deinit();

    try genksyms.renderGenksymsBridge(&output.writer, request);
    try testing.expectEqualStrings(
        "{\"tool\":\"scripts/genksyms/genksyms\",\"stdin\":\"cpp-stream\",\"stdout\":\"symversions\",\"argv\":[\"scripts/genksyms/genksyms\",\"-d\",\"--\",\"--tail=\\\"quoted\\\"\",\"path\\\\name\",\"line\\nnext\",\"carriage\\rnext\",\"tab\\tnext\"],\"options\":{\"debug_level\":1,\"warnings\":false,\"dump_defs\":false,\"preserve\":false,\"reference_files\":[],\"dump_types_file\":null}}\n",
        output.written(),
    );
}

test "terminator flushes buffered escaped positional data before tail" {
    const args = [_][]const u8{
        "--version",
        "left\"quote.c",
        "-w",
        "path\\before",
        "--",
        "--reference",
        "tail\nsymref",
    };

    const request = try expectRequest(&args);
    defer testing.allocator.free(request.rendered_args);
    defer testing.allocator.free(request.reference_files);

    try testing.expectEqual(@as(usize, 1), request.version_count);
    try testing.expect(request.warnings);
    try testing.expectEqual(@as(usize, 0), request.reference_files.len);
    try testing.expectEqual(@as(usize, 7), request.rendered_args.len);
    try testing.expectEqualStrings("--version", request.rendered_args[0]);
    try testing.expectEqualStrings("-w", request.rendered_args[1]);
    try testing.expectEqualStrings("left\"quote.c", request.rendered_args[2]);
    try testing.expectEqualStrings("path\\before", request.rendered_args[3]);
    try testing.expectEqualStrings("--", request.rendered_args[4]);
    try testing.expectEqualStrings("--reference", request.rendered_args[5]);
    try testing.expectEqualStrings("tail\nsymref", request.rendered_args[6]);

    var output: std.Io.Writer.Allocating = .init(testing.allocator);
    defer output.deinit();

    try genksyms.renderGenksymsBridge(&output.writer, request);
    try testing.expect(std.mem.containsAtLeast(
        u8,
        output.written(),
        1,
        "\"argv\":[\"scripts/genksyms/genksyms\",\"--version\",\"-w\",\"left\\\"quote.c\",\"path\\\\before\",\"--\",\"--reference\",\"tail\\nsymref\"]",
    ));
    try testing.expect(std.mem.containsAtLeast(
        u8,
        output.written(),
        1,
        "\"reference_files\":[]",
    ));
}
