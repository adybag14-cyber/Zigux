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

const Reservoir = enum { alpha, beta, gamma, delta };

fn entryFromNode(node: *const ListHead) *const Entry {
    return @fieldParentPtr("node", node);
}

fn compareByKey(priv: ?*anyopaque, a: *const ListHead, b: *const ListHead) i32 {
    const context: *const SortContext = @ptrCast(@alignCast(priv.?));
    const lhs = entryFromNode(a);
    const rhs = entryFromNode(b);

    if (lhs.key == rhs.key) return 0;
    const lhs_before_rhs = lhs.key < rhs.key;
    return if (context.mode == .ascending)
        (if (lhs_before_rhs) -9 else 11)
    else
        (if (lhs_before_rhs) 11 else -9);
}

fn compareAllTies(_: ?*anyopaque, _: *const ListHead, _: *const ListHead) i32 {
    return 0;
}

fn appendMixed(entries: []Entry, head: *ListHead) void {
    const front_insert = [_]bool{
        false,
        true,
        false,
        true,
        false,
        false,
        true,
        false,
        true,
        false,
        true,
        false,
        true,
        false,
    };
    for (&front_insert, 0..) |insert_front, index| {
        if (insert_front) {
            list_sort.listAdd(&entries[index].node, head);
        } else {
            list_sort.listAddTail(&entries[index].node, head);
        }
    }
}

fn pushReservoir(node: *ListHead, alpha: *ListHead, beta: *ListHead, gamma: *ListHead, delta: *ListHead, rank: usize) void {
    switch (rank % 4) {
        0 => list_sort.listAddTail(node, alpha),
        1 => list_sort.listAddTail(node, beta),
        2 => list_sort.listAddTail(node, gamma),
        else => list_sort.listAddTail(node, delta),
    }
}

fn drainIntoReservoirs(source: *ListHead, alpha: *ListHead, beta: *ListHead, gamma: *ListHead, delta: *ListHead) !void {
    var rank: usize = 0;
    while (!list_sort.listEmpty(source)) : (rank += 1) {
        const node = source.next.?;
        list_sort.listDel(node);
        try std.testing.expect(node.next == null);
        try std.testing.expect(node.prev == null);
        pushReservoir(node, alpha, beta, gamma, delta, rank);
    }
}

fn popFrontIntoTail(source: *ListHead, dest: *ListHead) !void {
    const node = source.next.?;
    list_sort.listDel(node);
    try std.testing.expect(node.next == null);
    try std.testing.expect(node.prev == null);
    list_sort.listAddTail(node, dest);
}

fn rebuildBraidedReservoir(dest: *ListHead, alpha: *ListHead, beta: *ListHead, gamma: *ListHead, delta: *ListHead) !void {
    const schedule = [_]Reservoir{
        .delta,
        .alpha,
        .beta,
        .gamma,
        .alpha,
        .delta,
        .beta,
        .gamma,
        .alpha,
        .beta,
        .delta,
        .gamma,
        .beta,
        .alpha,
    };
    for (&schedule) |reservoir| {
        switch (reservoir) {
            .alpha => try popFrontIntoTail(alpha, dest),
            .beta => try popFrontIntoTail(beta, dest),
            .gamma => try popFrontIntoTail(gamma, dest),
            .delta => try popFrontIntoTail(delta, dest),
        }
    }

    try std.testing.expect(list_sort.listEmpty(alpha));
    try std.testing.expect(list_sort.listEmpty(beta));
    try std.testing.expect(list_sort.listEmpty(gamma));
    try std.testing.expect(list_sort.listEmpty(delta));
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

test "list sort preserves stability through braided reservoir rebuild" {
    var head: ListHead = .{};
    var alpha: ListHead = .{};
    var beta: ListHead = .{};
    var gamma: ListHead = .{};
    var delta: ListHead = .{};
    head.init();
    alpha.init();
    beta.init();
    gamma.init();
    delta.init();

    var entries = [_]Entry{
        .{ .key = 5, .ordinal = 0 },
        .{ .key = 1, .ordinal = 1 },
        .{ .key = 8, .ordinal = 2 },
        .{ .key = 3, .ordinal = 3 },
        .{ .key = 1, .ordinal = 4 },
        .{ .key = 6, .ordinal = 5 },
        .{ .key = 4, .ordinal = 6 },
        .{ .key = 7, .ordinal = 7 },
        .{ .key = 2, .ordinal = 8 },
        .{ .key = 5, .ordinal = 9 },
        .{ .key = 0, .ordinal = 10 },
        .{ .key = 6, .ordinal = 11 },
        .{ .key = 3, .ordinal = 12 },
        .{ .key = 8, .ordinal = 13 },
    };

    appendMixed(&entries, &head);

    var ascending = SortContext{ .mode = .ascending };
    var descending = SortContext{ .mode = .descending };

    list_sort.listSort(&ascending, &head, compareByKey);
    try expectForward(&head, &.{ 10, 1, 4, 8, 12, 3, 6, 0, 9, 5, 11, 7, 2, 13 });

    try drainIntoReservoirs(&head, &alpha, &beta, &gamma, &delta);
    try std.testing.expect(list_sort.listEmpty(&head));
    try expectForward(&alpha, &.{ 10, 12, 9, 2 });
    try expectForward(&beta, &.{ 1, 3, 5, 13 });
    try expectForward(&gamma, &.{ 4, 6, 11 });
    try expectForward(&delta, &.{ 8, 0, 7 });

    list_sort.listSort(&descending, &alpha, compareByKey);
    list_sort.listSort(&ascending, &beta, compareByKey);
    list_sort.listSort(&descending, &gamma, compareByKey);
    list_sort.listSort(&ascending, &delta, compareByKey);
    try expectForward(&alpha, &.{ 2, 9, 12, 10 });
    try expectForward(&beta, &.{ 1, 3, 5, 13 });
    try expectForward(&gamma, &.{ 11, 6, 4 });
    try expectForward(&delta, &.{ 8, 0, 7 });

    try rebuildBraidedReservoir(&head, &alpha, &beta, &gamma, &delta);
    try expectForward(&head, &.{ 8, 2, 1, 11, 9, 0, 3, 6, 12, 5, 7, 4, 13, 10 });

    list_sort.listSort(&ascending, &head, compareByKey);
    try expectForward(&head, &.{ 10, 1, 4, 8, 3, 12, 6, 9, 0, 11, 5, 7, 2, 13 });
    try expectReverse(&head, &.{ 13, 2, 7, 5, 11, 0, 9, 6, 12, 3, 8, 4, 1, 10 });

    list_sort.listSort(null, &head, compareAllTies);
    try expectForward(&head, &.{ 10, 1, 4, 8, 3, 12, 6, 9, 0, 11, 5, 7, 2, 13 });
    try std.testing.expect(head.next == &entries[10].node);
    try std.testing.expect(head.prev == &entries[13].node);
}
