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
        .ordinal_desc => compareInt(@as(i32, @intCast(rhs.ordinal)), @as(i32, @intCast(lhs.ordinal))),
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

fn sortHead(head: *ListHead, mode: *SortMode) void {
    if (!list_sort.listEmpty(head)) {
        list_sort.listSort(mode, head, compare);
    }
}

test "list sort survives sorted lane shuffle replay" {
    var head: ListHead = .{};
    head.init();

    var entries = [_]Entry{
        .{ .key = 6, .ordinal = 0 },
        .{ .key = 1, .ordinal = 1 },
        .{ .key = 4, .ordinal = 2 },
        .{ .key = 1, .ordinal = 3 },
        .{ .key = 7, .ordinal = 4 },
        .{ .key = 3, .ordinal = 5 },
        .{ .key = 6, .ordinal = 6 },
        .{ .key = 2, .ordinal = 7 },
        .{ .key = 5, .ordinal = 8 },
        .{ .key = 3, .ordinal = 9 },
        .{ .key = 8, .ordinal = 10 },
        .{ .key = 0, .ordinal = 11 },
        .{ .key = 5, .ordinal = 12 },
        .{ .key = 2, .ordinal = 13 },
    };

    for (&entries) |*entry| list_sort.listAddTail(&entry.node, &head);

    var mode = SortMode.key_asc;
    list_sort.listSort(&mode, &head, compare);
    try expectCircularOrdinals(&head, &.{ 11, 1, 3, 7, 13, 5, 9, 2, 8, 12, 0, 6, 4, 10 });

    var lanes = [_]ListHead{ .{}, .{}, .{}, .{} };
    for (&lanes) |*lane| lane.init();

    var sorted_rank: usize = 0;
    while (popFront(&head)) |node| : (sorted_rank += 1) {
        try expectDetached(node);
        list_sort.listAddTail(node, &lanes[sorted_rank % lanes.len]);
    }
    try std.testing.expect(list_sort.listEmpty(&head));

    try expectCircularOrdinals(&lanes[0], &.{ 11, 13, 8, 4 });
    try expectCircularOrdinals(&lanes[1], &.{ 1, 5, 12, 10 });
    try expectCircularOrdinals(&lanes[2], &.{ 3, 9, 0 });
    try expectCircularOrdinals(&lanes[3], &.{ 7, 2, 6 });

    mode = .key_desc;
    sortHead(&lanes[0], &mode);
    mode = .ordinal_desc;
    sortHead(&lanes[1], &mode);
    mode = .key_asc;
    sortHead(&lanes[2], &mode);
    mode = .key_desc;
    sortHead(&lanes[3], &mode);

    try expectCircularOrdinals(&lanes[0], &.{ 4, 8, 13, 11 });
    try expectCircularOrdinals(&lanes[1], &.{ 12, 10, 5, 1 });
    try expectCircularOrdinals(&lanes[2], &.{ 3, 9, 0 });
    try expectCircularOrdinals(&lanes[3], &.{ 6, 2, 7 });

    while (!list_sort.listEmpty(&lanes[0]) or
        !list_sort.listEmpty(&lanes[1]) or
        !list_sort.listEmpty(&lanes[2]) or
        !list_sort.listEmpty(&lanes[3]))
    {
        if (popFront(&lanes[2])) |node| {
            try expectDetached(node);
            list_sort.listAddTail(node, &head);
        }
        if (popBack(&lanes[0])) |node| {
            try expectDetached(node);
            list_sort.listAddTail(node, &head);
        }
        if (popFront(&lanes[3])) |node| {
            try expectDetached(node);
            list_sort.listAddTail(node, &head);
        }
        if (popBack(&lanes[1])) |node| {
            try expectDetached(node);
            list_sort.listAddTail(node, &head);
        }
    }

    const shuffled_order = [_]usize{ 3, 11, 6, 1, 9, 13, 2, 5, 0, 8, 7, 10, 4, 12 };
    try expectCircularOrdinals(&head, &shuffled_order);
    try std.testing.expect(head.next == &entries[3].node);
    try std.testing.expect(head.prev == &entries[12].node);

    mode = .all_ties;
    list_sort.listSort(&mode, &head, compare);
    try expectCircularOrdinals(&head, &shuffled_order);
    try std.testing.expect(head.next == &entries[3].node);
    try std.testing.expect(head.prev == &entries[12].node);
}
