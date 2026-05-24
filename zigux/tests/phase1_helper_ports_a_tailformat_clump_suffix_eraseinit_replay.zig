const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

test "lane06 bitmap tail formatting and weighted aliases stay aligned" {
    const nbits = bitmap.bits_per_long + 6;
    const lhs = [_]bitmap.Word{
        (@as(bitmap.Word, 1) << (bitmap.bits_per_long - 2)) |
            (@as(bitmap.Word, 1) << (bitmap.bits_per_long - 1)),
        (@as(bitmap.Word, 1) << 0) | (@as(bitmap.Word, 1) << 3) | (@as(bitmap.Word, 1) << 9),
    };
    const rhs = [_]bitmap.Word{
        0,
        (@as(bitmap.Word, 1) << 1) | (@as(bitmap.Word, 1) << 3) | (@as(bitmap.Word, 1) << 10),
    };

    var direct_or = [_]bitmap.Word{ 0, 0 };
    var alias_or = [_]bitmap.Word{ 0, 0 };
    const direct_weight = bitmap.weightedOr(&direct_or, &lhs, &rhs, nbits);
    const alias_weight = bitmap.bitmap_weighted_or(&alias_or, &lhs, &rhs, nbits);
    try std.testing.expectEqual(direct_weight, alias_weight);
    try std.testing.expectEqualSlices(bitmap.Word, &direct_or, &alias_or);
    try std.testing.expectEqual(@as(usize, 5), direct_weight);

    var direct_text: [64]u8 = undefined;
    var alias_text: [64]u8 = undefined;
    const direct_len = bitmap.scnprintf(&direct_or, nbits, &direct_text);
    const alias_len = bitmap.bitmap_scnprintf(&alias_or, nbits, &alias_text);
    try std.testing.expectEqual(direct_len, alias_len);
    try std.testing.expectEqualStrings(direct_text[0..direct_len], alias_text[0..alias_len]);

    var expected: [48]u8 = undefined;
    const expected_text = try std.fmt.bufPrint(
        &expected,
        "{d}-{d},{d}",
        .{
            bitmap.bits_per_long - 2,
            bitmap.bits_per_long + 1,
            bitmap.bits_per_long + 3,
        },
    );
    try std.testing.expectEqualStrings(expected_text, direct_text[0..direct_len]);
}

test "lane06 find_bit clump and last-bit aliases stay tail-aware" {
    const nbits = find_bit.bits_per_long + 6;
    const bitmap_words = [_]find_bit.Word{
        0,
        (@as(find_bit.Word, 1) << 1) |
            (@as(find_bit.Word, 1) << 4) |
            (@as(find_bit.Word, 1) << 5) |
            (@as(find_bit.Word, 1) << 9),
    };

    var clump: u8 = 0;
    try std.testing.expectEqual(
        @as(usize, find_bit.bits_per_long),
        find_bit.findFirstClump8(&clump, &bitmap_words, nbits),
    );
    try std.testing.expectEqual(@as(u8, 0b0011_0010), clump);

    clump = 0;
    try std.testing.expectEqual(
        @as(usize, find_bit.bits_per_long),
        find_bit.find_next_clump8(&clump, &bitmap_words, nbits, find_bit.bits_per_long + 2),
    );
    try std.testing.expectEqual(@as(u8, 0b0011_0010), clump);

    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 5), find_bit.findLastBit(&bitmap_words, nbits));
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 5), find_bit.find_last_bit(&bitmap_words, nbits));
}

test "lane06 string suffix and newline-aware aliases stay aligned" {
    try std.testing.expect(string.strEndsWith("phase1-lane06", "lane06"));
    try std.testing.expect(string.str_ends_with("phase1-lane06", "lane06"));
    try std.testing.expect(!string.strEndsWith("phase1-lane06", "lane07"));

    try std.testing.expect(string.sysfsStreq("mode\n", "mode"));
    try std.testing.expect(string.sysfs_streq("ready", "ready\n"));

    const sysfs_entries = [_][]const u8{ "auto\n", "manual", "safe\n" };
    try std.testing.expectEqual(@as(?usize, 0), string.sysfsMatchString(&sysfs_entries, "auto"));
    try std.testing.expectEqual(@as(?usize, 2), string.sysfs_match_string(&sysfs_entries, "safe"));

    const plain_entries = [_][]const u8{ "amber", "blue", "cyan" };
    try std.testing.expectEqual(@as(?usize, 1), string.matchString(&plain_entries, "blue"));
    try std.testing.expectEqual(@as(?usize, 1), string.match_string(&plain_entries, "blue"));
    try std.testing.expectEqual(@as(?usize, 5), string.memchrInv("aaaaab", 'a'));
    try std.testing.expectEqual(@as(?usize, 5), string.memchr_inv("aaaaab", 'a'));
}

test "lane06 rbtree erase-init cached aliases keep leftmost state aligned" {
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

    var primary_entries = [_]Entry{
        .{ .key = 10, .serial = 0 },
        .{ .key = 5, .serial = 1 },
        .{ .key = 15, .serial = 2 },
    };
    var alias_entries = [_]Entry{
        .{ .key = 10, .serial = 0 },
        .{ .key = 5, .serial = 1 },
        .{ .key = 15, .serial = 2 },
    };
    var primary_replacement = Entry{ .key = 15, .serial = 3 };
    var alias_replacement = Entry{ .key = 15, .serial = 3 };
    var primary_root = rbtree.RootCached.init();
    var alias_root = rbtree.RootCached.init();

    for (&primary_entries, &alias_entries) |*primary_entry, *alias_entry| {
        _ = rbtree.addCached(&primary_entry.node, &primary_root, less);
        _ = rbtree.addCached(&alias_entry.node, &alias_root, less);
    }

    rbtree.replaceNodeCached(&primary_entries[2].node, &primary_replacement.node, &primary_root);
    rbtree.rb_replace_node_cached(&alias_entries[2].node, &alias_replacement.node, &alias_root);
    try std.testing.expectEqual(rbtree.first(&primary_root.root), rbtree.firstCached(&primary_root));
    try std.testing.expectEqual(rbtree.first(&alias_root.root), rbtree.firstCached(&alias_root));
    try std.testing.expectEqual(@as(?*rbtree.Node, &primary_entries[1].node), rbtree.firstCached(&primary_root));
    try std.testing.expectEqual(@as(?*rbtree.Node, &alias_entries[1].node), rbtree.firstCached(&alias_root));

    rbtree.eraseInitCached(&primary_entries[1].node, &primary_root);
    rbtree.rb_erase_init_cached(&alias_entries[1].node, &alias_root);
    try std.testing.expect(rbtree.emptyNode(&primary_entries[1].node));
    try std.testing.expect(rbtree.emptyNode(&alias_entries[1].node));
    try std.testing.expectEqual(rbtree.first(&primary_root.root), rbtree.firstCached(&primary_root));
    try std.testing.expectEqual(rbtree.first(&alias_root.root), rbtree.firstCached(&alias_root));
    try std.testing.expectEqual(@as(?*rbtree.Node, &primary_entries[0].node), rbtree.firstCached(&primary_root));
    try std.testing.expectEqual(@as(?*rbtree.Node, &alias_entries[0].node), rbtree.firstCached(&alias_root));
}
