const std = @import("std");

const fixture_bytes = @embedFile("fixtures/phase1_helpers.json");

const HweightFixture = struct {
    w8: u8,
    w16: u8,
    w32: u8,
    w64: u8,
    wlong: u8,
};

const Fixture = struct {
    hweight: HweightFixture,
};

fn loadFixture() !std.json.Parsed(Fixture) {
    return std.json.parseFromSlice(Fixture, std.testing.allocator, fixture_bytes, .{
        .ignore_unknown_fields = true,
    });
}

fn expectNeedleAfter(haystack: []const u8, earlier: []const u8, later: []const u8) !void {
    const earlier_index = std.mem.indexOf(u8, haystack, earlier) orelse return error.MissingEarlierNeedle;
    const later_index = std.mem.indexOf(u8, haystack, later) orelse return error.MissingLaterNeedle;
    try std.testing.expect(earlier_index < later_index);
}

test "phase 1 hweight fixture pins byte through u64 weights" {
    var parsed = try loadFixture();
    defer parsed.deinit();
    const hweight = parsed.value.hweight;

    try std.testing.expectEqual(@as(u8, 4), hweight.w8);
    try std.testing.expectEqual(@as(u8, 8), hweight.w16);
    try std.testing.expectEqual(@as(u8, 16), hweight.w32);
    try std.testing.expectEqual(@as(u8, 32), hweight.w64);
}

test "phase 1 hweight fixture pins unsigned long weight" {
    var parsed = try loadFixture();
    defer parsed.deinit();
    const hweight = parsed.value.hweight;

    try std.testing.expectEqual(@as(u8, 8), hweight.wlong);
}

test "phase 1 hweight fixture remains between ctype and list_sort sections" {
    try expectNeedleAfter(fixture_bytes, "\"ctype\"", "\"hweight\"");
    try expectNeedleAfter(fixture_bytes, "\"hweight\"", "\"list_sort\"");
    try std.testing.expectEqual(@as(usize, 1), std.mem.count(u8, fixture_bytes, "\"hweight\""));
}
