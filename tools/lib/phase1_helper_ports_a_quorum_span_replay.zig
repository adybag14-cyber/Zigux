const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

const Word = bitmap.Word;

const Entry = struct {
    key: usize,
    ordinal: usize,
    node: rbtree.Node = rbtree.Node.init(),
};

fn entryLess(lhs: *const rbtree.Node, rhs: *const rbtree.Node) bool {
    const lhs_entry: *const Entry = @fieldParentPtr("node", lhs);
    const rhs_entry: *const Entry = @fieldParentPtr("node", rhs);
    if (lhs_entry.key != rhs_entry.key) {
        return lhs_entry.key < rhs_entry.key;
    }
    return lhs_entry.ordinal < rhs_entry.ordinal;
}

fn compareKey(key: *const anyopaque, node: *const rbtree.Node) i32 {
    const wanted: *const usize = @ptrCast(@alignCast(key));
    const entry: *const Entry = @fieldParentPtr("node", node);
    if (wanted.* < entry.key) return -1;
    if (wanted.* > entry.key) return 1;
    return 0;
}

fn keyOf(node: *const rbtree.Node) usize {
    const entry: *const Entry = @fieldParentPtr("node", node);
    return entry.key;
}

fn ordinalOf(node: *const rbtree.Node) usize {
    const entry: *const Entry = @fieldParentPtr("node", node);
    return entry.ordinal;
}

