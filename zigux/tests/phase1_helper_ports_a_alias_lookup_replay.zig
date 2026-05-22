const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

test "phase1 helper ports A bitmap aliases keep weighted range output aligned" {
    const nbits = bitmap.bits_per_long + 7;

    var lhs = [_]bitmap.Word{ 0, 0 };
    var rhs = [_]bitmap.Word{ 0, 0 };
    bitmap.setRange(&lhs, 1, 3);
    bitmap.bitmap_set(&rhs, 2, 3);
    lhs[1] |= (@as(bitmap.Word, 1) << 1) | (@as(bitmap.Word, 1) << 10);
    rhs[1] |= (@as(bitmap.Word, 1) << 4) | (@as(bitmap.Word, 1) << 11);

    var direct_or = [_]bitmap.Word{ 0, 0 };
    var alias_or = [_]bitmap.Word{ 0, 0 };
    const direct_or_weight = bitmap.weightedOr(&direct_or, &lhs, &rhs, nbits);
    const alias_or_weight = bitmap.bitmap_weighted_or(&alias_or, &lhs, &rhs, nbits);
    try std.testing.expectEqual(direct_or_weight, alias_or_weight);
    try std.testing.expectEqualSlices(bitmap.Word, &direct_or, &alias_or);
    try std.testing.expectEqual(@as(usize, 6), direct_or_weight);

    var direct_andnot = [_]bitmap.Word{ 0, 0 };
    var alias_andnot = [_]bitmap.Word{ 0, 0 };
    try std.testing.expectEqual(
        bitmap.andNotBits(&direct_andnot, &direct_or, &rhs, nbits),
        bitmap.bitmap_andnot(&alias_andnot, &direct_or, &rhs, nbits),
    );
    try std.testing.expectEqualSlices(bitmap.Word, &direct_andnot, &alias_andnot);

    var direct_range = [_]bitmap.Word{ 0, 0 };
    var alias_range = [_]bitmap.Word{ 0, 0 };
    bitmap.setRange(&direct_range, 1, 5);
    bitmap.bitmap_set(&alias_range, 1, 5);
    bitmap.clearRange(&direct_range, 3, 1);
    bitmap.bitmap_clear(&alias_range, 3, 1);
    try std.testing.expectEqualSlices(bitmap.Word, &direct_range, &alias_range);

    var rendered: [64]u8 = undefined;
    var alias_rendered: [64]u8 = undefined;
    const rendered_len = bitmap.scnprintf(&alias_or, nbits, &rendered);
    const alias_len = bitmap.bitmap_scnprintf(&alias_or, nbits, &alias_rendered);
    try std.testing.expectEqual(rendered_len, alias_len);
    try std.testing.expectEqualStrings(rendered[0..rendered_len], alias_rendered[0..alias_len]);
    try std.testing.expectEqualStrings("1-4,65,68", rendered[0..rendered_len]);
}

