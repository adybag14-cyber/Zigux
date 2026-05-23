const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

test "lane06 bitmap or helpers keep alias parity across a masked tail" {
    const nbits = bitmap.bits_per_long + 6;
    const lhs = [_]bitmap.Word{ 0b1010, (@as(bitmap.Word, 1) << 1) | (@as(bitmap.Word, 1) << 8) };
    const rhs = [_]bitmap.Word{ 0b0101, (@as(bitmap.Word, 1) << 4) | (@as(bitmap.Word, 1) << 9) };
    var direct_or = [_]bitmap.Word{ 0, 0 };
    var alias_or = [_]bitmap.Word{ 0, 0 };

    bitmap.orBits(&direct_or, &lhs, &rhs, nbits);
    bitmap.bitmap_or(&alias_or, &lhs, &rhs, nbits);
    try std.testing.expectEqualSlices(bitmap.Word, &direct_or, &alias_or);
    try std.testing.expectEqual(@as(bitmap.Word, 0b1111), direct_or[0]);
    try std.testing.expectEqual(@as(bitmap.Word, (@as(bitmap.Word, 1) << 1) | (@as(bitmap.Word, 1) << 4) | (@as(bitmap.Word, 1) << 8) | (@as(bitmap.Word, 1) << 9)), direct_or[1]);
    try std.testing.expectEqual(@as(usize, 6), bitmap.weight(&direct_or, nbits));

    var weighted_direct = [_]bitmap.Word{ 0, 0 };
    var weighted_alias = [_]bitmap.Word{ 0, 0 };
    const direct_weight = bitmap.weightedOr(&weighted_direct, &lhs, &rhs, nbits);
    const alias_weight = bitmap.bitmap_weighted_or(&weighted_alias, &lhs, &rhs, nbits);
    try std.testing.expectEqual(@as(usize, 6), direct_weight);
    try std.testing.expectEqual(direct_weight, alias_weight);
    try std.testing.expectEqualSlices(bitmap.Word, &weighted_direct, &weighted_alias);
}

test "lane06 find_bit and-tail aliases keep inclusive tail-boundary scans reachable" {
    const tail_bits: usize = 6;
    const boundary = find_bit.bits_per_long + tail_bits - 1;
    const nbits = boundary + 1;
    const lhs = [_]find_bit.Word{
        0,
        (@as(find_bit.Word, 1) << 1) | (@as(find_bit.Word, 1) << @intCast(tail_bits - 1)) | (@as(find_bit.Word, 1) << @intCast(tail_bits + 2)),
    };
    const rhs = [_]find_bit.Word{
        0,
        (@as(find_bit.Word, 1) << 1) | (@as(find_bit.Word, 1) << @intCast(tail_bits - 1)),
    };

    try std.testing.expectEqual(@as(usize, boundary), find_bit.findNextAndBit(&lhs, &rhs, nbits, boundary));
    try std.testing.expectEqual(@as(usize, boundary), find_bit.find_next_and_bit(&lhs, &rhs, nbits, boundary));
    try std.testing.expectEqual(@as(usize, boundary), find_bit._find_next_and_bit(&lhs, &rhs, nbits, boundary));
    try std.testing.expectEqual(@as(usize, nbits), find_bit.findNextAndBit(&lhs, &rhs, nbits, boundary + 1));
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 1), find_bit.findFirstAndBit(&lhs, &rhs, nbits));
}

test "lane06 string charset helpers honor c-string boundaries and ordering" {
    const sysfs = [_][]const u8{ "off", "auto\n", "on" };
    const plain = [_][]const u8{ "blue", "green", "red" };

    try std.testing.expectEqual(@as(?usize, 1), string.sysfsMatchString(sysfs[0..], "auto"));
    try std.testing.expectEqual(@as(?usize, 1), string.matchString(plain[0..], "green"));
    try std.testing.expectEqual(@as(usize, 3), string.strHasPrefix("kernel", "ker"));
    try std.testing.expect(string.strstarts("kernel", "ker"));
    try std.testing.expect(string.strEndsWith("kernel", "nel"));
    try std.testing.expectEqual(@as(?usize, 3), string.strnchr("kernel", 6, 'n'));
}

test "lane06 rbtree prev aliases walk reverse order after cached duplicate probing" {
    const Entry = struct {
        key: i32,
        serial: usize,
        node: rbtree.Node = rbtree.Node.init(),
    };

    const less = struct {
        fn compare(lhs: *const rbtree.Node, rhs: *const rbtree.Node) bool {
            const lhs_entry: *const Entry = @fieldParentPtr("node", lhs);
            const rhs_entry: *const Entry = @fieldParentPtr("node", rhs);
            if (lhs_entry.key != rhs_entry.key) {
                return lhs_entry.key < rhs_entry.key;
            }
            return lhs_entry.serial < rhs_entry.serial;
        }
    }.compare;

    const cmp = struct {
        fn compare(lhs: *const rbtree.Node, rhs: *const rbtree.Node) i32 {
            const lhs_entry: *const Entry = @fieldParentPtr("node", lhs);
            const rhs_entry: *const Entry = @fieldParentPtr("node", rhs);
            if (lhs_entry.key < rhs_entry.key) return -1;
            if (lhs_entry.key > rhs_entry.key) return 1;
            return 0;
        }
    }.compare;

    var entries = [_]Entry{
        .{ .key = 10, .serial = 0 },
        .{ .key = 5, .serial = 1 },
        .{ .key = 20, .serial = 2 },
        .{ .key = 15, .serial = 3 },
    };
    var duplicate = Entry{ .key = 10, .serial = 4 };
    var root = rbtree.RootCached.init();

    for (&entries) |*entry| {
        _ = rbtree.addCached(&entry.node, &root, less);
    }

    const existing = rbtree.findAddCached(&duplicate.node, &root, cmp) orelse return error.TestUnexpectedResult;
    const existing_entry: *const Entry = @fieldParentPtr("node", existing);
    try std.testing.expectEqual(@as(i32, 10), existing_entry.key);
    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[1].node), rbtree.firstCached(&root));

    var order: [4]i32 = undefined;
    var count: usize = 0;
    var current = rbtree.last(&root.root);
    while (current) |node| : (current = rbtree.prev(node)) {
        const entry: *const Entry = @fieldParentPtr("node", node);
        order[count] = entry.key;
        count += 1;
    }

    try std.testing.expectEqual(@as(usize, 4), count);
    try std.testing.expectEqualSlices(i32, &[_]i32{ 20, 15, 10, 5 }, order[0..count]);
    try std.testing.expectEqual(rbtree.prev(rbtree.last(&root.root).?), rbtree.rb_prev(rbtree.rb_last(&root.root).?));
}