test "phase1 helper ports A quorum span replay" {
    const nbits = bitmap.bits_per_long + 24;
    var lane_a = [_]Word{ 0, 0 };
    var lane_b = [_]Word{ 0, 0 };
    var lane_c = [_]Word{ 0, 0 };

    bitmap.setRange(&lane_a, 3, 3);
    bitmap.setRange(&lane_a, bitmap.bits_per_long + 1, 3);
    bitmap.setRange(&lane_a, bitmap.bits_per_long + 12, 1);

    bitmap.setRange(&lane_b, 4, 3);
    bitmap.setRange(&lane_b, bitmap.bits_per_long + 3, 3);
    bitmap.setRange(&lane_b, bitmap.bits_per_long + 12, 1);

    bitmap.setRange(&lane_c, 5, 3);
    bitmap.setRange(&lane_c, bitmap.bits_per_long + 4, 3);
    bitmap.setRange(&lane_c, bitmap.bits_per_long + 18, 1);

    var ab = [_]Word{ 0, 0 };
    var ac = [_]Word{ 0, 0 };
    var bc = [_]Word{ 0, 0 };
    var majority = [_]Word{ 0, 0 };
    var exception = [_]Word{ 0, 0 };
    var scratch = [_]Word{ 0, 0 };

    try std.testing.expect(bitmap.andBits(&ab, &lane_a, &lane_b, nbits));
    try std.testing.expect(bitmap.andBits(&ac, &lane_a, &lane_c, nbits));
    try std.testing.expect(bitmap.andBits(&bc, &lane_b, &lane_c, nbits));
    bitmap.orBits(&scratch, &ab, &ac, nbits);
    bitmap.orBits(&majority, &scratch, &bc, nbits);
    try std.testing.expect(bitmap.andNotBits(&exception, &lane_c, &majority, nbits));

    try std.testing.expectEqual(@as(usize, 7), bitmap.weight(&majority, nbits));
    try std.testing.expectEqual(@as(usize, 3), bitmap.weight(&exception, nbits));
    try std.testing.expect(bitmap.subset(&ab, &majority, nbits));
    try std.testing.expect(bitmap.intersects(&majority, &lane_c, nbits));

    const first_majority = find_bit.findFirstBit(&majority, nbits);
    const next_majority = find_bit.findNextBit(&majority, nbits, first_majority + 2);
    const first_c_quorum = find_bit.findFirstAndBit(&majority, &lane_c, nbits);
    const first_exception = find_bit.findFirstAndNotBit(&lane_c, &majority, nbits);
    const last_exception = find_bit.findLastBit(&exception, nbits);

    try std.testing.expectEqual(@as(usize, 4), first_majority);
    try std.testing.expectEqual(@as(usize, 6), next_majority);
    try std.testing.expectEqual(@as(usize, 5), first_c_quorum);
    try std.testing.expectEqual(@as(usize, 7), first_exception);
    try std.testing.expectEqual(bitmap.bits_per_long + 18, last_exception);

    var first_clump: u8 = 0;
    try std.testing.expectEqual(@as(usize, 0), find_bit.findFirstClump8(&first_clump, &exception, nbits));
    try std.testing.expectEqual(@as(u8, 0x80), first_clump);

    var second_clump: u8 = 0;
    try std.testing.expectEqual(bitmap.bits_per_long, find_bit.findNextClump8(&second_clump, &exception, nbits, bitmap.bits_per_long));
    try std.testing.expectEqual(@as(u8, 0x40), second_clump);

    var rendered_buffer: [64]u8 = undefined;
    const rendered_len = bitmap.scnprintf(&majority, nbits, &rendered_buffer);
    const rendered = rendered_buffer[0..rendered_len];

    var padded = [_]u8{0} ** 80;
    padded[0] = ' ';
    @memcpy(padded[1 .. 1 + rendered.len], rendered);
    padded[1 + rendered.len] = ' ';
    padded[2 + rendered.len] = '\n';
    const trimmed = string.trimSpaces(padded[0 .. 3 + rendered.len]);
    try std.testing.expectEqualSlices(u8, rendered, trimmed);
    try std.testing.expectEqual(@as(usize, 3), string.strHasPrefix(trimmed, "4-6"));

    var last_range_buffer: [16]u8 = undefined;
    const last_range = try std.fmt.bufPrint(&last_range_buffer, "{d}", .{bitmap.bits_per_long + 12});
    try std.testing.expect(string.strEndsWith(trimmed, last_range));

    var label = [_]u8{ ' ', 'q', 'u', 'o', 'r', 'u', 'm', ' ', 's', 'p', 'a', 'n', ' ', 0 };
    const compact = string.removeSpaces(&label);
    try std.testing.expectEqualSlices(u8, "quorumspan", compact);
    try std.testing.expectEqual(@as(?usize, 1), string.sysfsMatchString(&[_][]const u8{ "other", trimmed, "miss" }, trimmed));

    var copied = [_]u8{0xaa} ** 24;
    try std.testing.expectEqual(@as(isize, @intCast(compact.len)), string.strscpyPad(&copied, compact));
    try std.testing.expectEqual(@as(u8, 0), copied[compact.len]);
    try std.testing.expectEqual(@as(u8, 0), copied[compact.len + 1]);

    var root = rbtree.RootCached.init();
    var entries = [_]Entry{
        .{ .key = first_majority, .ordinal = 0 },
        .{ .key = first_c_quorum, .ordinal = 1 },
        .{ .key = next_majority, .ordinal = 2 },
        .{ .key = first_c_quorum, .ordinal = 3 },
        .{ .key = first_exception, .ordinal = 4 },
        .{ .key = last_exception, .ordinal = 5 },
    };

    for (&entries) |*entry| {
        _ = rbtree.addCached(&entry.node, &root, entryLess);
    }

    try std.testing.expectEqual(first_majority, keyOf(rbtree.firstCached(&root).?));

    var duplicate_ordinals: [2]usize = undefined;
    var duplicate_count: usize = 0;
    var iter = rbtree.matchIterator(&first_c_quorum, &root.root, compareKey);
    while (iter.next()) |node| {
        duplicate_ordinals[duplicate_count] = ordinalOf(node);
        duplicate_count += 1;
    }
    try std.testing.expectEqual(@as(usize, 2), duplicate_count);
    try std.testing.expectEqualSlices(usize, &[_]usize{ 1, 3 }, duplicate_ordinals[0..duplicate_count]);

    const promoted = rbtree.eraseCached(&entries[0].node, &root) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(first_c_quorum, keyOf(promoted));
    try std.testing.expectEqual(first_c_quorum, keyOf(rbtree.firstCached(&root).?));

    rbtree.eraseInitCached(&entries[4].node, &root);
    try std.testing.expect(rbtree.emptyNode(&entries[4].node));
    try std.testing.expect(rbtree.find(&first_exception, &root.root, compareKey) == null);
    try std.testing.expectEqual(last_exception, keyOf(rbtree.last(&root.root).?));
}
