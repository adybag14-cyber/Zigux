const std = @import("std");
const testing = std.testing;

const parity_source = @embedFile("check-phase1-parity.py");

fn expectContains(needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, parity_source, needle) != null);
}

fn expectBefore(first: []const u8, second: []const u8) !void {
    const first_index = std.mem.indexOf(u8, parity_source, first) orelse return error.MissingFirstMarker;
    const second_index = std.mem.indexOf(u8, parity_source, second) orelse return error.MissingSecondMarker;
    try testing.expect(first_index < second_index);
}

fn fixtureValueTable() ![]const u8 {
    const start = std.mem.indexOf(u8, parity_source, "EXPECTED_FIXTURE_VALUES = {") orelse
        return error.MissingFixtureValueTable;
    const end = std.mem.indexOf(u8, parity_source[start..], "\n}\n\nEXPECTED_REPLAY_BLOCKER_IDS") orelse
        return error.MissingFixtureValueTableEnd;
    return parity_source[start .. start + end];
}

fn tableOccurrenceCount(table: []const u8, needle: []const u8) usize {
    var count: usize = 0;
    var rest: []const u8 = table;
    while (std.mem.indexOf(u8, rest, needle)) |index| {
        count += 1;
        rest = rest[index + needle.len ..];
    }
    return count;
}

const fixture_value_markers = [_][]const u8{
    "(\"string\", \"strtobool_invalid\"): 184,",
    "(\"string\", \"replace_char_cstr_end\"): 2,",
    "(\"string\", \"replace_char_cstr_bytes\"): [97, 95, 0, 45, 122],",
    "(\"slab\", \"zero_after_kmalloc\"): True,",
    "(\"bitmap\", \"truncated_scnprintf_len\"): 7,",
    "(\"bitmap\", \"truncated_scnprintf\"): \"1-3,66-\",",
    "(\"bitmap\", \"terminator_only_scnprintf_len\"): 0,",
    "(\"bitmap\", \"zero_length_scnprintf_len\"): 0,",
    "(\"bitmap\", \"copy_clear_tail_values\"): [18446744073709551615, 31],",
    "(\"bitmap\", \"copy_and_extend_values\"): [18446744073709551615, 31, 0],",
    "(\"find_bit\", \"inclusive_boundary_next\"): 63,",
    "(\"find_bit\", \"inclusive_boundary_zero\"): 63,",
    "(\"find_bit\", \"inclusive_boundary_and\"): 63,",
    "(\"find_bit\", \"tail_clamped_first\"): 67,",
    "(\"find_bit\", \"tail_clamped_last\"): 67,",
    "(\"find_bit\", \"tail_clamped_empty_last\"): 69,",
    "(\"rbtree\", \"cached_leftmost_return_serials\"): [0, -1, 2, -1],",
    "(\"rbtree\", \"cached_root_transition_serials\"): [0, 0, 4, 2],",
    "(\"rbtree\", \"next_match_terminal_null\"): True,",
    "(\"list_sort\", \"bool_sorted_ordinals\"): [1, 3, 0, 2, 4],",
};

test "phase1 parity checker pins representative fixture value sentinels" {
    const table = try fixtureValueTable();
    try testing.expectEqual(@as(usize, fixture_value_markers.len), tableOccurrenceCount(table, "\"):"));

    for (fixture_value_markers) |marker| {
        try expectContains(marker);
    }

    try expectBefore(
        "(\"string\", \"strtobool_invalid\"): 184,",
        "(\"slab\", \"zero_after_kmalloc\"): True,",
    );
    try expectBefore(
        "(\"bitmap\", \"copy_and_extend_values\"): [18446744073709551615, 31, 0],",
        "(\"find_bit\", \"inclusive_boundary_next\"): 63,",
    );
    try expectBefore(
        "(\"rbtree\", \"cached_root_transition_serials\"): [0, 0, 4, 2],",
        "(\"list_sort\", \"bool_sorted_ordinals\"): [1, 3, 0, 2, 4],",
    );
}

test "phase1 parity checker compares fixture sentinels fail closed" {
    try expectContains("for (section, key), expected_value in EXPECTED_FIXTURE_VALUES.items():");
    try expectContains("section_payload = fixture_payload.get(section)");
    try expectContains("ensure(isinstance(section_payload, dict), f\"fixture:{section}:not_object\", issues)");
    try expectContains(
        "section_payload.get(key) == expected_value,",
    );
    try expectContains(
        "f\"fixture:{section}.{key}:{section_payload.get(key)!r}!={expected_value!r}\",",
    );
}

test "phase1 parity checker self-test sample root mirrors sentinel values" {
    try expectContains("fixture_payload[\"string\"][\"strtobool_invalid\"] = 184");
    try expectContains("fixture_payload[\"slab\"][\"zero_after_kmalloc\"] = True");
    try expectContains("fixture_payload[\"bitmap\"][\"copy_clear_tail_values\"] = [18446744073709551615, 31]");
    try expectContains("fixture_payload[\"find_bit\"][\"tail_clamped_empty_last\"] = 69");
    try expectContains("fixture_payload[\"rbtree\"][\"cached_leftmost_return_serials\"] = [0, -1, 2, -1]");
    try expectContains("fixture_payload[\"list_sort\"][\"bool_sorted_ordinals\"] = [1, 3, 0, 2, 4]");
    try expectBefore(
        "fixture_payload[\"string\"][\"strtobool_invalid\"] = 184",
        "fixture_payload[\"slab\"][\"zero_after_kmalloc\"] = True",
    );
}
