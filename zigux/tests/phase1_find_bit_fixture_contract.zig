const std = @import("std");

const fixture_json = @embedFile("fixtures/phase1_helpers.json");

fn compactFixture(allocator: std.mem.Allocator) ![]u8 {
    var compact = std.ArrayList(u8).empty;
    errdefer compact.deinit(allocator);

    var in_string = false;
    var escaped = false;
    for (fixture_json) |byte| {
        if (in_string) {
            try compact.append(allocator, byte);
            if (escaped) {
                escaped = false;
            } else if (byte == '\\') {
                escaped = true;
            } else if (byte == '"') {
                in_string = false;
            }
            continue;
        }

        if (byte == '"') {
            in_string = true;
            try compact.append(allocator, byte);
        } else if (!std.ascii.isWhitespace(byte)) {
            try compact.append(allocator, byte);
        }
    }

    return compact.toOwnedSlice(allocator);
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectBefore(haystack: []const u8, earlier: []const u8, later: []const u8) !void {
    const earlier_index = std.mem.indexOf(u8, haystack, earlier) orelse return error.MissingEarlierMarker;
    const later_index = std.mem.indexOf(u8, haystack, later) orelse return error.MissingLaterMarker;
    try std.testing.expect(earlier_index < later_index);
}

test "find_bit fixture pins baseline cross-word replay values" {
    const compact = try compactFixture(std.testing.allocator);
    defer std.testing.allocator.free(compact);

    try expectContains(compact, "\"find_bit\":{");
    try expectContains(compact, "\"bits_per_long\":64");
    try expectContains(compact, "\"first\":5");
    try expectContains(compact, "\"next_after_6\":9");
    try expectContains(compact, "\"next_after_word\":66");
    try expectContains(compact, "\"first_zero\":3");
    try expectContains(compact, "\"next_zero\":68");
    try expectContains(compact, "\"first_and\":9");
    try expectContains(compact, "\"next_and\":66");
    try expectContains(compact, "\"last\":71");
}

test "find_bit fixture keeps inclusive and past-nbits guards explicit" {
    const compact = try compactFixture(std.testing.allocator);
    defer std.testing.allocator.free(compact);

    try expectContains(compact, "\"inclusive_boundary_next\":63");
    try expectContains(compact, "\"inclusive_boundary_zero\":63");
    try expectContains(compact, "\"inclusive_boundary_and\":63");
    try expectContains(compact, "\"past_nbits_next\":7");
    try expectContains(compact, "\"past_nbits_zero\":7");
    try expectContains(compact, "\"past_nbits_and\":7");
}

test "find_bit fixture pins tail clamp and clump8 replay values" {
    const compact = try compactFixture(std.testing.allocator);
    defer std.testing.allocator.free(compact);

    try expectContains(compact, "\"tail_clamped_first\":67");
    try expectContains(compact, "\"tail_clamped_next\":69");
    try expectContains(compact, "\"tail_zero_clamped_first\":68");
    try expectContains(compact, "\"tail_zero_clamped_next\":69");
    try expectContains(compact, "\"tail_and_clamped_first\":67");
    try expectContains(compact, "\"tail_and_clamped_next\":69");
    try expectContains(compact, "\"tail_andnot_clamped_first\":67");
    try expectContains(compact, "\"tail_andnot_clamped_next\":67");
    try expectContains(compact, "\"tail_andnot_clamped_exhausted\":69");
    try expectContains(compact, "\"tail_clamped_last\":67");
    try expectContains(compact, "\"tail_clamped_empty_last\":69");
    try expectContains(compact, "\"tail_inclusive_boundary_next\":68");
    try expectContains(compact, "\"tail_inclusive_boundary_zero\":68");
    try expectContains(compact, "\"tail_inclusive_boundary_and\":68");
    try expectContains(compact, "\"tail_clump_first\":64");
    try expectContains(compact, "\"tail_clump_first_value\":8");
    try expectContains(compact, "\"tail_clump_next\":64");
    try expectContains(compact, "\"tail_clump_next_value\":8");
    try expectContains(compact, "\"tail_clump_exhausted\":69");
    try expectContains(compact, "\"tail_clump_exhausted_value\":90");
}

test "find_bit fixture remains first and before bitmap in the phase1 packet" {
    const compact = try compactFixture(std.testing.allocator);
    defer std.testing.allocator.free(compact);

    try std.testing.expect(std.mem.startsWith(u8, compact, "{\"find_bit\":{"));
    try expectBefore(compact, "\"find_bit\":{", "\"bitmap\":{");
}
