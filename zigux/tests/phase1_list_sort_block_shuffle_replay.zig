const std = @import("std");
const list_sort = @import("list_sort");

const Entry = struct {
    key: i32,
    ordinal: usize,
    node: list_sort.ListHead = .{},
};

fn entryFromNode(node: *const list_sort.ListHead) *const Entry {
    return @fieldParentPtr("node", node);
}

fn keyCmp(_: ?*anyopaque, a: *const list_sort.ListHead, b: *const list_sort.ListHead) i32 {
    const lhs = entryFromNode(a);
    const rhs = entryFromNode(b);
    if (lhs.key < rhs.key) return -1;
    if (lhs.key > rhs.key) return 1;
    return 0;
}

fn reverseKeyCmp(_: ?*anyopaque, a: *const list_sort.ListHead, b: *const list_sort.ListHead) i32 {
    const lhs = entryFromNode(a);
    const rhs = entryFromNode(b);
    if (lhs.key > rhs.key) return -1;
    if (lhs.key < rhs.key) return 1;
    return 0;
}

fn moduloBucketCmp(_: ?*anyopaque, a: *const list_sort.ListHead, b: *const list_sort.ListHead) i32 {
    const lhs = @mod(entryFromNode(a).key, 3);
    const rhs = @mod(entryFromNode(b).key, 3);
    if (lhs < rhs) return -1;
    if (lhs > rhs) return 1;
    return 0;
}

fn collect(head: *const list_sort.ListHead, keys: []i32, ordinals: []usize) !usize {
    var idx: usize = 0;
    var current = head.next;
    while (current != head) : (current = current.?.next) {
        const entry = entryFromNode(current.?);
        keys[idx] = entry.key;
        ordinals[idx] = entry.ordinal;
        try std.testing.expect(current.?.next.?.prev == current.?);
        try std.testing.expect(current.?.prev.?.next == current.?);
        idx += 1;
    }
    return idx;
}

fn expectOrdinals(head: *const list_sort.ListHead, expected: []const usize) !void {
    var keys: [12]i32 = undefined;
    var ordinals: [12]usize = undefined;
    const count = try collect(head, &keys, &ordinals);
    try std.testing.expectEqual(expected.len, count);
    try std.testing.expectEqualSlices(usize, expected, ordinals[0..count]);
}

fn moveFrontToTail(from: *list_sort.ListHead, to: *list_sort.ListHead) void {
    const node = from.next.?;
    list_sort.listDel(node);
    std.debug.assert(node.next == null);
    std.debug.assert(node.prev == null);
    list_sort.listAddTail(node, to);
}

test "phase1 list_sort replay block-shuffles sorted runs before stable bucket pass" {
    var head: list_sort.ListHead = .{};
    head.init();
    var blocks = [_]list_sort.ListHead{ .{}, .{}, .{}, .{} };
    for (&blocks) |*block| block.init();

    var entries = [_]Entry{
        .{ .key = 7, .ordinal = 0 },
        .{ .key = 2, .ordinal = 1 },
        .{ .key = 10, .ordinal = 2 },
        .{ .key = 0, .ordinal = 3 },
        .{ .key = 5, .ordinal = 4 },
        .{ .key = 9, .ordinal = 5 },
        .{ .key = 1, .ordinal = 6 },
        .{ .key = 11, .ordinal = 7 },
        .{ .key = 4, .ordinal = 8 },
        .{ .key = 6, .ordinal = 9 },
        .{ .key = 3, .ordinal = 10 },
        .{ .key = 8, .ordinal = 11 },
    };

    for (&entries) |*entry| {
        list_sort.listAddTail(&entry.node, &head);
    }

    list_sort.listSort(null, &head, keyCmp);
    try expectOrdinals(&head, &.{ 3, 6, 1, 10, 8, 4, 9, 0, 11, 5, 2, 7 });
    try std.testing.expect(head.next == &entries[3].node);
    try std.testing.expect(head.prev == &entries[7].node);

    for (&blocks) |*block| {
        var moved: usize = 0;
        while (moved < 3) : (moved += 1) {
            moveFrontToTail(&head, block);
        }
        list_sort.listSort(null, block, reverseKeyCmp);
    }
    try std.testing.expect(list_sort.listEmpty(&head));
    try expectOrdinals(&blocks[0], &.{ 1, 6, 3 });
    try expectOrdinals(&blocks[1], &.{ 4, 8, 10 });
    try expectOrdinals(&blocks[2], &.{ 11, 0, 9 });
    try expectOrdinals(&blocks[3], &.{ 7, 2, 5 });

    const block_order = [_]usize{ 2, 0, 3, 1 };
    for (block_order) |block_index| {
        while (!list_sort.listEmpty(&blocks[block_index])) {
            moveFrontToTail(&blocks[block_index], &head);
        }
    }
    try expectOrdinals(&head, &.{ 11, 0, 9, 1, 6, 3, 7, 2, 5, 4, 8, 10 });
    try std.testing.expect(head.next == &entries[11].node);
    try std.testing.expect(head.prev == &entries[10].node);

    list_sort.listSort(null, &head, moduloBucketCmp);
    try expectOrdinals(&head, &.{ 9, 3, 5, 10, 0, 6, 2, 8, 11, 1, 7, 4 });
    try std.testing.expect(head.next == &entries[9].node);
    try std.testing.expect(head.prev == &entries[4].node);
    try std.testing.expect(entries[9].node.prev == &head);
    try std.testing.expect(entries[4].node.next == &head);
}
