const std = @import("std");
const testing = std.testing;
const genksyms = @import("genksyms.zig");

fn expectReferenceRequest(args: []const []const u8) !void {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const outcome = try genksyms.parseArgs(arena_state.allocator(), args);
    switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| {
                try testing.expectEqual(@as(usize, 1), request.version_count);
                try testing.expectEqual(@as(usize, 1), request.reference_files.len);
                try testing.expectEqualStrings("", request.reference_files[0]);
                try testing.expect(request.dump_types_file == null);
                try testing.expectEqualSlices([]const u8, args, request.rendered_args);
            },
            else => return error.ExpectedRequestCommand,
        },
        else => return error.ExpectedRequestCommand,
    }
}

fn expectDumpTypesRequest(args: []const []const u8) !void {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const outcome = try genksyms.parseArgs(arena_state.allocator(), args);
    switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| {
                try testing.expectEqual(@as(usize, 1), request.version_count);
                try testing.expectEqual(@as(usize, 0), request.reference_files.len);
                try testing.expect(request.dump_types_file != null);
                try testing.expectEqualStrings("", request.dump_types_file.?);
                try testing.expectEqualSlices([]const u8, args, request.rendered_args);
            },
            else => return error.ExpectedRequestCommand,
        },
        else => return error.ExpectedRequestCommand,
    }
}

test "genksyms bridge keeps abbreviated version side effect before empty inline reference request" {
    const args = [_][]const u8{
        "--ver",
        "--reference=",
    };
    try expectReferenceRequest(&args);
}

test "genksyms bridge keeps canonical version side effect before empty inline reference request" {
    const args = [_][]const u8{
        "--version",
        "--reference=",
    };
    try expectReferenceRequest(&args);
}

test "genksyms bridge keeps abbreviated version side effect before empty inline dump-types request" {
    const args = [_][]const u8{
        "--ver",
        "--dump-t=",
    };
    try expectDumpTypesRequest(&args);
}

test "genksyms bridge keeps canonical version side effect before empty inline dump-types request" {
    const args = [_][]const u8{
        "--version",
        "--dump-types=",
    };
    try expectDumpTypesRequest(&args);
}
