const std = @import("std");
const genksyms = @import("genksyms");

const testing = std.testing;

const ProcessFixture = struct {
    stdout: []const u8,
    stderr: []const u8,
    exit_code: i64,
};

const help_expected_json =
    @embedFile("fixtures/genksyms_bridge/help_expected.json");
const missing_reference_argument_expected_json =
    @embedFile("fixtures/genksyms_bridge/missing_reference_argument_expected.json");

fn expectMissingShortOptionArgumentFailure(
    version_prefixes: []const []const u8,
    failing_option: []const u8,
    expected_option_text: []const u8,
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
                .missing_option_argument => |option| {
                    try testing.expectEqualStrings(expected_option_text, option);
                },
                else => return error.ExpectedMissingOptionArgumentFailure,
            }
        },
        else => return error.ExpectedFailure,
    }
}

test "phase2 genksyms wrapper missing-short fixtures stay aligned before version-prefixed failures" {
    const help_fixture = try std.json.parseFromSlice(
        ProcessFixture,
        testing.allocator,
        help_expected_json,
        .{},
    );
    defer help_fixture.deinit();

    const missing_reference_fixture = try std.json.parseFromSlice(
        ProcessFixture,
        testing.allocator,
        missing_reference_argument_expected_json,
        .{},
    );
    defer missing_reference_fixture.deinit();

    try testing.expectEqualStrings("", help_fixture.value.stdout);
    try testing.expectEqual(@as(i64, 0), help_fixture.value.exit_code);

    try testing.expectEqualStrings("", missing_reference_fixture.value.stdout);
    const expected_stderr = try std.mem.concat(
        testing.allocator,
        u8,
        &.{ "option requires an argument -- 'r'\n", help_fixture.value.stderr },
    );
    defer testing.allocator.free(expected_stderr);
    try testing.expectEqualStrings(
        expected_stderr,
        missing_reference_fixture.value.stderr,
    );
    try testing.expectEqual(@as(i64, 1), missing_reference_fixture.value.exit_code);
}

test "phase2 genksyms wrapper preserves mixed version counts before missing short reference arguments" {
    try expectMissingShortOptionArgumentFailure(&.{ "--version", "--ver" }, "-r", "r", 2);
    try expectMissingShortOptionArgumentFailure(&.{ "-V", "--version", "--ver" }, "-r", "r", 3);
}

test "phase2 genksyms wrapper preserves mixed version counts before missing short dump-types arguments" {
    try expectMissingShortOptionArgumentFailure(&.{ "--version", "--ver" }, "-T", "T", 2);
    try expectMissingShortOptionArgumentFailure(&.{ "-V", "--version", "--ver" }, "-T", "T", 3);
}
