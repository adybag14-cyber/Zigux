const std = @import("std");
const list_sort = @import("list_sort");

const ListHead = list_sort.ListHead;

const Entry = struct {
    key: i32,
    ordinal: usize,
    node: ListHead = .{},
};

const SortMode = enum {
    key_asc,
    key_desc,
    ordinal_asc,
    all_ties,
};

fn compare(priv: ?*anyopaque, a: *const ListHead, b: *const ListHead) i32 {
    const mode: *const SortMode = @ptrCast(@alignCast(priv.?));
    const lhs: *const Entry = @fieldParentPtr("node", a);
    const rhs: *const Entry = @fieldParentPtr("node", b);

    return switch (mode.*) {
        .key_asc => compareInt(lhs.key, rhs.key),
        .key_desc => compareInt(rhs.key, lhs.key),
        .ordinal_asc => compareInt(@as(i32, @intCast(lhs.ordinal)), @as(i32, @intCast(rhs.ordinal))),
        .all_ties => 0,
    };
}

fn compareInt(lhs: i32, rhs: i32) i32 {
    if (lhs < rhs) return -1;
    if (lhs > rhs) return 1;
    return 0;
}

fn popFront(head: *ListHead) ?*ListHead {
    if (list_sort.listEmpty(head)) return null;
    const node = head.next.?;
    list_sort.listDel(node);
    return node;
}

fn popBack(head: *ListHead) ?*ListHead {
    if (list_sort.listEmpty(head)) return null;
    const node = head.prev.?;
    list_sort.listDel(node);
    return node;
}

fn expectDetached(node: *const ListHead) !void {
    try std.testing.expect(node.next == null);
    try std.testing.expect(node.prev == null);
}

fn expectCircularOrdinals(head: *ListHead, expected: []const usize) !void {
    var seen: [16]usize = undefined;
    var count: usize = 0;
    var current = head.next;
    while (current != head) : (current = current.?.next) {
        const entry: *const Entry = @fieldParentPtr("node", current.?);
        seen[count] = entry.ordinal;
        try std.testing.expect(current.?.next.?.prev == current.?);
        try std.testing.expect(current.?.prev.?.next == current.?);
        count += 1;
    }

    try std.testing.expectEqualSlices(usize, expected, seen[0..count]);

    var reverse_seen: [16]usize = undefined;
    var reverse_count: usize = 0;
    current = head.prev;
    while (current != head) : (current = current.?.prev) {
        const entry: *const Entry = @fieldParentPtr("node", current.?);
        reverse_seen[reverse_count] = entry.ordinal;
        reverse_count += 1;
    }

    try std.testing.expectEqual(count, reverse_count);
    for (0..count) |idx| {
        try std.testing.expectEqual(expected[count - 1 - idx], reverse_seen[idx]);
    }
}

test "list sort preserves braided gate detach and tie stability replay" {
    var head: ListHead = .{};
    var north: ListHead = .{};
    var east: ListHead = .{};
    var south: ListHead = .{};
    var west: ListHead = .{};
    head.init();
    north.init();
    east.init();
    south.init();
    west.init();

    var entries = [_]Entry{
        .{ .key = 5, .ordinal = 0 },
        .{ .key = 2, .ordinal = 1 },
        .{ .key = 7, .ordinal = 2 },
        .{ .key = 2, .ordinal = 3 },
        .{ .key = 9, .ordinal = 4 },
        .{ .key = 1, .ordinal = 5 },
        .{ .key = 6, .ordinal = 6 },
        .{ .key = 4, .ordinal = 7 },
        .{ .key = 7, .ordinal = 8 },
        .{ .key = 3, .ordinal = 9 },
        .{ .key = 5, .ordinal = 10 },
        .{ .key = 0, .ordinal = 11 },
    };

    for (&entries) |*entry| {
        if ((entry.ordinal & 1) == 0) {
            list_sort.listAddTail(&entry.node, &head);
        } else {
            list_sort.listAdd(&entry.node, &head);
        }
    }
    try expectCircularOrdinals(&head, &.{ 11, 9, 7, 5, 3, 1, 0, 2, 4, 6, 8, 10 });

    var mode = SortMode.key_asc;
    list_sort.listSort(&mode, &head, compare);
    try expectCircularOrdinals(&head, &.{ 11, 5, 3, 1, 9, 7, 0, 10, 6, 2, 8, 4 });

    var rank: usize = 0;
    var current = head.next;
    while (current != &head) {
        const node = current.?;
        current = node.next;
        list_sort.listDel(node);
        try expectDetached(node);

        switch (rank % 4) {
            0 => list_sort.listAddTail(node, &north),
            1 => list_sort.listAdd(node, &east),
            2 => list_sort.listAddTail(node, &south),
            else => list_sort.listAdd(node, &west),
        }
        rank += 1;
    }

    try std.testing.expect(list_sort.listEmpty(&head));
    try expectCircularOrdinals(&north, &.{ 11, 9, 6 });
    try expectCircularOrdinals(&east, &.{ 2, 7, 5 });
    try expectCircularOrdinals(&south, &.{ 3, 0, 8 });
    try expectCircularOrdinals(&west, &.{ 4, 10, 1 });

    mode = .key_desc;
    list_sort.listSort(&mode, &north, compare);
    mode = .ordinal_asc;
    list_sort.listSort(&mode, &east, compare);
    mode = .key_asc;
    list_sort.listSort(&mode, &south, compare);
    mode = .key_desc;
    list_sort.listSort(&mode, &west, compare);

    try expectCircularOrdinals(&north, &.{ 6, 9, 11 });
    try expectCircularOrdinals(&east, &.{ 2, 5, 7 });
    try expectCircularOrdinals(&south, &.{ 3, 0, 8 });
    try expectCircularOrdinals(&west, &.{ 4, 10, 1 });

    while (!list_sort.listEmpty(&north) or !list_sort.listEmpty(&east) or !list_sort.listEmpty(&south) or !list_sort.listEmpty(&west)) {
        if (popFront(&north)) |node| {
            try expectDetached(node);
            list_sort.listAddTail(node, &head);
        }
        if (popBack(&east)) |node| {
            try expectDetached(node);
            list_sort.listAddTail(node, &head);
        }
        if (popFront(&south)) |node| {
            try expectDetached(node);
            list_sort.listAddTail(node, &head);
        }
        if (popBack(&west)) |node| {
            try expectDetached(node);
            list_sort.listAddTail(node, &head);
        }
    }

    try std.testing.expect(list_sort.listEmpty(&north));
    try std.testing.expect(list_sort.listEmpty(&east));
    try std.testing.expect(list_sort.listEmpty(&south));
    try std.testing.expect(list_sort.listEmpty(&west));
    try expectCircularOrdinals(&head, &.{ 6, 7, 3, 1, 9, 5, 0, 10, 11, 2, 8, 4 });

    mode = .all_ties;
    list_sort.listSort(&mode, &head, compare);
    try expectCircularOrdinals(&head, &.{ 6, 7, 3, 1, 9, 5, 0, 10, 11, 2, 8, 4 });
    try std.testing.expect(head.next == &entries[6].node);
    try std.testing.expect(head.prev == &entries[4].node);
}
