const std = @import("std");
const genksyms = @import("genksyms");

const testing = std.testing;

fn expectMissingLongOptionArgumentFailure(
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
                else => return error.ExpectedMissingLongOptionArgumentFailure,
            }
        },
        else => return error.ExpectedFailure,
    }
}

test "phase2 genksyms wrapper preserves repeated abbreviated version counts before abbreviated missing long option argument failures" {
    try expectMissingLongOptionArgumentFailure(&.{ "--ver", "--ver" }, "--ref", 2, "--reference");
    try expectMissingLongOptionArgumentFailure(&.{ "--ver", "-V" }, "--dump-t", 2, "--dump-types");
}
