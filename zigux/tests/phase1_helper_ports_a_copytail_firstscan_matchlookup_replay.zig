const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

const DuplicateEntry = struct {
    key: i32,
    serial: usize,
    node: rbtree.Node = rbtree.Node.init(),
};

fn duplicateLess(lhs: *const rbtree.Node, rhs: *const rbtree.Node) bool {
    const lhs_entry: *const DuplicateEntry = @fieldParentPtr("node", lhs);
    const rhs_entry: *const DuplicateEntry = @fieldParentPtr("node", rhs);
    if (lhs_entry.key != rhs_entry.key) {
        return lhs_entry.key < rhs_entry.key;
    }
    return lhs_entry.serial < rhs_entry.serial;
}

fn duplicateCmp(key: *const anyopaque, node: *const rbtree.Node) i32 {
    const wanted: *const i32 = @ptrCast(@alignCast(key));
    const entry: *const DuplicateEntry = @fieldParentPtr("node", node);
    if (wanted.* < entry.key) return -1;
    if (wanted.* > entry.key) return 1;
    return 0;
}

test "lane06 replay keeps bitmap copy-tail helpers alias-aligned across masked tails and extension zeroing" {
    const tail_nbits = bitmap.bits_per_long + 5;
    const tail_src = [_]bitmap.Word{
        0x0123_4567_89ab_cdef,
        (@as(bitmap.Word, 1) << 2) | (@as(bitmap.Word, 1) << 4) | (@as(bitmap.Word, 1) << 11),
    };
    var direct_tail = [_]bitmap.Word{ ~@as(bitmap.Word, 0), ~@as(bitmap.Word, 0) };
    var alias_tail = direct_tail;

    bitmap.copyClearTail(&direct_tail, &tail_src, tail_nbits);
    bitmap.bitmap_copy_clear_tail(&alias_tail, &tail_src, tail_nbits);
    try std.testing.expectEqualSlices(bitmap.Word, &direct_tail, &alias_tail);
    try std.testing.expectEqual(@as(bitmap.Word, tail_src[1] & bitmap.lastWordMask(tail_nbits)), direct_tail[1]);

    const extend_count = bitmap.bits_per_long + 3;
    const extend_size = bitmap.bits_per_long * 2 + 4;
    const extend_src = [_]bitmap.Word{
        0xf0f0_f0f0_f0f0_f0f0,
        (@as(bitmap.Word, 1) << 1) | (@as(bitmap.Word, 1) << 2) | (@as(bitmap.Word, 1) << 9),
    };
    var direct_extend = [_]bitmap.Word{ ~@as(bitmap.Word, 0), ~@as(bitmap.Word, 0), ~@as(bitmap.Word, 0) };
    var alias_extend = direct_extend;

    bitmap.copyAndExtend(&direct_extend, &extend_src, extend_count, extend_size);
    bitmap.bitmap_copy_and_extend(&alias_extend, &extend_src, extend_count, extend_size);
    try std.testing.expectEqualSlices(bitmap.Word, &direct_extend, &alias_extend);
    try std.testing.expectEqual(@as(bitmap.Word, extend_src[1] & bitmap.lastWordMask(extend_count)), direct_extend[1]);
    try std.testing.expectEqual(@as(bitmap.Word, 0), direct_extend[2]);
}

test "lane06 replay keeps find_bit first-scan helpers aligned across tail masks and shared windows" {
    const nbits = find_bit.bits_per_long + 5;
    const set_map = [_]find_bit.Word{
        0,
        (@as(find_bit.Word, 1) << 2) | (@as(find_bit.Word, 1) << 7),
    };
    const and_lhs = [_]find_bit.Word{
        0,
        (@as(find_bit.Word, 1) << 2) | (@as(find_bit.Word, 1) << 4),
    };
    const and_rhs = [_]find_bit.Word{
        0,
        (@as(find_bit.Word, 1) << 2) | (@as(find_bit.Word, 1) << 9),
    };
    const andnot_rhs = [_]find_bit.Word{
        0,
        @as(find_bit.Word, 1) << 2,
    };
    const zero_map = [_]find_bit.Word{
        ~@as(find_bit.Word, 0),
        find_bit.lastWordMask(nbits) & ~(@as(find_bit.Word, 1) << 4),
    };

    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 2), find_bit.findFirstBit(&set_map, nbits));
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 2), find_bit.find_first_bit(&set_map, nbits));
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 2), find_bit._find_first_bit(&set_map, nbits));

    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 2), find_bit.findFirstAndBit(&and_lhs, &and_rhs, nbits));
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 2), find_bit.find_first_and_bit(&and_lhs, &and_rhs, nbits));
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 4), find_bit.findFirstAndNotBit(&and_lhs, &andnot_rhs, nbits));
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 4), find_bit.find_first_andnot_bit(&and_lhs, &andnot_rhs, nbits));

    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 4), find_bit.findFirstZeroBit(&zero_map, nbits));
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 4), find_bit.find_first_zero_bit(&zero_map, nbits));
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 4), find_bit._find_first_zero_bit(&zero_map, nbits));
}

