const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

const CachedEntry = struct {
    key: i32,
    serial: usize,
    node: rbtree.Node = rbtree.Node.init(),
};

fn cachedLess(lhs: *const rbtree.Node, rhs: *const rbtree.Node) bool {
    const lhs_entry: *const CachedEntry = @fieldParentPtr("node", lhs);
    const rhs_entry: *const CachedEntry = @fieldParentPtr("node", rhs);
    if (lhs_entry.key != rhs_entry.key) {
        return lhs_entry.key < rhs_entry.key;
    }
    return lhs_entry.serial < rhs_entry.serial;
}

fn cachedKeyCmp(key: *const anyopaque, node: *const rbtree.Node) i32 {
    const wanted: *const i32 = @ptrCast(@alignCast(key));
    const entry: *const CachedEntry = @fieldParentPtr("node", node);
    if (wanted.* < entry.key) return -1;
    if (wanted.* > entry.key) return 1;
    return 0;
}

fn appendSerials(serials: []usize, count: *usize, node: *const rbtree.Node) void {
    const entry: *const CachedEntry = @fieldParentPtr("node", node);
    serials[count.*] = entry.serial;
    count.* += 1;
}

test "lane06 replay keeps bitmap state and formatting aliases aligned across tail windows" {
    const nbits = bitmap.bits_per_long + 6;
    const in_range_tail = (@as(bitmap.Word, 1) << 1) | (@as(bitmap.Word, 1) << 5);
    const lhs = [_]bitmap.Word{ 0b10101, in_range_tail | (@as(bitmap.Word, 1) << 9) };
    const rhs = [_]bitmap.Word{ 0b10101, in_range_tail | (@as(bitmap.Word, 1) << 10) };
    const empty_tail = [_]bitmap.Word{ 0, @as(bitmap.Word, 1) << 9 };
    const full_tail = [_]bitmap.Word{ ~@as(bitmap.Word, 0), bitmap.lastWordMask(nbits) | (@as(bitmap.Word, 1) << 10) };

    try std.testing.expect(bitmap.bitmap_equal(&lhs, &rhs, nbits));
    try std.testing.expect(bitmap.bitmap_intersects(&lhs, &rhs, nbits));
    try std.testing.expect(bitmap.bitmap_subset(&rhs, &lhs, nbits));
    try std.testing.expectEqual(@as(usize, 5), bitmap.bitmap_weight(&lhs, nbits));
    try std.testing.expect(bitmap.bitmap_empty(&empty_tail, nbits));
    try std.testing.expect(bitmap.bitmap_full(&full_tail, nbits));

    var direct = [_]bitmap.Word{ 0, 0 };
    var alias = [_]bitmap.Word{ 0, 0 };
    bitmap.setRange(&direct, bitmap.bits_per_long - 1, 3);
    bitmap.bitmap_set(&alias, bitmap.bits_per_long - 1, 3);
    try std.testing.expectEqualSlices(bitmap.Word, &direct, &alias);

    bitmap.clearRange(&direct, bitmap.bits_per_long, 1);
    bitmap.bitmap_clear(&alias, bitmap.bits_per_long, 1);
    try std.testing.expectEqualSlices(bitmap.Word, &direct, &alias);

    var direct_buffer: [64]u8 = undefined;
    var alias_buffer: [64]u8 = undefined;
    const direct_len = bitmap.scnprintf(&direct, nbits, &direct_buffer);
    const alias_len = bitmap.bitmap_scnprintf(&alias, nbits, &alias_buffer);

    var expected: [32]u8 = undefined;
    const expected_text = try std.fmt.bufPrint(
        &expected,
        "{d},{d}",
        .{ bitmap.bits_per_long - 1, bitmap.bits_per_long + 1 },
    );
    try std.testing.expectEqual(direct_len, alias_len);
    try std.testing.expectEqualStrings(expected_text, direct_buffer[0..direct_len]);
    try std.testing.expectEqualStrings(expected_text, alias_buffer[0..alias_len]);

    var zero_length_backing = [_]u8{0xcc};
    try std.testing.expectEqual(@as(usize, 0), bitmap.bitmap_scnprintf(&direct, nbits, zero_length_backing[0..0]));
    try std.testing.expectEqual(@as(u8, 0xcc), zero_length_backing[0]);
}

