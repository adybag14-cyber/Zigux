const std = @import("std");
const testing = std.testing;
const genksyms = @import("genksyms.zig");

fn expectRequest(outcome: genksyms.ParseOutcome) !genksyms.Request {
    return switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| request,
            else => error.ExpectedRequestCommand,
        },
        .failure => error.ExpectedRequestCommand,
    };
}

fn expectBridgeJson(request: genksyms.Request, expected: []const u8) !void {
    var output: std.Io.Writer.Allocating = .init(testing.allocator);
    defer output.deinit();

    try genksyms.renderGenksymsBridge(&output.writer, request);
    try testing.expectEqualStrings(expected, output.written());
}

test "long required option consumes lone dash after delayed positionals" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "early.c",
        "--reference",
        "-",
        "--warnings",
        "--dump-types",
        "types.sym",
        "late.c",
    };
    const request = try expectRequest(try genksyms.parseArgs(arena_state.allocator(), &args));

    try testing.expectEqualSlices([]const u8, &args, request.raw_args);
    try testing.expectEqual(@as(usize, 1), request.reference_files.len);
    try testing.expectEqualStrings("-", request.reference_files[0]);
    try testing.expectEqualStrings("types.sym", request.dump_types_file.?);
    try testing.expect(request.warnings);
    try testing.expectEqual(@as(usize, 0), request.version_count);
    try testing.expectEqualSlices([]const u8, &.{
        "--reference",
        "-",
        "--warnings",
        "--dump-types",
        "types.sym",
        "early.c",
        "late.c",
    }, request.rendered_args);
    try expectBridgeJson(
        request,
        "{\"tool\":\"scripts/genksyms/genksyms\",\"stdin\":\"cpp-stream\",\"stdout\":\"symversions\",\"argv\":[\"scripts/genksyms/genksyms\",\"--reference\",\"-\",\"--warnings\",\"--dump-types\",\"types.sym\",\"early.c\",\"late.c\"],\"options\":{\"debug_level\":0,\"warnings\":true,\"dump_defs\":false,\"preserve\":false,\"reference_files\":[\"-\"],\"dump_types_file\":\"types.sym\"}}\n",
    );
}

test "short required option consumes lone dash after delayed positionals" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "first.c",
        "-V",
        "-T",
        "-",
        "-d",
        "second.c",
    };
    const request = try expectRequest(try genksyms.parseArgs(arena_state.allocator(), &args));

    try testing.expectEqualSlices([]const u8, &args, request.raw_args);
    try testing.expectEqual(@as(usize, 1), request.version_count);
    try testing.expectEqual(@as(usize, 1), request.debug_level);
    try testing.expectEqualStrings("-", request.dump_types_file.?);
    try testing.expectEqual(@as(usize, 0), request.reference_files.len);
    try testing.expectEqualSlices([]const u8, &.{
        "-V",
        "-T",
        "-",
        "-d",
        "first.c",
        "second.c",
    }, request.rendered_args);
    try expectBridgeJson(
        request,
        "{\"tool\":\"scripts/genksyms/genksyms\",\"stdin\":\"cpp-stream\",\"stdout\":\"symversions\",\"argv\":[\"scripts/genksyms/genksyms\",\"-V\",\"-T\",\"-\",\"-d\",\"first.c\",\"second.c\"],\"options\":{\"debug_level\":1,\"warnings\":false,\"dump_defs\":false,\"preserve\":false,\"reference_files\":[],\"dump_types_file\":\"-\"}}\n",
    );
}

test "standalone lone dash remains delayed positional after required value" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "before.c",
        "--reference=ref.sym",
        "-",
        "--quiet",
    };
    const request = try expectRequest(try genksyms.parseArgs(arena_state.allocator(), &args));

    try testing.expectEqual(@as(usize, 1), request.reference_files.len);
    try testing.expectEqualStrings("ref.sym", request.reference_files[0]);
    try testing.expectEqual(@as(usize, 0), request.version_count);
    try testing.expect(!request.warnings);
    try testing.expectEqualSlices([]const u8, &.{
        "--reference=ref.sym",
        "--quiet",
        "before.c",
        "-",
    }, request.rendered_args);
    try expectBridgeJson(
        request,
        "{\"tool\":\"scripts/genksyms/genksyms\",\"stdin\":\"cpp-stream\",\"stdout\":\"symversions\",\"argv\":[\"scripts/genksyms/genksyms\",\"--reference=ref.sym\",\"--quiet\",\"before.c\",\"-\"],\"options\":{\"debug_level\":0,\"warnings\":false,\"dump_defs\":false,\"preserve\":false,\"reference_files\":[\"ref.sym\"],\"dump_types_file\":null}}\n",
    );
}