test "lane06 replay keeps string match helpers C-string and newline aware" {
    const sysfs_haystack = [_][]const u8{
        "disabled",
        "auto\n",
        "manual",
    };
    const plain_haystack = [_][]const u8{
        "disabled",
        "manual",
        "auto",
    };
    const nul_auto = [_]u8{ 'a', 'u', 't', 'o', 0, 'x' };
    const nul_manual = [_]u8{ 'm', 'a', 'n', 'u', 'a', 'l', 0, 'y' };
    const prefix = [_]u8{ 'a', 'u', 't', 'o', 0, 'z' };
    const suffix = [_]u8{ 'u', 'a', 'l', 0, 'z' };

    try std.testing.expectEqual(@as(?usize, 1), string.sysfsMatchString(&sysfs_haystack, "auto"));
    try std.testing.expectEqual(@as(?usize, 1), string.sysfs_match_string(&sysfs_haystack, &nul_auto));
    try std.testing.expectEqual(@as(?usize, 1), string.matchString(&plain_haystack, &nul_manual));
    try std.testing.expectEqual(@as(?usize, 1), string.match_string(&plain_haystack, "manual"));
    try std.testing.expectEqual(@as(?usize, null), string.matchString(&plain_haystack, "missing"));

    try std.testing.expectEqual(@as(usize, 4), string.strHasPrefix(&nul_auto, &prefix));
    try std.testing.expectEqual(@as(usize, 4), string.str_has_prefix(&nul_auto, "auto"));
    try std.testing.expect(string.strstarts(&nul_auto, "auto"));
    try std.testing.expect(string.strEndsWith(&nul_manual, &suffix));
    try std.testing.expect(string.str_ends_with("manual", "ual"));
}

test "lane06 replay keeps rbtree duplicate lookup flow ordered across find and first-match helpers" {
    var entries = [_]DuplicateEntry{
        .{ .key = 10, .serial = 0 },
        .{ .key = 20, .serial = 1 },
        .{ .key = 10, .serial = 2 },
        .{ .key = 5, .serial = 3 },
        .{ .key = 10, .serial = 4 },
        .{ .key = 15, .serial = 5 },
    };
    var root = rbtree.Root.init();

    for (&entries) |*entry| {
        rbtree.add(&entry.node, &root, duplicateLess);
    }

    const present = @as(i32, 15);
    const present_node = rbtree.find(&present, &root, duplicateCmp) orelse return error.TestUnexpectedResult;
    const present_entry: *const DuplicateEntry = @fieldParentPtr("node", present_node);
    try std.testing.expectEqual(@as(usize, 5), present_entry.serial);

    const missing = @as(i32, 12);
    try std.testing.expect(rbtree.find(&missing, &root, duplicateCmp) == null);

    const duplicate = @as(i32, 10);
    const first_match = rbtree.findFirst(&duplicate, &root, duplicateCmp) orelse return error.TestUnexpectedResult;
    const first_entry: *const DuplicateEntry = @fieldParentPtr("node", first_match);
    try std.testing.expectEqual(@as(usize, 0), first_entry.serial);

    var serials: [3]usize = undefined;
    var count: usize = 0;
    var cursor: ?*rbtree.Node = first_match;
    while (cursor) |node| : (cursor = rbtree.nextMatch(&duplicate, node, duplicateCmp)) {
        const entry: *const DuplicateEntry = @fieldParentPtr("node", node);
        serials[count] = entry.serial;
        count += 1;
    }

    try std.testing.expectEqual(@as(usize, 3), count);
    try std.testing.expectEqualSlices(usize, &[_]usize{ 0, 2, 4 }, serials[0..count]);

    const smallest = rbtree.first(&root) orelse return error.TestUnexpectedResult;
    const smallest_entry: *const DuplicateEntry = @fieldParentPtr("node", smallest);
    try std.testing.expectEqual(@as(i32, 5), smallest_entry.key);
}
