const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const rbtree = @import("rbtree");
const string = @import("string");

const Word = bitmap.Word;

const Entry = struct {
    key: usize,
    serial: usize,
    label: []const u8,
    node: rbtree.Node = rbtree.Node.init(),
};

fn lessByKeyThenSerial(lhs_node: *const rbtree.Node, rhs_node: *const rbtree.Node) bool {
    const lhs: *const Entry = @fieldParentPtr("node", lhs_node);
    const rhs: *const Entry = @fieldParentPtr("node", rhs_node);
    if (lhs.key != rhs.key) {
        return lhs.key < rhs.key;
    }
    return lhs.serial < rhs.serial;
}

fn cmpKey(key: *const anyopaque, node: *const rbtree.Node) i32 {
    const wanted: *const usize = @ptrCast(@alignCast(key));
    const entry: *const Entry = @fieldParentPtr("node", node);
    if (wanted.* < entry.key) return -1;
    if (wanted.* > entry.key) return 1;
    return 0;
}

fn renderRange(map: []const Word, nbits: usize, buffer: []u8) []const u8 {
    const len = bitmap.scnprintf(map, nbits, buffer);
    return buffer[0..len];
}

test "bitmap range output feeds string token lookup" {
    const nbits = bitmap.bits_per_long + 9;
    var map = [_]Word{ 0, 0 };
    bitmap.setRange(&map, 1, 3);
    bitmap.setRange(&map, bitmap.bits_per_long - 1, 3);
    bitmap.setRange(&map, bitmap.bits_per_long + 7, 1);

    try std.testing.expectEqual(@as(usize, 1), find_bit.findFirstBit(&map, nbits));
    try std.testing.expectEqual(@as(usize, bitmap.bits_per_long - 1), find_bit.findNextBit(&map, nbits, 4));
    try std.testing.expectEqual(@as(usize, bitmap.bits_per_long + 7), find_bit.findNextBit(&map, nbits, bitmap.bits_per_long + 2));

    var rendered: [80]u8 = undefined;
    const text = renderRange(&map, nbits, &rendered);
    var expected: [80]u8 = undefined;
    const expected_text = try std.fmt.bufPrint(
        &expected,
        "1-3,{d}-{d},{d}",
        .{ bitmap.bits_per_long - 1, bitmap.bits_per_long + 1, bitmap.bits_per_long + 7 },
    );
    try std.testing.expectEqualStrings(expected_text, text);

    const haystack = [_][]const u8{ "missing", text, "1-2", "tail\n" };
    try std.testing.expectEqual(@as(?usize, 1), string.matchString(&haystack, expected_text));
    try std.testing.expectEqual(@as(?usize, null), string.matchString(&haystack, "1-3"));
    try std.testing.expectEqual(@as(?usize, 3), string.sysfs_match_string(&haystack, "tail"));
}

test "rbtree cached order follows bitmap first-bit keys and range labels" {
    const nbits = bitmap.bits_per_long * 2;
    var low_map = [_]Word{ 0, 0 };
    var mid_map = [_]Word{ 0, 0 };
    var high_map = [_]Word{ 0, 0 };

    bitmap.setRange(&mid_map, 9, 2);
    bitmap.setRange(&low_map, 2, 1);
    bitmap.setRange(&high_map, bitmap.bits_per_long + 4, 3);

    var low_label_buffer: [32]u8 = undefined;
    var mid_label_buffer: [32]u8 = undefined;
    var high_label_buffer: [32]u8 = undefined;
    const low_label = renderRange(&low_map, nbits, &low_label_buffer);
    const mid_label = renderRange(&mid_map, nbits, &mid_label_buffer);
    const high_label = renderRange(&high_map, nbits, &high_label_buffer);

    var entries = [_]Entry{
        .{ .key = find_bit.findFirstBit(&mid_map, nbits), .serial = 1, .label = mid_label },
        .{ .key = find_bit.findFirstBit(&low_map, nbits), .serial = 0, .label = low_label },
        .{ .key = find_bit.findFirstBit(&high_map, nbits), .serial = 2, .label = high_label },
    };
    var root = rbtree.RootCached.init();

    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[0].node), rbtree.addCached(&entries[0].node, &root, lessByKeyThenSerial));
    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[1].node), rbtree.addCached(&entries[1].node, &root, lessByKeyThenSerial));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.addCached(&entries[2].node, &root, lessByKeyThenSerial));
    try std.testing.expectEqual(rbtree.first(&root.root), rbtree.firstCached(&root));

    var labels: [3][]const u8 = undefined;
    var count: usize = 0;
    var cursor = rbtree.firstCached(&root);
    while (cursor) |node| : (cursor = rbtree.next(node)) {
        const entry: *const Entry = @fieldParentPtr("node", node);
        labels[count] = entry.label;
        count += 1;
    }

    var expected_high: [32]u8 = undefined;
    const expected_high_label = try std.fmt.bufPrint(&expected_high, "{d}-{d}", .{ bitmap.bits_per_long + 4, bitmap.bits_per_long + 6 });
    try std.testing.expectEqual(@as(usize, 3), count);
    try std.testing.expectEqualStrings("2", labels[0]);
    try std.testing.expectEqualStrings("9-10", labels[1]);
    try std.testing.expectEqualStrings(expected_high_label, labels[2]);

    const wanted = @as(usize, 9);
    const found = rbtree.find(&wanted, &root.root, cmpKey) orelse return error.TestUnexpectedResult;
    const found_entry: *const Entry = @fieldParentPtr("node", found);
    try std.testing.expectEqualStrings("9-10", found_entry.label);
}

test "range truncation keeps partial tokens from matching complete strings" {
    var map = [_]Word{0};
    bitmap.setRange(&map, 1, 3);
    bitmap.setRange(&map, 7, 1);

    var truncated = [_]u8{ 0xaa, 0xaa, 0xaa, 0xaa };
    const short_text = renderRange(&map, 16, &truncated);
    try std.testing.expectEqualStrings("1-3", short_text);
    try std.testing.expectEqual(@as(u8, 0), truncated[short_text.len]);

    const complete = "1-3,7";
    const haystack = [_][]const u8{ short_text, complete };
    try std.testing.expectEqual(@as(?usize, 0), string.match_string(&haystack, short_text));
    try std.testing.expectEqual(@as(?usize, 1), string.match_string(&haystack, complete));
    try std.testing.expectEqual(@as(?usize, null), string.match_string(haystack[0..1], complete));
}
