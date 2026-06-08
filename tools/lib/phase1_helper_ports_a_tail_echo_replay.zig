const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

const Word = bitmap.Word;

const Entry = struct {
    key: i32,
    serial: usize,
    node: rbtree.Node = rbtree.Node.init(),
};

fn less(lhs: *const rbtree.Node, rhs: *const rbtree.Node) bool {
    const lhs_entry: *const Entry = @fieldParentPtr("node", lhs);
    const rhs_entry: *const Entry = @fieldParentPtr("node", rhs);
    if (lhs_entry.key != rhs_entry.key) {
        return lhs_entry.key < rhs_entry.key;
    }
    return lhs_entry.serial < rhs_entry.serial;
}

fn cmpKey(key: *const anyopaque, node: *const rbtree.Node) i32 {
    const wanted: *const i32 = @ptrCast(@alignCast(key));
    const entry: *const Entry = @fieldParentPtr("node", node);
    if (wanted.* < entry.key) return -1;
    if (wanted.* > entry.key) return 1;
    return 0;
}

fn collectKeys(root: *const rbtree.RootCached, out: []i32) usize {
    var count: usize = 0;
    var cursor = rbtree.first(&root.root);
    while (cursor) |node| : (cursor = rbtree.next(node)) {
        const entry: *const Entry = @fieldParentPtr("node", node);
        out[count] = entry.key;
        count += 1;
    }
    return count;
}

fn setBits(map: []Word, bits: []const usize) void {
    for (bits) |bit| {
        bitmap.setRange(map, bit, 1);
    }
}

