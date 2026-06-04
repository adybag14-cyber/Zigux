const std = @import("std");
const testing = std.testing;
const genksyms = @import("genksyms");

fn expectInvalidShortCluster(args: []const []const u8, expected_version_count: usize, expected_option: []const u8) !void {
    const outcome = try genksyms.parseArgs(testing.allocator, args);
    switch (outcome) {
        .failure => |failure| {
            try testing.expectEqual(expected_version_count, failure.version_count);
            switch (failure.reason) {
                .invalid_option => |option| try testing.expectEqualStrings(expected_option, option),
                else => return error.ExpectedInvalidOptionFailure,
            }
        },
        .command => return error.ExpectedFailure,
    }
}

test "version side effect is preserved before invalid short cluster failure" {
    const args = [_][]const u8{
        "-V",
        "-dx",
    };
    try expectInvalidShortCluster(&args, 1, "x");
}

test "clustered version side effects are preserved before invalid short cluster failure" {
    const args = [_][]const u8{
        "-VV",
        "-qZ",
    };
    try expectInvalidShortCluster(&args, 2, "Z");
}

test "invalid short cluster failure does not turn a pure version command into a request" {
    const args = [_][]const u8{
        "--version",
        "-Vx",
    };
    try expectInvalidShortCluster(&args, 2, "x");
}
