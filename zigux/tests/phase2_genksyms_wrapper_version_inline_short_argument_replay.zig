const std = @import("std");
const testing = std.testing;

const genksyms = @import("genksyms");

fn expectInlineShortRequest(
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
                try testing.expectEqualSlices([]const u8, args, request.rendered_args);
                try testing.expectEqual(expected_reference_files.len, request.reference_files.len);
                for (expected_reference_files, 0..) |expected, index| {
                    try testing.expectEqualStrings(expected, request.reference_files[index]);
                }
                if (expected_dump_types_file) |expected| {
                    try testing.expectEqualStrings(expected, request.dump_types_file.?);
                } else {
                    try testing.expectEqual(@as(?[]const u8, null), request.dump_types_file);
                }
            },
            else => return error.ExpectedRequestCommand,
        },
        else => return error.ExpectedRequestCommand,
    }
}

test "exact version survives before inline short reference argument" {
    const args = [_][]const u8{
        "--version",
        "-rModule.symvers",
    };
    const expected_references = [_][]const u8{"Module.symvers"};

    try expectInlineShortRequest(&args, 1, &expected_references, null);
}

test "abbreviated version survives before inline short dump-types argument" {
    const args = [_][]const u8{
        "--ver",
        "-Ttypes.out",
    };

    try expectInlineShortRequest(&args, 1, &.{}, "types.out");
}

test "mixed versions survive before inline short request arguments" {
    const args = [_][]const u8{
        "-V",
        "--version",
        "-rfirst.symref",
        "-rsecond.symref",
        "-Ttypes.symtypes",
    };
    const expected_references = [_][]const u8{
        "first.symref",
        "second.symref",
    };

    try expectInlineShortRequest(&args, 2, &expected_references, "types.symtypes");
}
