const std = @import("std");
const testing = std.testing;
const genksyms = @import("genksyms");

fn expectVersionLoneDashRequest(
    args: []const []const u8,
    expected_version_count: usize,
    expected_rendered: []const []const u8,
) !void {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const outcome = try genksyms.parseArgs(arena_state.allocator(), args);
    switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| {
                try testing.expectEqual(expected_version_count, request.version_count);
                try testing.expectEqualSlices([]const u8, expected_rendered, request.rendered_args);
                try testing.expectEqual(@as(usize, 0), request.reference_files.len);
                try testing.expect(request.dump_types_file == null);
            },
            else => return error.ExpectedRequestCommand,
        },
        .failure => return error.ExpectedRequestCommand,
    }
}

test "long version before lone dash becomes request with delayed positional dash" {
    const args = [_][]const u8{
        "--version",
        "-",
        "-d",
    };
    const expected_rendered = [_][]const u8{
        "--version",
        "-d",
        "-",
    };

    try expectVersionLoneDashRequest(&args, 1, &expected_rendered);
}

test "clustered short versions before lone dash keep later options parsed" {
    const args = [_][]const u8{
        "-VV",
        "-",
        "-w",
        "-q",
    };
    const expected_rendered = [_][]const u8{
        "-VV",
        "-w",
        "-q",
        "-",
    };

    try expectVersionLoneDashRequest(&args, 2, &expected_rendered);
}

test "abbreviated version before lone dash and terminator keeps tail positional" {
    const args = [_][]const u8{
        "--ver",
        "-",
        "--",
        "-d",
    };
    const expected_rendered = [_][]const u8{
        "--ver",
        "--",
        "-",
        "-d",
    };

    try expectVersionLoneDashRequest(&args, 1, &expected_rendered);
}
