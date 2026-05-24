const std = @import("std");
const genksyms = @import("genksyms");

const testing = std.testing;

const ProcessFixture = struct {
    stdout: []const u8,
    stderr: []const u8,
    exit_code: i64,
};

const abbreviated_version_expected_json =
    @embedFile("fixtures/genksyms_bridge/abbreviated_version_expected.json");
const unexpected_long_help_argument_expected_json =
    @embedFile("fixtures/genksyms_bridge/unexpected_long_help_argument_expected.json");

fn expectUnexpectedHelpFailure(args: []const []const u8, expected_version_count: usize) !void {
    const outcome = try genksyms.parseArgs(testing.allocator, args);
    switch (outcome) {
        .failure => |failure| {
            try testing.expectEqual(expected_version_count, failure.version_count);
            switch (failure.reason) {
                .unexpected_option_argument => |option| try testing.expectEqualStrings("--help", option),
                else => return error.UnexpectedParseFailure,
            }
        },
        else => return error.ExpectedFailure,
    }
}

test "phase2 genksyms wrapper version-prefixed unexpected help packet stays aligned with fixtures" {
    const version_fixture = try std.json.parseFromSlice(
        ProcessFixture,
        testing.allocator,
        abbreviated_version_expected_json,
        .{},
    );
    defer version_fixture.deinit();

    const unexpected_help_fixture = try std.json.parseFromSlice(
        ProcessFixture,
        testing.allocator,
        unexpected_long_help_argument_expected_json,
        .{},
    );
    defer unexpected_help_fixture.deinit();

    try testing.expectEqualStrings("", version_fixture.value.stdout);
    try testing.expectEqualStrings("genksyms version 2.5.60\n", version_fixture.value.stderr);
    try testing.expectEqual(@as(i64, 0), version_fixture.value.exit_code);

    try testing.expectEqualStrings("", unexpected_help_fixture.value.stdout);
    try testing.expectEqual(@as(i64, 1), unexpected_help_fixture.value.exit_code);
    try testing.expect(std.mem.startsWith(u8, unexpected_help_fixture.value.stderr, "option '--help' doesn't allow an argument\n"));

    const combined_stderr = try std.mem.concat(
        testing.allocator,
        u8,
        &.{ version_fixture.value.stderr, unexpected_help_fixture.value.stderr },
    );
    defer testing.allocator.free(combined_stderr);

    try testing.expectEqualStrings(
        "genksyms version 2.5.60\n" ++
            "option '--help' doesn't allow an argument\n" ++
            "Usage:\n" ++
            "genksyms [-dDpwqhV] [-r file] [-T file] > /path/to/.tmp_obj.ver\n" ++
            "\n" ++
            " -d, --debug Increment the debug level (repeatable)\n" ++
            " -D, --dump Dump expanded symbol defs (for debugging only)\n" ++
            " -r, --reference file Read reference symbols from a file\n" ++
            " -T, --dump-types file Dump expanded types into file\n" ++
            " -p, --preserve Preserve reference modversions or fail\n" ++
            " -w, --warnings Enable warnings\n" ++
            " -q, --quiet Disable warnings (default)\n" ++
            " -h, --help Print this message\n" ++
            " -V, --version Print the release version\n",
        combined_stderr,
    );
}

test "phase2 genksyms wrapper version-prefixed unexpected help failures preserve version count" {
    try expectUnexpectedHelpFailure(&.{ "--version", "--help=extra" }, 1);
    try expectUnexpectedHelpFailure(&.{ "--ver", "--help=extra" }, 1);
    try expectUnexpectedHelpFailure(&.{ "--version", "--he=extra" }, 1);
    try expectUnexpectedHelpFailure(&.{ "--ver", "--he=extra" }, 1);
}
