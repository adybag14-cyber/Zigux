const std = @import("std");
const list_sort = @import("list_sort");

const ListHead = list_sort.ListHead;

const Entry = struct {
    key: i32,
    ordinal: usize,
    node: ListHead = .{},
};

const SortMode = enum { ascending, descending };

const SortContext = struct {
    mode: SortMode,
};

fn entryFromNode(node: *const ListHead) *const Entry {
    return @fieldParentPtr("node", node);
}

fn compareByKey(priv: ?*anyopaque, a: *const ListHead, b: *const ListHead) i32 {
    const context: *const SortContext = @ptrCast(@alignCast(priv.?));
    const lhs = entryFromNode(a);
    const rhs = entryFromNode(b);

    if (lhs.key == rhs.key) return 0;
    const ascending = lhs.key < rhs.key;
    return if (context.mode == .ascending)
        (if (ascending) -1 else 1)
    else
        (if (ascending) 1 else -1);
}

fn compareAllTies(_: ?*anyopaque, _: *const ListHead, _: *const ListHead) i32 {
    return 0;
}

fn appendMixed(entries: []Entry, head: *ListHead) void {
    const front_insert = [_]bool{ false, true, false, true, false, false, true, false, true, false };
    for (&front_insert, 0..) |insert_front, index| {
        if (insert_front) {
            list_sort.listAdd(&entries[index].node, head);
        } else {
            list_sort.listAddTail(&entries[index].node, head);
        }
    }
}

fn detachFrontIntoQueue(source: *ListHead, queue: *ListHead, count: usize) !void {
    for (0..count) |_| {
        const node = source.next.?;
        list_sort.listDel(node);
        try std.testing.expect(node.next == null);
        try std.testing.expect(node.prev == null);
        list_sort.listAddTail(node, queue);
    }
}

fn appendQueueToTail(source: *ListHead, queue: *ListHead) !void {
    while (!list_sort.listEmpty(queue)) {
        const node = queue.next.?;
        list_sort.listDel(node);
        try std.testing.expect(node.next == null);
        try std.testing.expect(node.prev == null);
        list_sort.listAddTail(node, source);
    }
}

fn expectForward(head: *const ListHead, expected: []const usize) !void {
    var index: usize = 0;
    var current = head.next;
    while (current != head) : (current = current.?.next) {
        const node = current.?;
        const entry = entryFromNode(node);
        try std.testing.expect(index < expected.len);
        try std.testing.expectEqual(expected[index], entry.ordinal);
        try std.testing.expect(node.next.?.prev == node);
        try std.testing.expect(node.prev.?.next == node);
        index += 1;
    }
    try std.testing.expectEqual(expected.len, index);
}

fn expectReverse(head: *const ListHead, expected: []const usize) !void {
    var index: usize = 0;
    var current = head.prev;
    while (current != head) : (current = current.?.prev) {
        const node = current.?;
        const entry = entryFromNode(node);
        try std.testing.expect(index < expected.len);
        try std.testing.expectEqual(expected[index], entry.ordinal);
        index += 1;
    }
    try std.testing.expectEqual(expected.len, index);
}

test "list sort preserves stability through detour queue rebuild" {
    var head: ListHead = .{};
    var detour: ListHead = .{};
    head.init();
    detour.init();

    var entries = [_]Entry{
        .{ .key = 4, .ordinal = 0 },
        .{ .key = 1, .ordinal = 1 },
        .{ .key = 3, .ordinal = 2 },
        .{ .key = 1, .ordinal = 3 },
        .{ .key = 5, .ordinal = 4 },
        .{ .key = 2, .ordinal = 5 },
        .{ .key = 4, .ordinal = 6 },
        .{ .key = 0, .ordinal = 7 },
        .{ .key = 2, .ordinal = 8 },
        .{ .key = 3, .ordinal = 9 },
    };

    appendMixed(&entries, &head);

    var ascending = SortContext{ .mode = .ascending };
    list_sort.listSort(&ascending, &head, compareByKey);
    try expectForward(&head, &.{ 7, 3, 1, 8, 5, 2, 9, 6, 0, 4 });

    try detachFrontIntoQueue(&head, &detour, 4);
    try expectForward(&detour, &.{ 7, 3, 1, 8 });
    try expectForward(&head, &.{ 5, 2, 9, 6, 0, 4 });

    var descending = SortContext{ .mode = .descending };
    list_sort.listSort(&descending, &detour, compareByKey);
    try expectForward(&detour, &.{ 8, 3, 1, 7 });

    try appendQueueToTail(&head, &detour);
    try std.testing.expect(list_sort.listEmpty(&detour));
    try expectForward(&head, &.{ 5, 2, 9, 6, 0, 4, 8, 3, 1, 7 });

    list_sort.listSort(&ascending, &head, compareByKey);
    try expectForward(&head, &.{ 7, 3, 1, 5, 8, 2, 9, 6, 0, 4 });
    try expectReverse(&head, &.{ 4, 0, 6, 9, 2, 8, 5, 1, 3, 7 });

    list_sort.listSort(null, &head, compareAllTies);
    try expectForward(&head, &.{ 7, 3, 1, 5, 8, 2, 9, 6, 0, 4 });
    try std.testing.expect(head.next == &entries[7].node);
    try std.testing.expect(head.prev == &entries[4].node);
}
