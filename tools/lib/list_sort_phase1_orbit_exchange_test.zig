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
        const entry: *const Entry = @fieldParentPtr("node", current.?);
        seen[count] = entry.ordinal;
        try std.testing.expect(current.?.next.?.prev == current.?);
        try std.testing.expect(current.?.prev.?.next == current.?);
        count += 1;
    }

    try std.testing.expectEqualSlices(usize, expected, seen[0..count]);
}

test "list sort survives sorted-rank orbit exchange replay" {
    var head: ListHead = .{};
    var inner: ListHead = .{};
    var outer: ListHead = .{};
    head.init();
    inner.init();
    outer.init();

    var entries = [_]Entry{
        .{ .key = 4, .ordinal = 0 },
        .{ .key = 1, .ordinal = 1 },
        .{ .key = 7, .ordinal = 2 },
        .{ .key = 2, .ordinal = 3 },
        .{ .key = 5, .ordinal = 4 },
        .{ .key = 0, .ordinal = 5 },
        .{ .key = 6, .ordinal = 6 },
        .{ .key = 2, .ordinal = 7 },
        .{ .key = 8, .ordinal = 8 },
        .{ .key = 1, .ordinal = 9 },
        .{ .key = 3, .ordinal = 10 },
        .{ .key = 5, .ordinal = 11 },
    };

    for (&entries) |*entry| list_sort.listAddTail(&entry.node, &head);

    var mode = SortMode.key_asc;
    list_sort.listSort(&mode, &head, compare);
    try expectCircularOrdinals(&head, &.{ 5, 1, 9, 3, 7, 10, 0, 4, 11, 6, 2, 8 });

    var rank: usize = 0;
    var current = head.next;
    while (current != &head) {
        const node = current.?;
        current = node.next;
        list_sort.listDel(node);
        try expectDetached(node);

        if ((rank & 1) == 0) {
            list_sort.listAddTail(node, &inner);
        } else {
            list_sort.listAddTail(node, &outer);
        }
        rank += 1;
    }

    try std.testing.expect(list_sort.listEmpty(&head));
    try expectCircularOrdinals(&inner, &.{ 5, 9, 7, 0, 11, 2 });
    try expectCircularOrdinals(&outer, &.{ 1, 3, 10, 4, 6, 8 });

    mode = .key_desc;
    list_sort.listSort(&mode, &inner, compare);
    mode = .ordinal_asc;
    list_sort.listSort(&mode, &outer, compare);

    try expectCircularOrdinals(&inner, &.{ 2, 11, 0, 7, 9, 5 });
    try expectCircularOrdinals(&outer, &.{ 1, 3, 4, 6, 8, 10 });

    while (!list_sort.listEmpty(&inner) or !list_sort.listEmpty(&outer)) {
        if (popFront(&inner)) |node| {
            try expectDetached(node);
            list_sort.listAddTail(node, &head);
        }
        if (popBack(&outer)) |node| {
            try expectDetached(node);
            list_sort.listAddTail(node, &head);
        }
        if (popBack(&inner)) |node| {
            try expectDetached(node);
            list_sort.listAddTail(node, &head);
        }
        if (popFront(&outer)) |node| {
            try expectDetached(node);
            list_sort.listAddTail(node, &head);
        }
    }

    try std.testing.expect(list_sort.listEmpty(&inner));
    try std.testing.expect(list_sort.listEmpty(&outer));
    try expectCircularOrdinals(&head, &.{ 2, 10, 5, 1, 11, 8, 9, 3, 0, 6, 7, 4 });

    mode = .all_ties;
    list_sort.listSort(&mode, &head, compare);
    try expectCircularOrdinals(&head, &.{ 2, 10, 5, 1, 11, 8, 9, 3, 0, 6, 7, 4 });
    try std.testing.expect(head.next == &entries[2].node);
    try std.testing.expect(head.prev == &entries[4].node);
}
