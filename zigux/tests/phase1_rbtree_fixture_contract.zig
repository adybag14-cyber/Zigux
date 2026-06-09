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

fn contains(needle: []const u8) bool {
    return std.mem.indexOf(u8, compactFixture(), needle) != null;
}

fn requireContains(needle: []const u8) !void {
    try std.testing.expect(contains(needle));
}

fn requireNotContains(needle: []const u8) !void {
    try std.testing.expect(!contains(needle));
}

fn requireOrder(before: []const u8, after: []const u8) !void {
    const compact = compactFixture();
    const before_index = std.mem.indexOf(u8, compact, before) orelse return error.MissingBeforeMarker;
    const after_index = std.mem.indexOf(u8, compact, after) orelse return error.MissingAfterMarker;
    try std.testing.expect(before_index < after_index);
}

test "phase1 rbtree fixture pins traversal and mutation vectors" {
    try requireContains("\"rbtree\"");
    try requireContains("\"empty_root\":true");
    try requireContains("\"insert_order\":[5,10,15,20,25]");
    try requireContains("\"reverse_order\":[25,20,15,10,5]");
    try requireContains("\"replace_order\":[5,10,15,25]");
    try requireContains("\"erase_init_order\":[5,15,25]");
    try requireContains("\"postorder_count\":3");
    try requireContains("\"erase_init_node_empty\":true");
    try requireContains("\"cleared_node_empty\":true");
}

test "phase1 rbtree fixture pins lookup and iterator witnesses" {
    if (contains("\"cached_leftmost_return_serials\"")) {
        try requireContains("\"find_found_key\":10");
        try requireContains("\"next_match_serials\":[0,2,6]");
        try requireContains("\"match_iterator_serials\":[0,2,6]");
        try requireContains("\"cached_leftmost_return_serials\":[0,-1,2,-1]");
        try requireContains("\"cached_root_transition_serials\":[0,0,4,2]");
    } else {
        try requireContains("\"find_found_key\":15");
        try requireContains("\"next_match_serials\":[0,2,4]");
        try requireContains("\"match_iterator_serials\":[0,2,4]");
    }
    try requireContains("\"find_missing\":true");
    try requireContains("\"find_first_serial\":0");
    try requireContains("\"next_match_terminal_null\":true");
}

test "phase1 rbtree fixture keeps bounded field roster" {
    try requireOrder("\"rbtree\"", "\"empty_root\"");
    try requireOrder("\"empty_root\"", "\"insert_order\"");
    try requireOrder("\"insert_order\"", "\"reverse_order\"");
    try requireOrder("\"reverse_order\"", "\"replace_order\"");
    try requireOrder("\"replace_order\"", "\"erase_init_order\"");
    try requireOrder("\"erase_init_order\"", "\"postorder_count\"");
    try requireOrder("\"postorder_count\"", "\"erase_init_node_empty\"");
    try requireOrder("\"erase_init_node_empty\"", "\"cleared_node_empty\"");
    try requireOrder("\"cleared_node_empty\"", "\"find_found_key\"");
    try requireOrder("\"find_found_key\"", "\"find_missing\"");
    try requireOrder("\"find_missing\"", "\"find_first_serial\"");
    try requireOrder("\"find_first_serial\"", "\"next_match_serials\"");
    try requireOrder("\"next_match_serials\"", "\"match_iterator_serials\"");
    if (contains("\"cached_leftmost_return_serials\"")) {
        try requireOrder("\"match_iterator_serials\"", "\"cached_leftmost_return_serials\"");
        try requireOrder("\"cached_leftmost_return_serials\"", "\"cached_root_transition_serials\"");
        try requireOrder("\"cached_root_transition_serials\"", "\"next_match_terminal_null\"");
    } else {
        try requireOrder("\"match_iterator_serials\"", "\"next_match_terminal_null\"");
    }
    try requireNotContains("\"rb_first_postorder_null\"");
    try requireNotContains("\"cached_root_empty_after_erase\"");
}

test "phase1 rbtree fixture keeps section placement" {
    try requireOrder("\"string\"", "\"rbtree\"");
    try requireOrder("\"rbtree\"", "\"argv_split\"");
    try requireOrder("\"bitmap\"", "\"string\"");
}
