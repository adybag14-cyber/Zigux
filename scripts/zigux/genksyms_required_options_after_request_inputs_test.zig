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
        .failure => error.ExpectedRequestCommand,
    };
}

fn expectBridge(request: genksyms.Request, expected: []const u8) !void {
    var output: std.Io.Writer.Allocating = .init(testing.allocator);
    defer output.deinit();

    try genksyms.renderGenksymsBridge(&output.writer, request);
    try testing.expectEqualStrings(expected, output.written());
}

test "positional request input keeps later long required options as request data" {
    const args = [_][]const u8{
        "input.c",
        "--reference",
        "after.symref",
        "--dump-types=after.types",
        "--debug",
    };
    const expected_rendered = [_][]const u8{
        "--reference",
        "after.symref",
        "--dump-types=after.types",
        "--debug",
        "input.c",
    };

    const request = try expectRequest(&args);
    defer testing.allocator.free(request.rendered_args);
    defer testing.allocator.free(request.reference_files);

    try testing.expectEqualSlices([]const u8, &args, request.raw_args);
    try testing.expectEqualSlices([]const u8, &expected_rendered, request.rendered_args);
    try testing.expectEqual(@as(usize, 1), request.debug_level);
    try testing.expectEqual(@as(usize, 1), request.reference_files.len);
    try testing.expectEqualStrings("after.symref", request.reference_files[0]);
    try testing.expectEqualStrings("after.types", request.dump_types_file.?);

    try expectBridge(
        request,
        "{\"tool\":\"scripts/genksyms/genksyms\",\"stdin\":\"cpp-stream\",\"stdout\":\"symversions\",\"argv\":[\"scripts/genksyms/genksyms\",\"--reference\",\"after.symref\",\"--dump-types=after.types\",\"--debug\",\"input.c\"],\"options\":{\"debug_level\":1,\"warnings\":false,\"dump_defs\":false,\"preserve\":false,\"reference_files\":[\"after.symref\"],\"dump_types_file\":\"after.types\"}}\n",
    );
}

test "lone dash request input keeps later short required options as request data" {
    const args = [_][]const u8{
        "-",
        "-rpost.symref",
        "-T",
        "post.types",
        "-p",
    };
    const expected_rendered = [_][]const u8{
        "-rpost.symref",
        "-T",
        "post.types",
        "-p",
        "-",
    };

    const request = try expectRequest(&args);
    defer testing.allocator.free(request.rendered_args);
    defer testing.allocator.free(request.reference_files);

    try testing.expectEqualSlices([]const u8, &args, request.raw_args);
    try testing.expectEqualSlices([]const u8, &expected_rendered, request.rendered_args);
    try testing.expect(request.preserve);
    try testing.expectEqual(@as(usize, 1), request.reference_files.len);
    try testing.expectEqualStrings("post.symref", request.reference_files[0]);
    try testing.expectEqualStrings("post.types", request.dump_types_file.?);

    try expectBridge(
        request,
        "{\"tool\":\"scripts/genksyms/genksyms\",\"stdin\":\"cpp-stream\",\"stdout\":\"symversions\",\"argv\":[\"scripts/genksyms/genksyms\",\"-rpost.symref\",\"-T\",\"post.types\",\"-p\",\"-\"],\"options\":{\"debug_level\":0,\"warnings\":false,\"dump_defs\":false,\"preserve\":true,\"reference_files\":[\"post.symref\"],\"dump_types_file\":\"post.types\"}}\n",
    );
}

test "required option values after request input can look like commands" {
    const args = [_][]const u8{
        "seed.sym",
        "--reference",
        "--version",
        "--dump-types",
        "--help",
        "--warnings",
    };
    const expected_rendered = [_][]const u8{
        "--reference",
        "--version",
        "--dump-types",
        "--help",
        "--warnings",
        "seed.sym",
    };

    const request = try expectRequest(&args);
    defer testing.allocator.free(request.rendered_args);
    defer testing.allocator.free(request.reference_files);

    try testing.expectEqualSlices([]const u8, &args, request.raw_args);
    try testing.expectEqualSlices([]const u8, &expected_rendered, request.rendered_args);
    try testing.expectEqual(@as(usize, 0), request.version_count);
    try testing.expect(request.warnings);
    try testing.expectEqual(@as(usize, 1), request.reference_files.len);
    try testing.expectEqualStrings("--version", request.reference_files[0]);
    try testing.expectEqualStrings("--help", request.dump_types_file.?);

    try expectBridge(
        request,
        "{\"tool\":\"scripts/genksyms/genksyms\",\"stdin\":\"cpp-stream\",\"stdout\":\"symversions\",\"argv\":[\"scripts/genksyms/genksyms\",\"--reference\",\"--version\",\"--dump-types\",\"--help\",\"--warnings\",\"seed.sym\"],\"options\":{\"debug_level\":0,\"warnings\":true,\"dump_defs\":false,\"preserve\":false,\"reference_files\":[\"--version\"],\"dump_types_file\":\"--help\"}}\n",
    );
}
