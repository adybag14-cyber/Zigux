const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

test "lane06 bitmap replace aliases clamp partial tails and preserve masked merges" {
    const nbits = bitmap.bits_per_long + 5;
    const old = [_]bitmap.Word{
        0b10110,
        (@as(bitmap.Word, 1) << 1) |
            (@as(bitmap.Word, 1) << 4) |
            (@as(bitmap.Word, 1) << 9),
    };
    const new = [_]bitmap.Word{
        0b01001,
        (@as(bitmap.Word, 1) << 0) |
            (@as(bitmap.Word, 1) << 3) |
            (@as(bitmap.Word, 1) << 8),
    };
    const mask = [_]bitmap.Word{
        0b11100,
        (@as(bitmap.Word, 1) << 0) |
            (@as(bitmap.Word, 1) << 3) |
            (@as(bitmap.Word, 1) << 9),
    };

    var direct = [_]bitmap.Word{ 0, 0 };
    var alias = [_]bitmap.Word{ 0, 0 };
    bitmap.replace(&direct, &old, &new, &mask, nbits);
    bitmap.bitmap_replace(&alias, &old, &new, &mask, nbits);

    try std.testing.expectEqualSlices(bitmap.Word, &direct, &alias);
    try std.testing.expectEqual(
        @as(bitmap.Word, (old[0] & ~mask[0]) | (new[0] & mask[0])),
        direct[0],
    );
    try std.testing.expectEqual(
        (((old[1] & ~mask[1]) | (new[1] & mask[1])) & bitmap.lastWordMask(nbits)),
        direct[1],
    );
}

test "lane06 find_bit and aliases respect word boundaries and tail masks" {
    const nbits = find_bit.bits_per_long + 6;
    const lhs = [_]find_bit.Word{
        (@as(find_bit.Word, 1) << 7) | (@as(find_bit.Word, 1) << 12),
        (@as(find_bit.Word, 1) << 1) | (@as(find_bit.Word, 1) << 9),
    };
    const rhs = [_]find_bit.Word{
        (@as(find_bit.Word, 1) << 7) | (@as(find_bit.Word, 1) << 12),
        (@as(find_bit.Word, 1) << 4) | (@as(find_bit.Word, 1) << 9),
    };

    try std.testing.expectEqual(@as(usize, 7), find_bit.findNextAndBit(&lhs, &rhs, nbits, 0));
    try std.testing.expectEqual(@as(usize, 12), find_bit.findNextAndBit(&lhs, &rhs, nbits, 8));
    try std.testing.expectEqual(
        @as(usize, nbits),
        find_bit.findNextAndBit(&lhs, &rhs, nbits, find_bit.bits_per_long + 2),
    );
    try std.testing.expectEqual(
        @as(usize, nbits),
        find_bit.find_next_and_bit(&lhs, &rhs, nbits, find_bit.bits_per_long + 2),
    );
    try std.testing.expectEqual(@as(usize, nbits), find_bit.findNextAndBit(&lhs, &rhs, nbits, find_bit.bits_per_long + 5));
}

test "lane06 string bool and memparse helpers keep Linux-style truth and signed suffix parsing" {
    try std.testing.expect(try string.strtobool("On"));
    try std.testing.expect(!(try string.strtobool("off")));
    try std.testing.expectError(error.Invalid, string.strtobool(null));
    try std.testing.expectError(error.Invalid, string.strtobool(""));

    const signed = string.memparse("-2K trailing");
    try std.testing.expectEqual(@as(u64, @bitCast(@as(i64, -2048))), signed.value);
    try std.testing.expectEqualStrings(" trailing", signed.rest);

    const saturated = string.memparse("+9223372036854775808");
    try std.testing.expectEqual(@as(u64, @intCast(std.math.maxInt(i64))), saturated.value);
}