test "phase1 helper ports A find_bit aliases keep shared tail scans and clumps aligned" {
    const nbits = find_bit.bits_per_long + 7;
    const boundary = find_bit.bits_per_long;

    const lhs = [_]find_bit.Word{
        @as(find_bit.Word, 1) << 5,
        (@as(find_bit.Word, 1) << 1) | (@as(find_bit.Word, 1) << 6) | (@as(find_bit.Word, 1) << 10),
    };
    const rhs = [_]find_bit.Word{
        0,
        (@as(find_bit.Word, 1) << 1) | (@as(find_bit.Word, 1) << 4) | (@as(find_bit.Word, 1) << 10),
    };

    try std.testing.expectEqual(@as(usize, boundary + 1), find_bit.findFirstAndBit(&lhs, &rhs, nbits));
    try std.testing.expectEqual(@as(usize, boundary + 1), find_bit.find_first_and_bit(&lhs, &rhs, nbits));
    try std.testing.expectEqual(@as(usize, nbits), find_bit.findNextAndBit(&lhs, &rhs, nbits, boundary + 2));
    try std.testing.expectEqual(@as(usize, nbits), find_bit.find_next_and_bit(&lhs, &rhs, nbits, boundary + 2));

    try std.testing.expectEqual(@as(usize, 5), find_bit.findFirstAndNotBit(&lhs, &rhs, nbits));
    try std.testing.expectEqual(@as(usize, 5), find_bit.find_first_andnot_bit(&lhs, &rhs, nbits));
    try std.testing.expectEqual(@as(usize, boundary + 6), find_bit.findNextAndNotBit(&lhs, &rhs, nbits, 6));
    try std.testing.expectEqual(@as(usize, boundary + 6), find_bit.find_next_andnot_bit(&lhs, &rhs, nbits, 6));
    try std.testing.expectEqual(@as(usize, boundary + 6), find_bit.findLastBit(&lhs, nbits));
    try std.testing.expectEqual(@as(usize, boundary + 6), find_bit.find_last_bit(&lhs, nbits));

    var direct_clump: u8 = 0;
    var alias_clump: u8 = 0;
    try std.testing.expectEqual(@as(usize, boundary), find_bit.findNextClump8(&direct_clump, &lhs, nbits, boundary + 1));
    try std.testing.expectEqual(@as(usize, boundary), find_bit.find_next_clump8(&alias_clump, &lhs, nbits, boundary + 1));
    try std.testing.expectEqual(direct_clump, alias_clump);
    try std.testing.expectEqual(@as(u8, 0b0100_0010), direct_clump);
}

test "phase1 helper ports A string aliases keep lookup and dirty-byte helpers aligned" {
    var padded = [_]u8{ 1, 1, 1, 1, 1, 1 };
    var alias_padded = [_]u8{ 1, 1, 1, 1, 1, 1 };
    try std.testing.expectEqual(@as(isize, 2), string.strscpyPad(padded[0..], &[_]u8{ 'o', 'k', 0, 'x' }));
    try std.testing.expectEqual(@as(isize, 2), string.strscpy_pad(alias_padded[0..], &[_]u8{ 'o', 'k', 0, 'y' }));
    try std.testing.expectEqualSlices(u8, &padded, &alias_padded);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'o', 'k', 0, 0, 0, 0 }, padded[0..]);

    try std.testing.expectEqual(@as(usize, 3), string.strHasPrefix("kernel", "ker"));
    try std.testing.expectEqual(@as(usize, 3), string.str_has_prefix("kernel", "ker"));
    try std.testing.expect(string.strstarts("kernel", "ker"));
    try std.testing.expect(!string.strstarts("kernel", "ern"));
    try std.testing.expect(string.strEndsWith("kernel", "nel"));
    try std.testing.expect(string.str_ends_with("kernel", "nel"));

    try std.testing.expectEqual(@as(?usize, 1), string.strnchr("abc", 2, 'b'));
    try std.testing.expectEqual(@as(?usize, null), string.strnchr("abc", 2, 'z'));
    try std.testing.expectEqual(@as(?usize, 2), string.strnchr("abc", 3, 'c'));

    const sysfs = [_][]const u8{ "off", "auto\n", "manual" };
    try std.testing.expectEqual(@as(?usize, 1), string.sysfsMatchString(sysfs[0..], "auto"));
    try std.testing.expectEqual(@as(?usize, 1), string.sysfs_match_string(sysfs[0..], "auto"));

    const exact = [_][]const u8{
        &[_]u8{ 'm', 'a', 'n', 0, 'x' },
        "manual",
        "auto",
    };
    try std.testing.expectEqual(@as(?usize, 0), string.matchString(exact[0..], "man"));
    try std.testing.expectEqual(@as(?usize, 0), string.match_string(exact[0..], "man"));

    var dirty = [_]u8{'a'} ** 24;
    dirty[@sizeOf(usize)] = 'b';
    try std.testing.expectEqual(@as(?usize, @sizeOf(usize)), string.memchrInv(dirty[0..], 'a'));
    try std.testing.expectEqual(string.memchrInv(dirty[0..], 'a'), string.memchr_inv(dirty[0..], 'a'));
}

