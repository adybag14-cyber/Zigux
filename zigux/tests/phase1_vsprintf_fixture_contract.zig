const std = @import("std");

const fixture_json = @embedFile("fixtures/phase1_helpers.json");

const Fixture = struct {
    vsprintf: struct {
        scnprintf_text: []const u8,
        scnprintf_len: usize,
        pad_text: []const u8,
        pad_len: usize,
    },
};

fn loadFixture() !std.json.Parsed(Fixture) {
    return std.json.parseFromSlice(Fixture, std.testing.allocator, fixture_json, .{
        .ignore_unknown_fields = true,
    });
}

fn expectContainsOnce(haystack: []const u8, needle: []const u8) !void {
    const first = std.mem.indexOf(u8, haystack, needle) orelse return error.MissingNeedle;
    const rest = haystack[first + needle.len ..];
    try std.testing.expectEqual(@as(?usize, null), std.mem.indexOf(u8, rest, needle));
}

test "phase1 vsprintf fixture preserves formatted text and lengths" {
    const parsed = try loadFixture();
    defer parsed.deinit();

    const values = parsed.value.vsprintf;
    try std.testing.expectEqualStrings("zigux:7", values.scnprintf_text);
    try std.testing.expectEqual(@as(usize, 7), values.scnprintf_len);
    try std.testing.expectEqual(values.scnprintf_text.len, values.scnprintf_len);
}

test "phase1 vsprintf fixture preserves padded visible window" {
    const parsed = try loadFixture();
    defer parsed.deinit();

    const values = parsed.value.vsprintf;
    try std.testing.expectEqualStrings("id=7    ", values.pad_text);
    try std.testing.expectEqual(@as(usize, 8), values.pad_len);
    try std.testing.expectEqual(values.pad_text.len, values.pad_len);
    try std.testing.expect(std.mem.startsWith(u8, values.pad_text, "id=7"));
    try std.testing.expectEqual(@as(usize, 4), std.mem.count(u8, values.pad_text, " "));
}

test "phase1 vsprintf fixture keeps exact key roster" {
    const markers = [_][]const u8{
        "\"vsprintf\":",
        "\"scnprintf_text\"",
        "\"scnprintf_len\"",
        "\"pad_text\"",
        "\"pad_len\"",
    };

    for (markers) |marker| {
        try expectContainsOnce(fixture_json, marker);
    }
}
