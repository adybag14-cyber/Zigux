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

const Horizon = enum { lower, middle, upper };

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
        (if (ascending) -5 else 7)
    else
        (if (ascending) 7 else -5);
}

fn compareAllTies(_: ?*anyopaque, _: *const ListHead, _: *const ListHead) i32 {
    return 0;
}

fn appendMixed(entries: []Entry, head: *ListHead) void {
    const front_insert = [_]bool{ false, true, false, true, false, false, true, false, true, false, true, false };
    for (&front_insert, 0..) |insert_front, index| {
        if (insert_front) {
            list_sort.listAdd(&entries[index].node, head);
        } else {
            list_sort.listAddTail(&entries[index].node, head);
        }
    }
}

fn drainIntoHorizons(source: *ListHead, lower: *ListHead, middle: *ListHead, upper: *ListHead) !void {
    var rank: usize = 0;
    while (!list_sort.listEmpty(source)) : (rank += 1) {
        const node = source.next.?;
        list_sort.listDel(node);
        try std.testing.expect(node.next == null);
        try std.testing.expect(node.prev == null);

        switch (rank % 3) {
            0 => list_sort.listAddTail(node, lower),
            1 => list_sort.listAddTail(node, middle),
            else => list_sort.listAddTail(node, upper),
        }
    }
}

fn popFrontIntoTail(source: *ListHead, dest: *ListHead) !void {
    const node = source.next.?;
    list_sort.listDel(node);
    try std.testing.expect(node.next == null);
    try std.testing.expect(node.prev == null);
    list_sort.listAddTail(node, dest);
}

fn rebuildSplitHorizon(dest: *ListHead, lower: *ListHead, middle: *ListHead, upper: *ListHead) !void {
    const schedule = [_]Horizon{ .upper, .lower, .middle, .lower, .upper, .middle, .middle, .lower, .upper, .upper, .middle, .lower };
    for (&schedule) |horizon| {
        switch (horizon) {
            .lower => try popFrontIntoTail(lower, dest),
            .middle => try popFrontIntoTail(middle, dest),
            .upper => try popFrontIntoTail(upper, dest),
        }
    }

    try std.testing.expect(list_sort.listEmpty(lower));
    try std.testing.expect(list_sort.listEmpty(middle));
    try std.testing.expect(list_sort.listEmpty(upper));
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

test "list sort preserves stability through split horizon rebuild" {
    var head: ListHead = .{};
    var lower: ListHead = .{};
    var middle: ListHead = .{};
    var upper: ListHead = .{};
    head.init();
    lower.init();
    middle.init();
    upper.init();

    var entries = [_]Entry{
        .{ .key = 6, .ordinal = 0 },
        .{ .key = 2, .ordinal = 1 },
        .{ .key = 4, .ordinal = 2 },
        .{ .key = 1, .ordinal = 3 },
        .{ .key = 5, .ordinal = 4 },
        .{ .key = 2, .ordinal = 5 },
        .{ .key = 7, .ordinal = 6 },
        .{ .key = 0, .ordinal = 7 },
        .{ .key = 4, .ordinal = 8 },
        .{ .key = 6, .ordinal = 9 },
        .{ .key = 1, .ordinal = 10 },
        .{ .key = 3, .ordinal = 11 },
    };

    appendMixed(&entries, &head);

    var ascending = SortContext{ .mode = .ascending };
    list_sort.listSort(&ascending, &head, compareByKey);
    try expectForward(&head, &.{ 7, 10, 3, 1, 5, 11, 8, 2, 4, 0, 9, 6 });

    try drainIntoHorizons(&head, &lower, &middle, &upper);
    try std.testing.expect(list_sort.listEmpty(&head));
    try expectForward(&lower, &.{ 7, 1, 8, 0 });
    try expectForward(&middle, &.{ 10, 5, 2, 9 });
    try expectForward(&upper, &.{ 3, 11, 4, 6 });

    var descending = SortContext{ .mode = .descending };
    list_sort.listSort(&descending, &lower, compareByKey);
    list_sort.listSort(&ascending, &middle, compareByKey);
    list_sort.listSort(&descending, &upper, compareByKey);
    try expectForward(&lower, &.{ 0, 8, 1, 7 });
    try expectForward(&middle, &.{ 10, 5, 2, 9 });
    try expectForward(&upper, &.{ 6, 4, 11, 3 });

    try rebuildSplitHorizon(&head, &lower, &middle, &upper);
    try expectForward(&head, &.{ 6, 0, 10, 8, 4, 5, 2, 1, 11, 3, 9, 7 });

    list_sort.listSort(&ascending, &head, compareByKey);
    try expectForward(&head, &.{ 7, 10, 3, 5, 1, 11, 8, 2, 4, 0, 9, 6 });
    try expectReverse(&head, &.{ 6, 9, 0, 4, 2, 8, 11, 1, 5, 3, 10, 7 });

    list_sort.listSort(null, &head, compareAllTies);
    try expectForward(&head, &.{ 7, 10, 3, 5, 1, 11, 8, 2, 4, 0, 9, 6 });
    try std.testing.expect(head.next == &entries[7].node);
    try std.testing.expect(head.prev == &entries[6].node);
}
