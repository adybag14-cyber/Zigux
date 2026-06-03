const std = @import("std");

const fixture = @embedFile("fixtures/phase1_helpers.json");

const expected_sections = [_][]const u8{
    "\"find_bit\"",
    "\"bitmap\"",
    "\"string\"",
    "\"rbtree\"",
    "\"argv_split\"",
    "\"cmdline\"",
    "\"ctype\"",
    "\"hweight\"",
    "\"list_sort\"",
    "\"zalloc\"",
    "\"str_error_r\"",
    "\"slab\"",
    "\"vsprintf\"",
};

fn markerCount(haystack: []const u8, needle: []const u8) usize {
    var count: usize = 0;
    var cursor: usize = 0;
    while (std.mem.indexOfPos(u8, haystack, cursor, needle)) |found| {
        count += 1;
        cursor = found + needle.len;
    }
    return count;
}

fn expectMarkersInOrder(haystack: []const u8, markers: []const []const u8) !void {
    var cursor: usize = 0;
    for (markers) |marker| {
        const found = std.mem.indexOfPos(u8, haystack, cursor, marker) orelse {
            std.debug.print("missing Phase 1 fixture marker: {s}\n", .{marker});
            return error.MissingPhase1FixtureMarker;
        };
        try std.testing.expectEqual(@as(usize, 1), markerCount(haystack, marker));
        cursor = found + marker.len;
    }
}

test "phase 1 helper fixture keeps canonical section order" {
    try expectMarkersInOrder(fixture, &expected_sections);
}

test "phase 1 helper fixture keeps parity-gate sentinels" {
    const required_sentinels = [_][]const u8{
        "\"tail_clamped_empty_last\"",
        "\"partial_xor_masked_values\"",
        "\"replace_char_cstr_bytes\"",
        "\"match_iterator_serials\"",
        "\"zero_after_kmalloc\"",
        "\"scnprintf_text\"",
    };
    for (required_sentinels) |sentinel| {
        try std.testing.expectEqual(@as(usize, 1), markerCount(fixture, sentinel));
    }
}