test "phase1 helper ports A tail echo replay" {
    const nbits = bitmap.bits_per_long + 11;
    var base = [_]Word{ 0, 0, 0 };
    var overlay = [_]Word{ 0, 0, 0 };
    var mask = [_]Word{ 0, 0, 0 };
    var echoed = [_]Word{ 0, 0, 0 };
    var extended = [_]Word{ 0xaaaa, 0xaaaa, 0xaaaa };
    var gaps = [_]Word{ 0, 0, 0 };

    setBits(&base, &[_]usize{ 1, 4, bitmap.bits_per_long - 1, bitmap.bits_per_long + 1, bitmap.bits_per_long + 9 });
    setBits(&overlay, &[_]usize{ 2, bitmap.bits_per_long - 1, bitmap.bits_per_long + 3, bitmap.bits_per_long + 10, bitmap.bits_per_long + 14 });
    setBits(&mask, &[_]usize{ 2, 4, bitmap.bits_per_long + 3, bitmap.bits_per_long + 9, bitmap.bits_per_long + 14 });

    bitmap.bitmap_replace(&echoed, &base, &overlay, &mask, nbits);
    bitmap.copyAndExtend(&extended, &echoed, nbits, bitmap.bits_per_long * 3);

    try std.testing.expectEqual(@as(usize, 5), bitmap.weight(&echoed, nbits));
    try std.testing.expectEqual(@as(usize, 5), bitmap.weight(&extended, nbits));
    try std.testing.expect(bitmap.subset(&echoed, &extended, nbits));
    try std.testing.expectEqual(@as(Word, 0), extended[1] & ~bitmap.lastWordMask(nbits));
    try std.testing.expectEqual(@as(Word, 0), extended[2]);

    try std.testing.expect(bitmap.andNotBits(&gaps, &base, &echoed, nbits));
    try std.testing.expectEqual(@as(usize, 2), bitmap.weight(&gaps, nbits));
    try std.testing.expectEqual(@as(usize, 4), find_bit.findFirstAndNotBit(&base, &echoed, nbits));
    try std.testing.expectEqual(@as(usize, bitmap.bits_per_long + 9), find_bit.findNextAndNotBit(&base, &echoed, nbits, bitmap.bits_per_long));
    try std.testing.expectEqual(@as(usize, bitmap.bits_per_long + 3), find_bit.findLastBit(&echoed, nbits));

    var clump: u8 = 0;
    try std.testing.expectEqual(@as(usize, 0), find_bit.findFirstClump8(&clump, &echoed, nbits));
    try std.testing.expectEqual(@as(u8, 0b0000_0110), clump);
    clump = 0;
    try std.testing.expectEqual(@as(usize, bitmap.bits_per_long), find_bit.findNextClump8(&clump, &echoed, nbits, bitmap.bits_per_long));
    try std.testing.expectEqual(@as(u8, 0b0000_1010), clump);
    clump = 0x5a;
    try std.testing.expectEqual(@as(usize, nbits), find_bit.findNextClump8(&clump, &echoed, nbits, bitmap.bits_per_long + 11));
    try std.testing.expectEqual(@as(u8, 0x5a), clump);

    var rendered = [_]u8{0} ** 64;
    const rendered_len = bitmap.scnprintf(&echoed, nbits, &rendered);
    try std.testing.expect(string.strEndsWith(rendered[0..rendered_len], "67"));

    var label = [_]u8{ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 };
    try std.testing.expectEqual(@as(usize, 11), string.strlcpy(&label, "tail-echo-1"));
    try std.testing.expectEqual(@as(usize, 4), string.strHasPrefix(&label, "tail"));
    try std.testing.expect(string.strEndsWith(&label, "-1"));

    var trim_buf = [_]u8{ ' ', 't', 'a', 'i', 'l', ' ', 'e', 'c', 'h', 'o', ' ', 0 };
    const trimmed = string.trimSpaces(&trim_buf);
    try std.testing.expectEqualStrings("tail echo", trimmed);
    try std.testing.expectEqual(@as(usize, 9), string.replaceChar(trimmed, ' ', '-'));
    try std.testing.expectEqualStrings("tail-echo", trimmed);
    try std.testing.expect(string.sysfsStreq("tail-echo\n", trimmed));

    const labels = [_][]const u8{ "base", "tail-echo\n", "other" };
    try std.testing.expectEqual(@as(?usize, 1), string.sysfsMatchString(labels[0..], trimmed));
    try std.testing.expectEqual(@as(?usize, null), string.matchString(labels[0..], trimmed));

    var entries = [_]Entry{
        .{ .key = @intCast(find_bit.findFirstBit(&echoed, nbits)), .serial = 0 },
        .{ .key = @intCast(find_bit.findNextBit(&echoed, nbits, 2)), .serial = 1 },
        .{ .key = @intCast(find_bit.findNextAndNotBit(&base, &echoed, nbits, 5)), .serial = 2 },
        .{ .key = @intCast(find_bit.findLastBit(&echoed, nbits)), .serial = 3 },
    };
    var root = rbtree.RootCached.init();
    for (&entries) |*entry| {
        _ = rbtree.addCached(&entry.node, &root, less);
    }

    var keys: [4]i32 = undefined;
    const count = collectKeys(&root, &keys);
    try std.testing.expectEqual(@as(usize, 4), count);
    try std.testing.expectEqualSlices(i32, &[_]i32{ 1, 2, @intCast(bitmap.bits_per_long + 3), @intCast(bitmap.bits_per_long + 9) }, keys[0..count]);
    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[0].node), rbtree.firstCached(&root));

    const wanted = @as(i32, @intCast(bitmap.bits_per_long + 9));
    try std.testing.expect(rbtree.find(&wanted, &root.root, cmpKey) == &entries[2].node);
    rbtree.eraseInitCached(&entries[0].node, &root);
    try std.testing.expect(rbtree.emptyNode(&entries[0].node));
    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[1].node), rbtree.firstCached(&root));

    var reseed = Entry{ .key = 0, .serial = 4 };
    try std.testing.expectEqual(@as(?*rbtree.Node, &reseed.node), rbtree.addCached(&reseed.node, &root, less));
    try std.testing.expectEqual(@as(?*rbtree.Node, &reseed.node), rbtree.firstCached(&root));
}
