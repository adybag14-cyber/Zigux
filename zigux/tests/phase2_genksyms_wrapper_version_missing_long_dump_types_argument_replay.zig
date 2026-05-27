const std = @import("std");
const genksyms = @import("genksyms");

const testing = std.testing;

const ProcessFixture = struct {
    stdout: []const u8,
    stderr: []const u8,
    exit_code: i64,
};

const version_expected_json =
    @embedFile("fixtures/genksyms_bridge/version_expected.json");
const abbreviated_version_expected_json =
    @embedFile("fixtures/genksyms_bridge/abbreviated_version_expected.json");
const missing_long_dump_types_argument_expected_json =
    @embedFile("fixtures/genksyms_bridge/missing_long_dump_types_argument_expected.json");

fn expectMissingLongDumpTypesFailure(
    version_prefixes: []const []const u8,
    dump_types_arg: []const u8,
    expected_version_count: usize,
) !void {
    const args = [_][]const u8{ version_prefixes[0], dump_types_arg };
    const outcome = try genksyms.parseArgs(testing.allocator, &args);
    switch (outcome) {
        .failure => |failure| {
            try testing.expectEqual(expected_version_count, failure.version_count);
            switch (failure.reason) {
                .missing_option_argument => |option| try testing.expectEqualStrings("--dump-types", option),
                else => return error.UnexpectedParseFailure,
            }
        },
        else => return error.ExpectedFailure,
    }
}

test "phase2 genksyms wrapper version fixtures stay aligned before missing long dump-types failures" {
    const version_fixture = try std.json.parseFromSlice(
        ProcessFixture,
        testing.allocator,
        version_expected_json,
        .{},
    );
    defer version_fixture.deinit();

    const abbreviated_fixture = try std.json.parseFromSlice(
        ProcessFixture,
        testing.allocator,
        abbreviated_version_expected_json,
        .{},
    );
    defer abbreviated_fixture.deinit();

    const failure_fixture = try std.json.parseFromSlice(
        ProcessFixture,
        testing.allocator,
        missing_long_dump_types_argument_expected_json,
        .{},
    );
    defer failure_fixture.deinit();

    try testing.expectEqualStrings("", version_fixture.value.stdout);
    try testing.expectEqualStrings("genksyms version 2.5.60\n", version_fixture.value.stderr);
    try testing.expectEqual(@as(i64, 0), version_fixture.value.exit_code);

    try testing.expectEqualStrings("", abbreviated_fixture.value.stdout);
    try testing.expectEqualStrings("genksyms version 2.5.60\n", abbreviated_fixture.value.stderr);
    try testing.expectEqual(@as(i64, 0), abbreviated_fixture.value.exit_code);

    try testing.expectEqualStrings("", failure_fixture.value.stdout);
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
        failure_fixture.value.stderr,
    );
    try testing.expectEqual(@as(i64, 1), failure_fixture.value.exit_code);
}

test "phase2 genksyms wrapper preserves long version side effect before missing long dump-types argument" {
    try expectMissingLongDumpTypesFailure(&.{"--version"}, "--dump-types", 1);
}

test "phase2 genksyms wrapper preserves abbreviated version side effect before missing long dump-types argument" {
    try expectMissingLongDumpTypesFailure(&.{"--ver"}, "--dump-t", 1);
}
