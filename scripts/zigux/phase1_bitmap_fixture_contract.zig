const std = @import("std");

const checker = @embedFile("check-phase1-parity.py");

fn readFixture() ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        "zigux/tests/fixtures/phase1_helpers.json",
        std.testing.allocator,
        .limited(64 * 1024),
    );
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectBefore(haystack: []const u8, before: []const u8, after: []const u8) !void {
    const before_index = std.mem.indexOf(u8, haystack, before) orelse return error.MissingBeforeMarker;
    const after_index = std.mem.indexOf(u8, haystack, after) orelse return error.MissingAfterMarker;
    try std.testing.expect(before_index < after_index);
}

fn expectContainsOnce(haystack: []const u8, needle: []const u8) !void {
    var count: usize = 0;
    var start: usize = 0;
    while (std.mem.indexOfPos(u8, haystack, start, needle)) |index| {
        count += 1;
        start = index + needle.len;
    }
    try std.testing.expectEqual(@as(usize, 1), count);
}

fn sliceBetween(haystack: []const u8, start_marker: []const u8, end_marker: []const u8) ![]const u8 {
    const start_index = std.mem.indexOf(u8, haystack, start_marker) orelse return error.MissingStartMarker;
    const content_start = start_index + start_marker.len;
    const end_offset = std.mem.indexOf(u8, haystack[content_start..], end_marker) orelse return error.MissingEndMarker;
    return haystack[start_index .. content_start + end_offset];
}

fn expectMarkersInOrder(haystack: []const u8, markers: []const []const u8) !void {
    var cursor: usize = 0;
    for (markers) |marker| {
        const relative = std.mem.indexOf(u8, haystack[cursor..], marker) orelse return error.MissingOrderedMarker;
        cursor += relative + marker.len;
    }
}

test "bitmap fixture remains between find_bit and string with direct-review ordering" {
    const fixture = try readFixture();
    defer std.testing.allocator.free(fixture);

    try expectBefore(fixture, "\"find_bit\": {", "\"bitmap\": {");
    try expectBefore(fixture, "\"bitmap\": {", "\"string\": {");

    const bitmap = try sliceBetween(fixture, "\"bitmap\": {", "\n  },\n  \"string\": {");
    const ordered_keys = [_][]const u8{
        "\"weight\": 5",
        "\"scnprintf\": \"1-3,66-67\"",
        "\"truncated_scnprintf_len\": 7",
        "\"truncated_scnprintf\": \"1-3,66-\"",
        "\"terminator_only_scnprintf_len\": 0",
        "\"terminator_only_nul\": 0",
        "\"zero_length_scnprintf_len\": 0",
        "\"alloc_words\": 3",
        "\"zalloc_words\": 3",
        "\"zalloc_values\": [0, 0, 0]",
        "\"copy_values\": [18446744073709551615, 18446744073709551615]",
        "\"copy_clear_tail_values\": [18446744073709551615, 31]",
        "\"copy_and_extend_values\": [18446744073709551615, 31, 0]",
    };
    try expectMarkersInOrder(bitmap, &ordered_keys);
}

test "bitmap fixture pins logical operation and partial-tail values" {
    const fixture = try readFixture();
    defer std.testing.allocator.free(fixture);

    const bitmap = try sliceBetween(fixture, "\"bitmap\": {", "\n  },\n  \"string\": {");
    const logical_values = [_][]const u8{
        "\"complement_values\": [18446744073709551605, 29]",
        "\"and_result\": true",
        "\"and_values\": [10, 0]",
        "\"andnot_result\": true",
        "\"andnot_values\": [4, 0]",
        "\"or_values\": [14, 0]",
        "\"xor_values\": [4, 0]",
        "\"partial_xor_nbits\": 4",
        "\"partial_xor_masked_values\": [14]",
        "\"equal\": true",
        "\"intersects\": true",
        "\"subset\": true",
    };
    for (logical_values) |marker| {
        try expectContainsOnce(bitmap, marker);
    }
}

test "bitmap fixture pins range mutation terminal state" {
    const fixture = try readFixture();
    defer std.testing.allocator.free(fixture);

    const bitmap = try sliceBetween(fixture, "\"bitmap\": {", "\n  },\n  \"string\": {");
    const range_values = [_][]const u8{
        "\"range_after_set\": [14, 12, 0]",
        "\"range_after_clear\": [0, 0, 0]",
        "\"full_after_fill\": true",
        "\"empty_after_zero\": true",
    };
    for (range_values) |marker| {
        try expectContainsOnce(bitmap, marker);
    }
}

test "parity checker keeps bitmap fixture keys coupled to direct review anchors" {
    const checker_bitmap = try sliceBetween(checker, "\"tools/lib/bitmap.zig\": {", "\n    \"tools/lib/find_bit.zig\": {");

    const checker_groups = [_][]const u8{
        "\"parity_fixture_keys\": (",
        "\"shared_logical_fixture_keys\": (",
        "\"shared_range_fixture_keys\": (",
        "\"partial_xor_review_fields\": (",
    };
    for (checker_groups) |marker| {
        try expectContainsOnce(checker_bitmap, marker);
    }

    const expected_bitmap_values = [_][]const u8{
        "(\"bitmap\", \"truncated_scnprintf_len\"): 7",
        "(\"bitmap\", \"truncated_scnprintf\"): \"1-3,66-\"",
        "(\"bitmap\", \"terminator_only_scnprintf_len\"): 0",
        "(\"bitmap\", \"zero_length_scnprintf_len\"): 0",
        "(\"bitmap\", \"copy_clear_tail_values\"): [18446744073709551615, 31]",
        "(\"bitmap\", \"copy_and_extend_values\"): [18446744073709551615, 31, 0]",
    };
    for (expected_bitmap_values) |marker| {
        try expectContains(checker, marker);
    }
}
