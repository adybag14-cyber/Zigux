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
    if (lhs < rhs) return -5;
    if (lhs > rhs) return 7;
    return 0;
}

fn sawtoothLane(rank: usize) usize {
    const folded = rank % 8;
    return if (folded <= 4) folded else 8 - folded;
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
    var seen: [24]usize = undefined;
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

    var reverse_seen: [24]usize = undefined;
    var reverse_count: usize = 0;
    current = head.prev;
    while (current != head) : (current = current.?.prev) {
        const entry: *const Entry = @fieldParentPtr("node", current.?);
        reverse_seen[reverse_count] = entry.ordinal;
        reverse_count += 1;
    }

    try std.testing.expectEqual(expected.len, reverse_count);
    for (expected, 0..) |_, index| {
        try std.testing.expectEqual(expected[expected.len - 1 - index], reverse_seen[index]);
    }
}

fn anyLaneHasNodes(lanes: *[5]ListHead) bool {
    for (lanes) |*lane| {
        if (!list_sort.listEmpty(lane)) return true;
    }
    return false;
}

test "list sort survives sawtooth staged conveyor rebuild" {
    var head: ListHead = .{};
    var lanes = [_]ListHead{ .{}, .{}, .{}, .{}, .{} };
    head.init();
    for (&lanes) |*lane| lane.init();

    var entries = [_]Entry{
        .{ .key = 7, .ordinal = 0 },
        .{ .key = 1, .ordinal = 1 },
        .{ .key = 5, .ordinal = 2 },
        .{ .key = 3, .ordinal = 3 },
        .{ .key = 1, .ordinal = 4 },
        .{ .key = 8, .ordinal = 5 },
        .{ .key = 0, .ordinal = 6 },
        .{ .key = 4, .ordinal = 7 },
        .{ .key = 6, .ordinal = 8 },
        .{ .key = 2, .ordinal = 9 },
        .{ .key = 5, .ordinal = 10 },
        .{ .key = 3, .ordinal = 11 },
        .{ .key = 9, .ordinal = 12 },
        .{ .key = 2, .ordinal = 13 },
        .{ .key = 4, .ordinal = 14 },
    };

    for (&entries, 0..) |*entry, index| {
        if ((index & 3) == 1) {
            list_sort.listAdd(&entry.node, &head);
        } else {
            list_sort.listAddTail(&entry.node, &head);
        }
    }

    try expectCircularOrdinals(&head, &.{ 13, 9, 5, 1, 0, 2, 3, 4, 6, 7, 8, 10, 11, 12, 14 });

    var mode = SortMode.key_asc;
    list_sort.listSort(&mode, &head, compare);
    try expectCircularOrdinals(&head, &.{ 6, 1, 4, 13, 9, 3, 11, 7, 14, 2, 10, 8, 0, 5, 12 });

    var rank: usize = 0;
    var current = head.next;
    while (current != &head) {
        const node = current.?;
        current = node.next;
        list_sort.listDel(node);
        try expectDetached(node);

        const lane_index = sawtoothLane(rank);
        if ((rank & 1) == 0) {
            list_sort.listAddTail(node, &lanes[lane_index]);
        } else {
            list_sort.listAdd(node, &lanes[lane_index]);
        }
        rank += 1;
    }
    try std.testing.expect(list_sort.listEmpty(&head));

    try expectCircularOrdinals(&lanes[0], &.{ 6, 14 });
    try expectCircularOrdinals(&lanes[1], &.{ 2, 7, 1 });
    try expectCircularOrdinals(&lanes[2], &.{ 4, 11, 10, 12 });
    try expectCircularOrdinals(&lanes[3], &.{ 5, 8, 3, 13 });
    try expectCircularOrdinals(&lanes[4], &.{ 9, 0 });

    mode = .ordinal_desc;
    list_sort.listSort(&mode, &lanes[0], compare);
    mode = .key_desc;
    list_sort.listSort(&mode, &lanes[1], compare);
    mode = .key_asc;
    list_sort.listSort(&mode, &lanes[2], compare);
    mode = .ordinal_asc;
    list_sort.listSort(&mode, &lanes[3], compare);
    mode = .key_desc;
    list_sort.listSort(&mode, &lanes[4], compare);

    try expectCircularOrdinals(&lanes[0], &.{ 14, 6 });
    try expectCircularOrdinals(&lanes[1], &.{ 2, 7, 1 });
    try expectCircularOrdinals(&lanes[2], &.{ 4, 11, 10, 12 });
    try expectCircularOrdinals(&lanes[3], &.{ 3, 5, 8, 13 });
    try expectCircularOrdinals(&lanes[4], &.{ 0, 9 });

    while (anyLaneHasNodes(&lanes)) {
        if (popFront(&lanes[4])) |node| {
            try expectDetached(node);
            list_sort.listAddTail(node, &head);
        }
        if (popBack(&lanes[0])) |node| {
            try expectDetached(node);
            list_sort.listAdd(node, &head);
        }
        if (popFront(&lanes[3])) |node| {
            try expectDetached(node);
            list_sort.listAddTail(node, &head);
        }
        if (popBack(&lanes[1])) |node| {
            try expectDetached(node);
            list_sort.listAddTail(node, &head);
        }
        if (popFront(&lanes[2])) |node| {
            try expectDetached(node);
            list_sort.listAdd(node, &head);
        }
    }

    for (&lanes) |*lane| try std.testing.expect(list_sort.listEmpty(lane));
    try expectCircularOrdinals(&head, &.{ 12, 10, 11, 14, 4, 6, 0, 3, 1, 9, 5, 7, 8, 2, 13 });

    mode = .all_ties;
    list_sort.listSort(&mode, &head, compare);
    try expectCircularOrdinals(&head, &.{ 12, 10, 11, 14, 4, 6, 0, 3, 1, 9, 5, 7, 8, 2, 13 });
    try std.testing.expect(head.next == &entries[12].node);
    try std.testing.expect(head.prev == &entries[13].node);

    mode = .key_desc;
    list_sort.listSort(&mode, &head, compare);
    try expectCircularOrdinals(&head, &.{ 12, 5, 0, 8, 10, 2, 14, 7, 11, 3, 9, 13, 4, 1, 6 });
}
