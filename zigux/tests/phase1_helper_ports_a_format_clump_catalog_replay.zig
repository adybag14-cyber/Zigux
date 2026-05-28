const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

test "phase1 helper ports A bitmap formatting keeps tail ranges stable across aliases" {
    const nbits = bitmap.bits_per_long + 5;
    var map = [_]bitmap.Word{ 0, 0 };
    bitmap.setRange(&map, bitmap.bits_per_long - 1, 3);
    bitmap.setRange(&map, bitmap.bits_per_long + 4, 1);

    var direct: [64]u8 = undefined;
    var alias: [64]u8 = undefined;
    const direct_len = bitmap.scnprintf(&map, nbits, &direct);
    const alias_len = bitmap.bitmap_scnprintf(&map, nbits, &alias);

    var expected: [48]u8 = undefined;
    const expected_text = try std.fmt.bufPrint(
        &expected,
        "{d}-{d},{d}",
        .{
            bitmap.bits_per_long - 1,
            bitmap.bits_per_long + 1,
            bitmap.bits_per_long + 4,
        },
    );

    try std.testing.expectEqual(direct_len, alias_len);
    try std.testing.expectEqualStrings(expected_text, direct[0..direct_len]);
    try std.testing.expectEqualStrings(expected_text, alias[0..alias_len]);
}

test "phase1 helper ports A find_bit tail clumps keep the last live byte and preserve exhausted callers" {
    const nbits = find_bit.bits_per_long + 8;
    const map = [_]find_bit.Word{
        0,
        (@as(find_bit.Word, 1) << 1) | (@as(find_bit.Word, 1) << 4),
    };

    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 4), find_bit.findLastBit(&map, nbits));
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 4), find_bit.find_last_bit(&map, nbits));

    var clump: u8 = 0;
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long), find_bit.findFirstClump8(&clump, &map, nbits));
    try std.testing.expectEqual(@as(u8, 0b0001_0010), clump);

    clump = 0x5a;
    try std.testing.expectEqual(@as(usize, nbits), find_bit._find_next_clump8(&clump, &map, nbits, find_bit.bits_per_long + 5));
    try std.testing.expectEqual(@as(u8, 0x5a), clump);
}

test "phase1 helper ports A string catalog helpers stay newline and c-string aware" {
    const sysfs_modes = [_][]const u8{ "auto\n", "auto", "manual" };
    const match_modes = [_][]const u8{
        &[_]u8{ 'z', 'i', 'g', 0, 'x' },
        "zigux",
        "tools",
    };
    const module_name = [_]u8{ 'p', 'o', 'r', 't', '.', 'z', 'i', 'g', 0, 'x' };
    const dirty = [_]u8{ 'o', 'o', 'o', 'x', 'o', 'o', 'o', 'o' };

    try std.testing.expectEqual(@as(?usize, 0), string.sysfsMatchString(sysfs_modes[0..], "auto"));
    try std.testing.expectEqual(@as(?usize, 0), string.sysfs_match_string(sysfs_modes[0..], "auto"));
    try std.testing.expectEqual(@as(?usize, 0), string.matchString(match_modes[0..], "zig"));
    try std.testing.expectEqual(@as(?usize, null), string.matchString(match_modes[0..], "missing"));
    try std.testing.expect(string.strEndsWith(&module_name, ".zig"));
    try std.testing.expectEqual(@as(?usize, 3), string.memchrInv(&dirty, 'o'));
}

test "phase1 helper ports A cached rbtree duplicate handoff keeps iteration anchored after replacement and erase" {
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

    const cmp_key = struct {
        fn compare(key: *const anyopaque, node: *const rbtree.Node) i32 {
            const wanted: *const i32 = @ptrCast(@alignCast(key));
            const entry: *const Entry = @fieldParentPtr("node", node);
            if (wanted.* < entry.key) return -1;
            if (wanted.* > entry.key) return 1;
            return 0;
        }
    }.compare;

    var first_entry = Entry{ .key = 2, .serial = 0 };
    var second_entry = Entry{ .key = 2, .serial = 1 };
    var third_entry = Entry{ .key = 5, .serial = 2 };
    var replacement = Entry{ .key = 2, .serial = 9 };
    var root = rbtree.RootCached.init();
    const needle: i32 = 2;

    _ = rbtree.addCached(&first_entry.node, &root, less);
    _ = rbtree.addCached(&second_entry.node, &root, less);
    _ = rbtree.addCached(&third_entry.node, &root, less);

    try std.testing.expectEqual(@as(?*rbtree.Node, &first_entry.node), rbtree.firstCached(&root));

    rbtree.replaceNodeCached(&second_entry.node, &replacement.node, &root);
    try std.testing.expectEqual(@as(?*rbtree.Node, &first_entry.node), rbtree.firstCached(&root));
    try std.testing.expectEqual(@as(?*rbtree.Node, &replacement.node), rbtree.nextMatch(&needle, &first_entry.node, cmp_key));

    rbtree.eraseInitCached(&first_entry.node, &root);
    try std.testing.expect(rbtree.emptyNode(&first_entry.node));
    try std.testing.expectEqual(@as(?*rbtree.Node, &replacement.node), rbtree.firstCached(&root));

    var serials: [1]usize = undefined;
    var count: usize = 0;
    var iter = rbtree.matchIterator(&needle, &root.root, cmp_key);
    while (iter.next()) |node| {
        const entry: *const Entry = @fieldParentPtr("node", node);
        serials[count] = entry.serial;
        count += 1;
    }

    try std.testing.expectEqual(@as(usize, 1), count);
    try std.testing.expectEqualSlices(usize, &[_]usize{9}, serials[0..count]);
}
