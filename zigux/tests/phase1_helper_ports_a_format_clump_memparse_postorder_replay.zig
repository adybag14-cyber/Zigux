const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

test "phase1 helper ports A bitmap range-format aliases keep cross-word rendering aligned" {
    const nbits = bitmap.bits_per_long + 6;

    var direct = [_]bitmap.Word{ 0, 0 };
    var alias = [_]bitmap.Word{ 0, 0 };
    bitmap.setRange(&direct, bitmap.bits_per_long - 2, 5);
    bitmap.bitmap_set(&alias, bitmap.bits_per_long - 2, 5);
    try std.testing.expectEqualSlices(bitmap.Word, &direct, &alias);

    var direct_buffer: [64]u8 = undefined;
    var alias_buffer: [64]u8 = undefined;
    const direct_len = bitmap.scnprintf(&direct, nbits, &direct_buffer);
    const alias_len = bitmap.bitmap_scnprintf(&alias, nbits, &alias_buffer);
    try std.testing.expectEqual(direct_len, alias_len);
    try std.testing.expectEqualStrings(direct_buffer[0..direct_len], alias_buffer[0..alias_len]);

    var expected: [32]u8 = undefined;
    const expected_text = try std.fmt.bufPrint(
        &expected,
        "{d}-{d}",
        .{ bitmap.bits_per_long - 2, bitmap.bits_per_long + 2 },
    );
    try std.testing.expectEqualStrings(expected_text, direct_buffer[0..direct_len]);

    bitmap.clearRange(&direct, bitmap.bits_per_long - 1, 3);
    bitmap.bitmap_clear(&alias, bitmap.bits_per_long - 1, 3);
    try std.testing.expectEqualSlices(bitmap.Word, &direct, &alias);
    try std.testing.expectEqual(@as(bitmap.Word, @as(bitmap.Word, 1) << (bitmap.bits_per_long - 2)), direct[0]);
    try std.testing.expectEqual(@as(bitmap.Word, @as(bitmap.Word, 1) << 2), direct[1]);
}

test "phase1 helper ports A find_bit clump and last-bit aliases keep tail masks aligned" {
    const nbits = find_bit.bits_per_long + 5;
    const bitmap_words = [_]find_bit.Word{
        0,
        (@as(find_bit.Word, 1) << 3) | (@as(find_bit.Word, 1) << 9),
    };

    var direct_clump: u8 = 0;
    var alias_clump: u8 = 0;
    var underscore_clump: u8 = 0;
    try std.testing.expectEqual(
        @as(usize, find_bit.bits_per_long),
        find_bit.findFirstClump8(&direct_clump, &bitmap_words, nbits),
    );
    try std.testing.expectEqual(
        @as(usize, find_bit.bits_per_long),
        find_bit.find_first_clump8(&alias_clump, &bitmap_words, nbits),
    );
    try std.testing.expectEqual(
        @as(usize, find_bit.bits_per_long),
        find_bit._find_first_clump8(&underscore_clump, &bitmap_words, nbits),
    );
    try std.testing.expectEqual(@as(u8, 0b0000_1000), direct_clump);
    try std.testing.expectEqual(direct_clump, alias_clump);
    try std.testing.expectEqual(direct_clump, underscore_clump);
    try std.testing.expectEqual(@as(u8, 0b0000_1000), find_bit.getValue8(&bitmap_words, find_bit.bits_per_long));

    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 3), find_bit.findLastBit(&bitmap_words, nbits));
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 3), find_bit.find_last_bit(&bitmap_words, nbits));
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 3), find_bit._find_last_bit(&bitmap_words, nbits));

    var next_clump: u8 = 0xaa;
    try std.testing.expectEqual(@as(usize, nbits), find_bit.findNextClump8(&next_clump, &bitmap_words, nbits, nbits));
    try std.testing.expectEqual(@as(u8, 0xaa), next_clump);
    try std.testing.expectEqual(@as(usize, nbits), find_bit.find_next_clump8(&next_clump, &bitmap_words, nbits, nbits + 7));
    try std.testing.expectEqual(@as(usize, nbits), find_bit._find_next_clump8(&next_clump, &bitmap_words, nbits, nbits + 11));
}

