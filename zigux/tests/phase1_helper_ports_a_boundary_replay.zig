const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const rbtree = @import("rbtree");
const string = @import("string");

const Word = bitmap.Word;
const bits_per_long = bitmap.bits_per_long;

test "bitmap boundary windows stay visible through find-bit and string rendering" {
    const nbits = bits_per_long * 2 + 9;
    const boundary_start = bits_per_long - 1;
    var map = [_]Word{ 0, 0, 0 };

    bitmap.setRange(&map, boundary_start, 2);
    bitmap.setRange(&map, bits_per_long * 2 + 1, 3);
    bitmap.clearRange(&map, bits_per_long, 1);

    try std.testing.expectEqual(@as(usize, 4), bitmap.weight(&map, nbits));
    try std.testing.expectEqual(boundary_start, find_bit.findFirstBit(&map, nbits));
    try std.testing.expectEqual(bits_per_long * 2 + 1, find_bit.findNextBit(&map, nbits, bits_per_long));
    try std.testing.expectEqual(bits_per_long * 2 + 3, find_bit.findLastBit(&map, nbits));

    var rendered: [80]u8 = undefined;
    const len = bitmap.scnprintf(&map, nbits, &rendered);
    var expected: [80]u8 = undefined;
    const expected_text = try std.fmt.bufPrint(
        &expected,
        "{d},{d}-{d}",
        .{ boundary_start, bits_per_long * 2 + 1, bits_per_long * 2 + 3 },
    );
    try std.testing.expectEqualStrings(expected_text, rendered[0..len]);

    var clump: u8 = 0;
    try std.testing.expectEqual(@as(usize, boundary_start & ~@as(usize, 7)), find_bit.findFirstClump8(&clump, &map, nbits));
    try std.testing.expect(clump != 0);
}

test "string cleanup can drive reusable rbtree key ordering" {
    const Entry = struct {
        key: []const u8,
        node: rbtree.Node = rbtree.Node.init(),
    };
    const less = struct {
        fn compare(lhs: *const rbtree.Node, rhs: *const rbtree.Node) bool {
            const lhs_entry: *const Entry = @fieldParentPtr("node", lhs);
            const rhs_entry: *const Entry = @fieldParentPtr("node", rhs);
            return std.mem.order(u8, lhs_entry.key, rhs_entry.key) == .lt;
        }
    }.compare;

    var alpha_buf = [_]u8{ ' ', 'a', 'l', 'p', 'h', 'a', ' ', 0 };
    var beta_buf = [_]u8{ ' ', 'b', 'e', 't', 'a', ' ', 0, 'x' };
    var gamma_buf = [_]u8{ 'g', 'a', 'm', 'm', 'a', 0 };

    const alpha = string.removeSpaces(string.trimSpaces(alpha_buf[0..]));
    const beta = string.removeSpaces(string.trimSpaces(beta_buf[0..]));
    const gamma = string.trimSpaces(gamma_buf[0..]);

    try std.testing.expectEqual(@as(usize, 5), string.strreplace(alpha, 'a', 'A'));
    try std.testing.expectEqualStrings("AlphA", alpha);
    try std.testing.expectEqual(@as(usize, 4), string.strHasPrefix(beta, "beta"));

    var entries = [_]Entry{
        .{ .key = gamma },
        .{ .key = beta },
        .{ .key = alpha },
    };
    var root = rbtree.RootCached.init();

    for (&entries) |*entry| {
        _ = rbtree.addCached(&entry.node, &root, less);
    }

    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[2].node), rbtree.firstCached(&root));

    var order: [3][]const u8 = undefined;
    var count: usize = 0;
    var current = rbtree.first(&root.root);
    while (current) |node| : (current = rbtree.next(node)) {
        const entry: *const Entry = @fieldParentPtr("node", node);
        order[count] = entry.key;
        count += 1;
    }

    try std.testing.expectEqual(@as(usize, 3), count);
    try std.testing.expectEqualStrings("AlphA", order[0]);
    try std.testing.expectEqualStrings("beta", order[1]);
    try std.testing.expectEqualStrings("gamma", order[2]);
}
