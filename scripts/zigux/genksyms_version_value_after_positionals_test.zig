const std = @import("std");
const testing = std.testing;

const genksyms = @import("genksyms.zig");

fn expectUnexpectedVersionValue(args: []const []const u8, expected_version_count: usize) !void {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const outcome = try genksyms.parseArgs(arena_state.allocator(), args);
    switch (outcome) {
        .failure => |failure| {
            try testing.expectEqual(expected_version_count, failure.version_count);
            switch (failure.reason) {
                .unexpected_option_argument => |option| {
                    try testing.expectEqualStrings("--version", option);
                },
                else => return error.ExpectedUnexpectedVersionArgument,
            }
        },
        else => return error.ExpectedParseFailure,
    }
}

test "genksyms rejects exact long version value after delayed positionals" {
    const args = [_][]const u8{
        "input.c",
        "--version",
        "--version=ignored",
        "--debug",
        "later.c",
    };

    try expectUnexpectedVersionValue(&args, 1);
}

test "genksyms rejects abbreviated long version value after delayed positionals" {
    const args = [_][]const u8{
        "leading.c",
        "-VV",
        "--ver=payload",
        "--reference",
        "ref.sym",
    };

    try expectUnexpectedVersionValue(&args, 2);
}

test "genksyms rejects empty long version value after delayed positionals" {
    const args = [_][]const u8{
        "first.c",
        "--version",
        "--ver=",
        "--dump-types",
        "types.symtypes",
    };

    try expectUnexpectedVersionValue(&args, 1);
}
