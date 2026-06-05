const std = @import("std");

const fixture_text = @embedFile("fixtures/phase1_helpers.json");

const Fixture = struct {
    list_sort: std.json.Value,
    zalloc: Zalloc,
    str_error_r: std.json.Value,
};

const Zalloc = struct {
    zeroed: bool,
    freed_is_null: bool,
    value_zeroed: bool,
    value_freed_is_null: bool,
};

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectOrdered(before: []const u8, middle: []const u8, after: []const u8) !void {
    const before_index = std.mem.indexOf(u8, fixture_text, before) orelse return error.MissingBeforeMarker;
    const middle_index = std.mem.indexOf(u8, fixture_text, middle) orelse return error.MissingMiddleMarker;
    const after_index = std.mem.indexOf(u8, fixture_text, after) orelse return error.MissingAfterMarker;

    try std.testing.expect(before_index < middle_index);
    try std.testing.expect(middle_index < after_index);
}

fn expectSingleMarker(needle: []const u8) !void {
    const first = std.mem.indexOf(u8, fixture_text, needle) orelse return error.MissingMarker;
    const rest = fixture_text[first + needle.len ..];
    try std.testing.expect(std.mem.indexOf(u8, rest, needle) == null);
}

test "zalloc fixture keeps pointer and value cleanup semantics" {
    const parsed = try std.json.parseFromSlice(Fixture, std.testing.allocator, fixture_text, .{
        .ignore_unknown_fields = true,
    });
    defer parsed.deinit();

    const zalloc = parsed.value.zalloc;
    try std.testing.expect(zalloc.zeroed);
    try std.testing.expect(zalloc.freed_is_null);
    try std.testing.expect(zalloc.value_zeroed);
    try std.testing.expect(zalloc.value_freed_is_null);
}

test "zalloc fixture section remains singular and ordered with completion helpers" {
    try expectSingleMarker("\"zalloc\"");
    try expectOrdered("\"list_sort\"", "\"zalloc\"", "\"str_error_r\"");

    try expectContains(fixture_text, "\"zeroed\"");
    try expectContains(fixture_text, "\"freed_is_null\"");
    try expectContains(fixture_text, "\"value_zeroed\"");
    try expectContains(fixture_text, "\"value_freed_is_null\"");
}
