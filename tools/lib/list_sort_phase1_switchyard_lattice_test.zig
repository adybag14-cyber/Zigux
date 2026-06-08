const std = @import("std");
const list_sort = @import("list_sort");

const ListHead = list_sort.ListHead;

const Entry = struct {
    key: i32,
    lane: usize,
    ordinal: usize,
    node: ListHead = .{},
};

const SortMode = enum {
    ascending_key,
    descending_key,
};

fn cmpByMode(priv: ?*anyopaque, a: *const ListHead, b: *const ListHead) i32 {
    const mode: *const SortMode = @ptrCast(@alignCast(priv.?));
    const lhs: *const Entry = @fieldParentPtr("node", a);
    const rhs: *const Entry = @fieldParentPtr("node", b);

    if (lhs.key == rhs.key) return 0;
    const ascending = lhs.key < rhs.key;
    return switch (mode.*) {
        .ascending_key => if (ascending) -5 else 7,
        .descending_key => if (ascending) 7 else -5,
    };
}

fn cmpAllTies(_: ?*anyopaque, _: *const ListHead, _: *const ListHead) i32 {
    return 0;
}

fn collectOrdinals(head: *ListHead, out: []usize) usize {
    var idx: usize = 0;
    var current = head.next;
    while (current != head) : (current = current.?.next) {
        const entry: *const Entry = @fieldParentPtr("node", current.?);
        out[idx] = entry.ordinal;
        idx += 1;
    }
    return idx;
}

fn expectCircularLinks(head: *ListHead, expected_len: usize) !void {
    var count: usize = 0;
    var current = head.next;
    while (current != head) : (current = current.?.next) {
        try std.testing.expect(current.?.next.?.prev == current.?);
        try std.testing.expect(current.?.prev.?.next == current.?);
        count += 1;
    }
    try std.testing.expectEqual(expected_len, count);

    count = 0;
    current = head.prev;
    while (current != head) : (current = current.?.prev) {
        count += 1;
    }
    try std.testing.expectEqual(expected_len, count);
}

fn popFront(head: *ListHead) !*ListHead {
    try std.testing.expect(!list_sort.listEmpty(head));
    const node = head.next.?;
    list_sort.listDel(node);
    try std.testing.expect(node.next == null);
    try std.testing.expect(node.prev == null);
    return node;
}

fn popBack(head: *ListHead) !*ListHead {
    try std.testing.expect(!list_sort.listEmpty(head));
    const node = head.prev.?;
    list_sort.listDel(node);
    try std.testing.expect(node.next == null);
    try std.testing.expect(node.prev == null);
    return node;
}

fn expectOrdinals(head: *ListHead, expected: []const usize) !void {
    var actual: [16]usize = undefined;
    const len = collectOrdinals(head, &actual);
    try std.testing.expectEqualSlices(usize, expected, actual[0..len]);
    try expectCircularLinks(head, expected.len);
}

