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

test "long state before later versions remains request after positionals" {
    const args = [_][]const u8{
        "alpha.c",
        "--debug",
        "--warnings",
        "--dump",
        "--preserve",
        "--version",
        "--ver",
        "beta.c",
    };

    const request = try expectRequest(&args);
    defer testing.allocator.free(request.rendered_args);
    defer testing.allocator.free(request.reference_files);

    const expected_rendered = [_][]const u8{
        "--debug",
        "--warnings",
        "--dump",
        "--preserve",
        "--version",
        "--ver",
        "alpha.c",
        "beta.c",
    };

    try testing.expectEqualSlices([]const u8, &args, request.raw_args);
    try testing.expectEqualSlices([]const u8, &expected_rendered, request.rendered_args);
    try testing.expectEqual(@as(usize, 1), request.debug_level);
    try testing.expect(request.warnings);
    try testing.expect(request.dump_defs);
    try testing.expect(request.preserve);
    try testing.expectEqual(@as(usize, 2), request.version_count);
    try testing.expectEqual(@as(usize, 0), request.reference_files.len);
    try testing.expect(request.dump_types_file == null);
}

test "quiet state before version renders bridge request after positionals" {
    const args = [_][]const u8{
        "input.c",
        "--warnings",
        "--quiet",
        "--version",
        "--debug",
        "tail.h",
    };

    const request = try expectRequest(&args);
    defer testing.allocator.free(request.rendered_args);
    defer testing.allocator.free(request.reference_files);

    const expected_rendered = [_][]const u8{
        "--warnings",
        "--quiet",
        "--version",
        "--debug",
        "input.c",
        "tail.h",
    };

    try testing.expectEqualSlices([]const u8, &expected_rendered, request.rendered_args);
    try testing.expectEqual(@as(usize, 1), request.debug_level);
    try testing.expect(!request.warnings);
    try testing.expect(!request.dump_defs);
    try testing.expect(!request.preserve);
    try testing.expectEqual(@as(usize, 1), request.version_count);

    var output: std.Io.Writer.Allocating = .init(testing.allocator);
    defer output.deinit();

    try genksyms.renderGenksymsBridge(&output.writer, request);
    try testing.expectEqualStrings(
        "{\"tool\":\"scripts/genksyms/genksyms\",\"stdin\":\"cpp-stream\",\"stdout\":\"symversions\",\"argv\":[\"scripts/genksyms/genksyms\",\"--warnings\",\"--quiet\",\"--version\",\"--debug\",\"input.c\",\"tail.h\"],\"options\":{\"debug_level\":1,\"warnings\":false,\"dump_defs\":false,\"preserve\":false,\"reference_files\":[],\"dump_types_file\":null}}\n",
        output.written(),
    );
}

test "state before version preserves version count on later failure" {
    const args = [_][]const u8{
        "unit.c",
        "--dump",
        "--version",
        "--unknown",
    };

    const outcome = try genksyms.parseArgs(testing.allocator, &args);
    switch (outcome) {
        .failure => |failure| {
            try testing.expectEqual(@as(usize, 1), failure.version_count);
            switch (failure.reason) {
                .invalid_option => |option| try testing.expectEqualStrings("--unknown", option),
                else => return error.UnexpectedParseFailure,
            }
        },
        else => return error.ExpectedFailure,
    }
}
