const std = @import("std");
const genksyms = @import("genksyms");

const testing = std.testing;

fn expectAmbiguousLongOptionFailure(
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
                .ambiguous_option => |option| try testing.expectEqualStrings(expected_option, option),
                else => return error.ExpectedAmbiguousLongOptionFailure,
            }
        },
        else => return error.ExpectedFailure,
    }
}

test "phase2 genksyms wrapper preserves repeated abbreviated version counts before ambiguous long option failures" {
    try expectAmbiguousLongOptionFailure(&.{ "--ver", "--ver" }, "--d", 2, "--d");
    try expectAmbiguousLongOptionFailure(&.{ "--ver", "-V", "--ver" }, "--d", 3, "--d");
}
