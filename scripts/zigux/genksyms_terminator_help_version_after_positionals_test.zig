const std = @import("std");
const genksyms = @import("genksyms.zig");

const testing = std.testing;

fn expectRequest(outcome: genksyms.ParseOutcome) !genksyms.Request {
    return switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| request,
            else => error.ExpectedRequestCommand,
        },
        else => error.ExpectedRequestCommand,
    };
}

test "genksyms terminator keeps long help and version after delayed positionals as data" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "prelude.c",
        "-d",
        "middle.h",
        "--",
        "--help",
        "--version",
        "--ver",
    };
    const request = try expectRequest(try genksyms.parseArgs(arena_state.allocator(), &args));

    try testing.expectEqualSlices([]const u8, &args, request.raw_args);
    try testing.expectEqual(@as(usize, 1), request.debug_level);
    try testing.expectEqual(@as(usize, 0), request.version_count);
    try testing.expectEqual(@as(usize, 0), request.reference_files.len);
    try testing.expect(request.dump_types_file == null);
    try testing.expectEqual(@as(usize, 7), request.rendered_args.len);
    try testing.expectEqualStrings("-d", request.rendered_args[0]);
    try testing.expectEqualStrings("prelude.c", request.rendered_args[1]);
    try testing.expectEqualStrings("middle.h", request.rendered_args[2]);
    try testing.expectEqualStrings("--", request.rendered_args[3]);
    try testing.expectEqualStrings("--help", request.rendered_args[4]);
    try testing.expectEqualStrings("--version", request.rendered_args[5]);
    try testing.expectEqualStrings("--ver", request.rendered_args[6]);
}

test "genksyms terminator keeps short help and version clusters after positionals as data" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "--warnings",
        "input.c",
        "--",
        "-h",
        "-V",
        "-VVhD",
    };
    const request = try expectRequest(try genksyms.parseArgs(arena_state.allocator(), &args));

    try testing.expectEqualSlices([]const u8, &args, request.raw_args);
    try testing.expect(request.warnings);
    try testing.expectEqual(@as(usize, 0), request.version_count);
    try testing.expectEqual(@as(usize, 0), request.debug_level);
    try testing.expect(!request.dump_defs);
    try testing.expectEqual(@as(usize, 6), request.rendered_args.len);
    try testing.expectEqualStrings("--warnings", request.rendered_args[0]);
    try testing.expectEqualStrings("input.c", request.rendered_args[1]);
    try testing.expectEqualStrings("--", request.rendered_args[2]);
    try testing.expectEqualStrings("-h", request.rendered_args[3]);
    try testing.expectEqualStrings("-V", request.rendered_args[4]);
    try testing.expectEqualStrings("-VVhD", request.rendered_args[5]);
}

test "genksyms bridge renders post-terminator help and version without command promotion" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "-Vd",
        "left.c",
        "--",
        "--help",
        "-V",
    };
    const request = try expectRequest(try genksyms.parseArgs(arena_state.allocator(), &args));

    try testing.expectEqual(@as(usize, 1), request.version_count);
    try testing.expectEqual(@as(usize, 1), request.debug_level);

    var output: std.Io.Writer.Allocating = .init(testing.allocator);
    defer output.deinit();

    try genksyms.renderGenksymsBridge(&output.writer, request);
    try testing.expectEqualStrings(
        "{\"tool\":\"scripts/genksyms/genksyms\",\"stdin\":\"cpp-stream\",\"stdout\":\"symversions\",\"argv\":[\"scripts/genksyms/genksyms\",\"-Vd\",\"left.c\",\"--\",\"--help\",\"-V\"],\"options\":{\"debug_level\":1,\"warnings\":false,\"dump_defs\":false,\"preserve\":false,\"reference_files\":[],\"dump_types_file\":null}}\n",
        output.written(),
    );
}
