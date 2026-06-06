const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const rbtree = @import("rbtree");
const string = @import("string");

const Word = bitmap.Word;

const Entry = struct {
    key: usize,
    serial: usize,
    node: rbtree.Node = rbtree.Node.init(),
};

fn less(lhs: *const rbtree.Node, rhs: *const rbtree.Node) bool {
    const lhs_entry: *const Entry = @fieldParentPtr("node", lhs);
    const rhs_entry: *const Entry = @fieldParentPtr("node", rhs);
    if (lhs_entry.key != rhs_entry.key) {
        return lhs_entry.key < rhs_entry.key;
    }
    return lhs_entry.serial < rhs_entry.serial;
}

fn collect(root: *const rbtree.Root, out: []usize) usize {
    var count: usize = 0;
    var cursor = rbtree.first(root);
    while (cursor) |node| : (cursor = rbtree.next(node)) {
        const entry: *const Entry = @fieldParentPtr("node", node);
        out[count] = entry.key;
        count += 1;
    }
    return count;
}

test "phase1 helper ports A masked cursor replay feeds stable rbtree order" {
    const nbits = bitmap.bits_per_long + 13;
    var source = [_]Word{ 0, 0 };
    var deny = [_]Word{ 0, 0 };
    var allowed = [_]Word{ 0, 0 };

    bitmap.setRange(&source, 2, 3);
    bitmap.setRange(&source, bitmap.bits_per_long - 1, 3);
    bitmap.setRange(&source, bitmap.bits_per_long + 8, 1);
    bitmap.setRange(&source, bitmap.bits_per_long + 12, 1);
    bitmap.setRange(&deny, 3, 1);
    bitmap.setRange(&deny, bitmap.bits_per_long, 1);
    bitmap.setRange(&deny, bitmap.bits_per_long + 12, 1);

    try std.testing.expect(bitmap.andNotBits(&allowed, &source, &deny, nbits));
    try std.testing.expectEqual(@as(usize, 5), bitmap.weight(&allowed, nbits));
    try std.testing.expectEqual(@as(usize, 2), find_bit.findFirstAndNotBit(&source, &deny, nbits));
    try std.testing.expectEqual(@as(usize, 4), find_bit.findNextAndNotBit(&source, &deny, nbits, 3));
    try std.testing.expectEqual(
        @as(usize, bitmap.bits_per_long - 1),
        find_bit.findNextAndNotBit(&source, &deny, nbits, 5),
    );
    try std.testing.expectEqual(
        @as(usize, bitmap.bits_per_long + 1),
        find_bit.findNextAndNotBit(&source, &deny, nbits, bitmap.bits_per_long),
    );
    try std.testing.expectEqual(
        @as(usize, bitmap.bits_per_long + 8),
        find_bit.findNextAndNotBit(&source, &deny, nbits, bitmap.bits_per_long + 2),
    );
    try std.testing.expectEqual(nbits, find_bit.findNextAndNotBit(&source, &deny, nbits, bitmap.bits_per_long + 9));

    var rendered: [64]u8 = undefined;
    const rendered_len = bitmap.scnprintf(&allowed, nbits, &rendered);
    const rendered_text = rendered[0..rendered_len];
    var expected_suffix: [16]u8 = undefined;
    const expected_suffix_text = try std.fmt.bufPrint(&expected_suffix, "{d}", .{bitmap.bits_per_long + 8});
    try std.testing.expect(string.strstarts(rendered_text, "2"));
    try std.testing.expect(string.strEndsWith(rendered_text, expected_suffix_text));
    try std.testing.expect(string.strnchr(rendered_text, rendered_len, ',') != null);
    try std.testing.expect(string.strnchr(rendered_text, rendered_len, 0) == null);

    var entries: [5]Entry = undefined;
    var count: usize = 0;
    var cursor = find_bit.findFirstBit(&allowed, nbits);
    while (cursor < nbits) : (cursor = find_bit.findNextBit(&allowed, nbits, cursor + 1)) {
        entries[count] = .{ .key = cursor, .serial = count };
        count += 1;
    }
    try std.testing.expectEqual(@as(usize, 5), count);

    var root = rbtree.Root.init();
    var insert_idx = count;
    while (insert_idx > 0) {
        insert_idx -= 1;
        rbtree.add(&entries[insert_idx].node, &root, less);
    }

    var order: [5]usize = undefined;
    const order_count = collect(&root, &order);
    try std.testing.expectEqualSlices(
        usize,
        &[_]usize{ 2, 4, bitmap.bits_per_long - 1, bitmap.bits_per_long + 1, bitmap.bits_per_long + 8 },
        order[0..order_count],
    );

    rbtree.eraseInit(&entries[2].node, &root);
    try std.testing.expect(rbtree.emptyNode(&entries[2].node));

    var after_erase: [4]usize = undefined;
    const after_erase_count = collect(&root, &after_erase);
    try std.testing.expectEqualSlices(
        usize,
        &[_]usize{ 2, 4, bitmap.bits_per_long + 1, bitmap.bits_per_long + 8 },
        after_erase[0..after_erase_count],
    );
}
