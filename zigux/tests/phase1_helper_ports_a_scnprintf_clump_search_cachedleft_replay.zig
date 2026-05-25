const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

test "lane06 replay keeps bitmap range formatting aligned across a word boundary" {
    const nbits = bitmap.bits_per_long + 8;
    var words = [_]bitmap.Word{ 0, 0 };
    bitmap.setRange(&words, bitmap.bits_per_long - 1, 3);
    bitmap.setRange(&words, bitmap.bits_per_long + 6, 1);

    var direct_buffer = [_]u8{0} ** 64;
    var alias_buffer = [_]u8{0} ** 64;
    const direct_len = bitmap.scnprintf(&words, nbits, &direct_buffer);
    const alias_len = bitmap.bitmap_scnprintf(&words, nbits, &alias_buffer);

    var expected_storage: [32]u8 = undefined;
    const expected = try std.fmt.bufPrint(
        &expected_storage,
        "{d}-{d},{d}",
        .{ bitmap.bits_per_long - 1, bitmap.bits_per_long + 1, bitmap.bits_per_long + 6 },
    );

    try std.testing.expectEqual(expected.len, direct_len);
    try std.testing.expectEqual(direct_len, alias_len);
    try std.testing.expectEqualStrings(expected, direct_buffer[0..direct_len]);
    try std.testing.expectEqualStrings(expected, alias_buffer[0..alias_len]);

    var truncated = [_]u8{ '#', '#', '#', '#', '#', '#' };
    const truncated_len = bitmap.bitmap_scnprintf(&words, nbits, &truncated);
    try std.testing.expectEqual(@as(usize, truncated.len - 1), truncated_len);
    try std.testing.expectEqual(@as(u8, 0), truncated[truncated.len - 1]);
}

test "lane06 replay keeps tail clump bytes stable and preserves caller state past the end" {
    const nbits = find_bit.bits_per_long + 5;
    const tail_bits = (@as(find_bit.Word, 1) << 1) | (@as(find_bit.Word, 1) << 4);
    const words = [_]find_bit.Word{ 0, tail_bits };

    var direct_clump: u8 = 0;
    var alias_clump: u8 = 0;
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long), find_bit.findFirstClump8(&direct_clump, &words, nbits));
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long), find_bit.find_first_clump8(&alias_clump, &words, nbits));
    try std.testing.expectEqual(@as(u8, 0b0001_0010), direct_clump);
    try std.testing.expectEqual(direct_clump, alias_clump);

    var preserved: u8 = direct_clump;
    try std.testing.expectEqual(@as(usize, nbits), find_bit.findNextClump8(&preserved, &words, nbits, find_bit.bits_per_long + 5));
    try std.testing.expectEqual(direct_clump, preserved);
}

test "lane06 replay keeps bounded string prefix copy and sysfs helpers pinned to C-string edges" {
    var padded = [_]u8{ 9, 9, 9, 9, 9 };
    var alias_padded = [_]u8{ 8, 8, 8, 8, 8 };
    try std.testing.expectEqual(@as(isize, 2), string.strscpyPad(&padded, &[_]u8{ 'o', 'k', 0, 'x' }));
    try std.testing.expectEqual(@as(isize, 2), string.strscpy_pad(&alias_padded, &[_]u8{ 'o', 'k', 0, 'x' }));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'o', 'k', 0, 0, 0 }, &padded);
    try std.testing.expectEqualSlices(u8, &padded, &alias_padded);

    try std.testing.expectEqual(@as(usize, 2), string.strHasPrefix(&[_]u8{ 'o', 'k', 0, 'x' }, "ok"));
    try std.testing.expectEqual(@as(usize, 0), string.strHasPrefix(&[_]u8{ 'o', 'k', 0, 'x' }, "okx"));

    const sysfs_values = [_][]const u8{ "off", "auto\n", "auto", "on" };
    try std.testing.expectEqual(@as(?usize, 1), string.sysfsMatchString(&sysfs_values, "auto"));
    try std.testing.expectEqual(@as(?usize, 2), string.matchString(&[_][]const u8{ "off", "auto", "on" }, "on"));

    var dirty = [_]u8{0} ** 24;
    dirty[std.mem.alignForward(usize, 5, @sizeOf(usize))] = 7;
    const dirty_idx = std.mem.alignForward(usize, 5, @sizeOf(usize));
    try std.testing.expectEqual(@as(?usize, dirty_idx), string.memchrInv(dirty[0..], 0));
    try std.testing.expectEqual(@as(?usize, dirty_idx), string.memchr_inv(dirty[0..], 0));
}

test "lane06 replay keeps cached leftmost handoff stable across duplicate probes and replacement" {
    const Entry = struct {
        key: i32,
        serial: i32,
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

    const node_cmp = struct {
        fn compare(lhs: *const rbtree.Node, rhs: *const rbtree.Node) i32 {
            const lhs_entry: *const Entry = @fieldParentPtr("node", lhs);
            const rhs_entry: *const Entry = @fieldParentPtr("node", rhs);
            if (lhs_entry.key < rhs_entry.key) return -1;
            if (lhs_entry.key > rhs_entry.key) return 1;
            return 0;
        }
    }.compare;

    const key_cmp = struct {
        fn compare(key: *const anyopaque, node: *const rbtree.Node) i32 {
            const wanted: *const i32 = @ptrCast(@alignCast(key));
            const entry: *const Entry = @fieldParentPtr("node", node);
            if (wanted.* < entry.key) return -1;
            if (wanted.* > entry.key) return 1;
            return 0;
        }
    }.compare;

    var entries = [_]Entry{
        .{ .key = 5, .serial = 0 },
        .{ .key = 10, .serial = 1 },
        .{ .key = 10, .serial = 2 },
        .{ .key = 15, .serial = 3 },
    };
    var replacement = Entry{ .key = 10, .serial = 9 };
    var duplicate_probe = Entry{ .key = 10, .serial = 99 };
    var root = rbtree.RootCached.init();

    for (&entries) |*entry| {
        _ = rbtree.rb_add_cached(&entry.node, &root, less);
    }

    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[0].node), rbtree.rb_first_cached(&root));

    const duplicate = rbtree.rb_find_add_cached(&duplicate_probe.node, &root, node_cmp) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(*rbtree.Node, &entries[1].node), duplicate);
    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[0].node), rbtree.rb_first_cached(&root));

    const promoted = rbtree.rb_erase_cached(&entries[0].node, &root) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(*rbtree.Node, &entries[1].node), promoted);
    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[1].node), rbtree.rb_first_cached(&root));

    rbtree.rb_replace_node_cached(&entries[2].node, &replacement.node, &root);
    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[1].node), rbtree.rb_first_cached(&root));

    const wanted = @as(i32, 10);
    var iter = rbtree.matchIterator(&wanted, &root.root, key_cmp);
    var seen: [2]i32 = undefined;
    var count: usize = 0;
    while (iter.next()) |node| {
        const entry: *const Entry = @fieldParentPtr("node", node);
        seen[count] = entry.serial;
        count += 1;
    }

    try std.testing.expectEqual(@as(usize, 2), count);
    try std.testing.expectEqualSlices(i32, &[_]i32{ 1, 9 }, seen[0..count]);
}
