const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

test "phase1 helper ports A bitmap replace complement and predicates stay tail-masked" {
    const Word = bitmap.Word;
    const nbits = bitmap.bits_per_long + 5;
    const old = [_]Word{ 0b1011, (@as(Word, 1) << 1) | (@as(Word, 1) << 6) };
    const new = [_]Word{ 0b0101, (@as(Word, 1) << 0) | (@as(Word, 1) << 4) | (@as(Word, 1) << 7) };
    const mask = [_]Word{ 0b1110, (@as(Word, 1) << 0) | (@as(Word, 1) << 4) | (@as(Word, 1) << 7) };

    var direct = [_]Word{ 0, 0 };
    var alias = [_]Word{ 0, 0 };
    bitmap.replace(&direct, &old, &new, &mask, nbits);
    bitmap.bitmap_replace(&alias, &old, &new, &mask, nbits);
    try std.testing.expectEqualSlices(Word, &direct, &alias);
    try std.testing.expectEqual(@as(Word, 0), direct[1] & ~bitmap.lastWordMask(nbits));

    var direct_complement = [_]Word{ 0, 0 };
    var alias_complement = [_]Word{ 0, 0 };
    bitmap.complement(&direct_complement, &direct, nbits);
    bitmap.bitmap_complement(&alias_complement, &alias, nbits);
    try std.testing.expectEqualSlices(Word, &direct_complement, &alias_complement);
    try std.testing.expect(bitmap.equal(&direct, &alias, nbits));
    try std.testing.expect(bitmap.bitmap_equal(&direct, &alias, nbits));
    try std.testing.expect(bitmap.intersects(&direct, &mask, nbits));
    try std.testing.expect(bitmap.bitmap_intersects(&alias, &mask, nbits));
}

test "phase1 helper ports A find_bit and clump aliases stay aligned across boundaries" {
    const Word = find_bit.Word;
    const nbits = find_bit.bits_per_long + 12;
    const lhs = [_]Word{
        @as(Word, 1) << @intCast(find_bit.bits_per_long - 2),
        (@as(Word, 1) << 3) | (@as(Word, 1) << 9),
    };
    const rhs = [_]Word{
        @as(Word, 1) << @intCast(find_bit.bits_per_long - 2),
        (@as(Word, 1) << 1) | (@as(Word, 1) << 3),
    };

    try std.testing.expectEqual(
        find_bit.findFirstAndBit(&lhs, &rhs, nbits),
        find_bit.find_first_and_bit(&lhs, &rhs, nbits),
    );
    try std.testing.expectEqual(
        find_bit.findNextAndBit(&lhs, &rhs, nbits, find_bit.bits_per_long),
        find_bit._find_next_and_bit(&lhs, &rhs, nbits, find_bit.bits_per_long),
    );
    try std.testing.expectEqual(
        find_bit.findLastBit(&lhs, nbits),
        find_bit.find_last_bit(&lhs, nbits),
    );

    var direct_first_clump: u8 = 0;
    var alias_first_clump: u8 = 0;
    try std.testing.expectEqual(
        find_bit.findFirstClump8(&direct_first_clump, &lhs, nbits),
        find_bit.find_first_clump8(&alias_first_clump, &lhs, nbits),
    );
    try std.testing.expectEqual(direct_first_clump, alias_first_clump);
    try std.testing.expectEqual(@as(u8, 0b0100_0000), direct_first_clump);

    var direct_next_clump: u8 = 0;
    var alias_next_clump: u8 = 0;
    try std.testing.expectEqual(
        find_bit.findNextClump8(&direct_next_clump, &lhs, nbits, find_bit.bits_per_long),
        find_bit.find_next_clump8(&alias_next_clump, &lhs, nbits, find_bit.bits_per_long),
    );
    try std.testing.expectEqual(direct_next_clump, alias_next_clump);
    try std.testing.expectEqual(@as(u8, 0b0000_1000), direct_next_clump);
}

