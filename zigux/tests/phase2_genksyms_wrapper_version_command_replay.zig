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

fn expectVersionCount(args: []const []const u8, expected_count: usize) !void {
    const outcome = try genksyms.parseArgs(testing.allocator, args);
    switch (outcome) {
        .command => |command| switch (command) {
            .version => |count| try testing.expectEqual(expected_count, count),
            else => return error.ExpectedVersionCommand,
        },
        else => return error.ExpectedVersionCommand,
    }
}

test "phase2 genksyms wrapper version fixtures stay aligned with pure version commands" {
    const abbreviated_fixture = try std.json.parseFromSlice(
        ProcessFixture,
        testing.allocator,
        abbreviated_version_expected_json,
        .{},
    );
    defer abbreviated_fixture.deinit();

    try testing.expectEqualStrings("", abbreviated_fixture.value.stdout);
    try testing.expectEqualStrings("genksyms version 2.5.60\n", abbreviated_fixture.value.stderr);
    try testing.expectEqual(@as(i64, 0), abbreviated_fixture.value.exit_code);

    try expectVersionCount(&.{"-V"}, 1);
    try expectVersionCount(&.{"--version"}, 1);
    try expectVersionCount(&.{"--ver"}, 1);
}

test "phase2 genksyms wrapper repeated pure version commands preserve accumulated count" {
    try expectVersionCount(&.{"-VV"}, 2);
    try expectVersionCount(&.{ "--version", "--ver" }, 2);
    try expectVersionCount(&.{ "-V", "--version", "--ver" }, 3);
}
