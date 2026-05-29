const std = @import("std");
const testing = std.testing;
const genksyms = @import("genksyms");

fn expectRequest(
    args: []const []const u8,
    expected_version_count: usize,
    expected_references: []const []const u8,
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
                try testing.expectEqual(expected_references.len, request.reference_files.len);
                for (expected_references, request.reference_files) |expected, actual| {
                    try testing.expectEqualStrings(expected, actual);
                }
                if (expected_dump_types_file) |expected| {
                    try testing.expect(request.dump_types_file != null);
                    try testing.expectEqualStrings(expected, request.dump_types_file.?);
                } else {
                    try testing.expect(request.dump_types_file == null);
                }
            },
            else => return error.ExpectedGenksymsRequest,
        },
        else => return error.ExpectedGenksymsRequest,
    }
}

test "version side effects survive before separate short reference arguments" {
    const exact_args = [_][]const u8{
        "--version",
        "-r",
        "Module.symvers",
    };
    try expectRequest(&exact_args, 1, &.{"Module.symvers"}, null);

    const abbreviated_args = [_][]const u8{
        "--ver",
        "-r",
        "extra.symvers",
    };
    try expectRequest(&abbreviated_args, 1, &.{"extra.symvers"}, null);

    const short_cluster_args = [_][]const u8{
        "-VV",
        "-r",
        "cluster.symvers",
    };
    try expectRequest(&short_cluster_args, 2, &.{"cluster.symvers"}, null);
}

test "version side effects survive before separate short dump-types arguments" {
    const exact_args = [_][]const u8{
        "-V",
        "-T",
        "types.symtypes",
    };
    try expectRequest(&exact_args, 1, &.{}, "types.symtypes");

    const mixed_args = [_][]const u8{
        "--version",
        "--ver",
        "-T",
        "mixed.symtypes",
    };
    try expectRequest(&mixed_args, 2, &.{}, "mixed.symtypes");
}
