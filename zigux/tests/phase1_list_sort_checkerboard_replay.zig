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

fn parityBucketCmp(_: ?*anyopaque, a: *const list_sort.ListHead, b: *const list_sort.ListHead) i32 {
    const lhs = @mod(entryFromNode(a).key, 2);
    const rhs = @mod(entryFromNode(b).key, 2);
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
    var keys: [10]i32 = undefined;
    var ordinals: [10]usize = undefined;
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

test "phase1 list_sort replay checkerboard partitions a sorted traversal before stable parity pass" {
    var head: list_sort.ListHead = .{};
    var dark: list_sort.ListHead = .{};
    var light: list_sort.ListHead = .{};
    head.init();
    dark.init();
    light.init();

    var entries = [_]Entry{
        .{ .key = 14, .ordinal = 0 },
        .{ .key = 3, .ordinal = 1 },
        .{ .key = 10, .ordinal = 2 },
        .{ .key = 1, .ordinal = 3 },
        .{ .key = 8, .ordinal = 4 },
        .{ .key = 5, .ordinal = 5 },
        .{ .key = 12, .ordinal = 6 },
        .{ .key = 7, .ordinal = 7 },
        .{ .key = 2, .ordinal = 8 },
        .{ .key = 9, .ordinal = 9 },
    };

    for (&entries) |*entry| {
        list_sort.listAddTail(&entry.node, &head);
    }

    list_sort.listSort(null, &head, keyCmp);
    try expectOrdinals(&head, &.{ 3, 8, 1, 5, 7, 4, 9, 2, 6, 0 });
    try std.testing.expect(head.next == &entries[3].node);
    try std.testing.expect(head.prev == &entries[0].node);

    var sorted_index: usize = 0;
    while (!list_sort.listEmpty(&head)) : (sorted_index += 1) {
        if ((sorted_index & 1) == 0) {
            moveFrontToTail(&head, &dark);
        } else {
            moveFrontToTail(&head, &light);
        }
    }
    try std.testing.expect(list_sort.listEmpty(&head));
    try expectOrdinals(&dark, &.{ 3, 1, 7, 9, 6 });
    try expectOrdinals(&light, &.{ 8, 5, 4, 2, 0 });

    list_sort.listSort(null, &dark, reverseKeyCmp);
    list_sort.listSort(null, &light, reverseKeyCmp);
    try expectOrdinals(&dark, &.{ 6, 9, 7, 1, 3 });
    try expectOrdinals(&light, &.{ 0, 2, 4, 5, 8 });

    while (!list_sort.listEmpty(&dark) or !list_sort.listEmpty(&light)) {
        if (!list_sort.listEmpty(&dark)) {
            moveFrontToTail(&dark, &head);
        }
        if (!list_sort.listEmpty(&light)) {
            moveFrontToTail(&light, &head);
        }
    }
    try expectOrdinals(&head, &.{ 6, 0, 9, 2, 7, 4, 1, 5, 3, 8 });
    try std.testing.expect(head.next == &entries[6].node);
    try std.testing.expect(head.prev == &entries[8].node);

    list_sort.listSort(null, &head, parityBucketCmp);
    try expectOrdinals(&head, &.{ 6, 0, 2, 4, 8, 9, 7, 1, 5, 3 });
    try std.testing.expect(head.next == &entries[6].node);
    try std.testing.expect(head.prev == &entries[3].node);
}
