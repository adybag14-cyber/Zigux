const std = @import("std");
const genksyms = @import("genksyms");

const testing = std.testing;

fn expectInvalidLongOptionFailure(
    version_prefixes: []const []const u8,
    failing_option: []const u8,
    expected_version_count: usize,
    expected_option: []const u8,
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
                .invalid_option => |option| try testing.expectEqualStrings(expected_option, option),
                else => return error.ExpectedInvalidLongOptionFailure,
            }
        },
        else => return error.ExpectedFailure,
    }
}

test "phase2 genksyms wrapper preserves repeated abbreviated version counts before invalid long option failures" {
    try expectInvalidLongOptionFailure(&.{ "--ver", "--ver" }, "--unknown", 2, "--unknown");
    try expectInvalidLongOptionFailure(&.{ "--ver", "-V", "--ver" }, "--not-a-real-option=extra", 3, "--not-a-real-option=extra");
}
