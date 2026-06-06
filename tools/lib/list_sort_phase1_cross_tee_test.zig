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
    ordinal_desc,
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
        .ordinal_desc => compareInt(@intCast(rhs.ordinal), @intCast(lhs.ordinal)),
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

test "list sort survives sorted-rank cross tee replay" {
    var head: ListHead = .{};
    var trunk: ListHead = .{};
    var left: ListHead = .{};
    var right: ListHead = .{};
    var stem: ListHead = .{};
    head.init();
    trunk.init();
    left.init();
    right.init();
    stem.init();

    var entries = [_]Entry{
        .{ .key = 6, .ordinal = 0 },
        .{ .key = 0, .ordinal = 1 },
        .{ .key = 4, .ordinal = 2 },
        .{ .key = 2, .ordinal = 3 },
        .{ .key = 8, .ordinal = 4 },
        .{ .key = 1, .ordinal = 5 },
        .{ .key = 5, .ordinal = 6 },
        .{ .key = 3, .ordinal = 7 },
        .{ .key = 7, .ordinal = 8 },
        .{ .key = 2, .ordinal = 9 },
        .{ .key = 6, .ordinal = 10 },
        .{ .key = 4, .ordinal = 11 },
        .{ .key = 9, .ordinal = 12 },
    };

    for (&entries) |*entry| list_sort.listAddTail(&entry.node, &head);

    var mode = SortMode.key_asc;
    list_sort.listSort(&mode, &head, compare);
    try expectCircularOrdinals(&head, &.{ 1, 5, 3, 9, 7, 2, 11, 6, 0, 10, 8, 4, 12 });

    var rank: usize = 0;
    var current = head.next;
    while (current != &head) {
        const node = current.?;
        current = node.next;
        list_sort.listDel(node);
        try expectDetached(node);

        switch (rank & 3) {
            0 => list_sort.listAddTail(node, &trunk),
            1 => list_sort.listAddTail(node, &left),
            2 => list_sort.listAddTail(node, &right),
            else => list_sort.listAddTail(node, &stem),
        }
        rank += 1;
    }

    try std.testing.expect(list_sort.listEmpty(&head));
    try expectCircularOrdinals(&trunk, &.{ 1, 7, 0, 12 });
    try expectCircularOrdinals(&left, &.{ 5, 2, 10 });
    try expectCircularOrdinals(&right, &.{ 3, 11, 8 });
    try expectCircularOrdinals(&stem, &.{ 9, 6, 4 });

    mode = .key_desc;
    list_sort.listSort(&mode, &trunk, compare);
    mode = .ordinal_desc;
    list_sort.listSort(&mode, &left, compare);
    mode = .key_asc;
    list_sort.listSort(&mode, &right, compare);
    mode = .ordinal_asc;
    list_sort.listSort(&mode, &stem, compare);

    try expectCircularOrdinals(&trunk, &.{ 12, 0, 7, 1 });
    try expectCircularOrdinals(&left, &.{ 10, 5, 2 });
    try expectCircularOrdinals(&right, &.{ 3, 11, 8 });
    try expectCircularOrdinals(&stem, &.{ 4, 6, 9 });

    while (!list_sort.listEmpty(&trunk) or
        !list_sort.listEmpty(&left) or
        !list_sort.listEmpty(&right) or
        !list_sort.listEmpty(&stem))
    {
        if (popFront(&trunk)) |node| {
            try expectDetached(node);
            list_sort.listAddTail(node, &head);
        }
        if (popFront(&left)) |node| {
            try expectDetached(node);
            list_sort.listAddTail(node, &head);
        }
        if (popBack(&right)) |node| {
            try expectDetached(node);
            list_sort.listAddTail(node, &head);
        }
        if (popBack(&stem)) |node| {
            try expectDetached(node);
            list_sort.listAddTail(node, &head);
        }
        if (popBack(&trunk)) |node| {
            try expectDetached(node);
            list_sort.listAddTail(node, &head);
        }
        if (popBack(&left)) |node| {
            try expectDetached(node);
            list_sort.listAddTail(node, &head);
        }
        if (popFront(&right)) |node| {
            try expectDetached(node);
            list_sort.listAddTail(node, &head);
        }
        if (popFront(&stem)) |node| {
            try expectDetached(node);
            list_sort.listAddTail(node, &head);
        }
    }

    try std.testing.expect(list_sort.listEmpty(&trunk));
    try std.testing.expect(list_sort.listEmpty(&left));
    try std.testing.expect(list_sort.listEmpty(&right));
    try std.testing.expect(list_sort.listEmpty(&stem));
    try expectCircularOrdinals(&head, &.{ 12, 10, 8, 9, 1, 2, 3, 4, 0, 5, 11, 6, 7 });

    mode = .all_ties;
    list_sort.listSort(&mode, &head, compare);
    try expectCircularOrdinals(&head, &.{ 12, 10, 8, 9, 1, 2, 3, 4, 0, 5, 11, 6, 7 });
    try std.testing.expect(head.next == &entries[12].node);
    try std.testing.expect(head.prev == &entries[7].node);
}
