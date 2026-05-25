const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

test "lane06 replay keeps exact-word bitmap relations fenced at nbits" {
    const Word = bitmap.Word;
    const nbits = bitmap.bits_per_long;
    const lhs = [_]Word{ 0b1010, @as(Word, 1) << 5 };
    const rhs = [_]Word{ 0b1010, @as(Word, 1) << 9 };
    const outside_only = [_]Word{ 0, @as(Word, 1) << 3 };
    const zero = [_]Word{ 0, 0 };

    try std.testing.expect(bitmap.equal(&lhs, &rhs, nbits));
    try std.testing.expect(bitmap.bitmap_equal(&lhs, &rhs, nbits));
    try std.testing.expect(!bitmap.intersects(&outside_only, &outside_only, nbits));
    try std.testing.expect(!bitmap.bitmap_intersects(&outside_only, &outside_only, nbits));
    try std.testing.expect(bitmap.subset(&outside_only, &zero, nbits));
    try std.testing.expect(bitmap.bitmap_subset(&outside_only, &zero, nbits));
}

test "lane06 replay keeps shared and and-not scans inclusive at exact-word and tail boundaries" {
    const Word = find_bit.Word;
    const exact_nbits = find_bit.bits_per_long;
    const exact_boundary = exact_nbits - 1;
    const exact_shared_lhs = [_]Word{ @as(Word, 1) << @intCast(exact_boundary), 0 };
    const exact_shared_rhs = [_]Word{ @as(Word, 1) << @intCast(exact_boundary), @as(Word, 1) << 5 };

    try std.testing.expectEqual(
        @as(usize, exact_boundary),
        find_bit.findNextAndBit(&exact_shared_lhs, &exact_shared_rhs, exact_nbits, exact_boundary),
    );
    try std.testing.expectEqual(
        @as(usize, exact_nbits),
        find_bit.findNextAndBit(&exact_shared_lhs, &exact_shared_rhs, exact_nbits, exact_boundary + 1),
    );

    const tail_bits: usize = 5;
    const tail_nbits = find_bit.bits_per_long + tail_bits;
    const tail_boundary = tail_nbits - 1;
    const tail_shared_lhs = [_]Word{
        0,
        (@as(Word, 1) << @intCast(tail_bits - 1)) | (@as(Word, 1) << @intCast(tail_bits + 2)),
    };
    const tail_shared_rhs = [_]Word{
        0,
        (@as(Word, 1) << @intCast(tail_bits - 1)) | (@as(Word, 1) << @intCast(tail_bits + 1)),
    };
    const tail_andnot_rhs = [_]Word{ 0, @as(Word, 1) << @intCast(tail_bits + 1) };

    try std.testing.expectEqual(
        @as(usize, tail_boundary),
        find_bit.findNextAndBit(&tail_shared_lhs, &tail_shared_rhs, tail_nbits, tail_boundary),
    );
    try std.testing.expectEqual(
        @as(usize, tail_nbits),
        find_bit.find_next_and_bit(&tail_shared_lhs, &tail_shared_rhs, tail_nbits, tail_boundary + 1),
    );
    try std.testing.expectEqual(
        @as(usize, tail_boundary),
        find_bit.findNextAndNotBit(&tail_shared_lhs, &tail_andnot_rhs, tail_nbits, tail_boundary),
    );
    try std.testing.expectEqual(
        @as(usize, tail_nbits),
        find_bit._find_next_andnot_bit(&tail_shared_lhs, &tail_andnot_rhs, tail_nbits, tail_boundary + 1),
    );
}

