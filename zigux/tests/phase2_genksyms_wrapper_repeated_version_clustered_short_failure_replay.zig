const std = @import("std");
const genksyms = @import("genksyms");

const testing = std.testing;

fn expectRepeatedVersionClusteredInvalidShortFailure(
    version_prefixes: []const []const u8,
    clustered_option: []const u8,
    expected_version_count: usize,
    expected_invalid_flag: []const u8,
) !void {
    var args = std.ArrayList([]const u8).empty;
    defer args.deinit(testing.allocator);

    try args.appendSlice(testing.allocator, version_prefixes);
    try args.append(testing.allocator, clustered_option);

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

fn expectRepeatedVersionClusteredMissingShortArgumentFailure(
    version_prefixes: []const []const u8,
    clustered_option: []const u8,
    expected_version_count: usize,
    expected_missing_flag: []const u8,
) !void {
    var args = std.ArrayList([]const u8).empty;
    defer args.deinit(testing.allocator);

    try args.appendSlice(testing.allocator, version_prefixes);
    try args.append(testing.allocator, clustered_option);

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

test "phase2 genksyms wrapper preserves repeated version counts before clustered invalid short option failures" {
    try expectRepeatedVersionClusteredInvalidShortFailure(
        &.{ "--version", "--ver", "--version" },
        "-Vx",
        4,
        "x",
    );
    try expectRepeatedVersionClusteredInvalidShortFailure(
        &.{ "-V", "--version", "--ver", "--version" },
        "-VVz",
        6,
        "z",
    );
}

test "phase2 genksyms wrapper preserves repeated version counts before clustered missing short option arguments" {
    try expectRepeatedVersionClusteredMissingShortArgumentFailure(
        &.{ "--version", "--ver", "--version" },
        "-VT",
        4,
        "T",
    );
    try expectRepeatedVersionClusteredMissingShortArgumentFailure(
        &.{ "-V", "--version", "--ver", "--version" },
        "-VVT",
        6,
        "T",
    );
}
