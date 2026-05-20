const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

test "lane06 helper ports A replay keeps bitmap and find_bit tail windows aligned" {
    const nbits = bitmap.bits_per_long + 5;

    var bounded = [_]bitmap.Word{ 0, 0 };
    bitmap.setRange(&bounded, bitmap.bits_per_long - 2, 4);
    bitmap.setRange(&bounded, bitmap.bits_per_long + 4, 1);
    bounded[1] |= @as(bitmap.Word, 1) << 9;

    try std.testing.expectEqual(bitmap.bits_per_long - 2, find_bit.findFirstBit(&bounded, nbits));
    try std.testing.expectEqual(bitmap.bits_per_long + 4, find_bit.findLastBit(&bounded, nbits));
    try std.testing.expectEqual(nbits, find_bit.findNextBit(&bounded, nbits, bitmap.bits_per_long + 5));
    try std.testing.expectEqual(@as(usize, 5), bitmap.weight(&bounded, nbits));
    try std.testing.expect(!bitmap.empty(&bounded, nbits));

    const tail_noise_only = [_]bitmap.Word{ 0, @as(bitmap.Word, 1) << 9 };
    const empty_words = [_]bitmap.Word{ 0, 0 };
    try std.testing.expect(bitmap.subset(&tail_noise_only, &empty_words, nbits));
    try std.testing.expect(!bitmap.intersects(&tail_noise_only, &bounded, nbits));
}

test "lane06 helper ports A replay keeps string sysfs and prefix boundaries stable" {
    const sysfs_modes = [_][]const u8{
        "disabled",
        "auto\n",
        "manual",
        "auto",
    };
    const exact_modes = [_][]const u8{
        "disabled",
        "manual",
        "manual",
        "auto",
    };

    const auto_cstr = [_]u8{ 'a', 'u', 't', 'o', 0, 'x' };
    try std.testing.expectEqual(@as(?usize, 1), string.sysfsMatchString(&sysfs_modes, &auto_cstr));
    try std.testing.expectEqual(@as(?usize, 3), string.matchString(&exact_modes, &auto_cstr));

    const prefixed = [_]u8{ 'p', 'r', 'e', 'f', 'i', 'x', 0, 'x' };
    const prefix = [_]u8{ 'p', 'r', 'e', 0, 'y' };
    const suffix = [_]u8{ 'f', 'i', 'x', 0, 'z' };
    try std.testing.expectEqual(@as(usize, 3), string.strHasPrefix(&prefixed, &prefix));
    try std.testing.expect(string.strstarts(&prefixed, &prefix));
    try std.testing.expect(string.strEndsWith(&prefixed, &suffix));
}

test "lane06 helper ports A replay keeps cached rbtree leftmost updates stable" {
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

    var first_entry = Entry{ .key = 10, .serial = 0 };
    var leftmost_entry = Entry{ .key = 5, .serial = 1 };
    var larger_entry = Entry{ .key = 15, .serial = 2 };
    var new_leftmost = Entry{ .key = 3, .serial = 3 };
    var root = rbtree.RootCached.init();

    try std.testing.expectEqual(@as(?*rbtree.Node, &first_entry.node), rbtree.addCached(&first_entry.node, &root, less));
    try std.testing.expectEqual(@as(?*rbtree.Node, &leftmost_entry.node), rbtree.addCached(&leftmost_entry.node, &root, less));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.addCached(&larger_entry.node, &root, less));
    try std.testing.expectEqual(@as(?*rbtree.Node, &leftmost_entry.node), rbtree.firstCached(&root));

    const promoted = rbtree.eraseCached(&leftmost_entry.node, &root) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(*rbtree.Node, &first_entry.node), promoted);
    try std.testing.expectEqual(@as(?*rbtree.Node, &first_entry.node), rbtree.firstCached(&root));

    try std.testing.expectEqual(@as(?*rbtree.Node, &new_leftmost.node), rbtree.addCached(&new_leftmost.node, &root, less));
    try std.testing.expectEqual(@as(?*rbtree.Node, &new_leftmost.node), rbtree.firstCached(&root));
    try std.testing.expectEqual(rbtree.first(&root.root), rbtree.firstCached(&root));
}

test "lane06 helper ports A replay keeps duplicate rbtree matches in insertion order" {
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
        .{ .key = 20, .serial = 3 },
        .{ .key = 10, .serial = 4 },
    };
    var root = rbtree.Root.init();
    for (&entries) |*entry| {
        rbtree.add(&entry.node, &root, less);
    }

    const wanted = @as(i32, 10);
    const first_match = rbtree.findFirst(&wanted, &root, cmp) orelse return error.TestUnexpectedResult;
    const first_entry: *const Entry = @fieldParentPtr("node", first_match);
    try std.testing.expectEqual(@as(usize, 0), first_entry.serial);

    var iterator = rbtree.matchIterator(&wanted, &root, cmp);
    var serials: [3]usize = undefined;
    var count: usize = 0;
    while (iterator.next()) |node| {
        const entry: *const Entry = @fieldParentPtr("node", node);
        serials[count] = entry.serial;
        count += 1;
    }

    try std.testing.expectEqual(@as(usize, 3), count);
    try std.testing.expectEqualSlices(usize, &[_]usize{ 0, 2, 4 }, serials[0..count]);
}
