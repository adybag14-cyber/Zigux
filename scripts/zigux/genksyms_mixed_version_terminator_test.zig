const std = @import("std");
const testing = std.testing;

const genksyms = @import("genksyms.zig");

fn expectMixedVersionTerminatorRequest(
    args: []const []const u8,
    expected_version_count: usize,
) !void {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const outcome = try genksyms.parseArgs(arena_state.allocator(), args);
    switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| {
                try testing.expectEqual(expected_version_count, request.version_count);
                try testing.expectEqual(@as(usize, 0), request.debug_level);
                try testing.expectEqual(@as(usize, 0), request.reference_files.len);
                try testing.expect(request.dump_types_file == null);
                try testing.expectEqualSlices([]const u8, args, request.rendered_args);
            },
            else => return error.ExpectedRequestCommand,
        },
        else => return error.ExpectedRequestCommand,
    }
}

test "mixed short and long versions before terminator preserve side effects" {
    const args = [_][]const u8{
        "-V",
        "--version",
        "--ver",
        "--",
        "--debug",
        "-r",
        "after.symref",
    };

    try expectMixedVersionTerminatorRequest(&args, 3);
}

test "mixed long and clustered short versions before terminator stay request mode" {
    const args = [_][]const u8{
        "--ver",
        "-VV",
        "--version",
        "--",
        "--dump-types",
        "types.symtypes",
    };

    try expectMixedVersionTerminatorRequest(&args, 4);
}
