const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

const Word = bitmap.Word;

test "masked bitmap tails line up with last-bit and clump scans" {
    const nbits = bitmap.bits_per_long + 13;
    const tail_bit = bitmap.bits_per_long + 11;
    const out_of_range_bit = bitmap.bits_per_long + 20;
    var old = [_]Word{ 0, 0 };
    var new = [_]Word{ 0, 0 };
    var mask = [_]Word{ 0, 0 };
    var dst = [_]Word{ 0, 0 };

    old[0] = (@as(Word, 1) << 3) | (@as(Word, 1) << 17);
    old[1] = @as(Word, 1) << @intCast(out_of_range_bit - bitmap.bits_per_long);
    new[0] = @as(Word, 1) << 5;
    new[1] = (@as(Word, 1) << @intCast(tail_bit - bitmap.bits_per_long)) |
        (@as(Word, 1) << @intCast(out_of_range_bit - bitmap.bits_per_long));
    mask[0] = (@as(Word, 1) << 3) | (@as(Word, 1) << 5);
    mask[1] = ~@as(Word, 0);

    bitmap.replace(&dst, &old, &new, &mask, nbits);

    try std.testing.expectEqual(@as(usize, 3), bitmap.weight(&dst, nbits));
    try std.testing.expectEqual(@as(usize, 5), find_bit.findFirstBit(&dst, nbits));
    try std.testing.expectEqual(tail_bit, find_bit.findLastBit(&dst, nbits));
    try std.testing.expectEqual(nbits, find_bit.findNextBit(&dst, nbits, tail_bit + 1));
    try std.testing.expectEqual(@as(Word, 0), dst[1] & ~bitmap.lastWordMask(nbits));

    var clump: u8 = 0;
    try std.testing.expectEqual(@as(usize, 0), find_bit.findNextClump8(&clump, &dst, nbits, 0));
    try std.testing.expectEqual(@as(u8, 0x20), clump);
    try std.testing.expectEqual(@as(usize, 16), find_bit.findNextClump8(&clump, &dst, nbits, 8));
    try std.testing.expectEqual(@as(u8, 0x02), clump);
    try std.testing.expectEqual(bitmap.bits_per_long + 8, find_bit.findNextClump8(&clump, &dst, nbits, bitmap.bits_per_long));
    try std.testing.expectEqual(@as(u8, 0x08), clump);
}

test "sysfs matching and bounded searches stop at C-string boundaries" {
    const modes = [_][]const u8{
        "disabled\n",
        "masked-last\n",
        "cached-replace\n",
    };

    try std.testing.expectEqual(@as(?usize, 1), string.sysfsMatchString(&modes, "masked-last"));
    try std.testing.expectEqual(@as(?usize, 2), string.sysfsMatchString(&modes, "cached-replace\n"));
    try std.testing.expectEqual(@as(?usize, null), string.matchString(&modes, "masked-last"));

    const c_text = [_]u8{ 'x', 'y', 0, 'z', 'y' };
    try std.testing.expectEqual(@as(?usize, 1), string.strnchr(&c_text, c_text.len, 'y'));
    try std.testing.expectEqual(@as(?usize, null), string.strnchr(&c_text, c_text.len, 'z'));
    try std.testing.expectEqual(@as(?usize, 2), string.strnchr(&c_text, c_text.len, 0));
    try std.testing.expectEqual(@as(?usize, 4), string.memchrInv("aaaaXaaa", 'a'));
    try std.testing.expectEqual(@as(?usize, null), string.memchrInv("aaaaaaaa", 'a'));
}

test "cached rb replacement preserves leftmost and iterator order" {
    const Entry = struct {
        key: i32,
        serial: usize,
        node: rbtree.Node = rbtree.Node.init(),
    };

    const less = struct {
        fn compare(lhs: *const rbtree.Node, rhs: *const rbtree.Node) bool {
            const lhs_entry: *const Entry = @fieldParentPtr("node", lhs);
            const rhs_entry: *const Entry = @fieldParentPtr("node", rhs);
            return if (lhs_entry.key == rhs_entry.key)
                lhs_entry.serial < rhs_entry.serial
            else
                lhs_entry.key < rhs_entry.key;
        }
    }.compare;

    const cmp_key = struct {
        fn compare(key_ptr: *const anyopaque, node: *const rbtree.Node) i32 {
            const key: *const i32 = @ptrCast(@alignCast(key_ptr));
            const entry: *const Entry = @fieldParentPtr("node", node);
            if (key.* < entry.key) return -1;
            if (key.* > entry.key) return 1;
            return 0;
        }
    }.compare;

    var entries = [_]Entry{
        .{ .key = 8, .serial = 0 },
        .{ .key = 4, .serial = 1 },
        .{ .key = 4, .serial = 2 },
        .{ .key = 12, .serial = 3 },
    };
    var replacement = Entry{ .key = 4, .serial = 9 };
    var root = rbtree.RootCached.init();

    for (&entries) |*entry| {
        _ = rbtree.addCached(&entry.node, &root, less);
    }

    try std.testing.expect(root.leftmost == &entries[1].node);
    rbtree.replaceNodeCached(&entries[1].node, &replacement.node, &root);
    try std.testing.expect(root.leftmost == &replacement.node);

    var key: i32 = 4;
    var iter = rbtree.matchIterator(&key, &root.root, cmp_key);
    const first = iter.next().?;
    const second = iter.next().?;

    const first_entry: *const Entry = @fieldParentPtr("node", first);
    const second_entry: *const Entry = @fieldParentPtr("node", second);
    try std.testing.expectEqual(@as(usize, 9), first_entry.serial);
    try std.testing.expectEqual(@as(usize, 2), second_entry.serial);
    try std.testing.expectEqual(@as(?*rbtree.Node, null), iter.next());

    _ = rbtree.eraseCached(&replacement.node, &root);
    try std.testing.expect(root.leftmost == &entries[2].node);
}
