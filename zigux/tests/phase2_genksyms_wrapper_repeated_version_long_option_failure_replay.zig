const std = @import("std");
const genksyms = @import("genksyms");

const testing = std.testing;

fn expectInvalidLongOptionFailure(
    version_prefixes: []const []const u8,
    failing_option: []const u8,
    expected_version_count: usize,
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
                .invalid_option => |option| try testing.expectEqualStrings(failing_option, option),
                else => return error.ExpectedInvalidLongOptionFailure,
            }
        },
        else => return error.ExpectedFailure,
    }
}

fn expectAmbiguousLongOptionFailure(
    version_prefixes: []const []const u8,
    failing_option: []const u8,
    expected_version_count: usize,
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
                .ambiguous_option => |option| try testing.expectEqualStrings(failing_option, option),
                else => return error.ExpectedAmbiguousLongOptionFailure,
            }
        },
        else => return error.ExpectedFailure,
    }
}

test "phase2 genksyms wrapper preserves repeated version counts before invalid long option failures" {
    try expectInvalidLongOptionFailure(&.{ "--version", "--ver", "--version" }, "--unknown", 3);
    try expectInvalidLongOptionFailure(
        &.{ "-V", "--version", "--ver", "--version" },
        "--not-a-real-option=extra",
        4,
    );
}

test "phase2 genksyms wrapper preserves repeated version counts before ambiguous long option failures" {
    try expectAmbiguousLongOptionFailure(&.{ "--version", "--ver", "--version" }, "--du", 3);
    try expectAmbiguousLongOptionFailure(
        &.{ "-V", "--version", "--ver", "--version" },
        "--du",
        4,
    );
}
