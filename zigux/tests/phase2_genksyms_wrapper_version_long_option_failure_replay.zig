const std = @import("std");
const genksyms = @import("genksyms");

const testing = std.testing;

const ProcessFixture = struct {
    stdout: []const u8,
    stderr: []const u8,
    exit_code: i64,
};

const unsupported_long_option_expected_json =
    @embedFile("fixtures/genksyms_bridge/unsupported_long_option_expected.json");
const ambiguous_long_option_expected_json =
    @embedFile("fixtures/genksyms_bridge/ambiguous_long_option_expected.json");

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

test "phase2 genksyms wrapper long-option failure fixtures stay aligned before version-prefixed failures" {
    const unsupported_fixture = try std.json.parseFromSlice(
        ProcessFixture,
        testing.allocator,
        unsupported_long_option_expected_json,
        .{},
    );
    defer unsupported_fixture.deinit();

    try testing.expectEqualStrings("", unsupported_fixture.value.stdout);
    try testing.expectEqualStrings(
        "unrecognized option '--unknown'\n" ++
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
        unsupported_fixture.value.stderr,
    );
    try testing.expectEqual(@as(i64, 1), unsupported_fixture.value.exit_code);

    const ambiguous_fixture = try std.json.parseFromSlice(
        ProcessFixture,
        testing.allocator,
        ambiguous_long_option_expected_json,
        .{},
    );
    defer ambiguous_fixture.deinit();

    try testing.expectEqualStrings("", ambiguous_fixture.value.stdout);
    try testing.expectEqualStrings(
        "option '--du' is ambiguous; possibilities: '--dump' '--dump-types'\n" ++
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
        ambiguous_fixture.value.stderr,
    );
    try testing.expectEqual(@as(i64, 1), ambiguous_fixture.value.exit_code);
}

test "phase2 genksyms wrapper preserves mixed version counts before invalid long option failures" {
    try expectInvalidLongOptionFailure(&.{ "--version", "--ver" }, "--unknown", 2);
    try expectInvalidLongOptionFailure(&.{ "-V", "--version", "--ver" }, "--not-a-real-option=extra", 3);
}

test "phase2 genksyms wrapper preserves mixed version counts before ambiguous long option failures" {
    try expectAmbiguousLongOptionFailure(&.{ "--version", "--ver" }, "--du", 2);
    try expectAmbiguousLongOptionFailure(&.{ "-V", "--version", "--ver" }, "--du", 3);
}
