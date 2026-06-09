const std = @import("std");

const fixture = @embedFile("fixtures/phase1_helpers.json");
var compact_fixture: [fixture.len]u8 = undefined;

fn compactFixture() []const u8 {
    var written: usize = 0;
    for (fixture) |byte| {
        if (std.ascii.isWhitespace(byte)) continue;
        compact_fixture[written] = byte;
        written += 1;
    }
    return compact_fixture[0..written];
}

fn requireContains(needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, compactFixture(), needle) != null);
}

fn requireNotContains(needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, compactFixture(), needle) == null);
}

fn requireOrder(before: []const u8, after: []const u8) !void {
    const compact = compactFixture();
    const before_index = std.mem.indexOf(u8, compact, before) orelse return error.MissingBeforeMarker;
    const after_index = std.mem.indexOf(u8, compact, after) orelse return error.MissingAfterMarker;
    try std.testing.expect(before_index < after_index);
}

test "phase1 slab fixture pins scalar parity values" {
    try requireContains("\"slab\"");
    try requireContains("\"null_without_reclaim\":true");
    try requireContains("\"alloc_count_after_kmalloc\":1");
    try requireContains("\"zero_after_kmalloc\":true");
    try requireContains("\"alloc_count_after_kmalloc_free\":0");
    try requireContains("\"array_zeroed\":true");
    try requireContains("\"alloc_count_after_kmalloc_array\":1");
    try requireContains("\"alloc_count_after_kmalloc_array_free\":0");
    try requireContains("\"slab_is_available\":true");
}

test "phase1 slab fixture keeps bounded field roster" {
    try requireOrder("\"slab\"", "\"null_without_reclaim\"");
    try requireOrder("\"null_without_reclaim\"", "\"alloc_count_after_kmalloc\"");
    try requireOrder("\"alloc_count_after_kmalloc\"", "\"zero_after_kmalloc\"");
    try requireOrder("\"zero_after_kmalloc\"", "\"alloc_count_after_kmalloc_free\"");
    try requireOrder("\"alloc_count_after_kmalloc_free\"", "\"array_zeroed\"");
    try requireOrder("\"array_zeroed\"", "\"alloc_count_after_kmalloc_array\"");
    try requireOrder("\"alloc_count_after_kmalloc_array\"", "\"alloc_count_after_kmalloc_array_free\"");
    try requireOrder("\"alloc_count_after_kmalloc_array_free\"", "\"slab_is_available\"");
    try requireNotContains("\"kmalloc_array_overflow\"");
    try requireNotContains("\"alloc_count_after_kzalloc\"");
}

test "phase1 slab fixture keeps section placement" {
    try requireOrder("\"str_error_r\"", "\"slab\"");
    try requireOrder("\"slab\"", "\"vsprintf\"");
    try requireOrder("\"zalloc\"", "\"str_error_r\"");
}
