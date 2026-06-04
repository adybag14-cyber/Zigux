const std = @import("std");

const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const rbtree = @import("rbtree");
const string = @import("string");

const Word = bitmap.Word;

test "empty bitmap and scan windows leave caller storage untouched" {
    var source = [_]Word{~@as(Word, 0)};
    var copy_dst = [_]Word{0x1357};
    var extend_dst = [_]Word{0x2468};
    var and_dst = [_]Word{0xaaaa};
    var format_buf = [_]u8{ 0xcc, 0xcc, 0xcc };

    bitmap.copy(copy_dst[0..0], source[0..0], 0);
    bitmap.copyAndExtend(extend_dst[0..0], source[0..0], 0, 0);
    try std.testing.expect(!bitmap.andBits(and_dst[0..0], source[0..0], source[0..0], 0));
    try std.testing.expect(bitmap.empty(source[0..0], 0));
    try std.testing.expect(bitmap.full(source[0..0], 0));
    try std.testing.expectEqual(@as(usize, 0), bitmap.weight(source[0..0], 0));
    try std.testing.expectEqual(@as(usize, 0), bitmap.scnprintf(source[0..0], 0, &format_buf));

    try std.testing.expectEqual(@as(Word, 0x1357), copy_dst[0]);
    try std.testing.expectEqual(@as(Word, 0x2468), extend_dst[0]);
    try std.testing.expectEqual(@as(Word, 0xaaaa), and_dst[0]);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0xcc, 0xcc, 0xcc }, &format_buf);

    var clump: u8 = 0x5a;
    const empty_words = [_]Word{};
    try std.testing.expectEqual(@as(usize, 0), find_bit.findFirstBit(empty_words[0..], 0));
    try std.testing.expectEqual(@as(usize, 0), find_bit.findFirstZeroBit(empty_words[0..], 0));
    try std.testing.expectEqual(@as(usize, 0), find_bit.findLastBit(empty_words[0..], 0));
    try std.testing.expectEqual(@as(usize, 8), find_bit.findNextClump8(&clump, empty_words[0..], 8, 8));
    try std.testing.expectEqual(@as(u8, 0x5a), clump);
}

test "string singleton trims and empty bounded searches keep C boundaries explicit" {
    var spaces = [_]u8{ ' ', '\t', 0, 'x' };
    try std.testing.expectEqualStrings("", string.strim(spaces[0..]));
    try std.testing.expectEqual(@as(u8, 0), spaces[0]);

    const sysfs_choices = [_][]const u8{ "off", "auto\n", "on" };
    try std.testing.expectEqual(@as(?usize, 1), string.sysfsMatchString(sysfs_choices[0..], "auto"));
    try std.testing.expectEqual(@as(?usize, null), string.matchString(sysfs_choices[0..], "auto"));

    try std.testing.expectEqual(@as(?usize, null), string.strnchr("abc", 3, 0));
    try std.testing.expectEqual(@as(?usize, 0), string.strnchr(&[_]u8{ 0, 'x' }, 2, 0));
}

test "rbtree singleton cached roots detach cleanly and keep empty-node scans inert" {
    const Entry = struct {
        key: i32,
        node: rbtree.Node = rbtree.Node.init(),
    };

    const less = struct {
        fn compare(lhs: *const rbtree.Node, rhs: *const rbtree.Node) bool {
            const lhs_entry: *const Entry = @fieldParentPtr("node", lhs);
            const rhs_entry: *const Entry = @fieldParentPtr("node", rhs);
            return lhs_entry.key < rhs_entry.key;
        }
    }.compare;

    var entry = Entry{ .key = 7 };
    var root = rbtree.RootCached.init();

    try std.testing.expectEqual(@as(?*rbtree.Node, &entry.node), rbtree.rb_add_cached(&entry.node, &root, less));
    try std.testing.expectEqual(@as(?*rbtree.Node, &entry.node), rbtree.rb_first_cached(&root));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.rb_erase_cached(&entry.node, &root));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.rb_first_cached(&root));
    try std.testing.expect(rbtree.emptyRoot(&root.root));

    rbtree.clearNode(&entry.node);
    try std.testing.expect(rbtree.emptyNode(&entry.node));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.rb_next(&entry.node));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.rb_prev(&entry.node));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.rb_next_postorder(null));
}
