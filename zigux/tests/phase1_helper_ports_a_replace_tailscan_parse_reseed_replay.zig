const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

test "phase1 helper ports a replace helpers clamp masked tail bits" {
    const nbits = bitmap.bits_per_long + 5;
    const old = [_]bitmap.Word{
        0b0011,
        (@as(bitmap.Word, 1) << 0) | (@as(bitmap.Word, 1) << 6),
    };
    const new = [_]bitmap.Word{
        0b1001,
        (@as(bitmap.Word, 1) << 2) | (@as(bitmap.Word, 1) << 7),
    };
    const mask = [_]bitmap.Word{
        0b1010,
        (@as(bitmap.Word, 1) << 2) | (@as(bitmap.Word, 1) << 6),
    };

    var replaced = [_]bitmap.Word{ 0, 0 };
    bitmap.bitmap_replace(&replaced, &old, &new, &mask, nbits);

    try std.testing.expectEqual(@as(bitmap.Word, 0b1001), replaced[0]);
    try std.testing.expectEqual(@as(bitmap.Word, 0b00101), replaced[1]);
    try std.testing.expect(bitmap.bitmap_subset(&replaced, &[_]bitmap.Word{ 0b1101, 0b11111 }, nbits));
    try std.testing.expect(bitmap.bitmap_intersects(&replaced, &[_]bitmap.Word{ 0b1000, 0 }, nbits));
}

test "phase1 helper ports a shared and andnot tail scans ignore out-of-range bits" {
    const nbits = find_bit.bits_per_long + 5;

    const shared_lhs = [_]find_bit.Word{
        @as(find_bit.Word, 1) << @intCast(find_bit.bits_per_long - 1),
        (@as(find_bit.Word, 1) << 1) | (@as(find_bit.Word, 1) << 4),
    };
    const shared_rhs = [_]find_bit.Word{
        @as(find_bit.Word, 1) << @intCast(find_bit.bits_per_long - 1),
        (@as(find_bit.Word, 1) << 4) | (@as(find_bit.Word, 1) << 7),
    };

    try std.testing.expectEqual(
        @as(usize, find_bit.bits_per_long - 1),
        find_bit.findNextAndBit(&shared_lhs, &shared_rhs, nbits, find_bit.bits_per_long - 1),
    );
    try std.testing.expectEqual(
        @as(usize, find_bit.bits_per_long + 4),
        find_bit.findNextAndBit(&shared_lhs, &shared_rhs, nbits, find_bit.bits_per_long),
    );

    const andnot_lhs = [_]find_bit.Word{ 0, (@as(find_bit.Word, 1) << 1) | (@as(find_bit.Word, 1) << 4) };
    const andnot_rhs = [_]find_bit.Word{ 0, (@as(find_bit.Word, 1) << 1) | (@as(find_bit.Word, 1) << 7) };

    try std.testing.expectEqual(
        @as(usize, find_bit.bits_per_long + 4),
        find_bit.findFirstAndNotBit(&andnot_lhs, &andnot_rhs, nbits),
    );
    try std.testing.expectEqual(
        @as(usize, find_bit.bits_per_long + 4),
        find_bit.findNextAndNotBit(&andnot_lhs, &andnot_rhs, nbits, find_bit.bits_per_long + 1),
    );
    try std.testing.expectEqual(
        @as(usize, nbits),
        find_bit.findNextAndNotBit(&andnot_lhs, &andnot_rhs, nbits, find_bit.bits_per_long + 5),
    );
}

test "phase1 helper ports a string parse and match helpers keep c-string boundaries" {
    try std.testing.expect(try string.strtobool("on"));
    try std.testing.expect(!(try string.strtobool("off")));

    const parsed = string.memparse("+0x10Krest");
    try std.testing.expectEqual(@as(u64, 16 * 1024), parsed.value);
    try std.testing.expectEqualStrings("rest", parsed.rest);

    const sysfs_choices = [_][]const u8{ "alpha\n", "beta", "gamma\n" };
    try std.testing.expectEqual(@as(?usize, 0), string.sysfsMatchString(&sysfs_choices, "alpha"));
    try std.testing.expectEqual(@as(?usize, 2), string.sysfsMatchString(&sysfs_choices, "gamma\n"));

    const exact_choices = [_][]const u8{ "alpha", "beta\x00ignored", "gamma" };
    try std.testing.expectEqual(@as(?usize, 1), string.matchString(&exact_choices, "beta"));
}

test "phase1 helper ports a cached leftmost reseeds after duplicate rejection and eraseCached" {
    const Entry = struct {
        key: i32,
        node: rbtree.Node = rbtree.Node.init(),
    };

    const orderToI32 = struct {
        fn convert(order: std.math.Order) i32 {
            return switch (order) {
                .lt => -1,
                .eq => 0,
                .gt => 1,
            };
        }
    }.convert;

    const cmpNode = struct {
        fn compare(lhs: *const rbtree.Node, rhs: *const rbtree.Node) i32 {
            const lhs_entry: *const Entry = @fieldParentPtr("node", lhs);
            const rhs_entry: *const Entry = @fieldParentPtr("node", rhs);
            return orderToI32(std.math.order(lhs_entry.key, rhs_entry.key));
        }
    }.compare;

    const cmpKey = struct {
        fn compare(key: *const anyopaque, node: *const rbtree.Node) i32 {
            const key_ptr: *const i32 = @ptrCast(@alignCast(key));
            const entry: *const Entry = @fieldParentPtr("node", node);
            return orderToI32(std.math.order(key_ptr.*, entry.key));
        }
    }.compare;

    const less = struct {
        fn compare(lhs: *const rbtree.Node, rhs: *const rbtree.Node) bool {
            return cmpNode(lhs, rhs) < 0;
        }
    }.compare;

    var root = rbtree.RootCached.init();
    const root_view = &root.root;

    var entry8 = Entry{ .key = 8 };
    var entry4 = Entry{ .key = 4 };
    var entry12 = Entry{ .key = 12 };
    var entry6 = Entry{ .key = 6 };
    var duplicate6 = Entry{ .key = 6 };

    _ = rbtree.addCached(&entry8.node, &root, less);
    _ = rbtree.addCached(&entry4.node, &root, less);
    _ = rbtree.addCached(&entry12.node, &root, less);
    _ = rbtree.addCached(&entry6.node, &root, less);

    try std.testing.expectEqual(@as(?*rbtree.Node, &entry4.node), rbtree.firstCached(&root));
    try std.testing.expectEqual(@as(?*rbtree.Node, &entry6.node), rbtree.findAddCached(&duplicate6.node, &root, cmpNode));
    try std.testing.expectEqual(@as(?*rbtree.Node, &entry4.node), rbtree.firstCached(&root));

    const key6: i32 = 6;
    var iterator = rbtree.matchIterator(&key6, root_view, cmpKey);
    try std.testing.expectEqual(@as(?*rbtree.Node, &entry6.node), iterator.next());
    try std.testing.expect(iterator.next() == null);

    const promoted = rbtree.eraseCached(&entry4.node, &root) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(*rbtree.Node, &entry6.node), promoted);
    try std.testing.expectEqual(@as(?*rbtree.Node, &entry6.node), rbtree.firstCached(&root));
    try std.testing.expectEqual(rbtree.first(root_view), rbtree.firstCached(&root));
}
