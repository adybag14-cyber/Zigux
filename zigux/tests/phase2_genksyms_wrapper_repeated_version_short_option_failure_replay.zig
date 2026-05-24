const std = @import("std");
const genksyms = @import("genksyms");

const testing = std.testing;

fn expectInvalidShortOptionFailure(
    version_prefixes: []const []const u8,
    failing_option: []const u8,
    expected_version_count: usize,
    expected_invalid_flag: []const u8,
) !void {
    var args = std.ArrayList([]const u8).empty;
    defer args.deinit(testing.allocator);

    try args.appendSlice(testing.allocator, version_prefixes);
    try args.append(testing.allocator, failing_option);

    const outcome = try genksyms.parseArgs(testing.allocator, args.items);
    switch (outcome) {
        .failure => |failure| {
            try testing.expectEqual(expected_version_count, failure.version_count);
            switch (failure.reason) {
                .invalid_option => |option| try testing.expectEqualStrings(expected_invalid_flag, option),
                else => return error.ExpectedInvalidShortOptionFailure,
            }
        },
        else => return error.ExpectedFailure,
    }
}

fn expectMissingShortOptionArgumentFailure(
    version_prefixes: []const []const u8,
    failing_option: []const u8,
    expected_version_count: usize,
    expected_missing_flag: []const u8,
) !void {
    var args = std.ArrayList([]const u8).empty;
    defer args.deinit(testing.allocator);

    try args.appendSlice(testing.allocator, version_prefixes);
    try args.append(testing.allocator, failing_option);

    const outcome = try genksyms.parseArgs(testing.allocator, args.items);
    switch (outcome) {
        .failure => |failure| {
            try testing.expectEqual(expected_version_count, failure.version_count);
            switch (failure.reason) {
                .missing_option_argument => |option| try testing.expectEqualStrings(expected_missing_flag, option),
                else => return error.ExpectedMissingShortOptionArgumentFailure,
            }
        },
        else => return error.ExpectedFailure,
    }
}

test "phase2 genksyms wrapper preserves repeated version counts before invalid short option failures" {
    try expectInvalidShortOptionFailure(&.{ "--version", "--ver", "--version" }, "-x", 3, "x");
    try expectInvalidShortOptionFailure(
        &.{ "-V", "--version", "--ver", "--version" },
        "-z",
        4,
        "z",
    );
}

test "phase2 genksyms wrapper preserves repeated version counts before missing short option arguments" {
    try expectMissingShortOptionArgumentFailure(&.{ "--version", "--ver", "--version" }, "-T", 3, "T");
    try expectMissingShortOptionArgumentFailure(
        &.{ "-V", "--version", "--ver", "--version" },
        "-r",
        4,
        "r",
    );
}
