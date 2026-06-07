const std = @import("std");
const genksyms = @import("genksyms.zig");

const testing = std.testing;

fn expectRequest(allocator: std.mem.Allocator, args: []const []const u8) !genksyms.Request {
    const outcome = try genksyms.parseArgs(allocator, args);
    return switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| request,
            else => error.ExpectedRequestCommand,
        },
        else => error.ExpectedRequestCommand,
    };
}

test "required long values survive later version side effects after positionals" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "seed.c",
        "--reference",
        "keep.symref",
        "--dump-types",
        "first.types",
        "--version",
        "-VV",
        "--dump-types=final.types",
        "-r",
        "tail.symref",
        "-d",
    };
    const request = try expectRequest(arena_state.allocator(), &args);

    try testing.expectEqualSlices([]const u8, &args, request.raw_args);
    try testing.expectEqual(@as(usize, 3), request.version_count);
    try testing.expectEqual(@as(usize, 1), request.debug_level);
    try testing.expectEqual(@as(usize, 2), request.reference_files.len);
    try testing.expectEqualStrings("keep.symref", request.reference_files[0]);
    try testing.expectEqualStrings("tail.symref", request.reference_files[1]);
    try testing.expectEqualStrings("final.types", request.dump_types_file.?);

    const rendered = [_][]const u8{
        "--reference",
        "keep.symref",
        "--dump-types",
        "first.types",
        "--version",
        "-VV",
        "--dump-types=final.types",
        "-r",
        "tail.symref",
        "-d",
        "seed.c",
    };
    try testing.expectEqualSlices([]const u8, &rendered, request.rendered_args);

    var output: std.Io.Writer.Allocating = .init(testing.allocator);
    defer output.deinit();

    try genksyms.renderGenksymsBridge(&output.writer, request);
    try testing.expectEqualStrings(
        "{\"tool\":\"scripts/genksyms/genksyms\",\"stdin\":\"cpp-stream\",\"stdout\":\"symversions\",\"argv\":[\"scripts/genksyms/genksyms\",\"--reference\",\"keep.symref\",\"--dump-types\",\"first.types\",\"--version\",\"-VV\",\"--dump-types=final.types\",\"-r\",\"tail.symref\",\"-d\",\"seed.c\"],\"options\":{\"debug_level\":1,\"warnings\":false,\"dump_defs\":false,\"preserve\":false,\"reference_files\":[\"keep.symref\",\"tail.symref\"],\"dump_types_file\":\"final.types\"}}\n",
        output.written(),
    );
}

test "short required values before version flags keep request command shape" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "unit.c",
        "-rpre.symref",
        "-Tfirst.types",
        "-V",
        "--ver",
        "-T",
        "second.types",
    };
    const request = try expectRequest(arena_state.allocator(), &args);

    try testing.expectEqual(@as(usize, 2), request.version_count);
    try testing.expectEqual(@as(usize, 1), request.reference_files.len);
    try testing.expectEqualStrings("pre.symref", request.reference_files[0]);
    try testing.expectEqualStrings("second.types", request.dump_types_file.?);

    const rendered = [_][]const u8{
        "-rpre.symref",
        "-Tfirst.types",
        "-V",
        "--ver",
        "-T",
        "second.types",
        "unit.c",
    };
    try testing.expectEqualSlices([]const u8, &rendered, request.rendered_args);
}

test "failure after required data and version preserves version count" {
    const args = [_][]const u8{
        "unit.c",
        "--reference",
        "keep.symref",
        "--version",
        "--bad",
    };
    const outcome = try genksyms.parseArgs(testing.allocator, &args);

    switch (outcome) {
        .failure => |failure| {
            try testing.expectEqual(@as(usize, 1), failure.version_count);
            switch (failure.reason) {
                .invalid_option => |option| try testing.expectEqualStrings("--bad", option),
                else => return error.UnexpectedParseFailure,
            }
        },
        else => return error.ExpectedFailure,
    }
}
