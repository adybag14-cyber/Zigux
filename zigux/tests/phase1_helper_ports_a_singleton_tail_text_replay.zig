const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const rbtree = @import("rbtree");
const string = @import("string");

test "bitmap masked replacement feeds tail-clamped find-bit scans" {
    const W = bitmap.Word;
    const nbits = bitmap.bits_per_long + 9;
    var old = [_]W{
        (@as(W, 1) << 2) | (@as(W, 1) << 8),
        (@as(W, 1) << 2) | (@as(W, 1) << 11),
    };
    var new = [_]W{
        (@as(W, 1) << 5) | (@as(W, 1) << 8),
        (@as(W, 1) << 4) | (@as(W, 1) << 12),
    };
    var mask = [_]W{
        (@as(W, 1) << 2) | (@as(W, 1) << 5),
        (@as(W, 1) << 2) | (@as(W, 1) << 4) | (@as(W, 1) << 12),
    };
    var dst = [_]W{ 0, ~@as(W, 0) };

    bitmap.bitmap_replace(&dst, &old, &new, &mask, nbits);

    try std.testing.expectEqual(@as(usize, 5), find_bit.findFirstBit(&dst, nbits));
    try std.testing.expectEqual(@as(usize, 8), find_bit.findNextBit(&dst, nbits, 6));
    try std.testing.expectEqual(@as(usize, bitmap.bits_per_long + 4), find_bit.findNextBit(&dst, nbits, bitmap.bits_per_long));
    try std.testing.expectEqual(@as(usize, bitmap.bits_per_long + 4), find_bit.findLastBit(&dst, nbits));
    try std.testing.expectEqual(@as(usize, nbits), find_bit.findNextBit(&dst, nbits, bitmap.bits_per_long + 5));
}

test "string bounded search keeps sysfs and plain matching distinct" {
    var token = [_]u8{ ' ', 'z', 'i', 'g', 'u', 'x', ' ', 0, 'x' };
    const trimmed = string.strim(&token);
    try std.testing.expectEqualStrings("zigux", trimmed);
    try std.testing.expectEqual(@as(usize, 2), string.strnchr(trimmed, trimmed.len, 'g').?);
    try std.testing.expect(string.strnchr(trimmed, 2, 'g') == null);

    const table = [_][]const u8{ "host", "zigux", "phase1\n", "helper" };
    try std.testing.expectEqual(@as(?usize, 2), string.sysfsMatchString(&table, "phase1"));
    try std.testing.expectEqual(@as(?usize, null), string.matchString(&table, "phase1"));
    try std.testing.expect(string.strEndsWith("tools/lib/rbtree.zig", "rbtree.zig"));
}

test "rbtree singleton erase and cached leftmost transitions stay aligned" {
    const Entry = struct {
        key: i32,
        node: rbtree.Node = rbtree.Node.init(),
    };

    const less = struct {
        fn compare(lhs: *const rbtree.Node, rhs: *const rbtree.Node) bool {
            const lhs_entry: *const Entry = @fieldParentPtr("node", lhs);
            const rhs_entry: *const Entry = @fieldParentPtr("node", rhs);
            return lhs_entry.key < rhs_entry.key;
        }
    }.compare;

    var singleton = Entry{ .key = 7 };
    var cached_root = rbtree.RootCached.init();
    try std.testing.expectEqual(@as(?*rbtree.Node, &singleton.node), rbtree.addCached(&singleton.node, &cached_root, less));
    try std.testing.expectEqual(@as(?*rbtree.Node, &singleton.node), rbtree.firstCached(&cached_root));
    try std.testing.expect(rbtree.eraseCached(&singleton.node, &cached_root) == null);
    try std.testing.expect(cached_root.root.node == null);
    try std.testing.expect(rbtree.firstCached(&cached_root) == null);

    var entries = [_]Entry{
        .{ .key = 10 },
        .{ .key = 5 },
        .{ .key = 15 },
    };
    cached_root = rbtree.RootCached.init();
    for (&entries) |*entry| {
        _ = rbtree.addCached(&entry.node, &cached_root, less);
    }

    rbtree.eraseInitCached(&entries[1].node, &cached_root);
    try std.testing.expect(rbtree.emptyNode(&entries[1].node));
    try std.testing.expectEqual(rbtree.first(&cached_root.root), rbtree.firstCached(&cached_root));

    var order: [2]i32 = undefined;
    var count: usize = 0;
    var current = rbtree.first(&cached_root.root);
    while (current) |node| : (current = rbtree.next(node)) {
        const entry: *const Entry = @fieldParentPtr("node", node);
        order[count] = entry.key;
        count += 1;
    }

    try std.testing.expectEqualSlices(i32, &[_]i32{ 10, 15 }, order[0..count]);
}
