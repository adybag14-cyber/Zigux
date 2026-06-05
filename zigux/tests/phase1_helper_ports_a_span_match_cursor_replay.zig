const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

test "phase1 helper ports A span match cursor replay" {
    const Word = bitmap.Word;
    const nbits = bitmap.bits_per_long + 7;

    const old = [_]Word{
        (@as(Word, 1) << 1) | (@as(Word, 1) << 3),
        (@as(Word, 1) << 2) | (@as(Word, 1) << 9),
    };
    const new = [_]Word{
        (@as(Word, 1) << 4) | (@as(Word, 1) << 6),
        (@as(Word, 1) << 5) | (@as(Word, 1) << 11),
    };
    const mask = [_]Word{
        (@as(Word, 1) << 3) | (@as(Word, 1) << 4) | (@as(Word, 1) << 6),
        (@as(Word, 1) << 2) | (@as(Word, 1) << 5) | (@as(Word, 1) << 11),
    };
    var merged = [_]Word{ 0, 0 };

    bitmap.bitmap_replace(&merged, &old, &new, &mask, nbits);
    try std.testing.expectEqual(@as(usize, 1), find_bit.findFirstBit(&merged, nbits));
    try std.testing.expectEqual(@as(usize, 4), find_bit.findNextBit(&merged, nbits, 2));
    try std.testing.expectEqual(@as(usize, bitmap.bits_per_long + 5), find_bit.findNextBit(&merged, nbits, bitmap.bits_per_long));
    try std.testing.expectEqual(@as(usize, bitmap.bits_per_long + 5), find_bit.findLastBit(&merged, nbits));
    try std.testing.expectEqual(@as(usize, nbits), find_bit.findNextBit(&merged, nbits, bitmap.bits_per_long + 6));

    var rendered: [64]u8 = undefined;
    const rendered_len = bitmap.scnprintf(&merged, nbits, &rendered);
    try std.testing.expectEqualStrings("1,4,6,69", rendered[0..rendered_len]);

    var text = [_]u8{ ' ', '1', ',', '4', ',', '6', ',', '6', '9', ' ', '\n', 0, 'x' };
    const trimmed = string.strim(&text);
    try std.testing.expectEqualStrings("1,4,6,69", trimmed);
    try std.testing.expectEqual(@as(usize, 1), string.strHasPrefix(trimmed, "1"));
    try std.testing.expectEqual(@as(?usize, 1), string.strnchr(trimmed, trimmed.len, ','));

    var rewritten = [_]u8{ '1', ',', '4', ',', '6', ',', '6', '9', 0 };
    try std.testing.expectEqual(@as(usize, 8), string.strreplace(&rewritten, ',', ':'));
    try std.testing.expectEqualSlices(u8, &[_]u8{ '1', ':', '4', ':', '6', ':', '6', '9', 0 }, &rewritten);
    try std.testing.expectEqual(@as(?usize, 1), string.strnchr(&rewritten, rewritten.len, ':'));
    try std.testing.expect(string.sysfsStreq("1,4,6,69\n", rendered[0..rendered_len]));

    const parsed = [_]i32{
        @intCast(find_bit.findFirstBit(&merged, nbits)),
        @intCast(find_bit.findNextBit(&merged, nbits, 2)),
        @intCast(find_bit.findNextBit(&merged, nbits, 5)),
        @intCast(find_bit.findLastBit(&merged, nbits)),
    };

    const Entry = struct {
        key: i32,
        serial: usize,
        node: rbtree.Node = rbtree.Node.init(),
    };

    const less = struct {
        fn compare(lhs: *const rbtree.Node, rhs: *const rbtree.Node) bool {
            const lhs_entry: *const Entry = @fieldParentPtr("node", lhs);
            const rhs_entry: *const Entry = @fieldParentPtr("node", rhs);
            if (lhs_entry.key != rhs_entry.key) {
                return lhs_entry.key < rhs_entry.key;
            }
            return lhs_entry.serial < rhs_entry.serial;
        }
    }.compare;

    const keyCmp = struct {
        fn compare(key: *const anyopaque, node: *const rbtree.Node) i32 {
            const wanted: *const i32 = @ptrCast(@alignCast(key));
            const entry: *const Entry = @fieldParentPtr("node", node);
            if (wanted.* < entry.key) return -1;
            if (wanted.* > entry.key) return 1;
            return 0;
        }
    }.compare;

    var entries = [_]Entry{
        .{ .key = parsed[0], .serial = 0 },
        .{ .key = parsed[1], .serial = 1 },
        .{ .key = parsed[2], .serial = 2 },
        .{ .key = parsed[3], .serial = 3 },
        .{ .key = parsed[1], .serial = 4 },
    };
    var root = rbtree.Root.init();
    for (&entries) |*entry| {
        rbtree.add(&entry.node, &root, less);
    }

    const duplicate_key = parsed[1];
    var iter = rbtree.matchIterator(&duplicate_key, &root, keyCmp);
    var duplicate_serials: [2]usize = undefined;
    var duplicate_count: usize = 0;
    while (iter.next()) |node| {
        const entry: *const Entry = @fieldParentPtr("node", node);
        duplicate_serials[duplicate_count] = entry.serial;
        duplicate_count += 1;
    }
    try std.testing.expectEqual(@as(usize, 2), duplicate_count);
    try std.testing.expectEqualSlices(usize, &[_]usize{ 1, 4 }, duplicate_serials[0..duplicate_count]);

    rbtree.eraseInit(&entries[1].node, &root);
    try std.testing.expect(rbtree.emptyNode(&entries[1].node));

    var after_iter = rbtree.matchIterator(&duplicate_key, &root, keyCmp);
    const remaining = after_iter.next() orelse return error.TestUnexpectedResult;
    const remaining_entry: *const Entry = @fieldParentPtr("node", remaining);
    try std.testing.expectEqual(@as(usize, 4), remaining_entry.serial);
    try std.testing.expect(after_iter.next() == null);

    var order: [4]i32 = undefined;
    var count: usize = 0;
    var current = rbtree.first(&root);
    while (current) |node| : (current = rbtree.next(node)) {
        const entry: *const Entry = @fieldParentPtr("node", node);
        order[count] = entry.key;
        count += 1;
    }
    try std.testing.expectEqualSlices(i32, &[_]i32{ 1, 4, 6, 69 }, order[0..count]);
}
