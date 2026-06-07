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

fn erasePlain(node: *rbtree.Node, root: *rbtree.Root) void {
    if (@hasDecl(rbtree, "rb_erase")) {
        rbtree.rb_erase(node, root);
    } else {
        rbtree.erase(node, root);
    }
}

fn eraseInitPlain(node: *rbtree.Node, root: *rbtree.Root) void {
    if (@hasDecl(rbtree, "rb_erase_init")) {
        rbtree.rb_erase_init(node, root);
    } else {
        rbtree.eraseInit(node, root);
    }
}

test "phase1 helper ports A alias gap drains bitmap-derived rbtree keys" {
    const bpl = bitmap.bits_per_long;
    const nbits = bpl + 12;
    const nwords = bitmap.bitsToWords(nbits);

    var old = [_]Word{0} ** 2;
    var new = [_]Word{0} ** 2;
    var mask = [_]Word{0} ** 2;
    old[0] = (@as(Word, 1) << 2) | (@as(Word, 1) << 5);
    old[1] = (@as(Word, 1) << 1) | (@as(Word, 1) << 9);
    new[0] = (@as(Word, 1) << 3) | (@as(Word, 1) << 5);
    new[1] = (@as(Word, 1) << 2) | (@as(Word, 1) << 11);
    mask[0] = (@as(Word, 1) << 2) | (@as(Word, 1) << 3);
    mask[1] = (@as(Word, 1) << 1) | (@as(Word, 1) << 2) | (@as(Word, 1) << 11);

    var replaced = [_]Word{0} ** 2;
    bitmap.replace(replaced[0..nwords], old[0..nwords], new[0..nwords], mask[0..nwords], nbits);
    try std.testing.expectEqual(@as(usize, 5), bitmap.weight(&replaced, nbits));

    var deny = [_]Word{0} ** 2;
    deny[0] = @as(Word, 1) << 5;
    deny[1] = @as(Word, 1) << 9;

    var allowed = [_]Word{0} ** 2;
    try std.testing.expect(bitmap.andNotBits(&allowed, &replaced, &deny, nbits));
    try std.testing.expectEqual(@as(usize, 3), bitmap.weight(&allowed, nbits));
    try std.testing.expect(bitmap.subset(&allowed, &replaced, nbits));
    try std.testing.expect(bitmap.intersects(&allowed, &replaced, nbits));

    const first = find_bit.findFirstAndNotBit(&replaced, &deny, nbits);
    const second = find_bit.findNextAndNotBit(&replaced, &deny, nbits, first + 1);
    const third = find_bit.findNextAndNotBit(&replaced, &deny, nbits, second + 1);
    try std.testing.expectEqual(@as(usize, 3), first);
    try std.testing.expectEqual(@as(usize, bpl + 2), second);
    try std.testing.expectEqual(@as(usize, bpl + 11), third);
    try std.testing.expectEqual(nbits, find_bit.findNextAndNotBit(&replaced, &deny, nbits, third + 1));
    try std.testing.expectEqual(second, find_bit.findNextBit(&allowed, nbits, bpl));

    var rendered_buf = [_]u8{0} ** 48;
    const rendered_len = bitmap.scnprintf(&allowed, nbits, &rendered_buf);
    const rendered = rendered_buf[0..rendered_len];
    var expected_buf = [_]u8{0} ** 48;
    const expected = try std.fmt.bufPrint(&expected_buf, "3,{d},{d}", .{ second, third });
    try std.testing.expectEqualStrings(expected, rendered);

    var padded = [_]u8{0xaa} ** 64;
    var decorated = [_]u8{0} ** 64;
    const decorated_len = try std.fmt.bufPrint(&decorated, "  {s}\n", .{rendered});
    try std.testing.expectEqual(@as(isize, @intCast(decorated_len.len)), string.strscpyPad(&padded, decorated_len));
    const trimmed = string.strim(&padded);
    try std.testing.expectEqualStrings(rendered, trimmed);
    try std.testing.expectEqual(@as(usize, 1), string.strHasPrefix(trimmed, "3"));
    try std.testing.expectEqual(third, try std.fmt.parseInt(usize, trimmed[trimmed.len - 2 ..], 10));
    try std.testing.expectEqual(@as(?usize, 1), string.memchrInv(trimmed, '3'));
    _ = string.strreplace(trimmed, ',', ':');
    var colon_expected_buf = [_]u8{0} ** 48;
    const colon_expected = try std.fmt.bufPrint(&colon_expected_buf, "3:{d}:{d}\n", .{ second, third });
    try std.testing.expectEqual(@as(?usize, 0), string.sysfsMatchString(&[_][]const u8{ trimmed, "unused" }, colon_expected));
    try std.testing.expectEqual(@as(?usize, 0), string.matchString(&[_][]const u8{ trimmed, "unused" }, trimmed));

    var entries = [_]Entry{
        .{ .key = third, .serial = 2 },
        .{ .key = first, .serial = 0 },
        .{ .key = second, .serial = 1 },
        .{ .key = bpl + 9, .serial = 3 },
    };
    var root = rbtree.Root.init();
    for (&entries) |*entry| {
        rbtree.add(&entry.node, &root, less);
    }

    erasePlain(&entries[3].node, &root);
    eraseInitPlain(&entries[1].node, &root);
    try std.testing.expect(rbtree.emptyNode(&entries[1].node));

    var order: [2]usize = undefined;
    var count: usize = 0;
    var current = rbtree.first(&root);
    while (current) |node| : (current = rbtree.next(node)) {
        const entry: *const Entry = @fieldParentPtr("node", node);
        order[count] = entry.key;
        count += 1;
    }

    try std.testing.expectEqual(@as(usize, 2), count);
    try std.testing.expectEqualSlices(usize, &[_]usize{ second, third }, order[0..count]);
}