test "phase1 helper ports A string memparse and matcher aliases keep C-string boundaries aligned" {
    const signed = string.memparse("-16 trailing");
    try std.testing.expectEqual(@as(u64, @bitCast(@as(i64, -16))), signed.value);
    try std.testing.expectEqualStrings(" trailing", signed.rest);

    const saturated = string.memparse("18446744073709551615Ktail");
    try std.testing.expectEqual(std.math.maxInt(u64), saturated.value);
    try std.testing.expectEqualStrings("tail", saturated.rest);

    const sysfs_haystack = [_][]const u8{ "off", "auto\n", "auto", "on" };
    try std.testing.expectEqual(@as(?usize, 1), string.sysfsMatchString(sysfs_haystack[0..], "auto"));
    try std.testing.expectEqual(@as(?usize, 1), string.sysfs_match_string(sysfs_haystack[0..], "auto"));

    const match_haystack = [_][]const u8{
        &[_]u8{ 'a', 'l', 'p', 'h', 'a', 0, 'x' },
        "beta",
    };
    try std.testing.expectEqual(@as(?usize, 0), string.matchString(match_haystack[0..], "alpha"));
    try std.testing.expectEqual(@as(?usize, 0), string.match_string(match_haystack[0..], "alpha"));

    var dirty = [_]u8{0} ** 24;
    dirty[@sizeOf(usize)] = 1;
    try std.testing.expectEqual(@as(?usize, @sizeOf(usize)), string.memchrInv(dirty[0..], 0));
    try std.testing.expectEqual(string.memchrInv(dirty[0..], 0), string.memchr_inv(dirty[0..], 0));

    const dup = try string.memdup(std.testing.allocator, "abc");
    defer std.testing.allocator.free(dup);
    try std.testing.expectEqualStrings("abc", dup);

    try std.testing.expectEqual(@as(?usize, 1), string.strnchr("abc", 2, 'b'));
    try std.testing.expectEqual(@as(?usize, null), string.strnchr(&[_]u8{ 'a', 0, 'b' }, 3, 'b'));
}

test "phase1 helper ports A rbtree duplicate iterators and postorder aliases stay in lockstep" {
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
        .{ .key = 20, .serial = 1 },
        .{ .key = 10, .serial = 2 },
        .{ .key = 5, .serial = 3 },
        .{ .key = 10, .serial = 4 },
        .{ .key = 15, .serial = 5 },
    };
    var root = rbtree.Root.init();
    for (&entries) |*entry| {
        rbtree.add(&entry.node, &root, less);
    }

    const duplicate = @as(i32, 10);
    const first_match = rbtree.findFirst(&duplicate, &root, key_cmp) orelse return error.TestUnexpectedResult;
    const first_entry: *const Entry = @fieldParentPtr("node", first_match);
    try std.testing.expectEqual(@as(usize, 0), first_entry.serial);

    var next_serials: [3]usize = undefined;
    var next_count: usize = 0;
    var cursor = first_match;
    while (true) {
        const entry: *const Entry = @fieldParentPtr("node", cursor);
        next_serials[next_count] = entry.serial;
        next_count += 1;
        cursor = rbtree.nextMatch(&duplicate, cursor, key_cmp) orelse break;
    }
    try std.testing.expectEqual(@as(usize, 3), next_count);
    try std.testing.expectEqualSlices(usize, &[_]usize{ 0, 2, 4 }, next_serials[0..next_count]);

    var iter = rbtree.matchIterator(&duplicate, &root, key_cmp);
    var iter_serials: [3]usize = undefined;
    var iter_count: usize = 0;
    while (iter.next()) |node| {
        const entry: *const Entry = @fieldParentPtr("node", node);
        iter_serials[iter_count] = entry.serial;
        iter_count += 1;
    }
    try std.testing.expectEqual(@as(usize, 3), iter_count);
    try std.testing.expectEqualSlices(usize, next_serials[0..next_count], iter_serials[0..iter_count]);

    var postorder_serials: [6]usize = undefined;
    var postorder_count: usize = 0;
    var postorder = rbtree.firstPostorder(&root);
    while (postorder) |node| {
        const entry: *const Entry = @fieldParentPtr("node", node);
        postorder_serials[postorder_count] = entry.serial;
        postorder_count += 1;
        postorder = rbtree.nextPostorder(node);
    }
    try std.testing.expectEqual(@as(usize, entries.len), postorder_count);
    try std.testing.expect(postorder_count >= 3);
    try std.testing.expect(rbtree.nextPostorder(null) == null);
}
