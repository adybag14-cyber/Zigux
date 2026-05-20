const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

const Word = bitmap.Word;
const bits_per_long = bitmap.bits_per_long;

const Entry = struct {
    key: i32,
    node: rbtree.Node = .{},

    fn init(key: i32) Entry {
        return .{ .key = key };
    }
};

fn entryFromNode(node: *const rbtree.Node) *const Entry {
    return @fieldParentPtr("node", node);
}

fn less(lhs: *const rbtree.Node, rhs: *const rbtree.Node) bool {
    return entryFromNode(lhs).key < entryFromNode(rhs).key;
}

fn cmpKey(key_ptr: *const anyopaque, node: *const rbtree.Node) i32 {
    const key: *const i32 = @ptrCast(@alignCast(key_ptr));
    const node_key = entryFromNode(node).key;
    return if (key.* < node_key) -1 else if (key.* > node_key) 1 else 0;
}

test "helper ports A replay keeps bitmap allocation and zero-full transitions aligned" {
    const allocator = std.testing.allocator;
    const nbits = bits_per_long + 6;

    var maybe_words = try bitmap.bitmap_zalloc(allocator, nbits);
    try std.testing.expect(maybe_words != null);
    const words = maybe_words.?;

    try std.testing.expect(bitmap.empty(words, nbits));
    try std.testing.expectEqual(@as(usize, 0), bitmap.weight(words, nbits));

    bitmap.fill(words, nbits);
    try std.testing.expect(bitmap.full(words, nbits));
    try std.testing.expectEqual(nbits, bitmap.weight(words, nbits));

    bitmap.clearRange(words, bits_per_long - 1, 3);
    try std.testing.expect(!bitmap.full(words, nbits));
    try std.testing.expectEqual(bits_per_long - 1, find_bit.findFirstZeroBit(words, nbits));
    try std.testing.expectEqual(bits_per_long, find_bit.findNextZeroBit(words, nbits, bits_per_long));

    bitmap.setRange(words, bits_per_long, 2);
    try std.testing.expectEqual(bits_per_long - 1, find_bit.findFirstZeroBit(words, nbits));
    try std.testing.expectEqual(nbits - 1, find_bit.findLastBit(words, nbits));

    bitmap.zero(words, nbits);
    try std.testing.expect(bitmap.empty(words, nbits));
    try std.testing.expectEqual(nbits, find_bit.findFirstBit(words, nbits));

    bitmap.bitmap_free(allocator, &maybe_words);
    try std.testing.expect(maybe_words == null);
}

test "helper ports A replay keeps clump scans pinned to aligned bytes across words" {
    const nbits = bits_per_long + 16;
    const cross_word_offset = bits_per_long - 8;

    var words = [_]Word{ 0, 0 };
    words[0] |= @as(Word, 0xa5) << @intCast(cross_word_offset);
    words[1] |= 0x1d;

    try std.testing.expectEqual(@as(u8, 0xa5), find_bit.getValue8(&words, cross_word_offset));
    try std.testing.expectEqual(@as(u8, 0x1d), find_bit.getValue8(&words, bits_per_long));

    var clump: u8 = 0;
    try std.testing.expectEqual(cross_word_offset, find_bit.findFirstClump8(&clump, &words, nbits));
    try std.testing.expectEqual(@as(u8, 0xa5), clump);

    clump = 0;
    try std.testing.expectEqual(cross_word_offset, find_bit.findNextClump8(&clump, &words, nbits, cross_word_offset + 1));
    try std.testing.expectEqual(@as(u8, 0xa5), clump);

    clump = 0;
    try std.testing.expectEqual(bits_per_long, find_bit._find_next_clump8(&clump, &words, nbits, bits_per_long));
    try std.testing.expectEqual(@as(u8, 0x1d), clump);
}

test "helper ports A replay keeps string copy and path helpers pinned to C-string boundaries" {
    const src_cstr = [_]u8{ ' ', 'o', 'k', ' ', 0, 'x' };
    var padded = [_]u8{0xaa} ** 8;
    try std.testing.expectEqual(@as(isize, 4), string.strscpyPad(&padded, &src_cstr));
    try std.testing.expectEqualStrings("ok", string.strim(padded[0..]));

    var removed = [_]u8{ 'a', ' ', 'b', ' ', 0, 'x' };
    try std.testing.expectEqualStrings("ab", string.removeSpaces(removed[0..]));
    try std.testing.expectEqual(@as(usize, 2), string.strreplace(removed[0..], 'b', 'z'));
    try std.testing.expectEqualStrings("az", removed[0..2]);

    const sysfs_lhs = [_]u8{ 'v', 'a', 'l', '\n', 0, 'x' };
    const sysfs_rhs = [_]u8{ 'v', 'a', 'l', 0, 'y' };
    try std.testing.expect(string.sysfsStreq(&sysfs_lhs, &sysfs_rhs));

    const slashy = [_]u8{ 'a', '/', 'b', '/', 'c', 0, 'x' };
    try std.testing.expectEqual(@as(?usize, 1), string.strnchr(&slashy, 5, '/'));
    try std.testing.expectEqual(@as(?usize, 1), string.strnchr(slashy[2..], 3, '/'));
    try std.testing.expect(string.strEndsWith(&slashy, "/c"));
    try std.testing.expectEqual(@as(?usize, 4), string.memchrInv(&[_]u8{ 'x', 'x', 'x', 'x', 'y' }, 'x'));
}

test "helper ports A replay keeps cached erase-init and neighbor walks stable" {
    var root = rbtree.RootCached.init();
    var entries = [_]Entry{
        Entry.init(4),
        Entry.init(2),
        Entry.init(6),
        Entry.init(1),
        Entry.init(3),
        Entry.init(5),
    };

    for (&entries) |*entry| {
        _ = rbtree.addCached(&entry.node, &root, less);
    }

    try std.testing.expectEqual(&entries[3].node, rbtree.firstCached(&root).?);
    try std.testing.expectEqual(&entries[3].node, rbtree.rb_first_cached(&root).?);

    const wanted_three: i32 = 3;
    const middle = rbtree.find(&wanted_three, &root.root, cmpKey).?;
    try std.testing.expectEqual(@as(i32, 2), entryFromNode(rbtree.prev(middle).?).key);
    try std.testing.expectEqual(@as(i32, 4), entryFromNode(rbtree.rb_next(middle).?).key);

    rbtree.eraseInitCached(&entries[3].node, &root);
    try std.testing.expect(rbtree.emptyNode(&entries[3].node));
    try std.testing.expectEqual(&entries[1].node, rbtree.firstCached(&root).?);

    var replacement = Entry.init(2);
    rbtree.replaceNodeCached(&entries[1].node, &replacement.node, &root);
    try std.testing.expectEqual(&replacement.node, rbtree.firstCached(&root).?);
    try std.testing.expect(rbtree.rb_prev(&replacement.node) == null);
    try std.testing.expectEqual(@as(i32, 3), entryFromNode(rbtree.next(&replacement.node).?).key);

    const missing: i32 = 9;
    var matches = rbtree.matchIterator(&missing, &root.root, cmpKey);
    try std.testing.expect(matches.next() == null);
}
