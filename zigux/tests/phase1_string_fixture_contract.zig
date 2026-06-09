const std = @import("std");

const fixture = @embedFile("fixtures/phase1_helpers.json");

fn isJsonWhitespace(byte: u8) bool {
    return switch (byte) {
        ' ', '\n', '\r', '\t' => true,
        else => false,
    };
}

fn compactFixture(buffer: []u8) []const u8 {
    var out: usize = 0;
    var in_string = false;
    var escaped = false;

    for (fixture) |byte| {
        if (in_string) {
            buffer[out] = byte;
            out += 1;

            if (escaped) {
                escaped = false;
                continue;
            }
            if (byte == '\\') {
                escaped = true;
                continue;
            }
            if (byte == '"') in_string = false;
            continue;
        }

        if (byte == '"') {
            in_string = true;
            buffer[out] = byte;
            out += 1;
        } else if (!isJsonWhitespace(byte)) {
            buffer[out] = byte;
            out += 1;
        }
    }

    return buffer[0..out];
}

fn requireContains(needle: []const u8) !void {
    var compact_buffer: [fixture.len]u8 = undefined;
    const compact = compactFixture(compact_buffer[0..]);
    try std.testing.expect(std.mem.indexOf(u8, compact, needle) != null);
}

fn requireOnce(needle: []const u8) !void {
    var compact_buffer: [fixture.len]u8 = undefined;
    const compact = compactFixture(compact_buffer[0..]);
    try std.testing.expectEqual(@as(usize, 1), countOccurrences(compact, needle));
}

fn countOccurrences(haystack: []const u8, needle: []const u8) usize {
    var count: usize = 0;
    var start: usize = 0;
    while (std.mem.indexOfPos(u8, haystack, start, needle)) |index| {
        count += 1;
        start = index + needle.len;
    }
    return count;
}

fn indexOfRequired(needle: []const u8) !usize {
    var compact_buffer: [fixture.len]u8 = undefined;
    const compact = compactFixture(compact_buffer[0..]);
    return std.mem.indexOf(u8, compact, needle) orelse error.MissingFixtureNeedle;
}

test "string fixture keeps bool conversion and copy values" {
    try requireOnce("\"string\"");
    try requireContains("\"strtobool_y\":true");
    try requireContains("\"strtobool_on\":true");
    try requireContains("\"strtobool_zero\":false");
    try requireContains("\"strtobool_off\":false");
    try requireContains("\"strtobool_invalid\":184");
    try requireContains("\"strlcpy_len\":5");
    try requireContains("\"strlcpy_buffer\":\"hel\"");
}

test "string fixture keeps whitespace and replacement values" {
    try requireContains("\"skip_spaces\":\"hello\"");
    try requireContains("\"trim_spaces\":\"hi\"");
    try requireContains("\"remove_spaces\":\"abc\"");
    try requireContains("\"replace_char\":\"a_b\"");
    try requireContains("\"replace_char_end\":3");
    try requireContains("\"replace_char_cstr_end\":2");
    try requireContains("\"replace_char_cstr_bytes\":[97,95,0,45,122]");
}

test "string fixture keeps inverse-byte scan values" {
    try requireContains("\"memchr_inv_index\":4");
    try requireContains("\"memchr_inv_none\":true");
}

test "string section remains between bitmap and rbtree fixture packets" {
    const bitmap_index = try indexOfRequired("\"bitmap\"");
    const string_index = try indexOfRequired("\"string\"");
    const rbtree_index = try indexOfRequired("\"rbtree\"");

    try std.testing.expect(bitmap_index < string_index);
    try std.testing.expect(string_index < rbtree_index);
}