test "phase1 list_sort switchyard lattice preserves staged stable order" {
    var source: ListHead = .{};
    source.init();
    var switchyards = [_]ListHead{ .{}, .{}, .{}, .{} };
    for (&switchyards) |*head| head.init();

    var entries = [_]Entry{
        .{ .key = 8, .lane = 2, .ordinal = 0 },
        .{ .key = 3, .lane = 0, .ordinal = 1 },
        .{ .key = 5, .lane = 1, .ordinal = 2 },
        .{ .key = 3, .lane = 2, .ordinal = 3 },
        .{ .key = 7, .lane = 3, .ordinal = 4 },
        .{ .key = 1, .lane = 0, .ordinal = 5 },
        .{ .key = 5, .lane = 3, .ordinal = 6 },
        .{ .key = 2, .lane = 1, .ordinal = 7 },
        .{ .key = 6, .lane = 2, .ordinal = 8 },
        .{ .key = 1, .lane = 3, .ordinal = 9 },
        .{ .key = 4, .lane = 0, .ordinal = 10 },
        .{ .key = 2, .lane = 2, .ordinal = 11 },
    };

    for (&entries, 0..) |*entry, idx| {
        if ((idx & 1) == 0) {
            list_sort.listAdd(&entry.node, &source);
        } else {
            list_sort.listAddTail(&entry.node, &source);
        }
    }
    try expectCircularLinks(&source, entries.len);

    var ascending = SortMode.ascending_key;
    list_sort.listSort(&ascending, &source, cmpByMode);
    try expectOrdinals(&source, &.{ 5, 9, 7, 11, 1, 3, 10, 6, 2, 8, 4, 0 });

    var rank: usize = 0;
    while (!list_sort.listEmpty(&source)) : (rank += 1) {
        const node = try popFront(&source);
        const yard = &switchyards[rank % switchyards.len];
        if ((rank & 1) == 0) {
            list_sort.listAddTail(node, yard);
        } else {
            list_sort.listAdd(node, yard);
        }
    }
    try std.testing.expect(list_sort.listEmpty(&source));
    try expectOrdinals(&switchyards[0], &.{ 5, 1, 2 });
    try expectOrdinals(&switchyards[1], &.{ 8, 3, 9 });
    try expectOrdinals(&switchyards[2], &.{ 7, 10, 4 });
    try expectOrdinals(&switchyards[3], &.{ 0, 6, 11 });

    var descending = SortMode.descending_key;
    list_sort.listSort(&descending, &switchyards[0], cmpByMode);
    list_sort.listSort(&ascending, &switchyards[1], cmpByMode);
    list_sort.listSort(&descending, &switchyards[2], cmpByMode);
    list_sort.listSort(&ascending, &switchyards[3], cmpByMode);
    try expectOrdinals(&switchyards[0], &.{ 2, 1, 5 });
    try expectOrdinals(&switchyards[1], &.{ 9, 3, 8 });
    try expectOrdinals(&switchyards[2], &.{ 4, 10, 7 });
    try expectOrdinals(&switchyards[3], &.{ 11, 6, 0 });

    const moves = [_]struct {
        yard: usize,
        front: bool,
        tail_insert: bool,
    }{
        .{ .yard = 2, .front = true, .tail_insert = true },
        .{ .yard = 0, .front = false, .tail_insert = false },
        .{ .yard = 3, .front = true, .tail_insert = true },
        .{ .yard = 1, .front = false, .tail_insert = false },
        .{ .yard = 0, .front = true, .tail_insert = true },
        .{ .yard = 2, .front = false, .tail_insert = false },
        .{ .yard = 1, .front = true, .tail_insert = true },
        .{ .yard = 3, .front = false, .tail_insert = false },
        .{ .yard = 2, .front = true, .tail_insert = true },
        .{ .yard = 0, .front = true, .tail_insert = false },
        .{ .yard = 3, .front = true, .tail_insert = true },
        .{ .yard = 1, .front = true, .tail_insert = false },
    };

    for (moves) |move| {
        const node = if (move.front)
            try popFront(&switchyards[move.yard])
        else
            try popBack(&switchyards[move.yard]);

        if (move.tail_insert) {
            list_sort.listAddTail(node, &source);
        } else {
            list_sort.listAdd(node, &source);
        }
    }
    for (&switchyards) |*head| try std.testing.expect(list_sort.listEmpty(head));
    try expectOrdinals(&source, &.{ 3, 1, 0, 7, 8, 5, 4, 11, 2, 9, 10, 6 });

    list_sort.listSort(null, &source, cmpAllTies);
    try expectOrdinals(&source, &.{ 3, 1, 0, 7, 8, 5, 4, 11, 2, 9, 10, 6 });
    try std.testing.expect(source.next == &entries[3].node);
    try std.testing.expect(source.prev == &entries[6].node);
}
