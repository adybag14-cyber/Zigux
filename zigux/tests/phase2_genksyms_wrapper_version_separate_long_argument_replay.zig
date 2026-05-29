const std = @import("std");
const testing = std.testing;

const genksyms = @import("genksyms");

fn expectRequest(
    args: []const []const u8,
    expected_version_count: usize,
    expected_reference_files: []const []const u8,
    expected_dump_types_file: ?[]const u8,
) !void {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const outcome = try genksyms.parseArgs(arena_state.allocator(), args);
    switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| {
                try testing.expectEqual(expected_version_count, request.version_count);
                try testing.expectEqualSlices([]const u8, args, request.raw_args);
                try testing.expectEqualSlices([]const u8, args, request.rendered_args);
                try testing.expectEqual(expected_reference_files.len, request.reference_files.len);
                for (expected_reference_files, 0..) |expected, index| {
                    try testing.expectEqualStrings(expected, request.reference_files[index]);
                }
                if (expected_dump_types_file) |expected| {
                    try testing.expect(request.dump_types_file != null);
                    try testing.expectEqualStrings(expected, request.dump_types_file.?);
                } else {
                    try testing.expect(request.dump_types_file == null);
                }
            },
            else => return error.ExpectedRequestCommand,
        },
        else => return error.ExpectedRequestCommand,
    }
}

test "version survives before exact separate long request arguments" {
    const refs = [_][]const u8{"Module.symvers"};
    const reference_args = [_][]const u8{ "--version", "--reference", "Module.symvers" };
    try expectRequest(&reference_args, 1, &refs, null);

    const dump_args = [_][]const u8{ "--version", "--dump-types", "types.out" };
    try expectRequest(&dump_args, 1, &.{}, "types.out");
}

test "abbreviated version survives before abbreviated separate long request arguments" {
    const refs = [_][]const u8{"abi.symref"};
    const reference_args = [_][]const u8{ "--ver", "--ref", "abi.symref" };
    try expectRequest(&reference_args, 1, &refs, null);

    const dump_args = [_][]const u8{ "--ver", "--dump-t", "abi.types" };
    try expectRequest(&dump_args, 1, &.{}, "abi.types");
}

test "mixed version prefixes accumulate before separate long request arguments" {
    const refs = [_][]const u8{ "first.symref", "second.symref" };
    const args = [_][]const u8{
        "--version",
        "--ver",
        "--reference",
        "first.symref",
        "--ref",
        "second.symref",
        "--dump-types",
        "combined.types",
    };

    try expectRequest(&args, 2, &refs, "combined.types");
}