test "lane06 replay keeps newline-aware and bounded match scans separated by C-string ends" {
    const sysfs = [_][]const u8{ "off", "auto\n", "auto", "on" };
    const bounded = [_][]const u8{ "zero", "one", "two" };
    const counted = [_]u8{ 'm', 'o', 'd', 'e', 0, 'x', 'y' };

    try std.testing.expectEqual(@as(?usize, 1), string.sysfsMatchString(sysfs[0..], "auto"));
    try std.testing.expectEqual(@as(?usize, 1), string.sysfs_match_string(sysfs[0..], "auto"));
    try std.testing.expectEqual(@as(?usize, 2), string.matchString(bounded[0..], "two"));
    try std.testing.expectEqual(@as(?usize, 1), string.match_string(bounded[0..], "one"));
    try std.testing.expectEqual(@as(?usize, null), string.sysfsMatchString(sysfs[0..], "missing"));
    try std.testing.expectEqual(@as(?usize, null), string.match_string(bounded[0..], "three"));
    try std.testing.expectEqual(@as(?usize, 2), string.strnchr(&counted, 3, 'd'));
    try std.testing.expectEqual(@as(?usize, null), string.strnchr(&counted, counted.len, 'x'));
}

test "lane06 replay keeps cached duplicate lookups and inserted misses aligned" {
    const Entry = struct {
        key: i32,
        serial: usize,
        node: rbtree.Node = rbtree.Node.init(),
    };

    const cmp = struct {
        fn compare(lhs: *const rbtree.Node, rhs: *const rbtree.Node) i32 {
            const lhs_entry: *const Entry = @fieldParentPtr("node", lhs);
            const rhs_entry: *const Entry = @fieldParentPtr("node", rhs);
            if (lhs_entry.key < rhs_entry.key) return -1;
            if (lhs_entry.key > rhs_entry.key) return 1;
            return 0;
        }
    }.compare;

    const firstKey = struct {
        fn read(root: *const rbtree.RootCached) ?i32 {
            const node = rbtree.firstCached(root) orelse return null;
            const entry: *const Entry = @fieldParentPtr("node", node);
            return entry.key;
        }
    }.read;

    var primary_root = rbtree.RootCached.init();
    var alias_root = rbtree.RootCached.init();
    var primary_root_entry = Entry{ .key = 10, .serial = 0 };
    var alias_root_entry = Entry{ .key = 10, .serial = 0 };
    var primary_leftmost = Entry{ .key = 5, .serial = 1 };
    var alias_leftmost = Entry{ .key = 5, .serial = 1 };
    var primary_larger = Entry{ .key = 15, .serial = 2 };
    var alias_larger = Entry{ .key = 15, .serial = 2 };
    var primary_miss = Entry{ .key = 12, .serial = 3 };
    var alias_miss = Entry{ .key = 12, .serial = 3 };
    var primary_duplicate = Entry{ .key = 10, .serial = 4 };
    var alias_duplicate = Entry{ .key = 10, .serial = 4 };

    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.findAddCached(&primary_root_entry.node, &primary_root, cmp));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.rb_find_add_cached(&alias_root_entry.node, &alias_root, cmp));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.findAddCached(&primary_leftmost.node, &primary_root, cmp));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.rb_find_add_cached(&alias_leftmost.node, &alias_root, cmp));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.findAddCached(&primary_larger.node, &primary_root, cmp));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.rb_find_add_cached(&alias_larger.node, &alias_root, cmp));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.findAddCached(&primary_miss.node, &primary_root, cmp));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.rb_find_add_cached(&alias_miss.node, &alias_root, cmp));

    const primary_existing = rbtree.findAddCached(&primary_duplicate.node, &primary_root, cmp) orelse return error.TestUnexpectedResult;
    const alias_existing = rbtree.rb_find_add_cached(&alias_duplicate.node, &alias_root, cmp) orelse return error.TestUnexpectedResult;
    const primary_existing_entry: *const Entry = @fieldParentPtr("node", primary_existing);
    const alias_existing_entry: *const Entry = @fieldParentPtr("node", alias_existing);

    try std.testing.expectEqual(@as(i32, 10), primary_existing_entry.key);
    try std.testing.expectEqual(primary_existing_entry.key, alias_existing_entry.key);
    try std.testing.expectEqual(primary_existing_entry.serial, alias_existing_entry.serial);
    try std.testing.expectEqual(firstKey(&primary_root), firstKey(&alias_root));
    try std.testing.expectEqual(rbtree.first(&primary_root.root), rbtree.firstCached(&primary_root));
    try std.testing.expectEqual(rbtree.first(&alias_root.root), rbtree.rb_first_cached(&alias_root));
}
