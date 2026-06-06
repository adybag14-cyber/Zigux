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

test "list sort preserves segment rollover after staged resort replay" {
    var head: ListHead = .{};
    var low_segment: ListHead = .{};
    var mid_segment: ListHead = .{};
    var high_segment: ListHead = .{};
    head.init();
    low_segment.init();
    mid_segment.init();
    high_segment.init();

    var entries = [_]Entry{
        .{ .key = 4, .ordinal = 0 },
        .{ .key = 10, .ordinal = 1 },
        .{ .key = 1, .ordinal = 2 },
        .{ .key = 7, .ordinal = 3 },
        .{ .key = 3, .ordinal = 4 },
        .{ .key = 8, .ordinal = 5 },
        .{ .key = 1, .ordinal = 6 },
        .{ .key = 6, .ordinal = 7 },
        .{ .key = 2, .ordinal = 8 },
        .{ .key = 9, .ordinal = 9 },
        .{ .key = 5, .ordinal = 10 },
        .{ .key = 0, .ordinal = 11 },
    };

    for (&entries) |*entry| list_sort.listAddTail(&entry.node, &head);

    var mode = SortMode.key_asc;
    list_sort.listSort(&mode, &head, compare);
    try expectCircularOrdinals(&head, &.{ 11, 2, 6, 8, 4, 0, 10, 7, 3, 5, 9, 1 });

    var rank: usize = 0;
    var current = head.next;
    while (current != &head) {
        const node = current.?;
        current = node.next;
        list_sort.listDel(node);
        try expectDetached(node);

        switch (rank / 4) {
            0 => list_sort.listAddTail(node, &low_segment),
            1 => list_sort.listAddTail(node, &mid_segment),
            else => list_sort.listAddTail(node, &high_segment),
        }
        rank += 1;
    }

    try std.testing.expect(list_sort.listEmpty(&head));
    try expectCircularOrdinals(&low_segment, &.{ 11, 2, 6, 8 });
    try expectCircularOrdinals(&mid_segment, &.{ 4, 0, 10, 7 });
    try expectCircularOrdinals(&high_segment, &.{ 3, 5, 9, 1 });

    mode = .key_desc;
    list_sort.listSort(&mode, &low_segment, compare);
    mode = .ordinal_asc;
    list_sort.listSort(&mode, &mid_segment, compare);
    mode = .key_desc;
    list_sort.listSort(&mode, &high_segment, compare);

    try expectCircularOrdinals(&low_segment, &.{ 8, 2, 6, 11 });
    try expectCircularOrdinals(&mid_segment, &.{ 0, 4, 7, 10 });
    try expectCircularOrdinals(&high_segment, &.{ 1, 9, 5, 3 });

    while (!list_sort.listEmpty(&mid_segment) or !list_sort.listEmpty(&high_segment) or !list_sort.listEmpty(&low_segment)) {
        if (popFront(&mid_segment)) |node| {
            try expectDetached(node);
            list_sort.listAddTail(node, &head);
        }
        if (popBack(&high_segment)) |node| {
            try expectDetached(node);
            list_sort.listAddTail(node, &head);
        }
        if (popFront(&low_segment)) |node| {
            try expectDetached(node);
            list_sort.listAddTail(node, &head);
        }
    }

    try std.testing.expect(list_sort.listEmpty(&low_segment));
    try std.testing.expect(list_sort.listEmpty(&mid_segment));
    try std.testing.expect(list_sort.listEmpty(&high_segment));
    try expectCircularOrdinals(&head, &.{ 0, 3, 8, 4, 5, 2, 7, 9, 6, 10, 1, 11 });

    mode = .all_ties;
    list_sort.listSort(&mode, &head, compare);
    try expectCircularOrdinals(&head, &.{ 0, 3, 8, 4, 5, 2, 7, 9, 6, 10, 1, 11 });
    try std.testing.expect(head.next == &entries[0].node);
    try std.testing.expect(head.prev == &entries[11].node);
}
