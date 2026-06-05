const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

test "andnot tail ranges drive clump scans and range rendering" {
    const nbits = find_bit.bits_per_long + 8;
    var lhs = [_]find_bit.Word{ 0, 0 };
    var rhs = [_]find_bit.Word{ 0, 0 };
    var diff = [_]find_bit.Word{ 0, 0 };

    bitmap.setRange(&lhs, 3, 5);
    bitmap.setRange(&lhs, find_bit.bits_per_long + 4, 4);
    bitmap.setRange(&rhs, 5, 2);
    bitmap.setRange(&rhs, find_bit.bits_per_long + 6, 1);

    try std.testing.expect(bitmap.andNotBits(&diff, &lhs, &rhs, nbits));
    try std.testing.expectEqual(@as(usize, 3), find_bit.findFirstBit(&diff, nbits));
    try std.testing.expectEqual(@as(usize, 7), find_bit.findNextBit(&diff, nbits, 5));
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 7), find_bit.findLastBit(&diff, nbits));

    var clump: u8 = 0;
    try std.testing.expectEqual(@as(usize, 0), find_bit.findNextClump8(&clump, &diff, nbits, 0));
    try std.testing.expectEqual(@as(u8, 0x98), clump);

    try std.testing.expectEqual(
        @as(usize, find_bit.bits_per_long),
        find_bit.findNextClump8(&clump, &diff, nbits, 8),
    );
    try std.testing.expectEqual(@as(u8, 0xb0), clump);

    var rendered: [48]u8 = undefined;
    const len = bitmap.scnprintf(&diff, nbits, &rendered);
    const expected = std.fmt.comptimePrint("3-4,7,{d}-{d},{d}", .{
        find_bit.bits_per_long + 4,
        find_bit.bits_per_long + 5,
        find_bit.bits_per_long + 7,
    });
    try std.testing.expectEqualStrings(expected, rendered[0..len]);
}

test "cleaned sysfs tokens keep exact and newline-aware matching separate" {
    var token = [_]u8{ ' ', 'm', 'o', 'd', 'e', '\t', 0, 'x' };
    const trimmed = string.strim(&token);
    try std.testing.expectEqualStrings("mode", trimmed);
    try std.testing.expect(string.streq(trimmed, "mode"));
    try std.testing.expect(!string.sysfsStreq(trimmed, "mode-extra\n"));

    const options = [_][]const u8{
        "disabled\n",
        "mode\n",
        "mode-extra\n",
    };
    try std.testing.expectEqual(@as(?usize, 1), string.sysfsMatchString(&options, "mode"));
    try std.testing.expectEqual(@as(?usize, 2), string.matchString(&options, "mode-extra\n"));
    try std.testing.expect(string.matchString(&options, "mode-extra") == null);

    var replace = [_]u8{ 'm', 'o', 'd', 'e', '-', 'o', 'n', 0 };
    try std.testing.expectEqual(@as(usize, 7), string.strreplace(&replace, '-', '_'));
    try std.testing.expectEqualStrings("mode_on", replace[0..7]);
    try std.testing.expectEqual(@as(?usize, 1), string.memchrInv(replace[0..7], 'm'));
}

test "cached rbtree erase handoff stays aligned after andnot ordering" {
    const Entry = struct {
        bit: usize,
        ordinal: usize,
        node: rbtree.Node = rbtree.Node.init(),

        fn less(lhs: *const rbtree.Node, rhs: *const rbtree.Node) bool {
            const lhs_entry: *const @This() = @fieldParentPtr("node", lhs);
            const rhs_entry: *const @This() = @fieldParentPtr("node", rhs);
            if (lhs_entry.bit != rhs_entry.bit) {
                return lhs_entry.bit < rhs_entry.bit;
            }
            return lhs_entry.ordinal < rhs_entry.ordinal;
        }
    };

    var entries = [_]Entry{
        .{ .bit = 7, .ordinal = 0 },
        .{ .bit = 3, .ordinal = 1 },
        .{ .bit = find_bit.bits_per_long + 4, .ordinal = 2 },
        .{ .bit = find_bit.bits_per_long + 7, .ordinal = 3 },
    };
    var root = rbtree.RootCached.init();

    for (&entries) |*entry| {
        _ = rbtree.addCached(&entry.node, &root, Entry.less);
    }

    try std.testing.expectEqual(@as(*rbtree.Node, &entries[1].node), rbtree.firstCached(&root).?);
    const promoted = rbtree.eraseCached(&entries[1].node, &root) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(*rbtree.Node, &entries[0].node), promoted);
    try std.testing.expectEqual(@as(*rbtree.Node, &entries[0].node), rbtree.firstCached(&root).?);

    var ordered: [3]usize = undefined;
    var count: usize = 0;
    var current = rbtree.first(&root.root);
    while (current) |node| : (current = rbtree.next(node)) {
        const entry: *const Entry = @fieldParentPtr("node", node);
        ordered[count] = entry.bit;
        count += 1;
    }

    try std.testing.expectEqualSlices(usize, &[_]usize{
        7,
        find_bit.bits_per_long + 4,
        find_bit.bits_per_long + 7,
    }, ordered[0..count]);
}
