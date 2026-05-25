const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

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

fn cmpNode(lhs: *const rbtree.Node, rhs: *const rbtree.Node) i32 {
    const lhs_entry: *const Entry = @fieldParentPtr("node", lhs);
    const rhs_entry: *const Entry = @fieldParentPtr("node", rhs);
    if (lhs_entry.key < rhs_entry.key) return -1;
    if (lhs_entry.key > rhs_entry.key) return 1;
    return 0;
}

fn cmpKey(key: *const anyopaque, node: *const rbtree.Node) i32 {
    const wanted: *const i32 = @ptrCast(@alignCast(key));
    const entry: *const Entry = @fieldParentPtr("node", node);
    if (wanted.* < entry.key) return -1;
    if (wanted.* > entry.key) return 1;
    return 0;
}

test "phase1 helper ports A weighted bitmap window keeps tail counts and clumps aligned" {
    const nbits = bitmap.bits_per_long + 5;
    const lhs = [_]bitmap.Word{
        0,
        (@as(bitmap.Word, 1) << 1) | (@as(bitmap.Word, 1) << 3) | (@as(bitmap.Word, 1) << 8),
    };
    const rhs = [_]bitmap.Word{
        0,
        (@as(bitmap.Word, 1) << 3) | (@as(bitmap.Word, 1) << 4) | (@as(bitmap.Word, 1) << 9),
    };

    var or_words = [_]bitmap.Word{ 0, 0 };
    var xor_words = [_]bitmap.Word{ 0, 0 };

    try std.testing.expectEqual(@as(usize, 3), bitmap.weightedOr(&or_words, &lhs, &rhs, nbits));
    try std.testing.expectEqual(@as(usize, 3), bitmap.weight(&or_words, nbits));
    try std.testing.expectEqual(@as(usize, 2), bitmap.weightedXor(&xor_words, &lhs, &rhs, nbits));
    try std.testing.expectEqual(@as(usize, 2), bitmap.weight(&xor_words, nbits));

    try std.testing.expectEqual(@as(usize, bitmap.bits_per_long + 1), find_bit.findNextAndNotBit(&lhs, &rhs, nbits, bitmap.bits_per_long));
    try std.testing.expectEqual(@as(usize, bitmap.bits_per_long + 4), find_bit.findLastBit(&or_words, nbits));

    var clump: u8 = 0;
    try std.testing.expectEqual(@as(usize, bitmap.bits_per_long), find_bit.findFirstClump8(&clump, &or_words, nbits));
    try std.testing.expectEqual(@as(u8, 0b0001_1010), clump);

    var buffer: [32]u8 = undefined;
    const len = bitmap.bitmap_scnprintf(&or_words, nbits, &buffer);
    try std.testing.expectEqualStrings("65,67-68", buffer[0..len]);
}

test "phase1 helper ports A locator-style string boundaries keep aliases and newline-aware matches stable" {
    const prefixed = [_]u8{ 'm', 'o', 'd', 'e', '=', 'f', 'a', 's', 't', 0, 'x' };
    try std.testing.expectEqual(@as(usize, 5), string.strHasPrefix(&prefixed, "mode="));
    try std.testing.expectEqual(@as(usize, 5), string.str_has_prefix(&prefixed, "mode="));

    const sysfs_labels = [_][]const u8{ "slow", "fast\n", "fast", "auto" };
    try std.testing.expectEqual(@as(?usize, 1), string.sysfsMatchString(sysfs_labels[0..], "fast"));
    try std.testing.expectEqual(@as(?usize, 1), string.sysfs_match_string(sysfs_labels[0..], "fast"));

    const plain_labels = [_][]const u8{
        "slow",
        &[_]u8{ 'f', 'a', 's', 't', 0, 'x' },
        "auto",
    };
    try std.testing.expectEqual(@as(?usize, 1), string.matchString(plain_labels[0..], "fast"));
    try std.testing.expectEqual(@as(?usize, 1), string.match_string(plain_labels[0..], "fast"));

    var padded = [_]u8{'x'} ** 32;
    padded[11] = 'y';
    try std.testing.expectEqual(@as(?usize, 11), string.memchrInv(padded[0..], 'x'));
    try std.testing.expectEqual(@as(?usize, 11), string.memchr_inv(padded[0..], 'x'));
}

test "phase1 helper ports A cached duplicates keep leftmost handoff and iterator order explicit" {
    var cached_root = rbtree.RootCached.init();
    var entries = [_]Entry{
        .{ .key = 10, .serial = 0 },
        .{ .key = 5, .serial = 1 },
        .{ .key = 5, .serial = 2 },
        .{ .key = 12, .serial = 3 },
    };
    var duplicate_probe = Entry{ .key = 10, .serial = 99 };
    var replacement = Entry{ .key = 5, .serial = 4 };

    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[0].node), rbtree.addCached(&entries[0].node, &cached_root, less));
    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[1].node), rbtree.addCached(&entries[1].node, &cached_root, less));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.addCached(&entries[2].node, &cached_root, less));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.addCached(&entries[3].node, &cached_root, less));
    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[1].node), rbtree.firstCached(&cached_root));

    const existing = rbtree.findAddCached(&duplicate_probe.node, &cached_root, cmpNode) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(*rbtree.Node, &entries[0].node), existing);
    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[1].node), rbtree.firstCached(&cached_root));

    const wanted = @as(i32, 5);
    var iterator = rbtree.matchIterator(&wanted, &cached_root.root, cmpKey);
    var serials: [2]usize = undefined;
    var count: usize = 0;
    while (iterator.next()) |node| {
        const entry: *const Entry = @fieldParentPtr("node", node);
        serials[count] = entry.serial;
        count += 1;
    }
    try std.testing.expectEqual(@as(usize, 2), count);
    try std.testing.expectEqualSlices(usize, &[_]usize{ 1, 2 }, serials[0..count]);

    const promoted = rbtree.eraseCached(&entries[1].node, &cached_root) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(*rbtree.Node, &entries[2].node), promoted);
    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[2].node), rbtree.firstCached(&cached_root));

    rbtree.replaceNodeCached(&entries[2].node, &replacement.node, &cached_root);
    try std.testing.expectEqual(@as(?*rbtree.Node, &replacement.node), rbtree.firstCached(&cached_root));
    try std.testing.expectEqual(rbtree.first(&cached_root.root), rbtree.firstCached(&cached_root));
}