test "lane06 replay keeps find_bit clump and last-bit helpers byte-aligned and tail-clamped" {
    const byte_offset = find_bit.bits_per_long - 8;
    const byte_map = [_]find_bit.Word{
        @as(find_bit.Word, 0xa5) << @intCast(byte_offset),
        @as(find_bit.Word, 0x11),
    };
    try std.testing.expectEqual(@as(u8, 0xa5), find_bit.getValue8(&byte_map, byte_offset));
    try std.testing.expectEqual(@as(u8, 0x11), find_bit.getValue8(&byte_map, find_bit.bits_per_long));

    const nbits = find_bit.bits_per_long + 5;
    const tail_map = [_]find_bit.Word{ 0, (@as(find_bit.Word, 1) << 3) | (@as(find_bit.Word, 1) << 6) };

    var first_clump: u8 = 0;
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long), find_bit.findFirstClump8(&first_clump, &tail_map, nbits));
    try std.testing.expectEqual(@as(u8, 0b0000_1000), first_clump);

    var alias_clump: u8 = 0x5a;
    try std.testing.expectEqual(@as(usize, nbits), find_bit.find_next_clump8(&alias_clump, &tail_map, nbits, nbits));
    try std.testing.expectEqual(@as(u8, 0x5a), alias_clump);

    var internal_clump: u8 = 0xa5;
    try std.testing.expectEqual(@as(usize, nbits), find_bit._find_next_clump8(&internal_clump, &tail_map, nbits, nbits + 3));
    try std.testing.expectEqual(@as(u8, 0xa5), internal_clump);

    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 3), find_bit.findLastBit(&tail_map, nbits));
    try std.testing.expectEqual(find_bit.findLastBit(&tail_map, nbits), find_bit.find_last_bit(&tail_map, nbits));
    try std.testing.expectEqual(find_bit.findLastBit(&tail_map, nbits), find_bit._find_last_bit(&tail_map, nbits));
}

test "lane06 replay keeps shared string prefix suffix and match helpers C-string aware" {
    var padded = [_]u8{ 'x', 'x', 'x', 'x' };
    try std.testing.expectEqual(@as(isize, 2), string.strscpy_pad(&padded, &[_]u8{ 'o', 'k', 0, '!' }));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'o', 'k', 0, 0 }, &padded);

    try std.testing.expect(string.streq(&[_]u8{ 'n', 'o', 'd', 'e', 0, 'x' }, "node"));
    try std.testing.expect(!string.streq(&[_]u8{ 'n', 'o', 'd', 'e', 0, 'x' }, "mode"));
    try std.testing.expect(string.sysfs_streq("auto\n", "auto"));
    try std.testing.expect(!string.sysfs_streq("auto\n", "manual"));

    try std.testing.expectEqual(@as(usize, 3), string.strHasPrefix(&[_]u8{ 'a', 'b', 'c', 0, 'x' }, "abc"));
    try std.testing.expectEqual(@as(usize, 3), string.str_has_prefix("abcdef", "abc"));
    try std.testing.expect(string.strstarts("kernel", "ker"));
    try std.testing.expect(string.strEndsWith(&[_]u8{ 'a', 'b', 'c', 0, 'x' }, "bc"));
    try std.testing.expect(string.str_ends_with("abcdef", "def"));

    const sysfs_haystack = [_][]const u8{ "off", "auto\n", "on" };
    try std.testing.expectEqual(@as(?usize, 1), string.sysfsMatchString(sysfs_haystack[0..], "auto"));
    try std.testing.expectEqual(@as(?usize, null), string.sysfsMatchString(sysfs_haystack[0..], "manual"));

    const match_haystack = [_][]const u8{
        &[_]u8{ 'a', 'l', 'p', 'h', 'a', 0, 'x' },
        "beta",
        "gamma",
    };
    try std.testing.expectEqual(@as(?usize, 0), string.matchString(match_haystack[0..], "alpha"));
    try std.testing.expectEqual(@as(?usize, 1), string.matchString(match_haystack[0..], "beta"));
    try std.testing.expectEqual(@as(?usize, null), string.matchString(match_haystack[0..], "alphabet"));

    try std.testing.expectEqual(@as(?usize, 1), string.strnchr("abc", 2, 'b'));
    try std.testing.expectEqual(@as(?usize, null), string.strnchr("abc", 1, 'b'));
}

