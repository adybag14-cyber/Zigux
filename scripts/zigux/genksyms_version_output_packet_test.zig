const std = @import("std");
const testing = std.testing;
const genksyms = @import("genksyms.zig");

const OutputFixture = struct {
    stdout: []const u8,
    stderr: []const u8,
    exit_code: i64,
};

const version_text = "genksyms version 2.5.60\n";

fn parseFixture(path: []const u8) !std.json.Parsed(OutputFixture) {
    const io = std.testing.io;
    const bytes = try std.Io.Dir.cwd().readFileAlloc(io, path, testing.allocator, .limited(4096));
    defer testing.allocator.free(bytes);
    return std.json.parseFromSlice(OutputFixture, testing.allocator, bytes, .{});
}

test "genksyms bridge pure version output fixture stays aligned with live command output" {
    const args = [_][]const u8{"--version"};
    const outcome = try genksyms.parseArgs(testing.allocator, &args);
    const parsed = try parseFixture("zigux/tests/fixtures/genksyms_bridge/version_expected.json");
    defer parsed.deinit();

    switch (outcome) {
        .command => |command| switch (command) {
            .version => |count| try testing.expectEqual(@as(usize, 1), count),
            else => return error.ExpectedVersionCommand,
        },
        else => return error.ExpectedVersionCommand,
    }

    try testing.expectEqualStrings("", parsed.value.stdout);
    try testing.expectEqualStrings(version_text, parsed.value.stderr);
    try testing.expectEqual(@as(i64, 0), parsed.value.exit_code);
}

test "genksyms bridge repeated pure version output fixture stays aligned with live command output" {
    const args = [_][]const u8{
        "--version",
        "--ver",
    };
    const outcome = try genksyms.parseArgs(testing.allocator, &args);
    const parsed = try parseFixture("zigux/tests/fixtures/genksyms_bridge/repeated_version_expected.json");
    defer parsed.deinit();

    switch (outcome) {
        .command => |command| switch (command) {
            .version => |count| try testing.expectEqual(@as(usize, 2), count),
            else => return error.ExpectedVersionCommand,
        },
        else => return error.ExpectedVersionCommand,
    }

    try testing.expectEqualStrings("", parsed.value.stdout);
    try testing.expectEqualStrings(version_text ++ version_text, parsed.value.stderr);
    try testing.expectEqual(@as(i64, 0), parsed.value.exit_code);
}
