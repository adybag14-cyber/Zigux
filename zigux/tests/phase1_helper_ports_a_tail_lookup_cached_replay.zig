const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

test "lane06 replay keeps tail-weighted bitmap and find_bit windows aligned" {
    const nbits = find_bit.bits_per_long + 5;
    const lhs = [_]find_bit.Word{
        0,
        (@as(find_bit.Word, 1) << 1) | (@as(find_bit.Word, 1) << 3) | (@as(find_bit.Word, 1) << 9),
    };
    const rhs = [_]find_bit.Word{
        0,
        (@as(find_bit.Word, 1) << 1) | (@as(find_bit.Word, 1) << 10),
    };
    var merged = [_]find_bit.Word{ 0, 0 };

    try std.testing.expectEqual(
        @as(usize, 1),
        bitmap.bitmap_weighted_xor(&merged, &lhs, &rhs, nbits),
    );
    try std.testing.expectEqual(
        @as(find_bit.Word, (@as(find_bit.Word, 1) << 3) | (@as(find_bit.Word, 1) << 9) | (@as(find_bit.Word, 1) << 10)),
        merged[1],
    );
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 3), find_bit.findFirstBit(&merged, nbits));
    try std.testing.expectEqual(
        @as(usize, find_bit.bits_per_long + 3),
        find_bit.findNextAndNotBit(&lhs, &rhs, nbits, find_bit.bits_per_long + 1),
    );
    try std.testing.expectEqual(
        @as(usize, find_bit.bits_per_long + 3),
        find_bit.find_next_andnot_bit(&lhs, &rhs, nbits, find_bit.bits_per_long + 1),
    );
    try std.testing.expectEqual(
        @as(usize, nbits),
        find_bit._find_next_andnot_bit(&lhs, &rhs, nbits, find_bit.bits_per_long + 4),
    );
}

test "lane06 replay keeps string lookup order and C-string boundaries review-visible" {
    const sysfs_modes = [_][]const u8{ "auto\n", "auto", "manual" };
    try std.testing.expectEqual(@as(?usize, 0), string.sysfsMatchString(sysfs_modes[0..], "auto"));
    try std.testing.expectEqual(@as(?usize, 0), string.sysfs_match_string(sysfs_modes[0..], "auto"));
    try std.testing.expectEqual(@as(?usize, 0), string.sysfsMatchString(sysfs_modes[0..1], "auto"));

    const named_modes = [_][]const u8{
        &[_]u8{ 'a', 'u', 't', 'o', 0, 'x' },
        "manual",
        "auto",
    };
    try std.testing.expectEqual(@as(?usize, 0), string.matchString(named_modes[0..], "auto"));
    try std.testing.expectEqual(@as(?usize, 0), string.match_string(named_modes[0..], "auto"));

    var scratch = [_]u8{'a'} ** 32;
    scratch[17] = 'b';
    try std.testing.expectEqual(@as(?usize, 17), string.memchrInv(scratch[0..], 'a'));
    try std.testing.expectEqual(@as(?usize, 17), string.memchr_inv(scratch[0..], 'a'));
}

test "lane06 replay keeps cached leftmost promotion aligned with duplicate traversal" {
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

    const cmp = struct {
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
        .{ .key = 10, .serial = 1 },
        .{ .key = 5, .serial = 2 },
        .{ .key = 20, .serial = 3 },
    };
    var root = rbtree.RootCached.init();

    for (&entries) |*entry| {
        _ = rbtree.addCached(&entry.node, &root, less);
    }

    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[2].node), rbtree.firstCached(&root));

    const duplicate_key = @as(i32, 10);
    const first_match = rbtree.findFirst(&duplicate_key, &root.root, cmp) orelse return error.TestUnexpectedResult;
    const first_match_entry: *const Entry = @fieldParentPtr("node", first_match);
    try std.testing.expectEqual(@as(usize, 0), first_match_entry.serial);

    const second_match = rbtree.nextMatch(&duplicate_key, first_match, cmp) orelse return error.TestUnexpectedResult;
    const second_match_entry: *const Entry = @fieldParentPtr("node", second_match);
    try std.testing.expectEqual(@as(usize, 1), second_match_entry.serial);
    try std.testing.expect(rbtree.nextMatch(&duplicate_key, second_match, cmp) == null);

    const promoted = rbtree.eraseCached(&entries[2].node, &root) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(*rbtree.Node, &entries[0].node), promoted);
    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[0].node), rbtree.firstCached(&root));
    try std.testing.expectEqual(rbtree.first(&root.root), rbtree.rb_first_cached(&root));
}
