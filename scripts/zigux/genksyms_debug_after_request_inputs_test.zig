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

test "long debug flags after positional request input keep request mode" {
    const args = [_][]const u8{
        "symbols.i",
        "--debug",
        "--debug",
        "--reference",
        "base.symref",
    };
    const request = try expectRequest(&args);
    defer testing.allocator.free(request.rendered_args);
    defer testing.allocator.free(request.reference_files);

    try testing.expectEqual(@as(usize, 2), request.debug_level);
    try testing.expectEqual(@as(usize, 1), request.reference_files.len);
    try testing.expectEqualStrings("base.symref", request.reference_files[0]);

    const expected_rendered = [_][]const u8{
        "--debug",
        "--debug",
        "--reference",
        "base.symref",
        "symbols.i",
    };
    try testing.expectEqualSlices([]const u8, &expected_rendered, request.rendered_args);

    var output: std.Io.Writer.Allocating = .init(testing.allocator);
    defer output.deinit();

    try genksyms.renderGenksymsBridge(&output.writer, request);
    try testing.expectEqualStrings(
        "{\"tool\":\"scripts/genksyms/genksyms\",\"stdin\":\"cpp-stream\",\"stdout\":\"symversions\",\"argv\":[\"scripts/genksyms/genksyms\",\"--debug\",\"--debug\",\"--reference\",\"base.symref\",\"symbols.i\"],\"options\":{\"debug_level\":2,\"warnings\":false,\"dump_defs\":false,\"preserve\":false,\"reference_files\":[\"base.symref\"],\"dump_types_file\":null}}\n",
        output.written(),
    );
}

test "short debug cluster after lone dash updates request state" {
    const args = [_][]const u8{
        "-",
        "-ddd",
        "--dump",
    };
    const request = try expectRequest(&args);
    defer testing.allocator.free(request.rendered_args);
    defer testing.allocator.free(request.reference_files);

    try testing.expectEqual(@as(usize, 3), request.debug_level);
    try testing.expect(request.dump_defs);
    try testing.expectEqual(@as(usize, 0), request.reference_files.len);

    const expected_rendered = [_][]const u8{
        "-ddd",
        "--dump",
        "-",
    };
    try testing.expectEqualSlices([]const u8, &expected_rendered, request.rendered_args);
}

test "required option data that looks like debug stays data before later debug" {
    const args = [_][]const u8{
        "--reference",
        "--debug",
        "--dump-types",
        "-d",
        "payload.i",
        "-dd",
    };
    const request = try expectRequest(&args);
    defer testing.allocator.free(request.rendered_args);
    defer testing.allocator.free(request.reference_files);

    try testing.expectEqual(@as(usize, 2), request.debug_level);
    try testing.expectEqual(@as(usize, 1), request.reference_files.len);
    try testing.expectEqualStrings("--debug", request.reference_files[0]);
    try testing.expectEqualStrings("-d", request.dump_types_file.?);

    const expected_rendered = [_][]const u8{
        "--reference",
        "--debug",
        "--dump-types",
        "-d",
        "-dd",
        "payload.i",
    };
    try testing.expectEqualSlices([]const u8, &expected_rendered, request.rendered_args);
}
