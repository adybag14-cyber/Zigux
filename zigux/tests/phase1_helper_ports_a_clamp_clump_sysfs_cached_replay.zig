const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

test "phase1 helper ports A bitmap clamp and terminator replay" {
    const nbits = bitmap.bits_per_long + 5;
    const lhs = [_]bitmap.Word{ 0, (@as(bitmap.Word, 1) << 1) | (@as(bitmap.Word, 1) << 8) };
    const rhs = [_]bitmap.Word{ 0, (@as(bitmap.Word, 1) << 3) | (@as(bitmap.Word, 1) << 9) };
    var direct_or = [_]bitmap.Word{ 0, 0 };
    var alias_or = [_]bitmap.Word{ 0, 0 };

    const direct_weight = bitmap.weightedOr(&direct_or, &lhs, &rhs, nbits);
    const alias_weight = bitmap.bitmap_weighted_or(&alias_or, &lhs, &rhs, nbits);
    try std.testing.expectEqual(@as(usize, 2), direct_weight);
    try std.testing.expectEqual(direct_weight, alias_weight);
    try std.testing.expectEqualSlices(bitmap.Word, &direct_or, &alias_or);
    try std.testing.expectEqual(@as(bitmap.Word, (@as(bitmap.Word, 1) << 1) | (@as(bitmap.Word, 1) << 3) | (@as(bitmap.Word, 1) << 8) | (@as(bitmap.Word, 1) << 9)), direct_or[1]);
    try std.testing.expectEqual(@as(usize, 2), bitmap.weight(&direct_or, nbits));

    var range = [_]bitmap.Word{0};
    bitmap.setRange(&range, 1, 3);
    var terminator_only = [_]u8{0xaa};
    const rendered = bitmap.bitmap_scnprintf(&range, 8, terminator_only[0..1]);
    try std.testing.expectEqual(@as(usize, 0), rendered);
    try std.testing.expectEqual(@as(u8, 0), terminator_only[0]);
}

test "phase1 helper ports A find_bit clump and tail replay" {
    const nbits = find_bit.bits_per_long + 5;
    const bitmap_tail = [_]find_bit.Word{ 0, (@as(find_bit.Word, 1) << 3) | (@as(find_bit.Word, 1) << 6) };
    var clump: u8 = 0;
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long), find_bit.findFirstClump8(&clump, &bitmap_tail, nbits));
    try std.testing.expectEqual(@as(u8, 0b0000_1000), clump);

    const empty = [_]find_bit.Word{0};
    var untouched: u8 = 0x5a;
    try std.testing.expectEqual(@as(usize, 8), find_bit.findNextClump8(&untouched, &empty, 8, 4));
    try std.testing.expectEqual(@as(u8, 0x5a), untouched);

    var last_map = [_]find_bit.Word{ 0, (@as(find_bit.Word, 1) << 3) | (@as(find_bit.Word, 1) << 10) };
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 3), find_bit.findLastBit(&last_map, nbits));
    last_map[1] &= ~(@as(find_bit.Word, 1) << 3);
    try std.testing.expectEqual(@as(usize, nbits), find_bit.find_last_bit(&last_map, nbits));
}

test "phase1 helper ports A string sysfs and embedded-nul replay" {
    var padded = [_]u8{ 1, 1, 1, 1, 1, 1 };
    try std.testing.expectEqual(@as(isize, 2), string.strscpy_pad(padded[0..], &[_]u8{ 'h', 'i', 0, 'x', 'x' }));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'h', 'i', 0, 0, 0, 0 }, padded[0..]);

    const sysfs = [_][]const u8{ "manual\n", "auto", "auto\n", "off" };
    try std.testing.expectEqual(@as(?usize, 0), string.sysfsMatchString(sysfs[0..], "manual"));
    try std.testing.expectEqual(@as(?usize, 1), string.sysfs_match_string(sysfs[0..], "auto"));
    try std.testing.expectEqual(@as(?usize, 1), string.match_string(sysfs[0..], "auto"));

    try std.testing.expectEqual(@as(?usize, null), string.strnchr("abcz", 2, 'z'));
    try std.testing.expectEqual(@as(?usize, 2), string.strnchr(&[_]u8{ 'a', 'b', 0, 'z' }, 4, 0));
}

test "phase1 helper ports A rbtree cached duplicate replay" {
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
        fn compare(lhs: *const rbtree.Node, rhs: *const rbtree.Node) i32 {
            const lhs_entry: *const Entry = @fieldParentPtr("node", lhs);
            const rhs_entry: *const Entry = @fieldParentPtr("node", rhs);
            if (lhs_entry.key < rhs_entry.key) return -1;
            if (lhs_entry.key > rhs_entry.key) return 1;
            return 0;
        }
    }.compare;

    var root = rbtree.RootCached.init();
    var first_entry = Entry{ .key = 10, .serial = 0 };
    var leftmost = Entry{ .key = 5, .serial = 1 };
    var larger = Entry{ .key = 15, .serial = 2 };
    var duplicate = Entry{ .key = 10, .serial = 3 };
    var singleton = Entry{ .key = 21, .serial = 4 };
    var singleton_root = rbtree.RootCached.init();

    try std.testing.expectEqual(@as(?*rbtree.Node, &first_entry.node), rbtree.rb_add_cached(&first_entry.node, &root, less));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.rb_find_add_cached(&leftmost.node, &root, cmp));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.findAddCached(&larger.node, &root, cmp));
    try std.testing.expectEqual(@as(?*rbtree.Node, &leftmost.node), rbtree.rb_first_cached(&root));

    const existing = rbtree.rb_find_add_cached(&duplicate.node, &root, cmp) orelse return error.TestUnexpectedResult;
    const existing_entry: *const Entry = @fieldParentPtr("node", existing);
    try std.testing.expectEqual(@as(i32, 10), existing_entry.key);
    try std.testing.expectEqual(@as(usize, 0), existing_entry.serial);
    try std.testing.expectEqual(@as(?*rbtree.Node, &leftmost.node), rbtree.firstCached(&root));
    try std.testing.expectEqual(rbtree.first(&root.root), rbtree.firstCached(&root));

    _ = rbtree.addCached(&singleton.node, &singleton_root, less);
    try std.testing.expectEqual(@as(?*rbtree.Node, &singleton.node), rbtree.firstCached(&singleton_root));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.rb_erase_cached(&singleton.node, &singleton_root));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.firstCached(&singleton_root));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), singleton_root.root.node);
}
