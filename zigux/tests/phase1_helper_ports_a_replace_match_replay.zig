const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const rbtree = @import("rbtree");
const string = @import("string");

test "phase1 helper ports A replace match replay keeps masked helpers aligned" {
    const Word = find_bit.Word;

    var old = [_]Word{ 0b0000_1111, 0 };
    var new = [_]Word{ 0b1111_0000, 0b1111 };
    var mask = [_]Word{ 0b1100_1100, 0b1111 };
    var replaced = [_]Word{ 0, 0 };

    bitmap.replace(&replaced, &old, &new, &mask, 68);
    try std.testing.expectEqual(@as(Word, 0b1100_0011), replaced[0]);
    try std.testing.expectEqual(@as(Word, 0b1111), replaced[1]);
    try std.testing.expectEqual(@as(usize, 8), bitmap.weight(&replaced, 68));
    try std.testing.expectEqual(@as(usize, 0), find_bit.findFirstBit(&replaced, 68));
    try std.testing.expectEqual(@as(usize, 6), find_bit.findNextBit(&replaced, 68, 2));
    try std.testing.expectEqual(@as(usize, 2), find_bit.findNextZeroBit(&replaced, 68, 0));
    try std.testing.expectEqual(@as(usize, 67), find_bit.findLastBit(&replaced, 68));

    var padded = [_]u8{ 0xaa, 0xaa, 0xaa, 0xaa, 0xaa };
    try std.testing.expectEqual(@as(isize, 2), string.strscpyPad(&padded, "xy"));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'x', 'y', 0, 0, 0 }, &padded);

    var trim_buf = [_]u8{ ' ', '\t', 'm', 'a', 't', 'c', 'h', ' ', '\n' };
    try std.testing.expectEqualSlices(u8, "match", string.trimSpaces(&trim_buf));
    try std.testing.expectEqual(@as(?usize, 2), string.memchrInv(&[_]u8{ 0xaa, 0xaa, 0xab }, 0xaa));

    const parsed = string.memparse("16Ktail");
    try std.testing.expectEqual(@as(u64, 16 * 1024), parsed.value);
    try std.testing.expectEqualSlices(u8, "tail", parsed.rest);
}

test "phase1 helper ports A rbtree duplicate match survives erase init" {
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

    const keyCmp = struct {
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
    };
    var root = rbtree.Root.init();
    for (&entries) |*entry| {
        rbtree.add(&entry.node, &root, less);
    }

    const duplicate = @as(i32, 10);
    const first_match = rbtree.findFirst(&duplicate, &root, keyCmp) orelse return error.TestUnexpectedResult;
    const first_entry: *const Entry = @fieldParentPtr("node", first_match);
    try std.testing.expectEqual(@as(usize, 0), first_entry.serial);

    const second_match = rbtree.nextMatch(&duplicate, first_match, keyCmp) orelse return error.TestUnexpectedResult;
    const second_entry: *const Entry = @fieldParentPtr("node", second_match);
    try std.testing.expectEqual(@as(usize, 2), second_entry.serial);
    try std.testing.expect(rbtree.nextMatch(&duplicate, second_match, keyCmp) == null);

    rbtree.eraseInit(first_match, &root);
    try std.testing.expect(rbtree.emptyNode(first_match));

    const surviving_match = rbtree.findFirst(&duplicate, &root, keyCmp) orelse return error.TestUnexpectedResult;
    const surviving_entry: *const Entry = @fieldParentPtr("node", surviving_match);
    try std.testing.expectEqual(@as(usize, 2), surviving_entry.serial);

    var order: [3]i32 = undefined;
    var count: usize = 0;
    var current = rbtree.first(&root);
    while (current) |node| : (current = rbtree.next(node)) {
        const entry: *const Entry = @fieldParentPtr("node", node);
        order[count] = entry.key;
        count += 1;
    }

    try std.testing.expectEqual(@as(usize, 3), count);
    try std.testing.expectEqualSlices(i32, &[_]i32{ 5, 10, 15 }, order[0..count]);
}
