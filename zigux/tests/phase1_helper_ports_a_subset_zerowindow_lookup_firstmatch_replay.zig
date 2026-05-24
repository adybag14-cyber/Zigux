const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

const Word = bitmap.Word;
const bits_per_long = bitmap.bits_per_long;

test "bitmap subset and replace stay inside the declared tail window" {
    const nbits = bits_per_long + 5;

    const old = [_]Word{ 0, (@as(Word, 1) << 1) | (@as(Word, 1) << 9) };
    const new = [_]Word{ 0, (@as(Word, 1) << 3) | (@as(Word, 1) << 9) };
    const mask = [_]Word{ 0, (@as(Word, 1) << 1) | (@as(Word, 1) << 3) | (@as(Word, 1) << 9) };

    var replaced = [_]Word{ 0, 0 };
    bitmap.replace(&replaced, &old, &new, &mask, nbits);

    const expected = [_]Word{ 0, @as(Word, 1) << 3 };
    try std.testing.expect(bitmap.equal(&expected, &replaced, nbits));
    try std.testing.expect(bitmap.bitmap_subset(&expected, &replaced, nbits));
    try std.testing.expect(bitmap.bitmap_intersects(&replaced, &expected, nbits));

    const disjoint = [_]Word{ 0, @as(Word, 1) << 4 };
    try std.testing.expect(!bitmap.bitmap_intersects(&replaced, &disjoint, nbits));
    try std.testing.expect(!bitmap.bitmap_subset(&disjoint, &replaced, nbits));
}

test "find_bit zero-window scans clamp tail-only noise" {
    const nbits = bits_per_long + 5;

    const fully_set = [_]Word{ ~@as(Word, 0), find_bit.lastWordMask(nbits) };
    try std.testing.expectEqual(@as(usize, nbits), find_bit.findFirstZeroBit(&fully_set, nbits));
    try std.testing.expectEqual(@as(usize, nbits), find_bit.findNextZeroBit(&fully_set, nbits, bits_per_long));

    var with_gap = fully_set;
    with_gap[1] &= ~(@as(Word, 1) << 2);
    try std.testing.expectEqual(@as(usize, bits_per_long + 2), find_bit.findFirstZeroBit(&with_gap, nbits));
    try std.testing.expectEqual(@as(usize, bits_per_long + 2), find_bit.find_next_zero_bit(&with_gap, nbits, bits_per_long + 1));
    try std.testing.expectEqual(@as(usize, nbits), find_bit.findNextZeroBit(&with_gap, nbits, bits_per_long + 3));
}

test "string lookup helpers keep sysfs and c-string boundaries distinct" {
    const sysfs_haystack = [_][]const u8{ "alpha\n", "beta", "gamma\n" };
    try std.testing.expect(string.sysfsStreq("alpha\n", "alpha"));
    try std.testing.expectEqual(@as(?usize, 1), string.sysfsMatchString(&sysfs_haystack, "beta\n"));
    try std.testing.expectEqual(@as(?usize, 2), string.sysfs_match_string(&sysfs_haystack, "gamma"));

    const match_haystack = [_][]const u8{
        &[_]u8{ 'o', 'n', 0, 'x' },
        &[_]u8{ 't', 'w', 'o', 0, 'y' },
        "three",
    };
    try std.testing.expectEqual(@as(?usize, 0), string.matchString(&match_haystack, "on"));
    try std.testing.expectEqual(@as(?usize, 1), string.match_string(&match_haystack, "two"));
    try std.testing.expectEqual(@as(?usize, null), string.matchString(&match_haystack, "four"));

    const bounded = [_]u8{ 'a', 'b', 0, 'c', 'd' };
    try std.testing.expectEqual(@as(?usize, null), string.strnchr(&bounded, 1, 'b'));
    try std.testing.expectEqual(@as(?usize, 1), string.strnchr(&bounded, 3, 'b'));
    try std.testing.expectEqual(@as(?usize, null), string.strnchr(&bounded, bounded.len, 'd'));
}

test "rbtree first-match lookup returns the leftmost duplicate run" {
    const Entry = struct {
        key: i32,
        tag: u8,
        node: rbtree.Node = rbtree.Node.init(),
    };

    const less = struct {
        fn compare(lhs: *const rbtree.Node, rhs: *const rbtree.Node) bool {
            const lhs_entry: *const Entry = @fieldParentPtr("node", lhs);
            const rhs_entry: *const Entry = @fieldParentPtr("node", rhs);
            if (lhs_entry.key != rhs_entry.key) {
                return lhs_entry.key < rhs_entry.key;
            }
            return lhs_entry.tag < rhs_entry.tag;
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
        .{ .key = 10, .tag = 'b' },
        .{ .key = 5, .tag = 'a' },
        .{ .key = 10, .tag = 'a' },
        .{ .key = 12, .tag = 'z' },
        .{ .key = 10, .tag = 'c' },
    };
    var root = rbtree.Root.init();

    for (&entries) |*entry| {
        rbtree.add(&entry.node, &root, less);
    }

    const wanted: i32 = 10;
    const any_match = rbtree.find(@ptrCast(&wanted), &root, key_cmp) orelse return error.TestUnexpectedResult;
    const first_match = rbtree.findFirst(@ptrCast(&wanted), &root, key_cmp) orelse return error.TestUnexpectedResult;

    try std.testing.expectEqual(@as(i32, 10), (@as(*const Entry, @fieldParentPtr("node", any_match))).key);
    try std.testing.expectEqual(@as(u8, 'a'), (@as(*const Entry, @fieldParentPtr("node", first_match))).tag);

    const second = rbtree.nextMatch(@ptrCast(&wanted), first_match, key_cmp) orelse return error.TestUnexpectedResult;
    const third = rbtree.nextMatch(@ptrCast(&wanted), second, key_cmp) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(u8, 'b'), (@as(*const Entry, @fieldParentPtr("node", second))).tag);
    try std.testing.expectEqual(@as(u8, 'c'), (@as(*const Entry, @fieldParentPtr("node", third))).tag);
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.nextMatch(@ptrCast(&wanted), third, key_cmp));
}
