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
    if (lhs < rhs) return -3;
    if (lhs > rhs) return 5;
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
    var seen: [20]usize = undefined;
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

fn drainSpiralRound(head: *ListHead, lanes: *[5]ListHead, round: usize) !bool {
    var moved = false;
    if ((round & 1) == 0) {
        if (popFront(&lanes[0])) |node| {
            try expectDetached(node);
            list_sort.listAddTail(node, head);
            moved = true;
        }
        if (popBack(&lanes[1])) |node| {
            try expectDetached(node);
            list_sort.listAddTail(node, head);
            moved = true;
        }
        if (popFront(&lanes[2])) |node| {
            try expectDetached(node);
            list_sort.listAddTail(node, head);
            moved = true;
        }
        if (popBack(&lanes[3])) |node| {
            try expectDetached(node);
            list_sort.listAddTail(node, head);
            moved = true;
        }
        if (popFront(&lanes[4])) |node| {
            try expectDetached(node);
            list_sort.listAddTail(node, head);
            moved = true;
        }
    } else {
        if (popBack(&lanes[4])) |node| {
            try expectDetached(node);
            list_sort.listAddTail(node, head);
            moved = true;
        }
        if (popFront(&lanes[3])) |node| {
            try expectDetached(node);
            list_sort.listAddTail(node, head);
            moved = true;
        }
        if (popBack(&lanes[2])) |node| {
            try expectDetached(node);
            list_sort.listAddTail(node, head);
            moved = true;
        }
        if (popFront(&lanes[1])) |node| {
            try expectDetached(node);
            list_sort.listAddTail(node, head);
            moved = true;
        }
        if (popBack(&lanes[0])) |node| {
            try expectDetached(node);
            list_sort.listAddTail(node, head);
            moved = true;
        }
    }
    return moved;
}

test "list sort survives spiral loom staged rebuild replay" {
    var head: ListHead = .{};
    var lanes = [_]ListHead{.{}} ** 5;
    head.init();
    for (&lanes) |*lane| lane.init();

    var entries = [_]Entry{
        .{ .key = 4, .ordinal = 0 },
        .{ .key = -1, .ordinal = 1 },
        .{ .key = 7, .ordinal = 2 },
        .{ .key = 2, .ordinal = 3 },
        .{ .key = 4, .ordinal = 4 },
        .{ .key = 0, .ordinal = 5 },
        .{ .key = 9, .ordinal = 6 },
        .{ .key = 2, .ordinal = 7 },
        .{ .key = -3, .ordinal = 8 },
        .{ .key = 6, .ordinal = 9 },
        .{ .key = 1, .ordinal = 10 },
        .{ .key = 7, .ordinal = 11 },
        .{ .key = -1, .ordinal = 12 },
        .{ .key = 5, .ordinal = 13 },
    };

    for (&entries) |*entry| {
        if ((entry.ordinal % 3) == 0) {
            list_sort.listAdd(&entry.node, &head);
        } else {
            list_sort.listAddTail(&entry.node, &head);
        }
    }

    var mode = SortMode.key_asc;
    list_sort.listSort(&mode, &head, compare);
    try expectCircularOrdinals(&head, &.{ 8, 12, 1, 5, 10, 3, 7, 0, 4, 13, 9, 2, 11, 6 });

    var rank: usize = 0;
    var current = head.next;
    while (current != &head) {
        const node = current.?;
        current = node.next;
        list_sort.listDel(node);
        try expectDetached(node);

        const lane = &lanes[rank % lanes.len];
        if ((rank & 1) == 0) {
            list_sort.listAddTail(node, lane);
        } else {
            list_sort.listAdd(node, lane);
        }
        rank += 1;
    }
    try std.testing.expect(list_sort.listEmpty(&head));
    try expectCircularOrdinals(&lanes[0], &.{ 3, 8, 9 });
    try expectCircularOrdinals(&lanes[1], &.{ 2, 12, 7 });
    try expectCircularOrdinals(&lanes[2], &.{ 0, 1, 11 });
    try expectCircularOrdinals(&lanes[3], &.{ 6, 5, 4 });
    try expectCircularOrdinals(&lanes[4], &.{ 13, 10 });

    mode = .key_desc;
    list_sort.listSort(&mode, &lanes[0], compare);
    mode = .ordinal_asc;
    list_sort.listSort(&mode, &lanes[1], compare);
    mode = .key_asc;
    list_sort.listSort(&mode, &lanes[2], compare);
    mode = .ordinal_desc;
    list_sort.listSort(&mode, &lanes[3], compare);
    mode = .key_desc;
    list_sort.listSort(&mode, &lanes[4], compare);

    try expectCircularOrdinals(&lanes[0], &.{ 9, 3, 8 });
    try expectCircularOrdinals(&lanes[1], &.{ 2, 7, 12 });
    try expectCircularOrdinals(&lanes[2], &.{ 1, 0, 11 });
    try expectCircularOrdinals(&lanes[3], &.{ 6, 5, 4 });
    try expectCircularOrdinals(&lanes[4], &.{ 13, 10 });

    var round: usize = 0;
    while (try drainSpiralRound(&head, &lanes, round)) : (round += 1) {}

    for (&lanes) |*lane| try std.testing.expect(list_sort.listEmpty(lane));
    try expectCircularOrdinals(&head, &.{ 9, 12, 1, 4, 13, 10, 6, 11, 2, 8, 3, 7, 0, 5 });

    mode = .all_ties;
    list_sort.listSort(&mode, &head, compare);
    try expectCircularOrdinals(&head, &.{ 9, 12, 1, 4, 13, 10, 6, 11, 2, 8, 3, 7, 0, 5 });
    try std.testing.expect(head.next == &entries[9].node);
    try std.testing.expect(head.prev == &entries[5].node);
}
