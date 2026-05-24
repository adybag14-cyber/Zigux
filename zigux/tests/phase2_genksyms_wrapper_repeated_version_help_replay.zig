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
const help_expected_json =
    @embedFile("fixtures/genksyms_bridge/help_expected.json");

fn expectHelpVersionCount(args: []const []const u8, expected_version_count: usize) !void {
    const outcome = try genksyms.parseArgs(testing.allocator, args);
    switch (outcome) {
        .command => |command| switch (command) {
            .help => |version_count| try testing.expectEqual(expected_version_count, version_count),
            else => return error.ExpectedHelpCommand,
        },
        else => return error.ExpectedCommand,
    }
}

test "phase2 genksyms wrapper repeated version-before-help packet stays aligned with fixtures" {
    const version_fixture = try std.json.parseFromSlice(
        ProcessFixture,
        testing.allocator,
        abbreviated_version_expected_json,
        .{},
    );
    defer version_fixture.deinit();

    const help_fixture = try std.json.parseFromSlice(
        ProcessFixture,
        testing.allocator,
        help_expected_json,
        .{},
    );
    defer help_fixture.deinit();

    try testing.expectEqualStrings("", version_fixture.value.stdout);
    try testing.expectEqualStrings("genksyms version 2.5.60\n", version_fixture.value.stderr);
    try testing.expectEqual(@as(i64, 0), version_fixture.value.exit_code);

    try testing.expectEqualStrings("", help_fixture.value.stdout);
    try testing.expectEqual(@as(i64, 0), help_fixture.value.exit_code);

    const combined_stderr = try std.mem.concat(
        testing.allocator,
        u8,
        &.{
            version_fixture.value.stderr,
            version_fixture.value.stderr,
            help_fixture.value.stderr,
        },
    );
    defer testing.allocator.free(combined_stderr);

    const expected_stderr = try std.mem.concat(
        testing.allocator,
        u8,
        &.{
            "genksyms version 2.5.60\n",
            "genksyms version 2.5.60\n",
            help_fixture.value.stderr,
        },
    );
    defer testing.allocator.free(expected_stderr);

    try testing.expectEqualStrings(expected_stderr, combined_stderr);
}

test "phase2 genksyms wrapper repeated version prefixes preserve help count" {
    try expectHelpVersionCount(&.{ "--ver", "--ver", "--help" }, 2);
    try expectHelpVersionCount(&.{ "--version", "--ver", "--help" }, 2);
    try expectHelpVersionCount(&.{ "--ver", "--version", "-h" }, 2);
}
