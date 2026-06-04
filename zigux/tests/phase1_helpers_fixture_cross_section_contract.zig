const std = @import("std");

const fixture = @embedFile("fixtures/phase1_helpers.json");

fn requireMarker(marker: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, fixture, marker) != null);
}

fn requireSingleMarker(marker: []const u8) !void {
    try requireMarker(marker);
    try std.testing.expectEqual(@as(usize, 1), std.mem.count(u8, fixture, marker));
}

fn requireInOrder(markers: []const []const u8) !void {
    var cursor: usize = 0;
    for (markers) |marker| {
        const found = std.mem.indexOf(u8, fixture[cursor..], marker) orelse return error.MarkerOutOfOrder;
        cursor += found + marker.len;
    }
}

test "phase 1 fixture keeps tail clamp and partial bitmap sentinels together" {
    try requireInOrder(&[_][]const u8{
        "\"find_bit\"",
        "\"tail_clamped_first\": 67",
        "\"tail_clamped_next\": 69",
        "\"tail_andnot_clamped_exhausted\": 69",
        "\"tail_clamped_empty_last\": 69",
        "\"tail_clump_exhausted_value\": 90",
        "\"bitmap\"",
        "\"partial_xor_nbits\": 4",
        "\"partial_xor_masked_values\": [14]",
    });
}

test "phase 1 fixture preserves shared direct-anchor smoke values" {
    try requireSingleMarker("\"strtobool_invalid\": 184");
    try requireSingleMarker("\"replace_char_cstr_bytes\": [97, 95, 0, 45, 122]");
    try requireSingleMarker("\"cached_leftmost_return_serials\": [0, -1, 2, -1]");
    try requireSingleMarker("\"next_match_terminal_null\": true");
}

test "phase 1 fixture keeps completion helpers anchored after list_sort" {
    try requireInOrder(&[_][]const u8{
        "\"list_sort\"",
        "\"tri_sorted_ordinals\": [1, 3, 0, 2, 4]",
        "\"zalloc\"",
        "\"value_freed_is_null\": true",
        "\"str_error_r\"",
        "\"tiny_unknown\": \"INTERNA\"",
        "\"slab\"",
        "\"zero_after_kmalloc\": true",
        "\"vsprintf\"",
        "\"pad_text\": \"id=7    \"",
    });
}