test "lane06 replay keeps cached rbtree duplicate iteration and reset helpers aligned" {
    var primary_entries = [_]CachedEntry{
        .{ .key = 10, .serial = 0 },
        .{ .key = 20, .serial = 1 },
        .{ .key = 10, .serial = 2 },
        .{ .key = 5, .serial = 3 },
        .{ .key = 10, .serial = 4 },
        .{ .key = 15, .serial = 5 },
    };
    var alias_entries = [_]CachedEntry{
        .{ .key = 10, .serial = 0 },
        .{ .key = 20, .serial = 1 },
        .{ .key = 10, .serial = 2 },
        .{ .key = 5, .serial = 3 },
        .{ .key = 10, .serial = 4 },
        .{ .key = 15, .serial = 5 },
    };
    var primary_root = rbtree.RootCached.init();
    var alias_root = rbtree.RootCached.init();

    for (&primary_entries, &alias_entries) |*primary_entry, *alias_entry| {
        _ = rbtree.addCached(&primary_entry.node, &primary_root, cachedLess);
        _ = rbtree.rb_add_cached(&alias_entry.node, &alias_root, cachedLess);
    }

    const duplicate = @as(i32, 10);
    var primary_iter = rbtree.matchIterator(&duplicate, &primary_root.root, cachedKeyCmp);
    var primary_serials: [3]usize = undefined;
    var primary_count: usize = 0;
    while (primary_iter.next()) |node| {
        appendSerials(&primary_serials, &primary_count, node);
    }

    const alias_first = rbtree.findFirst(&duplicate, &alias_root.root, cachedKeyCmp) orelse return error.TestUnexpectedResult;
    var alias_serials: [3]usize = undefined;
    var alias_count: usize = 0;
    var alias_cursor: ?*rbtree.Node = alias_first;
    while (alias_cursor) |node| {
        appendSerials(&alias_serials, &alias_count, node);
        alias_cursor = rbtree.nextMatch(&duplicate, node, cachedKeyCmp);
    }

    try std.testing.expectEqual(@as(usize, 3), primary_count);
    try std.testing.expectEqual(@as(usize, 3), alias_count);
    try std.testing.expectEqualSlices(usize, &[_]usize{ 0, 2, 4 }, primary_serials[0..primary_count]);
    try std.testing.expectEqualSlices(usize, primary_serials[0..primary_count], alias_serials[0..alias_count]);

    rbtree.eraseInitCached(&primary_entries[3].node, &primary_root);
    rbtree.rb_erase_init_cached(&alias_entries[3].node, &alias_root);
    try std.testing.expect(rbtree.emptyNode(&primary_entries[3].node));
    try std.testing.expect(rbtree.emptyNode(&alias_entries[3].node));
    try std.testing.expectEqual(rbtree.first(&primary_root.root), rbtree.firstCached(&primary_root));
    try std.testing.expectEqual(rbtree.first(&alias_root.root), rbtree.rb_first_cached(&alias_root));

    const primary_first = rbtree.firstCached(&primary_root) orelse return error.TestUnexpectedResult;
    const alias_first_after_reset = rbtree.rb_first_cached(&alias_root) orelse return error.TestUnexpectedResult;
    const primary_first_entry: *const CachedEntry = @fieldParentPtr("node", primary_first);
    const alias_first_entry: *const CachedEntry = @fieldParentPtr("node", alias_first_after_reset);
    try std.testing.expectEqual(primary_first_entry.key, alias_first_entry.key);
    try std.testing.expectEqual(primary_first_entry.serial, alias_first_entry.serial);
}
