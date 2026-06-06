const std = @import("std");
const list_sort = @import("list_sort");

const ListHead = list_sort.ListHead;

const Entry = struct {
    key: i32,
    ordinal: usize,
    node: ListHead = .{},
};

const SortMode = enum { ascending, descending };

fn keyCmp(priv: ?*anyopaque, a: *const ListHead, b: *const ListHead) i32 {
    const mode: *const SortMode = @ptrCast(@alignCast(priv.?));
    const lhs: *const Entry = @fieldParentPtr("node", a);
    const rhs: *const Entry = @fieldParentPtr("node", b);
    if (lhs.key == rhs.key) return 0;
    const ascending = lhs.key < rhs.key;
    return if (mode.* == .ascending)
        (if (ascending) -1 else 1)
    else
        (if (ascending) 1 else -1);
}

fn allTiesCmp(_: ?*anyopaque, _: *const ListHead, _: *const ListHead) i32 {
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

fn expectOrdinals(head: *const ListHead, expected: []const usize) !void {
    var seen: [16]usize = undefined;
    var idx: usize = 0;
    var current = head.next;
    while (current != head) : (current = current.?.next) {
        const entry: *const Entry = @fieldParentPtr("node", current.?);
        seen[idx] = entry.ordinal;
        try std.testing.expect(current.?.next.?.prev == current.?);
        try std.testing.expect(current.?.prev.?.next == current.?);
        idx += 1;
    }

    try std.testing.expectEqualSlices(usize, expected, seen[0..idx]);
}

test "list sort survives diagonal staged weave replay" {
    var head: ListHead = .{};
    var north: ListHead = .{};
    var center: ListHead = .{};
    var south: ListHead = .{};
    head.init();
    north.init();
    center.init();
    south.init();

    var entries = [_]Entry{
        .{ .key = 9, .ordinal = 0 },
        .{ .key = 1, .ordinal = 1 },
        .{ .key = 6, .ordinal = 2 },
        .{ .key = 4, .ordinal = 3 },
        .{ .key = 8, .ordinal = 4 },
        .{ .key = 3, .ordinal = 5 },
        .{ .key = 7, .ordinal = 6 },
        .{ .key = 2, .ordinal = 7 },
        .{ .key = 5, .ordinal = 8 },
        .{ .key = 0, .ordinal = 9 },
    };

    for (&entries) |*entry| list_sort.listAddTail(&entry.node, &head);

    var mode = SortMode.ascending;
    list_sort.listSort(&mode, &head, keyCmp);
    try expectOrdinals(&head, &.{ 9, 1, 7, 5, 3, 8, 2, 6, 4, 0 });

    var sorted_rank: usize = 0;
    while (popFront(&head)) |node| : (sorted_rank += 1) {
        try expectDetached(node);
        switch (sorted_rank % 3) {
            0 => list_sort.listAddTail(node, &center),
            1 => list_sort.listAdd(node, &north),
            else => list_sort.listAddTail(node, &south),
        }
    }

    try std.testing.expect(list_sort.listEmpty(&head));
    try expectOrdinals(&north, &.{ 6, 3, 1 });
    try expectOrdinals(&center, &.{ 9, 5, 2, 0 });
    try expectOrdinals(&south, &.{ 7, 8, 4 });

    mode = .descending;
    list_sort.listSort(&mode, &north, keyCmp);
    list_sort.listSort(&mode, &south, keyCmp);
    mode = .ascending;
    list_sort.listSort(&mode, &center, keyCmp);

    try expectOrdinals(&north, &.{ 6, 3, 1 });
    try expectOrdinals(&center, &.{ 9, 5, 2, 0 });
    try expectOrdinals(&south, &.{ 4, 8, 7 });

    while (!list_sort.listEmpty(&north) or !list_sort.listEmpty(&center) or !list_sort.listEmpty(&south)) {
        if (popFront(&north)) |node| {
            try expectDetached(node);
            list_sort.listAddTail(node, &head);
        }
        if (popBack(&center)) |node| {
            try expectDetached(node);
            list_sort.listAddTail(node, &head);
        }
        if (popFront(&south)) |node| {
            try expectDetached(node);
            list_sort.listAddTail(node, &head);
        }
        if (popFront(&center)) |node| {
            try expectDetached(node);
            list_sort.listAddTail(node, &head);
        }
        if (popBack(&north)) |node| {
            try expectDetached(node);
            list_sort.listAddTail(node, &head);
        }
        if (popBack(&south)) |node| {
            try expectDetached(node);
            list_sort.listAddTail(node, &head);
        }
    }

    const woven_ordinals = [_]usize{ 6, 0, 4, 9, 1, 7, 3, 2, 8, 5 };
    try expectOrdinals(&head, &woven_ordinals);
    try std.testing.expect(list_sort.listEmpty(&north));
    try std.testing.expect(list_sort.listEmpty(&center));
    try std.testing.expect(list_sort.listEmpty(&south));
    try std.testing.expect(head.next == &entries[6].node);
    try std.testing.expect(head.prev == &entries[5].node);

    list_sort.listSort(null, &head, allTiesCmp);
    try expectOrdinals(&head, &woven_ordinals);
    try std.testing.expect(head.next == &entries[6].node);
    try std.testing.expect(head.prev == &entries[5].node);
}
