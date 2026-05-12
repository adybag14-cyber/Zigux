const std = @import("std");
const rbtree = @import("rbtree");

const Fixture = struct {
    rbtree: struct {
        empty_root: bool,
        insert_order: []const i32,
        reverse_order: []const i32,
        replace_order: []const i32,
        erase_init_order: []const i32,
        postorder_count: usize,
        erase_init_node_empty: bool,
        cleared_node_empty: bool,
        find_found_key: i32,
        find_missing: bool,
        find_first_serial: usize,
        next_match_serials: []const usize,
        match_iterator_serials: []const usize,
        next_match_terminal_null: bool,
    },
};

fn loadFixture(allocator: std.mem.Allocator) !std.json.Parsed(Fixture) {
    return std.json.parseFromSlice(Fixture, allocator, @embedFile("fixtures/phase1_helpers.json"), .{
        .ignore_unknown_fields = true,
    });
}

test "phase 1 helper ports match committed parity fixture" {
    var parsed = try loadFixture(std.testing.allocator);
    defer parsed.deinit();
    const fixture = parsed.value;

    const SearchEntry = struct {
        key: i32,
        serial: usize,
        node: rbtree.Node = rbtree.Node.init(),
    };

    const searchLess = struct {
        fn compare(lhs: *const rbtree.Node, rhs: *const rbtree.Node) bool {
            const lhs_entry: *const SearchEntry = @fieldParentPtr("node", lhs);
            const rhs_entry: *const SearchEntry = @fieldParentPtr("node", rhs);
            if (lhs_entry.key != rhs_entry.key) {
                return lhs_entry.key < rhs_entry.key;
            }
            return lhs_entry.serial < rhs_entry.serial;
        }
    }.compare;

    const searchCmp = struct {
        fn compare(key: *const anyopaque, node: *const rbtree.Node) i32 {
            const wanted: *const i32 = @ptrCast(@alignCast(key));
            const entry: *const SearchEntry = @fieldParentPtr("node", node);
            if (wanted.* < entry.key) return -1;
            if (wanted.* > entry.key) return 1;
            return 0;
        }
    }.compare;

    var search_entries = [_]SearchEntry{
        .{ .key = 10, .serial = 0 },
        .{ .key = 5, .serial = 1 },
        .{ .key = 10, .serial = 2 },
        .{ .key = 20, .serial = 3 },
        .{ .key = 10, .serial = 4 },
        .{ .key = 15, .serial = 5 },
    };
    var search_root = rbtree.Root.init();
    for (&search_entries) |*entry| {
        rbtree.add(&entry.node, &search_root, searchLess);
    }

    const duplicate_wanted = @as(i32, 10);
    const first_match = rbtree.findFirst(&duplicate_wanted, &search_root, searchCmp) orelse return error.TestUnexpectedResult;
    const first_match_entry: *const SearchEntry = @fieldParentPtr("node", first_match);
    try std.testing.expectEqual(fixture.rbtree.find_first_serial, first_match_entry.serial);

    var next_match_serials: [3]usize = undefined;
    var next_match_count: usize = 0;
    var match_cursor = first_match;
    while (true) {
        const entry: *const SearchEntry = @fieldParentPtr("node", match_cursor);
        next_match_serials[next_match_count] = entry.serial;
        next_match_count += 1;
        match_cursor = rbtree.nextMatch(&duplicate_wanted, match_cursor, searchCmp) orelse break;
    }
    try std.testing.expectEqualSlices(usize, fixture.rbtree.next_match_serials, next_match_serials[0..next_match_count]);
    try std.testing.expectEqual(
        fixture.rbtree.next_match_terminal_null,
        rbtree.nextMatch(&duplicate_wanted, match_cursor, searchCmp) == null,
    );

    var iter = rbtree.matchIterator(&duplicate_wanted, &search_root, searchCmp);
    var match_iterator_serials: [3]usize = undefined;
    var match_iterator_count: usize = 0;
    while (iter.next()) |node| {
        const entry: *const SearchEntry = @fieldParentPtr("node", node);
        match_iterator_serials[match_iterator_count] = entry.serial;
        match_iterator_count += 1;
    }
    try std.testing.expectEqualSlices(
        usize,
        fixture.rbtree.match_iterator_serials,
        match_iterator_serials[0..match_iterator_count],
    );
}
