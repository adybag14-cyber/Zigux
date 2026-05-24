const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

test "phase 1 helper ports A replay keeps bitmap copy aliases aligned on tail masking and extension" {
    const nbits = find_bit.bits_per_long + 5;
    const src = [_]bitmap.Word{ ~@as(bitmap.Word, 0), ~@as(bitmap.Word, 0) };

    var direct_copy = [_]bitmap.Word{ 0, 0 };
    var alias_copy = [_]bitmap.Word{ 0, 0 };
    bitmap.copyClearTail(&direct_copy, &src, nbits);
    bitmap.bitmap_copy_clear_tail(&alias_copy, &src, nbits);
    try std.testing.expectEqualSlices(bitmap.Word, &direct_copy, &alias_copy);
    try std.testing.expectEqual(find_bit.lastWordMask(nbits), direct_copy[1]);

    var direct_extended = [_]bitmap.Word{ 9, 9, 9 };
    var alias_extended = [_]bitmap.Word{ 7, 7, 7 };
    bitmap.copyAndExtend(&direct_extended, &src, nbits, nbits + find_bit.bits_per_long);
    bitmap.bitmap_copy_and_extend(&alias_extended, &src, nbits, nbits + find_bit.bits_per_long);
    try std.testing.expectEqualSlices(bitmap.Word, &direct_extended, &alias_extended);
    try std.testing.expectEqual(find_bit.lastWordMask(nbits), direct_extended[1]);
    try std.testing.expectEqual(@as(bitmap.Word, 0), direct_extended[2]);

    const lhs = [_]bitmap.Word{ 0b10110, 0 };
    const rhs = [_]bitmap.Word{ 0b01101, 0 };
    var direct_or = [_]bitmap.Word{ 0, 0 };
    var alias_or = [_]bitmap.Word{ 0, 0 };
    try std.testing.expectEqual(
        bitmap.weightedOr(&direct_or, &lhs, &rhs, 5),
        bitmap.bitmap_weighted_or(&alias_or, &lhs, &rhs, 5),
    );
    try std.testing.expectEqualSlices(bitmap.Word, &direct_or, &alias_or);
    try std.testing.expectEqual(@as(usize, 5), bitmap.weight(&direct_or, 5));

    var direct_xor = [_]bitmap.Word{ 0, 0 };
    var alias_xor = [_]bitmap.Word{ 0, 0 };
    try std.testing.expectEqual(
        bitmap.weightedXor(&direct_xor, &lhs, &rhs, 5),
        bitmap.bitmap_weighted_xor(&alias_xor, &lhs, &rhs, 5),
    );
    try std.testing.expectEqualSlices(bitmap.Word, &direct_xor, &alias_xor);
    try std.testing.expectEqual(@as(usize, 4), bitmap.weight(&direct_xor, 5));
}

test "phase 1 helper ports A replay keeps find_bit byte extraction and last-bit aliases aligned" {
    const byte_map = [_]find_bit.Word{
        @as(find_bit.Word, 0xaa) << @intCast(find_bit.bits_per_long - 8),
        @as(find_bit.Word, 0x11),
    };
    try std.testing.expectEqual(@as(u8, 0xaa), find_bit.getValue8(&byte_map, find_bit.bits_per_long - 8));
    try std.testing.expectEqual(@as(u8, 0x11), find_bit.getValue8(&byte_map, find_bit.bits_per_long));

    const nbits = find_bit.bits_per_long + 5;
    const tail_map = [_]find_bit.Word{
        @as(find_bit.Word, 1) << @intCast(find_bit.bits_per_long - 1),
        (@as(find_bit.Word, 1) << 3) | (@as(find_bit.Word, 1) << 10),
    };
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 3), find_bit.findLastBit(&tail_map, nbits));
    try std.testing.expectEqual(find_bit.findLastBit(&tail_map, nbits), find_bit.find_last_bit(&tail_map, nbits));
    try std.testing.expectEqual(find_bit.findLastBit(&tail_map, nbits), find_bit._find_last_bit(&tail_map, nbits));
}

