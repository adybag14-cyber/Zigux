const std = @import("std");

const fixture_bytes = @embedFile("fixtures/phase1_helpers.json");

fn compactJson(allocator: std.mem.Allocator, input: []const u8) ![]u8 {
    var out = try std.ArrayList(u8).initCapacity(allocator, input.len);
    var in_string = false;
    var escaped = false;

    for (input) |byte| {
        if (in_string) {
            try out.append(allocator, byte);
            if (escaped) {
                escaped = false;
            } else if (byte == '\\') {
                escaped = true;
            } else if (byte == '"') {
                in_string = false;
            }
            continue;
        }

        switch (byte) {
            '"' => {
                in_string = true;
                try out.append(allocator, byte);
            },
            ' ', '\n', '\r', '\t' => {},
            else => try out.append(allocator, byte),
        }
    }

    return out.toOwnedSlice(allocator);
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectOrdered(haystack: []const u8, before: []const u8, after: []const u8) !void {
    const before_index = std.mem.indexOf(u8, haystack, before) orelse return error.MissingBeforeMarker;
    const after_index = std.mem.indexOf(u8, haystack, after) orelse return error.MissingAfterMarker;
    try std.testing.expect(before_index < after_index);
}

test "cmdline fixture section is parked between argv_split and ctype" {
    const compact = try compactJson(std.testing.allocator, fixture_bytes);
    defer std.testing.allocator.free(compact);

    try expectOrdered(compact, "\"argv_split\"", "\"cmdline\"");
    try expectOrdered(compact, "\"cmdline\"", "\"ctype\"");
    try std.testing.expectEqual(@as(usize, 1), std.mem.count(u8, compact, "\"cmdline\""));
}

test "cmdline fixture keeps base parse and option values" {
    const compact = try compactJson(std.testing.allocator, fixture_bytes);
    defer std.testing.allocator.free(compact);

    try expectContains(compact, "\"decimal_k\":{\"value\":65536,\"rest\":\" rest\"}");
    try expectContains(compact, "\"hex_m\":{\"value\":33554432,\"rest\":\"\"}");
    try expectContains(compact, "\"octal_k\":{\"value\":8192,\"rest\":\"\"}");
    try expectContains(compact, "\"invalid\":{\"value\":0,\"rest\":\"xyz\"}");
}

test "expanded cmdline fixture pins signed and quoted argument roster when present" {
    const compact = try compactJson(std.testing.allocator, fixture_bytes);
    defer std.testing.allocator.free(compact);

    if (std.mem.indexOf(u8, compact, "\"signed_k\"") == null) {
        try expectContains(
            compact,
            "\"cmdline\":{\"decimal_k\":{\"value\":65536,\"rest\":\" rest\"},\"hex_m\":{\"value\":33554432,\"rest\":\"\"},\"octal_k\":{\"value\":8192,\"rest\":\"\"},\"invalid\":{\"value\":0,\"rest\":\"xyz\"}}",
        );
        return;
    }

    try expectContains(compact, "\"signed_k\":{\"value\":18446744073709549568,\"rest\":\" tail\"}");
    try expectContains(compact, "\"signed_hex_k\":{\"value\":18446744073709549568,\"rest\":\"tail\"}");
    try expectContains(compact, "\"signed_octal_m\":{\"value\":8388608,\"rest\":\"more\"}");
    try expectContains(compact, "\"saturated_positive_signed\":{\"value\":9223372036854775807,\"rest\":\"\"}");
    try expectContains(compact, "\"option_debug\":true");
    try expectContains(compact, "\"option_empty_leading\":true");
    try expectContains(compact, "\"option_empty_double_comma\":true");
    try expectContains(compact, "\"option_empty_trailing\":false");
    try expectContains(compact, "\"option_absent\":false");
    try expectContains(compact, "\"first_arg\":{\"param\":\"console\",\"value\":\"ttyS0,115200\",\"remaining\":\"root=\\\"/dev/sda1 quiet\\\" panic=-1\"}");
    try expectContains(compact, "\"second_arg\":{\"param\":\"root\",\"value\":\"/dev/sda1 quiet\",\"remaining\":\"panic=-1\"}");
    try expectContains(compact, "\"quoted_arg\":{\"param\":\"mode\",\"value\":\"fast path\",\"remaining\":\"tail\"}");
    try expectContains(compact, "\"empty_quoted_arg\":{\"param\":\"root\",\"value\":\"\",\"remaining\":\"quiet\"}");
    try expectContains(compact, "\"unterminated_arg\":{\"param\":\"mode\",\"value\":\"fast boot\",\"remaining\":\"\"}");

    const expected_roster =
        "\"cmdline\":{\"decimal_k\":{\"value\":65536,\"rest\":\" rest\"}," ++
        "\"signed_k\":{\"value\":18446744073709549568,\"rest\":\" tail\"}," ++
        "\"signed_hex_k\":{\"value\":18446744073709549568,\"rest\":\"tail\"}," ++
        "\"signed_octal_m\":{\"value\":8388608,\"rest\":\"more\"}," ++
        "\"saturated_positive_signed\":{\"value\":9223372036854775807,\"rest\":\"\"}," ++
        "\"option_debug\":true,\"option_empty_leading\":true,\"option_empty_double_comma\":true," ++
        "\"option_empty_trailing\":false,\"option_absent\":false,\"first_arg\":";
    try expectContains(compact, expected_roster);
}
