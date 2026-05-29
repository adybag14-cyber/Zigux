const std = @import("std");
const testing = std.testing;

const genksyms = @import("genksyms");

fn expectRequest(outcome: genksyms.ParseOutcome) !genksyms.Request {
    return switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| request,
            else => error.ExpectedRequestCommand,
        },
        else => error.ExpectedRequestCommand,
    };
}

test "genksyms wrapper preserves version before positional terminator flush" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "--version",
        "input-before.c",
        "-d",
        "--",
        "--literal-after",
        "tail-after.h",
    };
    const request = try expectRequest(try genksyms.parseArgs(arena_state.allocator(), &args));

    try testing.expectEqual(@as(usize, 1), request.version_count);
    try testing.expectEqual(@as(usize, 1), request.debug_level);
    try testing.expectEqual(@as(usize, 6), request.rendered_args.len);
    try testing.expectEqualStrings("--version", request.rendered_args[0]);
    try testing.expectEqualStrings("-d", request.rendered_args[1]);
    try testing.expectEqualStrings("input-before.c", request.rendered_args[2]);
    try testing.expectEqualStrings("--", request.rendered_args[3]);
    try testing.expectEqualStrings("--literal-after", request.rendered_args[4]);
    try testing.expectEqualStrings("tail-after.h", request.rendered_args[5]);

    var output: std.Io.Writer.Allocating = .init(testing.allocator);
    defer output.deinit();

    try genksyms.renderGenksymsBridge(&output.writer, request);
    try testing.expectEqualStrings(
        "{\"tool\":\"scripts/genksyms/genksyms\",\"stdin\":\"cpp-stream\",\"stdout\":\"symversions\",\"argv\":[\"scripts/genksyms/genksyms\",\"--version\",\"-d\",\"input-before.c\",\"--\",\"--literal-after\",\"tail-after.h\"],\"options\":{\"debug_level\":1,\"warnings\":false,\"dump_defs\":false,\"preserve\":false,\"reference_files\":[],\"dump_types_file\":null}}\n",
        output.written(),
    );
}

test "genksyms wrapper keeps short versions before terminator tail literals" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "-VV",
        "prelude.h",
        "--ver",
        "--",
        "-not-an-option",
        "--dump-types=literal.types",
    };
    const request = try expectRequest(try genksyms.parseArgs(arena_state.allocator(), &args));

    try testing.expectEqual(@as(usize, 3), request.version_count);
    try testing.expectEqual(@as(usize, 6), request.rendered_args.len);
    try testing.expectEqualStrings("-VV", request.rendered_args[0]);
    try testing.expectEqualStrings("--ver", request.rendered_args[1]);
    try testing.expectEqualStrings("prelude.h", request.rendered_args[2]);
    try testing.expectEqualStrings("--", request.rendered_args[3]);
    try testing.expectEqualStrings("-not-an-option", request.rendered_args[4]);
    try testing.expectEqualStrings("--dump-types=literal.types", request.rendered_args[5]);

    var output: std.Io.Writer.Allocating = .init(testing.allocator);
    defer output.deinit();

    try genksyms.renderGenksymsBridge(&output.writer, request);
    try testing.expectEqualStrings(
        "{\"tool\":\"scripts/genksyms/genksyms\",\"stdin\":\"cpp-stream\",\"stdout\":\"symversions\",\"argv\":[\"scripts/genksyms/genksyms\",\"-VV\",\"--ver\",\"prelude.h\",\"--\",\"-not-an-option\",\"--dump-types=literal.types\"],\"options\":{\"debug_level\":0,\"warnings\":false,\"dump_defs\":false,\"preserve\":false,\"reference_files\":[],\"dump_types_file\":null}}\n",
        output.written(),
    );
}
