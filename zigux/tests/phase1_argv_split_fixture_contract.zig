const std = @import("std");

const fixture_path = "zigux/tests/fixtures/phase1_helpers.json";

const Fixture = struct {
    argv_split: struct {
        argc: usize,
        argv: []const []const u8,
        blank_argc: usize,
    },
};

fn readFixture(allocator: std.mem.Allocator) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, fixture_path, allocator, .limited(64 * 1024));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectSingleOccurrence(haystack: []const u8, needle: []const u8) !void {
    var count: usize = 0;
    var offset: usize = 0;
    while (std.mem.indexOfPos(u8, haystack, offset, needle)) |found| {
        count += 1;
        offset = found + needle.len;
    }
    try std.testing.expectEqual(@as(usize, 1), count);
}

test "phase1 argv_split fixture pins token and blank-input parity" {
    const allocator = std.testing.allocator;
    const fixture_bytes = try readFixture(allocator);
    defer allocator.free(fixture_bytes);

    var parsed = try std.json.parseFromSlice(Fixture, allocator, fixture_bytes, .{
        .ignore_unknown_fields = true,
    });
    defer parsed.deinit();

    const fixture = parsed.value.argv_split;
    try std.testing.expectEqual(@as(usize, 3), fixture.argc);
    try std.testing.expectEqual(@as(usize, 3), fixture.argv.len);
    try std.testing.expectEqualStrings("alpha", fixture.argv[0]);
    try std.testing.expectEqualStrings("beta", fixture.argv[1]);
    try std.testing.expectEqualStrings("gamma", fixture.argv[2]);
    try std.testing.expectEqual(@as(usize, 0), fixture.blank_argc);
}

test "phase1 argv_split fixture section is uniquely parked between rbtree and cmdline" {
    const allocator = std.testing.allocator;
    const fixture_bytes = try readFixture(allocator);
    defer allocator.free(fixture_bytes);

    try expectSingleOccurrence(fixture_bytes, "\"argv_split\"");
    try expectSingleOccurrence(fixture_bytes, "\"argc\"");
    try expectSingleOccurrence(fixture_bytes, "\"blank_argc\"");
    try expectContains(fixture_bytes, "\"argv_split\"");
    try expectContains(fixture_bytes, "\"cmdline\"");
    try expectContains(fixture_bytes, "\"rbtree\"");

    const rbtree_pos = std.mem.indexOf(u8, fixture_bytes, "\"rbtree\"") orelse return error.TestUnexpectedResult;
    const argv_pos = std.mem.indexOf(u8, fixture_bytes, "\"argv_split\"") orelse return error.TestUnexpectedResult;
    const cmdline_pos = std.mem.indexOf(u8, fixture_bytes, "\"cmdline\"") orelse return error.TestUnexpectedResult;
    try std.testing.expect(rbtree_pos < argv_pos);
    try std.testing.expect(argv_pos < cmdline_pos);
}

test "phase1 argv_split fixture keeps exact committed field roster" {
    const allocator = std.testing.allocator;
    const fixture_bytes = try readFixture(allocator);
    defer allocator.free(fixture_bytes);

    try expectContains(fixture_bytes, "\"argv_split\"");
    try expectContains(fixture_bytes, "\"argc\"");
    try expectContains(fixture_bytes, "\"argv\"");
    try expectContains(fixture_bytes, "\"blank_argc\"");
    try expectContains(fixture_bytes, "\"alpha\"");
    try expectContains(fixture_bytes, "\"beta\"");
    try expectContains(fixture_bytes, "\"gamma\"");
}