test "phase 1 helper ports A replay keeps string parsing and match helpers aligned" {
    const parsed = string.memparse("0x20Ktail");
    try std.testing.expectEqual(@as(u64, 0x20 << 10), parsed.value);
    try std.testing.expectEqualStrings("tail", parsed.rest);

    const negative = string.memparse("-17 done");
    try std.testing.expectEqual(@as(u64, @bitCast(@as(i64, -17))), negative.value);
    try std.testing.expectEqualStrings(" done", negative.rest);

    const sysfs_haystack = [_][]const u8{
        "disabled",
        "auto\n",
        "manual",
    };
    try std.testing.expectEqual(
        string.sysfsMatchString(&sysfs_haystack, "auto"),
        string.sysfs_match_string(&sysfs_haystack, "auto"),
    );

    const plain_haystack = [_][]const u8{
        "disabled",
        "manual",
        "manual",
        "auto",
    };
    const cstr_auto = [_]u8{ 'a', 'u', 't', 'o', 0, 'x' };
    try std.testing.expectEqual(
        string.matchString(&plain_haystack, &cstr_auto),
        string.match_string(&plain_haystack, &cstr_auto),
    );

    const bounded = [_]u8{ 'a', 'b', 0, 'c', 'd' };
    try std.testing.expectEqual(@as(?usize, 1), string.strnchr(&bounded, bounded.len, 'b'));
    try std.testing.expectEqual(@as(?usize, null), string.strnchr(&bounded, 2, 0));
}

test "phase 1 helper ports A replay keeps rbtree ordered lookup helpers stable on duplicate keys" {
    const Entry = struct {
        key: i32,
        serial: usize,
        node: rbtree.Node = rbtree.Node.init(),
    };

    const less = struct {
        fn compare(lhs: *const rbtree.Node, rhs: *const rbtree.Node) bool {
            const lhs_entry: *const Entry = @fieldParentPtr("node", lhs);
            const rhs_entry: *const Entry = @fieldParentPtr("node", rhs);
            if (lhs_entry.key != rhs_entry.key) return lhs_entry.key < rhs_entry.key;
            return lhs_entry.serial < rhs_entry.serial;
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
        .{ .key = 10, .serial = 0 },
        .{ .key = 5, .serial = 1 },
        .{ .key = 10, .serial = 2 },
        .{ .key = 15, .serial = 3 },
        .{ .key = 10, .serial = 4 },
    };
    var root = rbtree.Root.init();
    for (&entries) |*entry| {
        rbtree.add(&entry.node, &root, less);
    }

    const wanted = @as(i32, 10);
    const found = rbtree.find(&wanted, &root, key_cmp) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(i32, 10), @as(*const Entry, @fieldParentPtr("node", found)).key);

    const first = rbtree.findFirst(&wanted, &root, key_cmp) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(usize, 0), @as(*const Entry, @fieldParentPtr("node", first)).serial);

    var match_serials: [3]usize = undefined;
    var idx: usize = 0;
    var current: ?*rbtree.Node = first;
    while (current) |node| {
        const entry: *const Entry = @fieldParentPtr("node", node);
        match_serials[idx] = entry.serial;
        idx += 1;
        current = rbtree.nextMatch(&wanted, node, key_cmp);
    }

    try std.testing.expectEqualSlices(usize, &[_]usize{ 0, 2, 4 }, match_serials[0..idx]);

    var iter = rbtree.matchIterator(&wanted, &root, key_cmp);
    var iter_serials: [3]usize = undefined;
    idx = 0;
    while (iter.next()) |node| {
        const entry: *const Entry = @fieldParentPtr("node", node);
        iter_serials[idx] = entry.serial;
        idx += 1;
    }
    try std.testing.expectEqualSlices(usize, match_serials[0..idx], iter_serials[0..idx]);
}