test "phase1 helper ports A rbtree cached aliases keep duplicate iteration and reseed aligned" {
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

    const node_cmp = struct {
        fn compare(lhs: *const rbtree.Node, rhs: *const rbtree.Node) i32 {
            const lhs_entry: *const Entry = @fieldParentPtr("node", lhs);
            const rhs_entry: *const Entry = @fieldParentPtr("node", rhs);
            if (lhs_entry.key < rhs_entry.key) return -1;
            if (lhs_entry.key > rhs_entry.key) return 1;
            return 0;
        }
    }.compare;

    const node_id = struct {
        fn read(node: ?*rbtree.Node) ?struct { i32, usize } {
            const current = node orelse return null;
            const entry: *const Entry = @fieldParentPtr("node", current);
            return .{ entry.key, entry.serial };
        }
    }.read;

    var primary_entries = [_]Entry{
        .{ .key = 10, .serial = 0 },
        .{ .key = 5, .serial = 1 },
        .{ .key = 15, .serial = 2 },
        .{ .key = 10, .serial = 3 },
    };
    var alias_entries = [_]Entry{
        .{ .key = 10, .serial = 0 },
        .{ .key = 5, .serial = 1 },
        .{ .key = 15, .serial = 2 },
        .{ .key = 10, .serial = 3 },
    };
    var primary_reseed = Entry{ .key = 4, .serial = 4 };
    var alias_reseed = Entry{ .key = 4, .serial = 4 };
    var primary_root = rbtree.RootCached.init();
    var alias_root = rbtree.RootCached.init();

    for (&primary_entries) |*entry| {
        _ = rbtree.addCached(&entry.node, &primary_root, less);
    }
    for (&alias_entries) |*entry| {
        _ = rbtree.rb_add_cached(&entry.node, &alias_root, less);
    }

    try std.testing.expectEqual(node_id(rbtree.firstCached(&primary_root)), node_id(rbtree.rb_first_cached(&alias_root)));

    const wanted = @as(i32, 10);
    var primary_iter = rbtree.matchIterator(&wanted, &primary_root.root, key_cmp);
    var alias_iter = rbtree.matchIterator(&wanted, &alias_root.root, key_cmp);
    var primary_serials: [2]usize = undefined;
    var alias_serials: [2]usize = undefined;
    var count: usize = 0;
    while (primary_iter.next()) |node| : (count += 1) {
        const entry: *const Entry = @fieldParentPtr("node", node);
        primary_serials[count] = entry.serial;
    }
    var alias_count: usize = 0;
    while (alias_iter.next()) |node| : (alias_count += 1) {
        const entry: *const Entry = @fieldParentPtr("node", node);
        alias_serials[alias_count] = entry.serial;
    }
    try std.testing.expectEqual(count, alias_count);
    try std.testing.expectEqualSlices(usize, primary_serials[0..count], alias_serials[0..alias_count]);
    try std.testing.expectEqualSlices(usize, &[_]usize{ 0, 3 }, primary_serials[0..count]);

    try std.testing.expectEqual(
        node_id(rbtree.eraseCached(&primary_entries[1].node, &primary_root)),
        node_id(rbtree.rb_erase_cached(&alias_entries[1].node, &alias_root)),
    );
    try std.testing.expectEqual(node_id(rbtree.firstCached(&primary_root)), node_id(rbtree.rb_first_cached(&alias_root)));

    rbtree.eraseInitCached(&primary_entries[0].node, &primary_root);
    rbtree.rb_erase_init_cached(&alias_entries[0].node, &alias_root);
    try std.testing.expectEqual(node_id(rbtree.firstCached(&primary_root)), node_id(rbtree.rb_first_cached(&alias_root)));

    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.findAddCached(&primary_reseed.node, &primary_root, node_cmp));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.rb_find_add_cached(&alias_reseed.node, &alias_root, node_cmp));
    try std.testing.expectEqual(node_id(rbtree.firstCached(&primary_root)), node_id(rbtree.rb_first_cached(&alias_root)));
    try std.testing.expectEqual(@as(?struct { i32, usize }, .{ 4, 4 }), node_id(rbtree.firstCached(&primary_root)));
}
