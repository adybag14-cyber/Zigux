const std = @import("std");
const genksyms = @import("genksyms");

const testing = std.testing;

const ProcessFixture = struct {
    stdout: []const u8,
    stderr: []const u8,
    exit_code: i64,
};

const missing_long_reference_argument_expected_json =
    @embedFile("fixtures/genksyms_bridge/missing_long_reference_argument_expected.json");
const missing_long_dump_types_argument_expected_json =
    @embedFile("fixtures/genksyms_bridge/missing_long_dump_types_argument_expected.json");

fn expectMissingLongOptionArgumentFailure(
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
                .missing_option_argument => |option| {
                    try testing.expectEqualStrings(failing_option, option);
                },
                else => return error.ExpectedMissingOptionArgumentFailure,
            }
        },
        else => return error.ExpectedFailure,
    }
}

test "phase2 genksyms wrapper missing-long-option fixtures stay aligned before version-prefixed failures" {
    const missing_reference_fixture = try std.json.parseFromSlice(
        ProcessFixture,
        testing.allocator,
        missing_long_reference_argument_expected_json,
        .{},
    );
    defer missing_reference_fixture.deinit();

    try testing.expectEqualStrings("", missing_reference_fixture.value.stdout);
    try testing.expectEqualStrings(
        "option '--reference' requires an argument\n" ++
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
        missing_reference_fixture.value.stderr,
    );
    try testing.expectEqual(@as(i64, 1), missing_reference_fixture.value.exit_code);

    const missing_dump_types_fixture = try std.json.parseFromSlice(
        ProcessFixture,
        testing.allocator,
        missing_long_dump_types_argument_expected_json,
        .{},
    );
    defer missing_dump_types_fixture.deinit();

    try testing.expectEqualStrings("", missing_dump_types_fixture.value.stdout);
    try testing.expectEqualStrings(
        "option '--dump-types' requires an argument\n" ++
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
        missing_dump_types_fixture.value.stderr,
    );
    try testing.expectEqual(@as(i64, 1), missing_dump_types_fixture.value.exit_code);
}

test "phase2 genksyms wrapper preserves mixed version counts before missing long reference arguments" {
    try expectMissingLongOptionArgumentFailure(&.{ "--version", "--ver" }, "--reference", 2);
    try expectMissingLongOptionArgumentFailure(&.{ "-V", "--version", "--ver" }, "--reference", 3);
}

test "phase2 genksyms wrapper preserves mixed version counts before missing long dump-types arguments" {
    try expectMissingLongOptionArgumentFailure(&.{ "--version", "--ver" }, "--dump-types", 2);
    try expectMissingLongOptionArgumentFailure(&.{ "-V", "--version", "--ver" }, "--dump-types", 3);
}
