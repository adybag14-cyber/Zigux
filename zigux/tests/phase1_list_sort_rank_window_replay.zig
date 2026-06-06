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
}

test "list sort survives rank-window detach and folded rejoin" {
    var head: ListHead = .{};
    var low: ListHead = .{};
    var mid: ListHead = .{};
    var high: ListHead = .{};
    head.init();
    low.init();
    mid.init();
    high.init();

    var entries = [_]Entry{
        .{ .key = 7, .ordinal = 0 },
        .{ .key = 2, .ordinal = 1 },
        .{ .key = 5, .ordinal = 2 },
        .{ .key = 0, .ordinal = 3 },
        .{ .key = 9, .ordinal = 4 },
        .{ .key = 4, .ordinal = 5 },
        .{ .key = 1, .ordinal = 6 },
        .{ .key = 8, .ordinal = 7 },
        .{ .key = 3, .ordinal = 8 },
        .{ .key = 6, .ordinal = 9 },
        .{ .key = 2, .ordinal = 10 },
        .{ .key = 5, .ordinal = 11 },
    };

    for (&entries) |*entry| list_sort.listAddTail(&entry.node, &head);

    var mode = SortMode.key_asc;
    list_sort.listSort(&mode, &head, compare);
    try expectCircularOrdinals(&head, &.{ 3, 6, 1, 10, 8, 5, 2, 11, 9, 0, 7, 4 });

    var rank: usize = 0;
    var current = head.next;
    while (current != &head) {
        const node = current.?;
        current = node.next;
        list_sort.listDel(node);
        try expectDetached(node);
        if (rank < 4) {
            list_sort.listAddTail(node, &low);
        } else if (rank < 8) {
            list_sort.listAddTail(node, &mid);
        } else {
            list_sort.listAddTail(node, &high);
        }
        rank += 1;
    }
    try std.testing.expect(list_sort.listEmpty(&head));

    mode = .key_desc;
    list_sort.listSort(&mode, &low, compare);
    mode = .ordinal_asc;
    list_sort.listSort(&mode, &mid, compare);
    mode = .key_asc;
    list_sort.listSort(&mode, &high, compare);

    while (popFront(&low)) |node| {
        try expectDetached(node);
        list_sort.listAddTail(node, &head);
    }

    while (!list_sort.listEmpty(&high) or !list_sort.listEmpty(&mid)) {
        if (popBack(&high)) |node| {
            try expectDetached(node);
            list_sort.listAddTail(node, &head);
        }
        if (popFront(&mid)) |node| {
            try expectDetached(node);
            list_sort.listAddTail(node, &head);
        }
    }

    try std.testing.expect(list_sort.listEmpty(&low));
    try std.testing.expect(list_sort.listEmpty(&mid));
    try std.testing.expect(list_sort.listEmpty(&high));
    try expectCircularOrdinals(&head, &.{ 1, 10, 6, 3, 4, 2, 7, 5, 0, 8, 9, 11 });

    mode = .all_ties;
    list_sort.listSort(&mode, &head, compare);
    try expectCircularOrdinals(&head, &.{ 1, 10, 6, 3, 4, 2, 7, 5, 0, 8, 9, 11 });
    try std.testing.expect(head.next == &entries[1].node);
    try std.testing.expect(head.prev == &entries[11].node);
}
