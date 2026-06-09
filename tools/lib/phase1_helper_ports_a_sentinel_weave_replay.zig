const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

const testing = std.testing;
const Word = bitmap.Word;

fn setRange(words: []Word, start: usize, len: usize) void {
    bitmap.bitmap_set(words, start, len);
}

fn nodeKey(comptime Entry: type, node: *const rbtree.Node) usize {
    const entry: *const Entry = @fieldParentPtr("node", node);
    return entry.key;
}

fn keyCompare(comptime Entry: type, key: *const anyopaque, node: *const rbtree.Node) i32 {
    const wanted: *const usize = @ptrCast(@alignCast(key));
    const entry: *const Entry = @fieldParentPtr("node", node);
    if (wanted.* < entry.key) {
        return -1;
    }
    if (wanted.* > entry.key) {
        return 1;
    }
    return 0;
}

test "Lane 06 sentinel weave keeps bitmap find string and cached rbtree aligned" {
    const nbits = 96;
    var old = [_]Word{0} ** bitmap.bitsToWords(nbits);
    var new = [_]Word{0} ** bitmap.bitsToWords(nbits);
    var mask = [_]Word{0} ** bitmap.bitsToWords(nbits);
    var woven = [_]Word{0} ** bitmap.bitsToWords(nbits);
    var overlap = [_]Word{0} ** bitmap.bitsToWords(nbits);
    var sentinel = [_]Word{0} ** bitmap.bitsToWords(nbits);

    setRange(&old, 2, 4);
    setRange(&old, 18, 2);
    setRange(&old, 70, 3);
    setRange(&old, 94, 2);

    setRange(&new, 0, 2);
    setRange(&new, 4, 3);
    setRange(&new, 64, 2);
    setRange(&new, 90, 3);

    setRange(&mask, 0, 8);
    setRange(&mask, 64, 32);

    bitmap.bitmap_replace(&woven, &old, &new, &mask, nbits);
    try testing.expectEqual(@as(usize, 12), bitmap.bitmap_weight(&woven, nbits));
    try testing.expect(bitmap.bitmap_and(&overlap, &woven, &old, nbits));
    try testing.expectEqual(@as(usize, 4), bitmap.bitmap_weight(&overlap, nbits));
    try testing.expect(bitmap.bitmap_andnot(&sentinel, &woven, &old, nbits));
    try testing.expectEqual(@as(usize, 8), bitmap.bitmap_weight(&sentinel, nbits));
    try testing.expect(bitmap.bitmap_subset(&sentinel, &woven, nbits));
    try testing.expect(!bitmap.bitmap_intersects(&sentinel, &old, nbits));

    try testing.expectEqual(@as(usize, 0), find_bit.find_first_bit(&sentinel, nbits));
    try testing.expectEqual(@as(usize, 4), find_bit.find_next_and_bit(&woven, &old, nbits, 0));
    try testing.expectEqual(@as(usize, 6), find_bit.find_next_bit(&sentinel, nbits, 2));
    try testing.expectEqual(@as(usize, 6), find_bit.find_next_andnot_bit(&woven, &old, nbits, 2));
    try testing.expectEqual(@as(usize, 90), find_bit.find_next_bit(&sentinel, nbits, 88));
    try testing.expectEqual(@as(usize, 92), find_bit.find_last_bit(&sentinel, nbits));

    var clump: u8 = 0xaa;
    try testing.expectEqual(@as(usize, 0), find_bit.find_next_clump8(&clump, &sentinel, nbits, 0));
    try testing.expectEqual(@as(u8, 0x43), clump);
    try testing.expectEqual(@as(usize, 64), find_bit.find_next_clump8(&clump, &sentinel, nbits, 64));
    try testing.expectEqual(@as(u8, 0x03), clump);
    try testing.expectEqual(@as(usize, 88), find_bit.find_next_clump8(&clump, &sentinel, nbits, 88));
    try testing.expectEqual(@as(u8, 0x1c), clump);

    var rendered_buf: [40]u8 = undefined;
    @memset(&rendered_buf, 0);
    const rendered_len = bitmap.bitmap_scnprintf(&sentinel, nbits, &rendered_buf);
    const rendered = rendered_buf[0..rendered_len];
    try testing.expectEqualSlices(u8, "0-1,6,64-65,90-92", rendered);

    var decorated = [_]u8{
        ' ', '\t', '0',  '-', '1', ',', ' ', '6', ',', ' ',
        '6', '4',  '-',  '6', '5', ',', ' ', '9', '0', '-',
        '9', '2',  '\n', 0,   0,   0,   0,   0,
    };
    const trimmed = string.strim(&decorated);
    try testing.expectEqualSlices(u8, "0-1, 6, 64-65, 90-92", trimmed);
    const compact = string.remove_spaces(trimmed);
    try testing.expectEqualSlices(u8, rendered, compact);
    try testing.expectEqual(@as(usize, 3), string.str_has_prefix(compact, "0-1"));
    try testing.expect(string.str_ends_with(compact, "90-92"));

    var copied: [40]u8 = undefined;
    @memset(&copied, 0xff);
    const copied_len = string.strscpy_pad(&copied, compact);
    try testing.expectEqual(@as(isize, @intCast(compact.len)), copied_len);
    const replaced_len = string.strreplace(copied[0..compact.len], ',', '|');
    try testing.expectEqual(compact.len, replaced_len);
    try testing.expectEqualSlices(u8, "0-1|6|64-65|90-92", copied[0..compact.len]);
    try testing.expectEqual(@as(?usize, null), string.memchr_inv(copied[compact.len + 1 ..], 0));

    const sysfs_choices = [_][]const u8{
        "idle",
        "0-1|6|64-65|90-92\n",
        "miss",
    };
    const exact_choices = [_][]const u8{
        "idle",
        "0-1|6|64-65|90-92",
        "miss",
    };
    try testing.expectEqual(@as(?usize, 1), string.sysfs_match_string(&sysfs_choices, copied[0..compact.len]));
    try testing.expectEqual(@as(?usize, 1), string.match_string(&exact_choices, "0-1|6|64-65|90-92"));

    const Entry = struct {
        key: usize,
        ordinal: usize,
        node: rbtree.Node = rbtree.Node.init(),
    };
    const less = struct {
        fn compare(lhs: *const rbtree.Node, rhs: *const rbtree.Node) bool {
            const lhs_entry: *const Entry = @fieldParentPtr("node", lhs);
            const rhs_entry: *const Entry = @fieldParentPtr("node", rhs);
            if (lhs_entry.key != rhs_entry.key) {
                return lhs_entry.key < rhs_entry.key;
            }
            return lhs_entry.ordinal < rhs_entry.ordinal;
        }
    }.compare;
    const cmp_key = struct {
        fn compare(key: *const anyopaque, node: *const rbtree.Node) i32 {
            return keyCompare(Entry, key, node);
        }
    }.compare;

    var entries = [_]Entry{
        .{ .key = find_bit.find_next_bit(&sentinel, nbits, 64), .ordinal = 1 },
        .{ .key = find_bit.find_next_bit(&sentinel, nbits, 6), .ordinal = 0 },
        .{ .key = find_bit.find_next_bit(&sentinel, nbits, 90), .ordinal = 0 },
        .{ .key = find_bit.find_next_bit(&sentinel, nbits, 90), .ordinal = 1 },
    };
    var root = rbtree.RootCached.init();

    try testing.expectEqual(@as(?*rbtree.Node, &entries[0].node), rbtree.addCached(&entries[0].node, &root, less));
    try testing.expectEqual(@as(?*rbtree.Node, &entries[1].node), rbtree.addCached(&entries[1].node, &root, less));
    try testing.expectEqual(@as(?*rbtree.Node, null), rbtree.addCached(&entries[2].node, &root, less));
    try testing.expectEqual(@as(?*rbtree.Node, null), rbtree.addCached(&entries[3].node, &root, less));
    try testing.expectEqual(@as(usize, 6), nodeKey(Entry, rbtree.firstCached(&root).?));

    const duplicate_key: usize = 90;
    var duplicates = rbtree.matchIterator(&duplicate_key, &root.root, cmp_key);
    const first_duplicate = duplicates.next() orelse return error.TestUnexpectedResult;
    const second_duplicate = duplicates.next() orelse return error.TestUnexpectedResult;
    try testing.expectEqual(@as(usize, 90), nodeKey(Entry, first_duplicate));
    try testing.expectEqual(@as(usize, 90), nodeKey(Entry, second_duplicate));
    try testing.expectEqual(@as(?*rbtree.Node, null), duplicates.next());

    const promoted = rbtree.eraseCached(&entries[1].node, &root) orelse return error.TestUnexpectedResult;
    try testing.expectEqual(@as(usize, 64), nodeKey(Entry, promoted));
    try testing.expectEqual(@as(usize, 64), nodeKey(Entry, rbtree.firstCached(&root).?));
    rbtree.eraseInitCached(&entries[0].node, &root);
    try testing.expect(rbtree.emptyNode(&entries[0].node));

    var ordered: [2]usize = undefined;
    var count: usize = 0;
    var current = rbtree.first(&root.root);
    while (current) |node| : (current = rbtree.next(node)) {
        ordered[count] = nodeKey(Entry, node);
        count += 1;
    }

    try testing.expectEqual(@as(usize, 2), count);
    try testing.expectEqualSlices(usize, &[_]usize{ 90, 90 }, ordered[0..count]);
}
