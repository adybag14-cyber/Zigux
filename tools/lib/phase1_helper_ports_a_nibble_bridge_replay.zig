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

test "Lane 06 nibble bridge keeps bitmap find string and cached rbtree aligned" {
    const nbits = 76;
    var base = [_]Word{0}**bitmap.bitsToWords(nbits);
    var gate = [_]Word{0}**bitmap.bitsToWords(nbits);
    var remaining = [_]Word{0}**bitmap.bitsToWords(nbits);
    var merged = [_]Word{0}**bitmap.bitsToWords(nbits);

    setRange(&base, 4, 4);
    setRange(&base, 64, 4);
    setRange(&base, 72, 4);

    setRange(&gate, 6, 4);
    setRange(&gate, 66, 4);
    setRange(&gate, 74, 4);

    try testing.expect(bitmap.bitmap_andnot(&remaining, &base, &gate, nbits));
    bitmap.bitmap_or(&merged, &remaining, &gate, nbits);
    try testing.expectEqual(@as(usize, 6), bitmap.bitmap_weight(&remaining, nbits));
    try testing.expect(bitmap.bitmap_subset(&remaining, &base, nbits));
    try testing.expect(bitmap.bitmap_intersects(&remaining, &merged, nbits));
    try testing.expect(!bitmap.bitmap_equal(&remaining, &base, nbits));

    try testing.expectEqual(@as(usize, 4), find_bit.find_first_bit(&remaining, nbits));
    try testing.expectEqual(@as(usize, 5), find_bit.find_next_bit(&remaining, nbits, 5));
    try testing.expectEqual(@as(usize, 64), find_bit.find_next_bit(&remaining, nbits, 6));
    try testing.expectEqual(@as(usize, 72), find_bit.find_next_andnot_bit(&base, &gate, nbits, 66));
    try testing.expectEqual(@as(usize, 73), find_bit.find_last_bit(&remaining, nbits));

    var clump: u8 = 0xaa;
    try testing.expectEqual(@as(usize, 0), find_bit.find_next_clump8(&clump, &remaining, nbits, 0));
    try testing.expectEqual(@as(u8, 0x30), clump);
    try testing.expectEqual(@as(usize, 64), find_bit.find_next_clump8(&clump, &remaining, nbits, 64));
    try testing.expectEqual(@as(u8, 0x03), clump);
    try testing.expectEqual(@as(usize, 72), find_bit.find_next_clump8(&clump, &remaining, nbits, 70));
    try testing.expectEqual(@as(u8, 0x03), clump);

    var rendered_buf: [32]u8 = undefined;
    @memset(&rendered_buf, 0);
    const rendered_len = bitmap.bitmap_scnprintf(&remaining, nbits, &rendered_buf);
    const rendered = rendered_buf[0..rendered_len];
    try testing.expectEqualSlices(u8, "4-5,64-65,72-73", rendered);

    var padded: [32]u8 = undefined;
    @memset(&padded, 0xff);
    const copied = string.strscpyPad(&padded, rendered);
    try testing.expectEqual(@as(isize, @intCast(rendered.len)), copied);
    try testing.expectEqual(@as(u8, 0), padded[rendered.len]);
    try testing.expectEqual(@as(u8, 0), padded[rendered.len + 1]);

    var decorated: [32]u8 = undefined;
    @memset(&decorated, 0);
    @memcpy(decorated[0 .. rendered.len + 3], "  " ++ "4-5,64-65,72-73" ++ "\n");
    const trimmed = string.strim(&decorated);
    try testing.expectEqualSlices(u8, rendered, trimmed);
    try testing.expectEqual(@as(usize, 3), string.strHasPrefix(trimmed, "4-5"));
    try testing.expect(string.strEndsWith(trimmed, "72-73"));

    const replaced_count = string.strreplace(padded[0..rendered.len], ',', '|');
    try testing.expectEqual(rendered.len, replaced_count);
    try testing.expectEqualSlices(u8, "4-5|64-65|72-73", padded[0..rendered.len]);

    const sysfs_choices = [_][]const u8{
        "idle",
        "4-5|64-65|72-73\n",
        "miss",
    };
    const exact_choices = [_][]const u8{
        "idle",
        "4-5|64-65|72-73",
        "miss",
    };
    try testing.expectEqual(@as(?usize, 1), string.sysfs_match_string(&sysfs_choices, padded[0..rendered.len]));
    try testing.expectEqual(@as(?usize, 1), string.match_string(&exact_choices, "4-5|64-65|72-73"));

    const Entry = struct {
        key: usize,
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
        .{ .key = find_bit.find_next_bit(&remaining, nbits, 64) },
        .{ .key = find_bit.find_first_bit(&remaining, nbits) },
        .{ .key = find_bit.find_next_andnot_bit(&base, &gate, nbits, 66) },
    };
    var root = rbtree.RootCached.init();

    try testing.expectEqual(@as(?*rbtree.Node, &entries[0].node), rbtree.addCached(&entries[0].node, &root, less));
    try testing.expectEqual(@as(?*rbtree.Node, &entries[1].node), rbtree.addCached(&entries[1].node, &root, less));
    try testing.expectEqual(@as(?*rbtree.Node, null), rbtree.addCached(&entries[2].node, &root, less));
    try testing.expectEqual(@as(usize, 4), nodeKey(Entry, rbtree.firstCached(&root).?));

    const promoted = rbtree.eraseCached(&entries[1].node, &root) orelse return error.TestUnexpectedResult;
    try testing.expectEqual(@as(usize, 64), nodeKey(Entry, promoted));
    try testing.expectEqual(@as(usize, 64), nodeKey(Entry, rbtree.firstCached(&root).?));

    var ordered: [2]usize = undefined;
    var count: usize = 0;
    var current = rbtree.first(&root.root);
    while (current) |node| : (current = rbtree.next(node)) {
        ordered[count] = nodeKey(Entry, node);
        count += 1;
    }

    try testing.expectEqual(@as(usize, 2), count);
    try testing.expectEqualSlices(usize, &[_]usize{ 64, 72 }, ordered[0..count]);
}
