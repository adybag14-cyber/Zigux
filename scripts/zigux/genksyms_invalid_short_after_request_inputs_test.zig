const std = @import("std");
const testing = std.testing;
const genksyms = @import("genksyms.zig");

fn expectInvalidShortAfterRequest(args: []const []const u8, expected_option: []const u8, expected_versions: usize) !void {
    const outcome = try genksyms.parseArgs(testing.allocator, args);
    switch (outcome) {
        .failure => |failure| {
            try testing.expectEqual(expected_versions, failure.version_count);
            switch (failure.reason) {
                .invalid_option => |option| try testing.expectEqualStrings(expected_option, option),
                else => return error.UnexpectedParseFailure,
            }
        },
        else => return error.ExpectedInvalidShortFailure,
    }
}

test "genksyms bridge keeps positional request before invalid short option failure" {
    const args = [_][]const u8{
        "leftover.c",
        "--version",
        "-x",
    };
    try expectInvalidShortAfterRequest(&args, "x", 1);
}

test "genksyms bridge keeps lone dash request before invalid short option failure" {
    const args = [_][]const u8{
        "--version",
        "-",
        "-z",
    };
    try expectInvalidShortAfterRequest(&args, "z", 1);
}

test "genksyms bridge keeps required option data before invalid short option failure" {
    const args = [_][]const u8{
        "--version",
        "--reference",
        "-x",
        "-z",
    };
    try expectInvalidShortAfterRequest(&args, "z", 1);
}

test "genksyms bridge keeps clustered versions before invalid short option failure" {
    const args = [_][]const u8{
        "request.c",
        "-VVx",
    };
    try expectInvalidShortAfterRequest(&args, "x", 2);
}
