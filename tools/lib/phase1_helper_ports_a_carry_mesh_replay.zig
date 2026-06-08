const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

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

fn keyOf(node: *const rbtree.Node) usize {
    const entry: *const Entry = @fieldParentPtr("node", node);
    return entry.key;
}

test "phase1 helper ports A carry mesh replay" {
    const nbits = bitmap.bits_per_long + 19;
    var lower_gate = [_]Word{ 0, 0 };
    var upper_gate = [_]Word{ 0, 0 };
    var mask = [_]Word{ 0, 0 };
    var merged = [_]Word{ 0, 0 };
    var carried = [_]Word{ 0, 0 };
    var separated = [_]Word{ 0, 0 };
    var rendered: [160]u8 = undefined;

    bitmap.bitmap_set(&lower_gate, 1, 5);
    bitmap.bitmap_set(&lower_gate, bitmap.bits_per_long - 3, 5);
    bitmap.bitmap_set(&upper_gate, 4, 1);
    bitmap.bitmap_set(&upper_gate, bitmap.bits_per_long + 2, 7);
    bitmap.bitmap_set(&mask, 4, 1);
    bitmap.bitmap_set(&mask, bitmap.bits_per_long + 2, 7);
    bitmap.bitmap_replace(&merged, &lower_gate, &upper_gate, &mask, nbits);

    try std.testing.expectEqual(@as(usize, 1), find_bit.findFirstAndBit(&merged, &lower_gate, nbits));
    try std.testing.expectEqual(@as(usize, bitmap.bits_per_long + 2), find_bit.findFirstAndNotBit(&merged, &lower_gate, nbits));
    try std.testing.expectEqual(@as(usize, bitmap.bits_per_long + 8), find_bit.findLastBit(&merged, nbits));
    var clump: u8 = 0;
    try std.testing.expectEqual(@as(usize, 0), find_bit.findFirstClump8(&clump, &merged, nbits));
    try std.testing.expectEqual(@as(u8, 0x3e), clump);

    const carried_weight = bitmap.bitmap_weighted_or(&carried, &merged, &lower_gate, nbits);
    try std.testing.expectEqual(@as(usize, 17), carried_weight);
    try std.testing.expect(bitmap.bitmap_andnot(&separated, &carried, &lower_gate, nbits));
    try std.testing.expectEqual(@as(usize, 7), bitmap.bitmap_weight(&separated, nbits));
    try std.testing.expect(bitmap.bitmap_subset(&separated, &mask, nbits));

    const rendered_len = bitmap.bitmap_scnprintf(&carried, nbits, &rendered);
    var label: [96]u8 = undefined;
    @memset(&label, 0);
    const prefix = "  carry:";
    const suffix = "  \n";
    @memcpy(label[0..prefix.len], prefix);
    @memcpy(label[prefix.len .. prefix.len + rendered_len], rendered[0..rendered_len]);
    @memcpy(label[prefix.len + rendered_len .. prefix.len + rendered_len + suffix.len], suffix);

    const trimmed = string.strim(&label);
    try std.testing.expectEqual(@as(usize, "carry:".len), string.strHasPrefix(trimmed, "carry:"));
    try std.testing.expect(string.sysfs_streq(trimmed, label[2 .. prefix.len + rendered_len]));
    _ = string.strreplace(trimmed, ',', '|');
    try std.testing.expect(string.memchr_inv(trimmed[0.."carry:".len], 'c') != null);

    var entries = [_]Entry{
        .{ .key = find_bit.findFirstBit(&carried, nbits), .serial = 0 },
        .{ .key = find_bit.findFirstAndNotBit(&carried, &lower_gate, nbits), .serial = 1 },
        .{ .key = find_bit.findLastBit(&carried, nbits), .serial = 2 },
        .{ .key = carried_weight, .serial = 3 },
    };
    var root = rbtree.RootCached.init();
    for (&entries) |*entry| {
        _ = rbtree.rb_add_cached(&entry.node, &root, less);
    }

    try std.testing.expectEqual(@as(usize, 1), keyOf(rbtree.rb_first_cached(&root).?));
    try std.testing.expectEqual(@as(usize, bitmap.bits_per_long + 8), keyOf(rbtree.rb_last(&root.root).?));

    const erased = rbtree.rb_erase_cached(&entries[0].node, &root) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(usize, carried_weight), keyOf(erased));
    try std.testing.expectEqual(@as(usize, carried_weight), keyOf(rbtree.rb_first_cached(&root).?));

    rbtree.eraseInitCached(&entries[1].node, &root);
    try std.testing.expect(rbtree.emptyNode(&entries[1].node));
    try std.testing.expectEqual(@as(usize, carried_weight), keyOf(rbtree.rb_first_cached(&root).?));
}
