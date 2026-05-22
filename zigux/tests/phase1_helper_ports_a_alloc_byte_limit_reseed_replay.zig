const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

test "phase1 helper ports A bitmap alloc render and alias replay" {
    const allocator = std.testing.allocator;
    const nbits = bitmap.bits_per_long + 5;

    try std.testing.expectEqual(bitmap.sizeBytes(0), bitmap.bitmap_size(0));
    try std.testing.expectEqual(bitmap.sizeBytes(nbits), bitmap.bitmap_size(nbits));

    var zeroed: ?[]bitmap.Word = try bitmap.bitmap_zalloc(allocator, nbits);
    defer bitmap.bitmap_free(allocator, &zeroed);
    try std.testing.expectEqual(@as(usize, bitmap.bitsToWords(nbits)), zeroed.?.len);
    for (zeroed.?) |word| {
        try std.testing.expectEqual(@as(bitmap.Word, 0), word);
    }

    bitmap.bitmap_set(zeroed.?, bitmap.bits_per_long - 1, 2);
    zeroed.?[1] |= @as(bitmap.Word, 1) << 9;

    var copied = [_]bitmap.Word{ 0, 0 };
    bitmap.bitmap_copy_clear_tail(&copied, zeroed.?, nbits);
    try std.testing.expectEqual(@as(bitmap.Word, 0), copied[1] & ~bitmap.lastWordMask(nbits));
    try std.testing.expect(bitmap.bitmap_intersects(&copied, zeroed.?, nbits));
    try std.testing.expect(bitmap.bitmap_subset(&copied, zeroed.?, nbits));

    var buffer = [_]u8{ 0xaa, 0xaa, 0xaa, 0xaa, 0xaa };
    const len = bitmap.bitmap_scnprintf(&copied, nbits, &buffer);
    try std.testing.expectEqual(@as(usize, 4), len);
    var expected_full: [32]u8 = undefined;
    const expected_text = try std.fmt.bufPrint(
        &expected_full,
        "{d}-{d}",
        .{ bitmap.bits_per_long - 1, bitmap.bits_per_long },
    );
    try std.testing.expectEqualStrings(expected_text[0..4], buffer[0..len]);
    try std.testing.expectEqual(@as(u8, 0), buffer[len]);

    bitmap.bitmap_free(allocator, &zeroed);
    try std.testing.expect(zeroed == null);
}

test "phase1 helper ports A find_bit byte-window and alias replay" {
    const nbits = find_bit.bits_per_long + 5;
    const boundary = find_bit.bits_per_long;
    const last_aligned_byte = find_bit.bits_per_long - 8;

    const bytes = [_]find_bit.Word{
        @as(find_bit.Word, 0xa5) << @intCast(last_aligned_byte),
        (@as(find_bit.Word, 0x12) << 0) | (@as(find_bit.Word, 1) << 9),
    };
    try std.testing.expectEqual(@as(u8, 0xa5), find_bit.getValue8(&bytes, last_aligned_byte));
    try std.testing.expectEqual(@as(u8, 0x12), find_bit.getValue8(&bytes, boundary));

    const scan = [_]find_bit.Word{
        0,
        (@as(find_bit.Word, 1) << 2) | (@as(find_bit.Word, 1) << 4) | (@as(find_bit.Word, 1) << 9),
    };
    try std.testing.expectEqual(@as(usize, boundary + 2), find_bit.find_next_bit(&scan, nbits, boundary + 2));
    try std.testing.expectEqual(@as(usize, boundary + 4), find_bit._find_next_bit(&scan, nbits, boundary + 3));
    try std.testing.expectEqual(@as(usize, nbits), find_bit.find_next_bit(&scan, nbits, boundary + 5));
    try std.testing.expectEqual(@as(usize, boundary + 4), find_bit.find_last_bit(&scan, nbits));

    var clump: u8 = 0x5a;
    try std.testing.expectEqual(@as(usize, nbits), find_bit.find_next_clump8(&clump, &scan, nbits, nbits));
    try std.testing.expectEqual(@as(u8, 0x5a), clump);
    try std.testing.expectEqual(@as(usize, nbits), find_bit._find_next_clump8(&clump, &scan, nbits, nbits + 4));
    try std.testing.expectEqual(@as(u8, 0x5a), clump);
}

