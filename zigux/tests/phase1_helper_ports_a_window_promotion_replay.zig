const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

const Word = bitmap.Word;
const bits_per_long = bitmap.bits_per_long;

test "phase1 helper ports A replay keeps masked windows renderable and searchable" {
    const nbits = bits_per_long + 11;
    var lhs = [_]Word{ 0, 0 };
    var rhs = [_]Word{ 0, 0 };
    var visible = [_]Word{ 0, 0 };

    bitmap.setRange(&lhs, bits_per_long - 2, 5);
    bitmap.setRange(&lhs, bits_per_long + 8, 1);
    bitmap.setRange(&rhs, bits_per_long - 1, 3);
    bitmap.setRange(&rhs, bits_per_long + 8, 1);

    try std.testing.expect(bitmap.andNotBits(&visible, &lhs, &rhs, nbits));
    try std.testing.expectEqual(@as(usize, 2), bitmap.weight(&visible, nbits));
    try std.testing.expectEqual(@as(usize, bits_per_long - 2), find_bit.findFirstBit(&visible, nbits));
    try std.testing.expectEqual(@as(usize, bits_per_long + 2), find_bit.findNextBit(&visible, nbits, bits_per_long - 1));
    try std.testing.expectEqual(@as(usize, bits_per_long + 2), find_bit.findLastBit(&visible, nbits));

    var first_clump: u8 = 0;
    try std.testing.expectEqual(
        @as(usize, bits_per_long - 8),
        find_bit.findFirstClump8(&first_clump, &visible, nbits),
    );
    try std.testing.expectEqual(@as(u8, 0b0100_0000), first_clump);

    var next_clump: u8 = 0;
    try std.testing.expectEqual(
        @as(usize, bits_per_long),
        find_bit.findNextClump8(&next_clump, &visible, nbits, bits_per_long),
    );
    try std.testing.expectEqual(@as(u8, 0b0000_0100), next_clump);

    var rendered: [64]u8 = undefined;
    const rendered_len = bitmap.scnprintf(&visible, nbits, &rendered);

    var expected: [32]u8 = undefined;
    const expected_text = try std.fmt.bufPrint(
        &expected,
        "{d},{d}",
        .{ bits_per_long - 2, bits_per_long + 2 },
    );
    try std.testing.expectEqualStrings(expected_text, rendered[0..rendered_len]);

    var prefix: [16]u8 = undefined;
    const prefix_text = try std.fmt.bufPrint(&prefix, "{d}", .{bits_per_long - 2});
    var suffix: [16]u8 = undefined;
    const suffix_text = try std.fmt.bufPrint(&suffix, "{d}", .{bits_per_long + 2});
    try std.testing.expect(string.strstarts(rendered[0 .. rendered_len + 1], prefix_text));
    try std.testing.expect(string.strEndsWith(rendered[0 .. rendered_len + 1], suffix_text));
}

test "phase1 helper ports A replay promotes cached scan keys in order" {
    const Entry = struct {
        key: usize,
        label: []const u8,
        node: rbtree.Node = rbtree.Node.init(),
    };

    const less = struct {
        fn compare(lhs: *const rbtree.Node, rhs: *const rbtree.Node) bool {
            const lhs_entry: *const Entry = @fieldParentPtr("node", lhs);
            const rhs_entry: *const Entry = @fieldParentPtr("node", rhs);
            return lhs_entry.key < rhs_entry.key;
        }
    }.compare;

    var map = [_]Word{ 0, 0 };
    bitmap.setRange(&map, 3, 1);
    bitmap.setRange(&map, bits_per_long + 1, 1);
    bitmap.setRange(&map, bits_per_long + 5, 1);

    var entries = [_]Entry{
        .{ .key = find_bit.findFirstBit(&map, bits_per_long * 2), .label = "first" },
        .{ .key = find_bit.findNextBit(&map, bits_per_long * 2, 4), .label = "middle" },
        .{ .key = find_bit.findLastBit(&map, bits_per_long * 2), .label = "tail" },
    };
    var root = rbtree.RootCached.init();

    for (&entries) |*entry| {
        _ = rbtree.addCached(&entry.node, &root, less);
    }

    const first_node = rbtree.firstCached(&root) orelse return error.TestUnexpectedResult;
    const first_entry: *const Entry = @fieldParentPtr("node", first_node);
    try std.testing.expectEqual(@as(usize, 3), first_entry.key);

    const promoted_node = rbtree.eraseCached(&entries[0].node, &root) orelse return error.TestUnexpectedResult;
    const promoted_entry: *const Entry = @fieldParentPtr("node", promoted_node);
    try std.testing.expectEqual(@as(usize, bits_per_long + 1), promoted_entry.key);
    try std.testing.expectEqual(
        @as(?usize, 1),
        string.matchString(&[_][]const u8{ "first", "middle", "tail" }, promoted_entry.label),
    );
    try std.testing.expectEqual(
        @as(?usize, 1),
        string.sysfsMatchString(&[_][]const u8{ "first\n", "middle\n", "tail\n" }, promoted_entry.label),
    );
    try std.testing.expectEqual(@as(?*rbtree.Node, promoted_node), rbtree.firstCached(&root));
}
