const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

const Word = find_bit.Word;

test "bitmap range formatting and clump scans share tail boundaries" {
    const nbits = find_bit.bits_per_long + 12;
    var map = [_]Word{ 0, 0 };

    bitmap.setRange(&map, 3, 2);
    bitmap.setRange(&map, 12, 1);
    bitmap.setRange(&map, find_bit.bits_per_long + 4, 2);

    var formatted: [48]u8 = undefined;
    const formatted_len = bitmap.scnprintf(&map, nbits, &formatted);

    var expected: [48]u8 = undefined;
    const expected_text = try std.fmt.bufPrint(
        &expected,
        "3-4,12,{d}-{d}",
        .{ find_bit.bits_per_long + 4, find_bit.bits_per_long + 5 },
    );
    try std.testing.expectEqualStrings(expected_text, formatted[0..formatted_len]);

    var clump: u8 = 0;
    try std.testing.expectEqual(@as(usize, 0), find_bit.findFirstClump8(&clump, &map, nbits));
    try std.testing.expectEqual(@as(u8, 0b0001_1000), clump);

    clump = 0;
    try std.testing.expectEqual(@as(usize, 8), find_bit.findNextClump8(&clump, &map, nbits, 8));
    try std.testing.expectEqual(@as(u8, 0b0001_0000), clump);

    clump = 0;
    try std.testing.expectEqual(find_bit.bits_per_long, find_bit.findNextClump8(&clump, &map, nbits, find_bit.bits_per_long));
    try std.testing.expectEqual(@as(u8, 0b0011_0000), clump);

    clump = 0xa5;
    try std.testing.expectEqual(nbits, find_bit.findNextClump8(&clump, &map, nbits, nbits));
    try std.testing.expectEqual(@as(u8, 0xa5), clump);
}

test "string token cleanup preserves C-string search boundaries" {
    var spaced = [_]u8{ ' ', 'l', 'a', 'n', 'e', ' ', '0', '6', ' ', 0, 'x' };
    const trimmed = string.strim(spaced[0..]);
    try std.testing.expectEqualStrings("lane 06", trimmed);

    const token_names = [_][]const u8{ "bitmap", "find_bit", "string", "rbtree" };
    try std.testing.expectEqual(@as(?usize, 1), string.matchString(token_names[0..], "find_bit"));
    try std.testing.expectEqual(@as(?usize, null), string.match_string(token_names[0..], "cmdline"));

    try std.testing.expectEqual(@as(?usize, 4), string.strnchr("zero-token", 8, '-'));
    try std.testing.expectEqual(@as(?usize, null), string.strnchr("zero-token", 4, '-'));
    try std.testing.expect(string.strEndsWith("phase1-helper-ports-a", "ports-a"));

    var compact = [_]u8{ 'f', 'i', 'n', 'd', ' ', 'b', 'i', 't', 0, 'x' };
    const compacted = string.remove_spaces(compact[0..]);
    try std.testing.expectEqualStrings("findbit", compacted);
    try std.testing.expectEqual(@as(usize, 7), string.strreplace(compact[0..], 'i', 'I'));
    try std.testing.expectEqualStrings("fIndbIt", compact[0..7]);
}

test "rbtree match iterator exhausts duplicate ranges without leaking neighbors" {
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

    const cmp = struct {
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
        .{ .key = 10, .serial = 4 },
    };
    var root = rbtree.Root.init();

    for (&entries) |*entry| {
        rbtree.add(&entry.node, &root, less);
    }

    const wanted = @as(i32, 10);
    var iter = rbtree.matchIterator(&wanted, &root, cmp);
    var serials: [3]usize = undefined;
    var count: usize = 0;
    while (iter.next()) |node| {
        const entry: *const Entry = @fieldParentPtr("node", node);
        serials[count] = entry.serial;
        count += 1;
    }

    try std.testing.expectEqual(@as(usize, 3), count);
    try std.testing.expectEqualSlices(usize, &[_]usize{ 0, 2, 4 }, serials[0..count]);
    try std.testing.expect(iter.next() == null);

    const neighbor = @as(i32, 15);
    var neighbor_iter = rbtree.matchIterator(&neighbor, &root, cmp);
    const neighbor_node = neighbor_iter.next() orelse return error.TestUnexpectedResult;
    const neighbor_entry: *const Entry = @fieldParentPtr("node", neighbor_node);
    try std.testing.expectEqual(@as(usize, 3), neighbor_entry.serial);
    try std.testing.expect(neighbor_iter.next() == null);
}

test "helper aliases keep formatted tokens and tree lookup decisions aligned" {
    var map = [_]Word{0};
    bitmap.bitmap_set(&map, 1, 3);
    bitmap.bitmap_set(&map, 7, 1);

    var encoded: [16]u8 = undefined;
    const encoded_len = bitmap.bitmap_scnprintf(&map, 8, &encoded);
    try std.testing.expectEqualStrings("1-3,7", encoded[0..encoded_len]);
    try std.testing.expect(string.strEndsWith(encoded[0..encoded_len], "7"));
    try std.testing.expectEqual(@as(?usize, 3), string.strnchr(encoded[0..encoded_len], encoded_len, ','));

    const Entry = struct {
        key: i32,
        node: rbtree.Node = rbtree.Node.init(),
    };
    const cmp = struct {
        fn compare(lhs: *const rbtree.Node, rhs: *const rbtree.Node) i32 {
            const lhs_entry: *const Entry = @fieldParentPtr("node", lhs);
            const rhs_entry: *const Entry = @fieldParentPtr("node", rhs);
            if (lhs_entry.key < rhs_entry.key) return -1;
            if (lhs_entry.key > rhs_entry.key) return 1;
            return 0;
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

    var root = rbtree.Root.init();
    var first = Entry{ .key = 1 };
    var second = Entry{ .key = 7 };
    var duplicate = Entry{ .key = 7 };

    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.findAdd(&first.node, &root, cmp));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.findAdd(&second.node, &root, cmp));
    try std.testing.expectEqual(@as(?*rbtree.Node, &second.node), rbtree.findAdd(&duplicate.node, &root, cmp));

    const selected = @as(i32, @intCast(find_bit.findLastBit(&map, 8)));
    const found = rbtree.find(&selected, &root, key_cmp) orelse return error.TestUnexpectedResult;
    try std.testing.expect(found == &second.node);
}
