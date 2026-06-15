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
    if (lhs < rhs) return -13;
    if (lhs > rhs) return 17;
    return 0;
}

fn slotRamp(rank: usize) usize {
    const folded = rank % 10;
    return if (folded <= 5) folded else 10 - folded;
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
    var seen: [32]usize = undefined;
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

    var reverse_seen: [32]usize = undefined;
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

fn anySlotHasNodes(slots: *[6]ListHead) bool {
    for (slots) |*slot| {
        if (!list_sort.listEmpty(slot)) return true;
    }
    return false;
}

test "list sort survives slot ramp staged rebuild" {
    var head: ListHead = .{};
    var slots = [_]ListHead{ .{}, .{}, .{}, .{}, .{}, .{} };
    head.init();
    for (&slots) |*slot| slot.init();

    var entries = [_]Entry{
        .{ .key = 6, .ordinal = 0 },
        .{ .key = 1, .ordinal = 1 },
        .{ .key = 8, .ordinal = 2 },
        .{ .key = 3, .ordinal = 3 },
        .{ .key = 5, .ordinal = 4 },
        .{ .key = 2, .ordinal = 5 },
        .{ .key = 7, .ordinal = 6 },
        .{ .key = 0, .ordinal = 7 },
        .{ .key = 4, .ordinal = 8 },
        .{ .key = 9, .ordinal = 9 },
        .{ .key = 3, .ordinal = 10 },
        .{ .key = 6, .ordinal = 11 },
        .{ .key = 1, .ordinal = 12 },
        .{ .key = 8, .ordinal = 13 },
        .{ .key = 2, .ordinal = 14 },
        .{ .key = 5, .ordinal = 15 },
        .{ .key = 0, .ordinal = 16 },
        .{ .key = 4, .ordinal = 17 },
    };

    for (&entries, 0..) |*entry, index| {
        if ((index % 5) == 2 or (index % 5) == 4) {
            list_sort.listAdd(&entry.node, &head);
        } else {
            list_sort.listAddTail(&entry.node, &head);
        }
    }

    try expectCircularOrdinals(&head, &.{ 17, 14, 12, 9, 7, 4, 2, 0, 1, 3, 5, 6, 8, 10, 11, 13, 15, 16 });

    var mode = SortMode.key_asc;
    list_sort.listSort(&mode, &head, compare);
    try expectCircularOrdinals(&head, &.{ 7, 16, 12, 1, 14, 5, 3, 10, 17, 8, 4, 15, 0, 11, 6, 2, 13, 9 });

    var rank: usize = 0;
    var current = head.next;
    while (current != &head) {
        const node = current.?;
        current = node.next;
        list_sort.listDel(node);
        try expectDetached(node);

        const slot_index = slotRamp(rank);
        if ((rank % 3) == 1) {
            list_sort.listAdd(node, &slots[slot_index]);
        } else {
            list_sort.listAddTail(node, &slots[slot_index]);
        }
        rank += 1;
    }
    try std.testing.expect(list_sort.listEmpty(&head));

    try expectCircularOrdinals(&slots[0], &.{ 4, 7 });
    try expectCircularOrdinals(&slots[1], &.{ 16, 8, 15 });
    try expectCircularOrdinals(&slots[2], &.{ 12, 17, 0 });
    try expectCircularOrdinals(&slots[3], &.{ 11, 10, 1, 9 });
    try expectCircularOrdinals(&slots[4], &.{ 13, 14, 3, 6 });
    try expectCircularOrdinals(&slots[5], &.{ 5, 2 });

    mode = .ordinal_desc;
    list_sort.listSort(&mode, &slots[0], compare);
    mode = .key_desc;
    list_sort.listSort(&mode, &slots[1], compare);
    mode = .ordinal_asc;
    list_sort.listSort(&mode, &slots[2], compare);
    mode = .key_asc;
    list_sort.listSort(&mode, &slots[3], compare);
    mode = .ordinal_desc;
    list_sort.listSort(&mode, &slots[4], compare);
    mode = .key_desc;
    list_sort.listSort(&mode, &slots[5], compare);

    try expectCircularOrdinals(&slots[0], &.{ 7, 4 });
    try expectCircularOrdinals(&slots[1], &.{ 15, 8, 16 });
    try expectCircularOrdinals(&slots[2], &.{ 0, 12, 17 });
    try expectCircularOrdinals(&slots[3], &.{ 1, 10, 11, 9 });
    try expectCircularOrdinals(&slots[4], &.{ 14, 13, 6, 3 });
    try expectCircularOrdinals(&slots[5], &.{ 2, 5 });

    while (anySlotHasNodes(&slots)) {
        if (popFront(&slots[5])) |node| {
            try expectDetached(node);
            list_sort.listAddTail(node, &head);
        }
        if (popBack(&slots[0])) |node| {
            try expectDetached(node);
            list_sort.listAdd(node, &head);
        }
        if (popFront(&slots[3])) |node| {
            try expectDetached(node);
            list_sort.listAddTail(node, &head);
        }
        if (popBack(&slots[1])) |node| {
            try expectDetached(node);
            list_sort.listAddTail(node, &head);
        }
        if (popFront(&slots[4])) |node| {
            try expectDetached(node);
            list_sort.listAdd(node, &head);
        }
        if (popBack(&slots[2])) |node| {
            try expectDetached(node);
            list_sort.listAddTail(node, &head);
        }
    }

    for (&slots) |*slot| try std.testing.expect(list_sort.listEmpty(slot));
    try expectCircularOrdinals(&head, &.{ 3, 6, 13, 7, 14, 4, 2, 1, 16, 17, 5, 10, 8, 12, 11, 15, 0, 9 });

    mode = .all_ties;
    list_sort.listSort(&mode, &head, compare);
    try expectCircularOrdinals(&head, &.{ 3, 6, 13, 7, 14, 4, 2, 1, 16, 17, 5, 10, 8, 12, 11, 15, 0, 9 });
    try std.testing.expect(head.next == &entries[3].node);
    try std.testing.expect(head.prev == &entries[9].node);

    mode = .key_desc;
    list_sort.listSort(&mode, &head, compare);
    try expectCircularOrdinals(&head, &.{ 9, 13, 2, 6, 11, 0, 4, 15, 17, 8, 3, 10, 14, 5, 1, 12, 7, 16 });
}
