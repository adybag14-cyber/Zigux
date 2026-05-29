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

test "genksyms required long arguments consume terminator tokens as data" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "--reference",
        "--",
        "--version",
        "input.c",
    };
    const request = try expectRequest(try genksyms.parseArgs(arena_state.allocator(), &args));

    try testing.expectEqual(@as(usize, 1), request.version_count);
    try testing.expectEqual(@as(usize, 1), request.reference_files.len);
    try testing.expectEqualStrings("--", request.reference_files[0]);
    try testing.expectEqual(@as(usize, 4), request.rendered_args.len);
    try testing.expectEqualStrings("--reference", request.rendered_args[0]);
    try testing.expectEqualStrings("--", request.rendered_args[1]);
    try testing.expectEqualStrings("--version", request.rendered_args[2]);
    try testing.expectEqualStrings("input.c", request.rendered_args[3]);
}

test "genksyms required short arguments consume terminator tokens as data" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "-T",
        "--",
        "-V",
        "input.c",
    };
    const request = try expectRequest(try genksyms.parseArgs(arena_state.allocator(), &args));

    try testing.expectEqual(@as(usize, 1), request.version_count);
    try testing.expectEqualStrings("--", request.dump_types_file.?);
    try testing.expectEqualSlices([]const u8, &args, request.rendered_args);
}

test "genksyms inline short terminator-looking values do not hide a later terminator" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "-r--",
        "--",
        "-V",
        "--help",
    };
    const request = try expectRequest(try genksyms.parseArgs(arena_state.allocator(), &args));

    try testing.expectEqual(@as(usize, 0), request.version_count);
    try testing.expectEqual(@as(usize, 1), request.reference_files.len);
    try testing.expectEqualStrings("--", request.reference_files[0]);
    try testing.expectEqualSlices([]const u8, &args, request.rendered_args);
}