test "lane06 rbtree cached find-add helpers keep duplicate and miss semantics aligned" {
    const Entry = struct {
        key: i32,
        serial: usize,
        node: rbtree.Node = rbtree.Node.init(),
    };

    const less = struct {
        fn compare(lhs: *const rbtree.Node, rhs: *const rbtree.Node) bool {
            const lhs_entry: *const Entry = @fieldParentPtr("node", lhs);
            const rhs_entry: *const Entry = @fieldParentPtr("node", rhs);
            if (lhs_entry.key != rhs_entry.key) return lhs_entry.key < rhs_entry.key;
            return lhs_entry.serial < rhs_entry.serial;
        }
    }.compare;

    const cmp_node = struct {
        fn compare(lhs: *const rbtree.Node, rhs: *const rbtree.Node) i32 {
            const lhs_entry: *const Entry = @fieldParentPtr("node", lhs);
            const rhs_entry: *const Entry = @fieldParentPtr("node", rhs);
            if (lhs_entry.key < rhs_entry.key) return -1;
            if (lhs_entry.key > rhs_entry.key) return 1;
            return 0;
        }
    }.compare;

    const cmp_key = struct {
        fn compare(key: *const anyopaque, node: *const rbtree.Node) i32 {
            const wanted: *const i32 = @ptrCast(@alignCast(key));
            const entry: *const Entry = @fieldParentPtr("node", node);
            if (wanted.* < entry.key) return -1;
            if (wanted.* > entry.key) return 1;
            return 0;
        }
    }.compare;

    var primary_entries = [_]Entry{
        .{ .key = 10, .serial = 0 },
        .{ .key = 5, .serial = 1 },
        .{ .key = 15, .serial = 2 },
    };
    var alias_entries = [_]Entry{
        .{ .key = 10, .serial = 0 },
        .{ .key = 5, .serial = 1 },
        .{ .key = 15, .serial = 2 },
    };
    var primary_root = rbtree.RootCached.init();
    var alias_root = rbtree.RootCached.init();

    for (&primary_entries, &alias_entries) |*primary_entry, *alias_entry| {
        _ = rbtree.addCached(&primary_entry.node, &primary_root, less);
        _ = rbtree.addCached(&alias_entry.node, &alias_root, less);
    }

    var primary_new = Entry{ .key = 12, .serial = 3 };
    var alias_new = Entry{ .key = 12, .serial = 3 };
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.findAddCached(&primary_new.node, &primary_root, cmp_node));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.rb_find_add_cached(&alias_new.node, &alias_root, cmp_node));

    var primary_dup = Entry{ .key = 10, .serial = 4 };
    var alias_dup = Entry{ .key = 10, .serial = 4 };
    const primary_existing = rbtree.findAddCached(&primary_dup.node, &primary_root, cmp_node) orelse return error.TestUnexpectedResult;
    const alias_existing = rbtree.rb_find_add_cached(&alias_dup.node, &alias_root, cmp_node) orelse return error.TestUnexpectedResult;
    const primary_existing_entry: *const Entry = @fieldParentPtr("node", primary_existing);
    const alias_existing_entry: *const Entry = @fieldParentPtr("node", alias_existing);
    try std.testing.expectEqual(primary_existing_entry.key, alias_existing_entry.key);
    try std.testing.expectEqual(primary_existing_entry.serial, alias_existing_entry.serial);

    const wanted: i32 = 10;
    const primary_found = rbtree.find(&wanted, &primary_root.root, cmp_key) orelse return error.TestUnexpectedResult;
    const alias_found = rbtree.find(&wanted, &alias_root.root, cmp_key) orelse return error.TestUnexpectedResult;
    const primary_first = rbtree.findFirst(&wanted, &primary_root.root, cmp_key) orelse return error.TestUnexpectedResult;
    const alias_first = rbtree.findFirst(&wanted, &alias_root.root, cmp_key) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(*rbtree.Node, primary_first), primary_found);
    try std.testing.expectEqual(@as(*rbtree.Node, alias_first), alias_found);
    try std.testing.expectEqual(@as(?*rbtree.Node, &primary_entries[1].node), rbtree.firstCached(&primary_root));
    try std.testing.expectEqual(@as(?*rbtree.Node, &alias_entries[1].node), rbtree.firstCached(&alias_root));

    const missing: i32 = 17;
    try std.testing.expect(rbtree.find(&missing, &primary_root.root, cmp_key) == null);
    try std.testing.expect(rbtree.find(&missing, &alias_root.root, cmp_key) == null);
}
