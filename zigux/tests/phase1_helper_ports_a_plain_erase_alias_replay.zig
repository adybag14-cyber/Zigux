const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

const Word = bitmap.Word;

fn rbErase(node: *rbtree.Node, root: *rbtree.Root) void {
    if (@hasDecl(rbtree, "rb_erase")) {
        rbtree.rb_erase(node, root);
    } else {
        rbtree.erase(node, root);
    }
}

fn rbEraseInit(node: *rbtree.Node, root: *rbtree.Root) void {
    if (@hasDecl(rbtree, "rb_erase_init")) {
        rbtree.rb_erase_init(node, root);
    } else {
        rbtree.eraseInit(node, root);
    }
}

fn setBit(words: []Word, bit: usize) void {
    words[bit / bitmap.bits_per_long] |= @as(Word, 1) << @intCast(bit & (bitmap.bits_per_long - 1));
}

fn keyFromNode(node: *const rbtree.Node) i32 {
    const entry: *const Entry = @fieldParentPtr("node", node);
    return entry.key;
}

const Entry = struct {
    key: i32,
    node: rbtree.Node = rbtree.Node.init(),
};

const lessByKey = struct {
    fn compare(lhs: *const rbtree.Node, rhs: *const rbtree.Node) bool {
        return keyFromNode(lhs) < keyFromNode(rhs);
    }
}.compare;

const cmpByKey = struct {
    fn compare(key: *const anyopaque, node: *const rbtree.Node) i32 {
        const wanted: *const i32 = @ptrCast(@alignCast(key));
        const current = keyFromNode(node);
        if (wanted.* < current) return -1;
        if (wanted.* > current) return 1;
        return 0;
    }
}.compare;

test "bitmap replacement feeds find-bit cursors and string normalization" {
    const nbits = bitmap.bits_per_long + 7;
    var old = [_]Word{0} ** 2;
    var new = [_]Word{0} ** 2;
    var mask = [_]Word{0} ** 2;
    var merged = [_]Word{0} ** 2;

    inline for (.{ 2, 5, 9, 63, 68 }) |bit| {
        setBit(&new, bit);
    }
    inline for (.{ 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 63, 64, 65, 66, 67, 68, 69 }) |bit| {
        setBit(&mask, bit);
    }
    setBit(&old, 69);

    bitmap.replace(&merged, &old, &new, &mask, nbits);

    try std.testing.expectEqual(@as(usize, 5), bitmap.weight(&merged, nbits));
    try std.testing.expectEqual(@as(usize, 2), find_bit.findFirstBit(&merged, nbits));
    try std.testing.expectEqual(@as(usize, 5), find_bit.findNextBit(&merged, nbits, 3));
    try std.testing.expectEqual(@as(usize, 3), find_bit.findNextZeroBit(&merged, nbits, 2));
    try std.testing.expectEqual(@as(usize, 68), find_bit.findLastBit(&merged, nbits));

    var clump: u8 = 0;
    try std.testing.expectEqual(@as(usize, 0), find_bit.findFirstClump8(&clump, &merged, nbits));
    try std.testing.expectEqual(@as(u8, 0b0010_0100), clump);
    try std.testing.expectEqual(@as(usize, 64), find_bit.findNextClump8(&clump, &merged, nbits, 64));
    try std.testing.expectEqual(@as(u8, 0b0001_0000), clump);

    var rendered: [64]u8 = undefined;
    const rendered_len = bitmap.scnprintf(&merged, nbits, &rendered);
    try std.testing.expectEqualStrings("2,5,9,63,68", rendered[0..rendered_len]);

    var padded = [_]u8{ ' ', ' ', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 };
    @memcpy(padded[2 .. 2 + rendered_len], rendered[0..rendered_len]);
    padded[2 + rendered_len] = '\n';
    const trimmed = string.strim(&padded);
    try std.testing.expectEqualStrings("2,5,9,63,68", trimmed);
    try std.testing.expect(string.sysfs_streq(trimmed, "2,5,9,63,68\n"));
    try std.testing.expectEqual(@as(?usize, 0), string.match_string(&[_][]const u8{ trimmed, "missing" }, "2,5,9,63,68"));
    try std.testing.expectEqual(@as(?usize, 1), string.memchr_inv(trimmed, '2'));
}

test "plain erase compatibility wrappers preserve rbtree traversal" {
    var entries = [_]Entry{
        .{ .key = 2 },
        .{ .key = 5 },
        .{ .key = 9 },
        .{ .key = 63 },
        .{ .key = 68 },
    };
    var root = rbtree.Root.init();

    for (&entries) |*entry| {
        rbtree.add(&entry.node, &root, lessByKey);
    }

    const wanted = @as(i32, 9);
    const found = rbtree.find(&wanted, &root, cmpByKey) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(i32, 9), keyFromNode(found));

    rbErase(&entries[1].node, &root);
    rbEraseInit(&entries[3].node, &root);
    try std.testing.expect(rbtree.emptyNode(&entries[3].node));

    var order: [3]i32 = undefined;
    var count: usize = 0;
    var current = rbtree.first(&root);
    while (current) |node| : (current = rbtree.next(node)) {
        order[count] = keyFromNode(node);
        count += 1;
    }

    try std.testing.expectEqual(@as(usize, 3), count);
    try std.testing.expectEqualSlices(i32, &[_]i32{ 2, 9, 68 }, order[0..count]);
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.find(&@as(i32, 5), &root, cmpByKey));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.find(&@as(i32, 63), &root, cmpByKey));
}
