const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

const Word = bitmap.Word;
const bits_per_long = bitmap.bits_per_long;

fn bitmapReplace(dst: []Word, old: []const Word, new: []const Word, mask: []const Word, nbits: usize) void {
    if (@hasDecl(bitmap, "replaceBits")) {
        bitmap.replaceBits(dst, old, new, mask, nbits);
    } else {
        bitmap.replace(dst, old, new, mask, nbits);
    }
}

fn findNextOrBit(lhs: []const Word, rhs: []const Word, nbits: usize, start: usize) usize {
    if (@hasDecl(find_bit, "findNextOrBit")) {
        return find_bit.findNextOrBit(lhs, rhs, nbits, start);
    }

    var idx = start;
    while (idx < nbits) : (idx += 1) {
        const word = idx / bits_per_long;
        const bit = idx & (bits_per_long - 1);
        if ((((lhs[word] | rhs[word]) >> @intCast(bit)) & 1) != 0) {
            return idx;
        }
    }
    return nbits;
}

fn stringContains(haystack: []const u8, needle: []const u8) bool {
    if (@hasDecl(string, "strstr")) {
        return string.strstr(haystack, needle) != null;
    }
    return std.mem.indexOf(u8, haystack, needle) != null;
}

fn erasePlain(node: *rbtree.Node, root: *rbtree.Root) void {
    if (@hasDecl(rbtree, "rb_erase")) {
        rbtree.rb_erase(node, root);
    } else {
        rbtree.erase(node, root);
    }
}

fn eraseInitPlain(node: *rbtree.Node, root: *rbtree.Root) void {
    if (@hasDecl(rbtree, "rb_erase_init")) {
        rbtree.rb_erase_init(node, root);
    } else {
        rbtree.eraseInit(node, root);
    }
}

test "phase1 helper ports A lattice clasp replay" {
    const nbits = bits_per_long + 12;

    const old = [_]Word{
        (@as(Word, 1) << 1) | (@as(Word, 1) << 8) | (@as(Word, 1) << 13),
        (@as(Word, 1) << 2) | (@as(Word, 1) << 9),
    };
    const new = [_]Word{
        (@as(Word, 1) << 3) | (@as(Word, 1) << 8) | (@as(Word, 1) << 21),
        (@as(Word, 1) << 4) | (@as(Word, 1) << 10),
    };
    const mask = [_]Word{
        (@as(Word, 1) << 1) | (@as(Word, 1) << 3) | (@as(Word, 1) << 21),
        (@as(Word, 1) << 4) | (@as(Word, 1) << 9) | (@as(Word, 1) << 15),
    };

    var clasp = [_]Word{ 0, 0 };
    bitmapReplace(&clasp, &old, &new, &mask, nbits);
    try std.testing.expectEqual(@as(usize, 6), bitmap.weight(&clasp, nbits));
    try std.testing.expect(bitmap.intersects(&clasp, &new, nbits));

    var old_only = [_]Word{ 0, 0 };
    try std.testing.expect(bitmap.andNotBits(&old_only, &old, &new, nbits));
    try std.testing.expectEqual(@as(usize, 4), bitmap.weight(&old_only, nbits));
    try std.testing.expect(bitmap.subset(&old_only, &old, nbits));

    try std.testing.expectEqual(@as(usize, 3), findNextOrBit(&clasp, &old_only, nbits, 2));
    try std.testing.expectEqual(@as(usize, bits_per_long + 2), find_bit.findNextBit(&clasp, nbits, bits_per_long));
    try std.testing.expectEqual(@as(usize, 1), find_bit.findNextAndNotBit(&old, &new, nbits, 0));
    try std.testing.expectEqual(@as(usize, bits_per_long + 4), find_bit.findLastBit(&clasp, nbits));

    var clump: u8 = 0;
    try std.testing.expectEqual(@as(usize, 0), find_bit.findFirstClump8(&clump, &clasp, nbits));
    try std.testing.expectEqual(@as(u8, 0b0000_1000), clump);

    var rendered: [48]u8 = undefined;
    const rendered_len = bitmap.scnprintf(&clasp, nbits, &rendered);
    try std.testing.expectEqualStrings("3,8,13", rendered[0..@min(rendered_len, 6)]);

    var label = [_]u8{ ' ', '\t', 'l', 'a', 't', 't', 'i', 'c', 'e', '-', '3', 0, 'x' };
    const trimmed = string.strstrip(label[0..]);
    try std.testing.expect(string.strstarts(trimmed, "lattice"));
    try std.testing.expect(string.strEndsWith(trimmed, "-3"));
    try std.testing.expect(stringContains(trimmed, "ice"));
    try std.testing.expectEqual(@as(?usize, 3), string.memchrInv("lllclasp", 'l'));

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

    var entries = [_]Entry{
        .{ .key = 13 },
        .{ .key = 3 },
        .{ .key = 8 },
        .{ .key = 4 },
        .{ .key = 10 },
    };
    var root = rbtree.Root.init();

    for (&entries) |*entry| {
        rbtree.add(&entry.node, &root, less);
    }

    erasePlain(&entries[0].node, &root);
    eraseInitPlain(&entries[3].node, &root);
    try std.testing.expect(rbtree.emptyNode(&entries[3].node));

    var order: [3]i32 = undefined;
    var count: usize = 0;
    var current = rbtree.first(&root);
    while (current) |node| : (current = rbtree.next(node)) {
        const entry: *const Entry = @fieldParentPtr("node", node);
        order[count] = entry.key;
        count += 1;
    }

    try std.testing.expectEqual(@as(usize, 3), count);
    try std.testing.expectEqualSlices(i32, &[_]i32{ 3, 8, 10 }, order[0..count]);
}
