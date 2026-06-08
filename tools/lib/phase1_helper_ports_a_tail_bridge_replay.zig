const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

const Word = bitmap.Word;
const bits_per_long = bitmap.bits_per_long;

const Entry = struct {
    key: i32,
    serial: usize,
    node: rbtree.Node = rbtree.Node.init(),
};

fn lessByKeyThenSerial(lhs: *const rbtree.Node, rhs: *const rbtree.Node) bool {
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

fn readEntry(node: *const rbtree.Node) *const Entry {
    return @fieldParentPtr("node", node);
}

test "phase1 helper ports A tail bridge replay" {
    const count = bits_per_long + 6;
    const nbits = bits_per_long + 14;
    const words = bitmap.bitsToWords(nbits);

    var src = [_]Word{ 0, 0 };
    bitmap.setRange(&src, bits_per_long - 2, 3);
    bitmap.setRange(&src, bits_per_long + 4, 2);
    src[1] |= @as(Word, 1) << 11;

    var extended = [_]Word{ ~@as(Word, 0), ~@as(Word, 0) };
    bitmap.copyAndExtend(&extended, &src, count, nbits);
    try std.testing.expectEqual(@as(usize, 5), bitmap.weight(&extended, nbits));
    try std.testing.expectEqual(@as(usize, bits_per_long - 2), find_bit.findFirstBit(&extended, nbits));
    try std.testing.expectEqual(@as(usize, bits_per_long + 5), find_bit.findLastBit(&extended, nbits));

    var bridge = [_]Word{ 0, 0 };
    bitmap.setRange(&bridge, 2, 2);
    bitmap.setRange(&bridge, bits_per_long + 8, 3);

    var complement = [_]Word{ 0, 0 };
    bitmap.complement(&complement, &extended, nbits);
    try std.testing.expectEqual(@as(usize, nbits - 5), bitmap.weight(&complement, nbits));
    try std.testing.expectEqual(@as(usize, 2), find_bit.findNextAndBit(&complement, &bridge, nbits, 0));

    var merged = [_]Word{ 0, 0 };
    const merged_weight = bitmap.weightedOr(&merged, &extended, &bridge, nbits);
    try std.testing.expectEqual(@as(usize, 10), merged_weight);
    try std.testing.expectEqual(merged_weight, bitmap.weight(&merged, nbits));
    try std.testing.expectEqual(@as(usize, bits_per_long + 8), find_bit.findNextBit(&merged, nbits, bits_per_long + 6));

    var changed = [_]Word{ 0, 0 };
    const changed_weight = bitmap.weightedXor(&changed, &merged, &extended, nbits);
    try std.testing.expectEqual(@as(usize, 5), changed_weight);
    try std.testing.expectEqual(@as(usize, 2), find_bit.findFirstBit(&changed, nbits));

    var clump: u8 = 0;
    try std.testing.expectEqual(@as(usize, bits_per_long - 8), find_bit.findNextClump8(&clump, &merged, nbits, bits_per_long - 2));
    try std.testing.expectEqual(@as(u8, 0b1100_0000), clump & 0b1100_0000);
    try std.testing.expectEqual(@as(usize, bits_per_long + 8), find_bit.findNextClump8(&clump, &merged, nbits, bits_per_long + 6));
    try std.testing.expectEqual(@as(u8, 0b0000_0111), clump & 0b0000_0111);

    var rendered: [80]u8 = undefined;
    const rendered_len = bitmap.scnprintf(&merged, nbits, &rendered);
    const ranges = rendered[0..rendered_len];
    try std.testing.expectEqualStrings("2-3,62-64,68-69,72-74", ranges);

    var label = [_]u8{ ' ', 't', 'a', 'i', 'l', ':', '2', '-', '3', ',', '6', '2', '-', '6', '4', ',', '6', '8', '-', '6', '9', ',', '7', '2', '-', '7', '4', ' ', 0, 'x' };
    const trimmed = string.strstrip(label[0..]);
    try std.testing.expectEqualStrings("tail:2-3,62-64,68-69,72-74", trimmed);
    try std.testing.expectEqual(@as(usize, 5), string.str_has_prefix(trimmed, "tail:"));
    try std.testing.expect(string.strEndsWith(trimmed, "72-74"));

    var padded = [_]u8{0xaa} ** 10;
    try std.testing.expectEqual(@as(isize, 4), string.strscpy_pad(padded[0..], "tail"));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 't', 'a', 'i', 'l', 0, 0, 0, 0, 0, 0 }, padded[0..]);
    try std.testing.expectEqual(@as(?usize, 1), string.sysfs_match_string(&[_][]const u8{ "off", "tail\n", "tail" }, "tail"));
    try std.testing.expectEqual(@as(?usize, 2), string.match_string(&[_][]const u8{ "bitmap", "find_bit", "string", "rbtree" }, "string"));

    var entries = [_]Entry{
        .{ .key = @intCast(find_bit.findFirstBit(&merged, nbits)), .serial = 0 },
        .{ .key = @intCast(find_bit.findNextBit(&merged, nbits, bits_per_long + 6)), .serial = 1 },
        .{ .key = @intCast(find_bit.findLastBit(&merged, nbits)), .serial = 2 },
        .{ .key = @intCast(words + 80), .serial = 3 },
        .{ .key = @intCast(words + 80), .serial = 4 },
    };

    var root = rbtree.RootCached.init();
    for (&entries) |*entry| {
        _ = rbtree.addCached(&entry.node, &root, lessByKeyThenSerial);
    }

    try std.testing.expectEqual(@as(i32, 2), readEntry(rbtree.firstCached(&root).?).key);

    const duplicate_key: i32 = @intCast(words + 80);
    var iter = rbtree.matchIterator(&duplicate_key, &root.root, cmpKey);
    var duplicate_serials: [2]usize = undefined;
    var duplicate_count: usize = 0;
    while (iter.next()) |node| {
        duplicate_serials[duplicate_count] = readEntry(node).serial;
        duplicate_count += 1;
    }
    try std.testing.expectEqual(@as(usize, 2), duplicate_count);
    try std.testing.expectEqualSlices(usize, &[_]usize{ 3, 4 }, duplicate_serials[0..duplicate_count]);

    const promoted = rbtree.eraseCached(&entries[0].node, &root) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(i32, bits_per_long + 8), readEntry(promoted).key);
    rbtree.eraseInitCached(&entries[1].node, &root);
    try std.testing.expect(rbtree.emptyNode(&entries[1].node));
    try std.testing.expectEqual(@as(i32, bits_per_long + 10), readEntry(rbtree.firstCached(&root).?).key);
}