test "phase1 helper ports A string memchr sysfs and prefix-suffix helpers stay aligned" {
    try std.testing.expectEqual(
        string.memchrInv(&[_]u8{ 'z', 'z', 'z', 'x', 'z' }, 'z'),
        string.memchr_inv(&[_]u8{ 'z', 'z', 'z', 'x', 'z' }, 'z'),
    );
    try std.testing.expectEqual(@as(?usize, 3), string.memchrInv(&[_]u8{ 'z', 'z', 'z', 'x', 'z' }, 'z'));

    try std.testing.expect(string.sysfsStreq("auto\n", "auto"));
    try std.testing.expect(string.sysfs_streq("auto", "auto\n"));

    const sysfs_haystack = [_][]const u8{ "off", "auto\n", "on" };
    try std.testing.expectEqual(
        string.sysfsMatchString(sysfs_haystack[0..], "auto"),
        string.sysfs_match_string(sysfs_haystack[0..], "auto"),
    );

    const match_haystack = [_][]const u8{ &[_]u8{ 'a', 0, 'x' }, "beta", "gamma" };
    try std.testing.expectEqual(
        string.matchString(match_haystack[0..], "a"),
        string.match_string(match_haystack[0..], "a"),
    );
    try std.testing.expectEqual(
        string.strHasPrefix(&[_]u8{ 'z', 'i', 'g', 0, 'x' }, "zig"),
        string.str_has_prefix(&[_]u8{ 'z', 'i', 'g', 0, 'x' }, "zig"),
    );
    try std.testing.expectEqual(
        string.strEndsWith(&[_]u8{ 'z', 'i', 'g', '-', 'm', 'o', 'd', 'e', 0, 'x' }, "mode"),
        string.str_ends_with(&[_]u8{ 'z', 'i', 'g', '-', 'm', 'o', 'd', 'e', 0, 'x' }, "mode"),
    );
}

test "phase1 helper ports A rbtree plain traversal duplicate lookup and replacement stay ordered" {
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

    const cmp_node = struct {
        fn compare(lhs: *const rbtree.Node, rhs: *const rbtree.Node) i32 {
            const lhs_entry: *const Entry = @fieldParentPtr("node", lhs);
            const rhs_entry: *const Entry = @fieldParentPtr("node", rhs);
            if (lhs_entry.key < rhs_entry.key) return -1;
            if (lhs_entry.key > rhs_entry.key) return 1;
            if (lhs_entry.serial < rhs_entry.serial) return -1;
            if (lhs_entry.serial > rhs_entry.serial) return 1;
            return 0;
        }
    }.compare;

    const cmp_key = struct {
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
    };
    var root = rbtree.Root.init();
    for (&entries) |*entry| {
        rbtree.add(&entry.node, &root, less);
    }

    var duplicate_probe = Entry{ .key = 10, .serial = 2 };
    const duplicate = rbtree.findAdd(&duplicate_probe.node, &root, cmp_node) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(*rbtree.Node, &entries[2].node), duplicate);

    const wanted = @as(i32, 10);
    const first_match = rbtree.findFirst(&wanted, &root, cmp_key) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(*rbtree.Node, &entries[0].node), first_match);
    const second_match = rbtree.nextMatch(&wanted, first_match, cmp_key) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(*rbtree.Node, &entries[2].node), second_match);
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.nextMatch(&wanted, second_match, cmp_key));

    var replacement = Entry{ .key = 5, .serial = 9 };
    rbtree.rb_replace_node(&entries[1].node, &replacement.node, &root);
    try std.testing.expectEqual(@as(?*rbtree.Node, &replacement.node), rbtree.rb_first(&root));

    const last = rbtree.rb_last(&root) orelse return error.TestUnexpectedResult;
    const last_entry: *const Entry = @fieldParentPtr("node", last);
    try std.testing.expectEqual(@as(i32, 15), last_entry.key);

    const previous = rbtree.rb_prev(last) orelse return error.TestUnexpectedResult;
    const previous_entry: *const Entry = @fieldParentPtr("node", previous);
    try std.testing.expectEqual(@as(i32, 10), previous_entry.key);
    try std.testing.expectEqual(@as(usize, 2), previous_entry.serial);
}
