const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

const Word = bitmap.Word;
const bits_per_long = bitmap.bits_per_long;

test "helper ports A copy-clear tail feeds clamped find-bit scans" {
    const nbits = bits_per_long + 5;
    var source = [_]Word{ 0, 0 };
    source[0] |= @as(Word, 1) << 1;
    source[1] |= @as(Word, 1) << 3;
    source[1] |= @as(Word, 1) << 10;

    var copied = [_]Word{ ~@as(Word, 0), ~@as(Word, 0) };
    bitmap.copyClearTail(&copied, &source, nbits);

    try std.testing.expectEqual(@as(Word, 1) << 1, copied[0]);
    try std.testing.expectEqual(@as(Word, 1) << 3, copied[1]);
    try std.testing.expectEqual(@as(usize, 2), bitmap.weight(&copied, nbits));
    try std.testing.expectEqual(@as(usize, 1), find_bit.findFirstBit(&copied, nbits));
    try std.testing.expectEqual(@as(usize, bits_per_long + 3), find_bit.findNextBit(&copied, nbits, 2));
    try std.testing.expectEqual(@as(usize, bits_per_long + 3), find_bit.findLastBit(&copied, nbits));
    try std.testing.expectEqual(nbits, find_bit.findNextBit(&copied, nbits, bits_per_long + 4));

    var formatted: [32]u8 = undefined;
    @memset(&formatted, 0xaa);
    const written = bitmap.scnprintf(&copied, nbits, &formatted);
    var expected_storage: [32]u8 = undefined;
    const expected = try std.fmt.bufPrint(&expected_storage, "1,{d}", .{bits_per_long + 3});

    try std.testing.expectEqual(expected.len, written);
    try std.testing.expectEqualSlices(u8, expected, formatted[0..written]);
    try std.testing.expectEqual(@as(u8, 0), formatted[written]);
}

test "helper ports A padded string copies keep counted search boundaries" {
    const src = [_]u8{ 'p', 'r', 'e', 0, 'x', 'y' };
    var padded = [_]u8{0xcc} ** 8;

    try std.testing.expectEqual(@as(isize, 3), string.strscpy_pad(&padded, &src));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'p', 'r', 'e', 0, 0, 0, 0, 0 }, &padded);
    try std.testing.expectEqual(@as(usize, 3), string.str_has_prefix(&padded, "pre"));
    try std.testing.expectEqual(@as(?usize, null), string.strnchr(&padded, padded.len, 'x'));
    try std.testing.expectEqual(@as(?usize, 3), string.strnchr(&padded, padded.len, 0));
    try std.testing.expectEqual(@as(?usize, null), string.strnchr(&padded, 3, 0));
}

test "helper ports A cached erase-init preserves reverse traversal" {
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

    const cmp_key = struct {
        fn compare(key_ptr: *const anyopaque, node: *const rbtree.Node) i32 {
            const key: *const i32 = @ptrCast(@alignCast(key_ptr));
            const entry: *const Entry = @fieldParentPtr("node", node);
            return if (key.* < entry.key) -1 else if (key.* > entry.key) 1 else 0;
        }
    }.compare;

    var entries = [_]Entry{
        .{ .key = 30 },
        .{ .key = 10 },
        .{ .key = 20 },
        .{ .key = 40 },
    };
    var root = rbtree.RootCached.init();

    for (&entries) |*entry| {
        _ = rbtree.addCached(&entry.node, &root, less);
    }

    try std.testing.expectEqual(&entries[1].node, rbtree.rb_first_cached(&root));
    rbtree.eraseInitCached(&entries[1].node, &root);
    try std.testing.expect(rbtree.emptyNode(&entries[1].node));
    try std.testing.expectEqual(&entries[2].node, rbtree.rb_first_cached(&root));

    const lookup_key: i32 = 30;
    const found = rbtree.find(&lookup_key, &root.root, cmp_key) orelse unreachable;
    const found_entry: *const Entry = @fieldParentPtr("node", found);
    try std.testing.expectEqual(@as(i32, 30), found_entry.key);

    var reverse: [3]i32 = undefined;
    var count: usize = 0;
    var current = rbtree.rb_last(&root.root);
    while (current) |node| : (current = rbtree.rb_prev(node)) {
        const entry: *const Entry = @fieldParentPtr("node", node);
        reverse[count] = entry.key;
        count += 1;
    }

    try std.testing.expectEqual(@as(usize, 3), count);
    try std.testing.expectEqualSlices(i32, &[_]i32{ 40, 30, 20 }, reverse[0..count]);
}
