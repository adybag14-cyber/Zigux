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
        .ordinal_asc => compareInt(@intCast(lhs.ordinal), @intCast(rhs.ordinal)),
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
        const node = current.?;
        const entry: *const Entry = @fieldParentPtr("node", node);
        seen[count] = entry.ordinal;
        try std.testing.expect(node.next.?.prev == node);
        try std.testing.expect(node.prev.?.next == node);
        count += 1;
    }

    try std.testing.expectEqualSlices(usize, expected, seen[0..count]);
}

fn appendPop(pop: ?*ListHead, head: *ListHead) !void {
    if (pop) |node| {
        try expectDetached(node);
        list_sort.listAddTail(node, head);
    }
}

test "list sort preserves trellis weave staging lifecycle" {
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
        .{ .key = 9, .ordinal = 2 },
        .{ .key = 1, .ordinal = 3 },
        .{ .key = 6, .ordinal = 4 },
        .{ .key = 2, .ordinal = 5 },
        .{ .key = 8, .ordinal = 6 },
        .{ .key = 4, .ordinal = 7 },
        .{ .key = 3, .ordinal = 8 },
        .{ .key = 7, .ordinal = 9 },
        .{ .key = 0, .ordinal = 10 },
        .{ .key = 5, .ordinal = 11 },
        .{ .key = 4, .ordinal = 12 },
        .{ .key = 1, .ordinal = 13 },
    };

    for (&entries) |*entry| list_sort.listAddTail(&entry.node, &head);

    var mode = SortMode.key_asc;
    list_sort.listSort(&mode, &head, compare);
    try expectCircularOrdinals(&head, &.{ 10, 3, 13, 1, 5, 8, 7, 12, 0, 11, 4, 9, 6, 2 });

    var rank: usize = 0;
    var current = head.next;
    while (current != &head) {
        const node = current.?;
        current = node.next;
        list_sort.listDel(node);
        try expectDetached(node);

        switch (rank & 3) {
            0 => list_sort.listAddTail(node, &north),
            1 => list_sort.listAdd(node, &east),
            2 => list_sort.listAddTail(node, &south),
            else => list_sort.listAdd(node, &west),
        }
        rank += 1;
    }
    try std.testing.expect(list_sort.listEmpty(&head));
    try expectCircularOrdinals(&north, &.{ 10, 5, 0, 6 });
    try expectCircularOrdinals(&east, &.{ 2, 11, 8, 3 });
    try expectCircularOrdinals(&south, &.{ 13, 7, 4 });
    try expectCircularOrdinals(&west, &.{ 9, 12, 1 });

    mode = .key_desc;
    list_sort.listSort(&mode, &north, compare);
    mode = .ordinal_asc;
    list_sort.listSort(&mode, &east, compare);
    mode = .key_asc;
    list_sort.listSort(&mode, &south, compare);
    mode = .key_desc;
    list_sort.listSort(&mode, &west, compare);

    try expectCircularOrdinals(&north, &.{ 6, 0, 5, 10 });
    try expectCircularOrdinals(&east, &.{ 2, 3, 8, 11 });
    try expectCircularOrdinals(&south, &.{ 13, 7, 4 });
    try expectCircularOrdinals(&west, &.{ 9, 12, 1 });

    while (!list_sort.listEmpty(&north) or !list_sort.listEmpty(&east) or !list_sort.listEmpty(&south) or !list_sort.listEmpty(&west)) {
        try appendPop(popFront(&north), &head);
        try appendPop(popBack(&east), &head);
        try appendPop(popFront(&south), &head);
        try appendPop(popBack(&west), &head);
        try appendPop(popBack(&north), &head);
        try appendPop(popFront(&east), &head);
        try appendPop(popBack(&south), &head);
        try appendPop(popFront(&west), &head);
    }

    try std.testing.expect(list_sort.listEmpty(&north));
    try std.testing.expect(list_sort.listEmpty(&east));
    try std.testing.expect(list_sort.listEmpty(&south));
    try std.testing.expect(list_sort.listEmpty(&west));
    try expectCircularOrdinals(&head, &.{ 6, 11, 13, 1, 10, 2, 4, 9, 0, 8, 7, 12, 5, 3 });

    mode = .all_ties;
    list_sort.listSort(&mode, &head, compare);
    try expectCircularOrdinals(&head, &.{ 6, 11, 13, 1, 10, 2, 4, 9, 0, 8, 7, 12, 5, 3 });
    try std.testing.expect(head.next == &entries[6].node);
    try std.testing.expect(head.prev == &entries[3].node);
}
