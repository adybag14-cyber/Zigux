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
const too_many_reference_files_expected_json =
    @embedFile("fixtures/genksyms_bridge/too_many_reference_files_expected.json");

const reference_args = [_][]const u8{
    "-r", "01.symref",
    "-r", "02.symref",
    "-r", "03.symref",
    "-r", "04.symref",
    "-r", "05.symref",
    "-r", "06.symref",
    "-r", "07.symref",
    "-r", "08.symref",
    "-r", "09.symref",
    "-r", "10.symref",
    "-r", "11.symref",
    "-r", "12.symref",
    "-r", "13.symref",
    "-r", "14.symref",
    "-r", "15.symref",
    "-r", "16.symref",
    "-r", "17.symref",
};

fn expectTooManyReferenceFailure(
    version_prefixes: []const []const u8,
    expected_version_count: usize,
) !void {
    var args = std.ArrayList([]const u8).empty;
    defer args.deinit(testing.allocator);

    try args.appendSlice(testing.allocator, version_prefixes);
    try args.appendSlice(testing.allocator, &reference_args);

    const outcome = try genksyms.parseArgs(testing.allocator, args.items);
    switch (outcome) {
        .failure => |failure| {
            try testing.expectEqual(expected_version_count, failure.version_count);
            try testing.expectEqual(genksyms.ParseFailure.too_many_reference_files, failure.reason);
        },
        else => return error.ExpectedFailure,
    }
}

test "phase2 genksyms wrapper version fixtures stay aligned before reference-limit failures" {
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
        too_many_reference_files_expected_json,
        .{},
    );
    defer failure_fixture.deinit();

    try testing.expectEqualStrings("genksyms version 2.5.60\n", version_fixture.value.stderr);
    try testing.expectEqual(@as(i64, 0), version_fixture.value.exit_code);
    try testing.expectEqualStrings("genksyms version 2.5.60\n", abbreviated_fixture.value.stderr);
    try testing.expectEqual(@as(i64, 0), abbreviated_fixture.value.exit_code);
    try testing.expectEqualStrings("too many reference files\n", failure_fixture.value.stderr);
    try testing.expectEqual(@as(i64, 1), failure_fixture.value.exit_code);
}

test "phase2 genksyms wrapper preserves long version side effect before too many reference files" {
    try expectTooManyReferenceFailure(&.{"--version"}, 1);
}

test "phase2 genksyms wrapper preserves abbreviated version side effect before too many reference files" {
    try expectTooManyReferenceFailure(&.{"--ver"}, 1);
}