test "phase1 helper ports A string count basename and terminator replay" {
    const sysfs = [_][]const u8{ "off", "auto\n", "manual" };
    try std.testing.expectEqual(@as(?usize, 1), string.sysfs_match_string(sysfs[0..], "auto"));
    try std.testing.expectEqual(@as(?usize, 1), string.sysfsMatchString(sysfs[0..], "auto"));

    try std.testing.expectEqual(@as(?usize, null), string.strnchr("abc", 2, 'z'));
    try std.testing.expectEqual(@as(?usize, 1), string.strnchr(&[_]u8{ 'a', 'b', 0, 'c' }, 4, 'b'));
    try std.testing.expectEqual(@as(?usize, 2), string.strnchr(&[_]u8{ 'a', 'b', 0, 'c' }, 4, 0));
    try std.testing.expect(string.streq(&[_]u8{ 'm', 'o', 0, 'x' }, &[_]u8{ 'm', 'o', 0, 'y' }));
    try std.testing.expectEqual(@as(usize, 3), string.strHasPrefix(&[_]u8{ 'n', 'o', 'd', 'e', 0, 'x' }, "nod"));

    const exact = [_][]const u8{
        &[_]u8{ 'm', 'a', 'n', 0, 'x' },
        "manual",
        "mode",
    };
    try std.testing.expectEqual(@as(?usize, 0), string.match_string(exact[0..], "man"));
    try std.testing.expectEqual(@as(?usize, null), string.match_string(exact[0..], "ma "));
}

test "phase1 helper ports A rbtree duplicate alias and reseed replay" {
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

    const cmp = struct {
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

    var root_entry = Entry{ .key = 10, .serial = 0 };
    var left_entry = Entry{ .key = 5, .serial = 1 };
    var duplicate_entry = Entry{ .key = 10, .serial = 2 };
    var reseed_entry = Entry{ .key = 4, .serial = 3 };
    var root = rbtree.RootCached.init();

    try std.testing.expectEqual(@as(?*rbtree.Node, &root_entry.node), rbtree.rb_add_cached(&root_entry.node, &root, less));
    try std.testing.expectEqual(@as(?*rbtree.Node, &root_entry.node), rbtree.rb_first_cached(&root));

    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.rb_find_add_cached(&left_entry.node, &root, cmp));
    try std.testing.expectEqual(@as(?*rbtree.Node, &left_entry.node), rbtree.rb_first_cached(&root));

    const duplicate = rbtree.rb_find_add_cached(&duplicate_entry.node, &root, cmp) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(*rbtree.Node, &root_entry.node), duplicate);
    try std.testing.expectEqual(rbtree.rb_first(&root.root), rbtree.rb_first_cached(&root));

    const wanted = @as(i32, 10);
    var iter = rbtree.matchIterator(&wanted, &root.root, key_cmp);
    const first_match = iter.next() orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(*rbtree.Node, &root_entry.node), first_match);
    try std.testing.expect(iter.next() == null);

    rbtree.rb_erase_init_cached(&left_entry.node, &root);
    try std.testing.expect(rbtree.emptyNode(&left_entry.node));
    try std.testing.expectEqual(@as(?*rbtree.Node, &root_entry.node), rbtree.rb_first_cached(&root));

    rbtree.rb_erase_init_cached(&root_entry.node, &root);
    try std.testing.expect(rbtree.emptyNode(&root_entry.node));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), root.root.node);
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.rb_first_cached(&root));

    try std.testing.expectEqual(@as(?*rbtree.Node, &reseed_entry.node), rbtree.rb_add_cached(&reseed_entry.node, &root, less));
    try std.testing.expectEqual(@as(?*rbtree.Node, &reseed_entry.node), rbtree.rb_first_cached(&root));
    try std.testing.expectEqual(rbtree.rb_first(&root.root), rbtree.rb_first_cached(&root));
}
