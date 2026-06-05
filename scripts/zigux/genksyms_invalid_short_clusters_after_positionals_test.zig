const std = @import("std");
const testing = std.testing;
const genksyms = @import("genksyms.zig");

fn expectInvalidShortCluster(
    args: []const []const u8,
    expected_option: []const u8,
    expected_version_count: usize,
) !void {
    const outcome = try genksyms.parseArgs(testing.allocator, args);
    switch (outcome) {
        .failure => |failure| {
            try testing.expectEqual(expected_version_count, failure.version_count);
            switch (failure.reason) {
                .invalid_option => |option| try testing.expectEqualStrings(expected_option, option),
                else => return error.ExpectedInvalidOption,
            }
        },
        else => return error.ExpectedParseFailure,
    }
}

test "invalid short cluster after positionals preserves earlier version side effects" {
    const args = [_][]const u8{
        "delayed-input.c",
        "-Vdx",
        "ignored-tail.c",
    };

    try expectInvalidShortCluster(&args, "x", 1);
}

test "invalid short cluster after positionals reports the failing non-version byte" {
    const args = [_][]const u8{
        "delayed-input.c",
        "-qZ",
        "--reference",
        "not-consumed.symref",
    };

    try expectInvalidShortCluster(&args, "Z", 0);
}

test "invalid short cluster after positionals stops before later version bytes" {
    const args = [_][]const u8{
        "delayed-input.c",
        "-xV",
        "--dump-types",
        "not-consumed.symtypes",
    };

    try expectInvalidShortCluster(&args, "x", 0);
}
