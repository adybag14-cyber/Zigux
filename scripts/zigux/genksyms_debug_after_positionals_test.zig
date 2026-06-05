const std = @import("std");
const testing = std.testing;
const genksyms = @import("genksyms.zig");

fn expectRequest(outcome: genksyms.ParseOutcome) !genksyms.Request {
    return switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| request,
            else => error.ExpectedRequestCommand,
        },
        else => error.ExpectedRequestCommand,
    };
}

test "long debug after delayed positionals preserves normalized order" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "left.c",
        "--debug",
        "middle.h",
        "--deb",
        "-V",
        "right.S",
    };
    const outcome = try genksyms.parseArgs(arena_state.allocator(), &args);
    const request = try expectRequest(outcome);

    try testing.expectEqual(@as(usize, 2), request.debug_level);
    try testing.expectEqual(@as(usize, 1), request.version_count);
    try testing.expectEqual(@as(usize, 6), request.rendered_args.len);
    try testing.expectEqualStrings("--debug", request.rendered_args[0]);
    try testing.expectEqualStrings("--deb", request.rendered_args[1]);
    try testing.expectEqualStrings("-V", request.rendered_args[2]);
    try testing.expectEqualStrings("left.c", request.rendered_args[3]);
    try testing.expectEqualStrings("middle.h", request.rendered_args[4]);
    try testing.expectEqualStrings("right.S", request.rendered_args[5]);
    try testing.expectEqualSlices([]const u8, &args, request.raw_args);
}

test "clustered short debug after delayed positionals accumulates with version flags" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "before.c",
        "-dVdd",
        "after.c",
        "-Vd",
    };
    const outcome = try genksyms.parseArgs(arena_state.allocator(), &args);
    const request = try expectRequest(outcome);

    try testing.expectEqual(@as(usize, 4), request.debug_level);
    try testing.expectEqual(@as(usize, 2), request.version_count);
    try testing.expectEqual(@as(usize, 4), request.rendered_args.len);
    try testing.expectEqualStrings("-dVdd", request.rendered_args[0]);
    try testing.expectEqualStrings("-Vd", request.rendered_args[1]);
    try testing.expectEqualStrings("before.c", request.rendered_args[2]);
    try testing.expectEqualStrings("after.c", request.rendered_args[3]);
}

test "debug after positionals renders bridge json with delayed tails" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "first.o",
        "--debug",
        "-dd",
        "last.o",
    };
    const outcome = try genksyms.parseArgs(arena_state.allocator(), &args);
    const request = try expectRequest(outcome);

    try testing.expectEqual(@as(usize, 3), request.debug_level);
    var output: std.Io.Writer.Allocating = .init(testing.allocator);
    defer output.deinit();

    try genksyms.renderGenksymsBridge(&output.writer, request);
    try testing.expectEqualStrings(
        "{\"tool\":\"scripts/genksyms/genksyms\",\"stdin\":\"cpp-stream\",\"stdout\":\"symversions\",\"argv\":[\"scripts/genksyms/genksyms\",\"--debug\",\"-dd\",\"first.o\",\"last.o\"],\"options\":{\"debug_level\":3,\"warnings\":false,\"dump_defs\":false,\"preserve\":false,\"reference_files\":[],\"dump_types_file\":null}}\n",
        output.written(),
    );
}
