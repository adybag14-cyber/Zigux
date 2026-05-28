const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

test "phase1 helper ports A bitmap tail formatting keeps partial tails merged" {
    const nbits = bitmap.bits_per_long + 9;
    var map = [_]bitmap.Word{ 0, 0 };

    bitmap.setRange(&map, bitmap.bits_per_long - 2, 6);
    bitmap.setRange(&map, bitmap.bits_per_long + 7, 1);

    var direct_buffer: [64]u8 = undefined;
    var alias_buffer: [64]u8 = undefined;
    const direct_len = bitmap.scnprintf(&map, nbits, &direct_buffer);
    const alias_len = bitmap.bitmap_scnprintf(&map, nbits, &alias_buffer);

    var expected: [32]u8 = undefined;
    const expected_text = try std.fmt.bufPrint(
        &expected,
        "{d}-{d},{d}",
        .{ bitmap.bits_per_long - 2, bitmap.bits_per_long + 3, bitmap.bits_per_long + 7 },
    );

    try std.testing.expectEqual(direct_len, alias_len);
    try std.testing.expectEqualStrings(expected_text, direct_buffer[0..direct_len]);
    try std.testing.expectEqualStrings(expected_text, alias_buffer[0..alias_len]);

    var terminator_only = [_]u8{0xaa};
    const terminator_only_len = bitmap.bitmap_scnprintf(&map, nbits, terminator_only[0..1]);
    try std.testing.expectEqual(@as(usize, 0), terminator_only_len);
    try std.testing.expectEqual(@as(u8, 0), terminator_only[0]);
}

test "phase1 helper ports A clump scans mask tail bytes and preserve exhausted caller state" {
    const nbits = find_bit.bits_per_long + 5;
    const tail_map = [_]find_bit.Word{ 0, (@as(find_bit.Word, 1) << 3) | (@as(find_bit.Word, 1) << 6) };

    var clump: u8 = 0;
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long), find_bit.findFirstClump8(&clump, &tail_map, nbits));
    try std.testing.expectEqual(@as(u8, 0b0000_1000), clump);

    clump = 0x5a;
    try std.testing.expectEqual(@as(usize, nbits), find_bit.findNextClump8(&clump, &tail_map, nbits, find_bit.bits_per_long + 5));
    try std.testing.expectEqual(@as(u8, 0x5a), clump);
}

test "phase1 helper ports A counted string lookups keep newline-aware matches and NUL boundaries" {
    const sysfs_haystack = [_][]const u8{ "off", "auto\n", "auto", "on" };
    try std.testing.expectEqual(@as(?usize, 1), string.sysfsMatchString(sysfs_haystack[0..], "auto"));

    const exact_haystack = [_][]const u8{
        &[_]u8{ 'a', 0, 'x' },
        "beta",
        "alpha",
    };
    try std.testing.expectEqual(@as(?usize, 0), string.matchString(exact_haystack[0..], "a"));

    try std.testing.expectEqual(@as(usize, 3), string.strHasPrefix(&[_]u8{ 'k', 'e', 'r', 0, 'x' }, "ker"));
    try std.testing.expectEqual(@as(?usize, 1), string.strnchr(&[_]u8{ 'a', 0, 'b' }, 3, 0));
    try std.testing.expectEqual(@as(?usize, null), string.strnchr("abc", 3, 0));
}

test "phase1 helper ports A cached replacement keeps leftmost promotion stable" {
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

    var entries = [_]Entry{
        .{ .key = 10, .serial = 0 },
        .{ .key = 5, .serial = 1 },
        .{ .key = 20, .serial = 2 },
        .{ .key = 15, .serial = 3 },
    };
    var replacement = Entry{ .key = 20, .serial = 4 };
    var root = rbtree.RootCached.init();

    for (&entries) |*entry| {
        _ = rbtree.addCached(&entry.node, &root, less);
    }

    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[1].node), rbtree.firstCached(&root));

    rbtree.replaceNodeCached(&entries[2].node, &replacement.node, &root);
    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[1].node), rbtree.firstCached(&root));
    try std.testing.expectEqual(rbtree.first(&root.root), rbtree.firstCached(&root));
    try std.testing.expectEqual(@as(?*rbtree.Node, &replacement.node), rbtree.last(&root.root));

    const promoted_leftmost = rbtree.eraseCached(&entries[1].node, &root) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(*rbtree.Node, &entries[0].node), promoted_leftmost);
    try std.testing.expectEqual(@as(?*rbtree.Node, promoted_leftmost), rbtree.firstCached(&root));
    try std.testing.expectEqual(rbtree.first(&root.root), rbtree.firstCached(&root));
}
