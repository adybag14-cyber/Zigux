const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

const Word = bitmap.Word;
const bits_per_long = bitmap.bits_per_long;

test "bitmap helpers keep tail-clamped copy and formatted ranges aligned" {
    const nbits = bits_per_long + 5;
    const size = bits_per_long * 3;
    const src = [_]Word{
        ~@as(Word, 0),
        (@as(Word, 1) << 1) | (@as(Word, 1) << 4) | (@as(Word, 1) << 8),
        ~@as(Word, 0),
    };

    var copied = [_]Word{ 0, 0, 0 };
    bitmap.copyClearTail(copied[0..2], src[0..2], nbits);
    try std.testing.expectEqual(@as(Word, ~@as(Word, 0)), copied[0]);
    try std.testing.expectEqual((@as(Word, 1) << 1) | (@as(Word, 1) << 4), copied[1]);

    var extended = [_]Word{ 0xdead, 0xbeef, 0xcafe };
    bitmap.copyAndExtend(extended[0..], src[0..2], nbits, size);
    try std.testing.expectEqual(copied[0], extended[0]);
    try std.testing.expectEqual(copied[1], extended[1]);
    try std.testing.expectEqual(@as(Word, 0), extended[2]);

    var buffer: [64]u8 = undefined;
    const len = bitmap.bitmap_scnprintf(extended[0..], nbits, buffer[0..]);

    var expected: [32]u8 = undefined;
    const expected_text = try std.fmt.bufPrint(
        &expected,
        "0-{d},{d},{d}",
        .{ bits_per_long - 1, bits_per_long + 1, bits_per_long + 4 },
    );
    try std.testing.expectEqualStrings(expected_text, buffer[0..len]);
}

test "find_bit clump and byte helpers keep tail-byte windows reviewable" {
    const nbits = bits_per_long + 16;
    const map = [_]find_bit.Word{
        0,
        (@as(find_bit.Word, 1) << 2) |
            (@as(find_bit.Word, 1) << 5) |
            (@as(find_bit.Word, 1) << 9) |
            (@as(find_bit.Word, 1) << 14),
    };

    var clump: u8 = 0;
    try std.testing.expectEqual(@as(usize, bits_per_long), find_bit.findFirstClump8(&clump, map[0..], nbits));
    try std.testing.expectEqual(@as(u8, 0b0010_0100), clump);
    try std.testing.expectEqual(@as(u8, 0b0010_0100), find_bit.getValue8(map[0..], bits_per_long));

    clump = 0;
    try std.testing.expectEqual(@as(usize, bits_per_long + 8), find_bit.findNextClump8(&clump, map[0..], nbits, bits_per_long + 6));
    try std.testing.expectEqual(@as(u8, 0b0100_0010), clump);
    try std.testing.expectEqual(@as(u8, 0b0100_0010), find_bit.getValue8(map[0..], bits_per_long + 8));

    clump = 0x5a;
    try std.testing.expectEqual(@as(usize, nbits), find_bit.findNextClump8(&clump, map[0..], nbits, nbits));
    try std.testing.expectEqual(@as(u8, 0x5a), clump);
}

test "string sysfs and bounded search helpers stop at visible boundaries" {
    const sysfs_haystack = [_][]const u8{ "off", "auto\n", "auto", "manual" };
    try std.testing.expectEqual(@as(?usize, 1), string.sysfsMatchString(sysfs_haystack[0..], "auto"));
    try std.testing.expectEqual(@as(?usize, 1), string.sysfs_match_string(sysfs_haystack[0..], "auto"));
    try std.testing.expectEqual(@as(?usize, null), string.sysfsMatchString(sysfs_haystack[0..], "missing"));

    const match_haystack = [_][]const u8{
        &[_]u8{ 'a', 'l', 'p', 'h', 'a', 0, 'x' },
        "beta",
    };
    try std.testing.expectEqual(@as(?usize, 0), string.matchString(match_haystack[0..], "alpha"));
    try std.testing.expectEqual(@as(?usize, 1), string.match_string(match_haystack[0..], "beta"));
    try std.testing.expectEqual(@as(?usize, null), string.matchString(match_haystack[0..], "alphax"));

    const bounded = [_]u8{ 'a', 'b', 0, 'c', 'd' };
    try std.testing.expectEqual(@as(?usize, 1), string.strnchr(&bounded, bounded.len, 'b'));
    try std.testing.expectEqual(@as(?usize, null), string.strnchr(&bounded, bounded.len, 'c'));
    try std.testing.expectEqual(@as(?usize, null), string.strnchr(&bounded, 2, 'z'));
}

test "rbtree cached reset and postorder replay stay aligned after reseeding leftmost" {
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
        .{ .key = 10 },
        .{ .key = 5 },
        .{ .key = 15 },
    };
    var reseed = Entry{ .key = 3 };
    var root = rbtree.RootCached.init();

    for (&entries) |*entry| {
        _ = rbtree.addCached(&entry.node, &root, less);
    }

    rbtree.eraseInitCached(&entries[1].node, &root);
    try std.testing.expect(rbtree.emptyNode(&entries[1].node));
    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[0].node), rbtree.firstCached(&root));

    _ = rbtree.addCached(&reseed.node, &root, less);
    try std.testing.expectEqual(@as(?*rbtree.Node, &reseed.node), rbtree.firstCached(&root));
    try std.testing.expectEqual(rbtree.first(&root.root), rbtree.firstCached(&root));

    var postorder: [3]i32 = undefined;
    var count: usize = 0;
    var current = rbtree.firstPostorder(&root.root);
    while (current) |node| : (current = rbtree.nextPostorder(node)) {
        const entry: *const Entry = @fieldParentPtr("node", node);
        postorder[count] = entry.key;
        count += 1;
    }

    try std.testing.expectEqual(@as(usize, 3), count);
    try std.testing.expectEqualSlices(i32, &[_]i32{ 3, 15, 10 }, postorder[0..count]);
}
