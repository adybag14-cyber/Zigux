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

test "genksyms empty positional argument keeps pure short version in request mode" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "-V",
        "",
    };
    const request = try expectRequest(try genksyms.parseArgs(arena_state.allocator(), &args));

    try testing.expectEqual(@as(usize, 1), request.version_count);
    try testing.expectEqual(@as(usize, 2), request.rendered_args.len);
    try testing.expectEqualStrings("-V", request.rendered_args[0]);
    try testing.expectEqualStrings("", request.rendered_args[1]);
}

test "genksyms empty positional argument is replayed before explicit terminator" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "",
        "--version",
        "--",
        "--help",
        "",
    };
    const request = try expectRequest(try genksyms.parseArgs(arena_state.allocator(), &args));

    try testing.expectEqual(@as(usize, 1), request.version_count);
    try testing.expectEqual(@as(usize, 5), request.rendered_args.len);
    try testing.expectEqualStrings("--version", request.rendered_args[0]);
    try testing.expectEqualStrings("", request.rendered_args[1]);
    try testing.expectEqualStrings("--", request.rendered_args[2]);
    try testing.expectEqualStrings("--help", request.rendered_args[3]);
    try testing.expectEqualStrings("", request.rendered_args[4]);
}

test "genksyms empty positional argument keeps later options parsed until terminator" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "",
        "-d",
        "--reference",
        "ref.symvers",
        "--",
        "-V",
    };
    const request = try expectRequest(try genksyms.parseArgs(arena_state.allocator(), &args));

    try testing.expectEqual(@as(usize, 0), request.version_count);
    try testing.expectEqual(@as(usize, 1), request.debug_level);
    try testing.expectEqual(@as(usize, 1), request.reference_files.len);
    try testing.expectEqualStrings("ref.symvers", request.reference_files[0]);
    try testing.expectEqualSlices([]const u8, &.{
        "-d",
        "--reference",
        "ref.symvers",
        "",
        "--",
        "-V",
    }, request.rendered_args);
}
