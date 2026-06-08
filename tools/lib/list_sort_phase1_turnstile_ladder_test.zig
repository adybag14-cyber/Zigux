const std = @import("std");
const list_sort = @import("list_sort");

const ListHead = list_sort.ListHead;

const Entry = struct {
    key: i32,
    ordinal: usize,
    ladder: usize,
    node: ListHead = .{},
};

const SortMode = enum {
    key_stable,
    key_asc,
    key_desc,
    ladder_asc,
    ordinal_desc,
    all_tie,
};

fn cmpByMode(priv: ?*anyopaque, a: *const ListHead, b: *const ListHead) i32 {
    const mode: *const SortMode = @ptrCast(@alignCast(priv.?));
    const lhs: *const Entry = @fieldParentPtr("node", a);
    const rhs: *const Entry = @fieldParentPtr("node", b);

    return switch (mode.*) {
        .key_stable => compareValue(lhs.key, rhs.key),
        .key_asc => compareWithOrdinal(lhs.key, rhs.key, lhs.ordinal, rhs.ordinal),
        .key_desc => compareWithOrdinal(rhs.key, lhs.key, lhs.ordinal, rhs.ordinal),
        .ladder_asc => compareWithOrdinal(lhs.ladder, rhs.ladder, lhs.ordinal, rhs.ordinal),
        .ordinal_desc => compareValue(rhs.ordinal, lhs.ordinal),
        .all_tie => 0,
    };
}

fn compareWithOrdinal(primary_lhs: anytype, primary_rhs: @TypeOf(primary_lhs), ordinal_lhs: usize, ordinal_rhs: usize) i32 {
    const primary = compareValue(primary_lhs, primary_rhs);
    if (primary != 0) return primary;
    return compareValue(ordinal_lhs, ordinal_rhs);
}

fn compareValue(lhs: anytype, rhs: @TypeOf(lhs)) i32 {
    if (lhs < rhs) return -5;
    if (lhs > rhs) return 7;
    return 0;
}

fn collectOrdinals(head: *const ListHead, out: []usize) ![]usize {
    var idx: usize = 0;
    var current = head.next;
    while (current != head) : (current = current.?.next) {
        const entry: *const Entry = @fieldParentPtr("node", current.?);
        out[idx] = entry.ordinal;
        try std.testing.expect(current.?.next.?.prev == current.?);
        try std.testing.expect(current.?.prev.?.next == current.?);
        idx += 1;
    }
    return out[0..idx];
}

fn collectKeys(head: *const ListHead, out: []i32) ![]i32 {
    var idx: usize = 0;
    var current = head.next;
    while (current != head) : (current = current.?.next) {
        const entry: *const Entry = @fieldParentPtr("node", current.?);
        out[idx] = entry.key;
        idx += 1;
    }
    return out[0..idx];
}

fn popFront(head: *ListHead) *ListHead {
    const node = head.next.?;
    list_sort.listDel(node);
    return node;
}

fn popBack(head: *ListHead) *ListHead {
    const node = head.prev.?;
    list_sort.listDel(node);
    return node;
}

fn entryFromNode(node: *ListHead) *Entry {
    return @fieldParentPtr("node", node);
}

fn expectDetached(node: *const ListHead) !void {
    try std.testing.expect(node.next == null);
    try std.testing.expect(node.prev == null);
}

test "phase1 list_sort turnstile ladder lifecycle" {
    var head: ListHead = .{};
    head.init();

    var entries = [_]Entry{
        .{ .key = 4, .ordinal = 0, .ladder = 1 },
        .{ .key = 1, .ordinal = 1, .ladder = 3 },
        .{ .key = 5, .ordinal = 2, .ladder = 0 },
        .{ .key = 2, .ordinal = 3, .ladder = 2 },
        .{ .key = 4, .ordinal = 4, .ladder = 0 },
        .{ .key = 0, .ordinal = 5, .ladder = 3 },
        .{ .key = 3, .ordinal = 6, .ladder = 1 },
        .{ .key = 2, .ordinal = 7, .ladder = 0 },
        .{ .key = 5, .ordinal = 8, .ladder = 2 },
        .{ .key = 1, .ordinal = 9, .ladder = 1 },
        .{ .key = 6, .ordinal = 10, .ladder = 3 },
        .{ .key = 3, .ordinal = 11, .ladder = 2 },
        .{ .key = 0, .ordinal = 12, .ladder = 0 },
        .{ .key = 4, .ordinal = 13, .ladder = 3 },
    };

    const seed_order = [_]usize{ 10, 0, 5, 12, 3, 8, 1, 6, 13, 2, 9, 4, 11, 7 };
    inline for (seed_order, 0..) |entry_idx, step| {
        if ((step % 5) == 0 or (step % 5) == 2) {
            list_sort.listAdd(&entries[entry_idx].node, &head);
        } else {
            list_sort.listAddTail(&entries[entry_idx].node, &head);
        }
    }

    var mode = SortMode.key_stable;
    list_sort.listSort(&mode, &head, cmpByMode);

    var keys_buf: [entries.len]i32 = undefined;
    var ord_buf: [entries.len]usize = undefined;
    try std.testing.expectEqualSlices(i32, &.{ 0, 0, 1, 1, 2, 2, 3, 3, 4, 4, 4, 5, 5, 6 }, try collectKeys(&head, &keys_buf));
    try std.testing.expectEqualSlices(usize, &.{ 5, 12, 9, 1, 3, 7, 11, 6, 0, 13, 4, 8, 2, 10 }, try collectOrdinals(&head, &ord_buf));

    var ladders = [_]ListHead{ .{}, .{}, .{}, .{} };
    for (&ladders) |*ladder| ladder.init();

    var drain_step: usize = 0;
    while (!list_sort.listEmpty(&head)) : (drain_step += 1) {
        const detached = if ((drain_step % 4) == 1 or (drain_step % 4) == 2) popBack(&head) else popFront(&head);
        try expectDetached(detached);

        const entry = entryFromNode(detached);
        const ladder_idx = (entry.ladder + drain_step * 3) % ladders.len;
        if ((drain_step & 1) == 0) {
            list_sort.listAddTail(detached, &ladders[ladder_idx]);
        } else {
            list_sort.listAdd(detached, &ladders[ladder_idx]);
        }
    }

    try std.testing.expect(list_sort.listEmpty(&head));

    var ladder0_buf: [entries.len]usize = undefined;
    var ladder1_buf: [entries.len]usize = undefined;
    var ladder2_buf: [entries.len]usize = undefined;
    var ladder3_buf: [entries.len]usize = undefined;
    try std.testing.expectEqualSlices(usize, &.{ 6, 1 }, try collectOrdinals(&ladders[0], &ladder0_buf));
    try std.testing.expectEqualSlices(usize, &.{ 7, 8, 12, 9 }, try collectOrdinals(&ladders[1], &ladder1_buf));
    try std.testing.expectEqualSlices(usize, &.{ 13, 10, 2, 4, 3, 11 }, try collectOrdinals(&ladders[2], &ladder2_buf));
    try std.testing.expectEqualSlices(usize, &.{ 5, 0 }, try collectOrdinals(&ladders[3], &ladder3_buf));

    mode = .ladder_asc;
    list_sort.listSort(&mode, &ladders[0], cmpByMode);
    mode = .key_desc;
    list_sort.listSort(&mode, &ladders[1], cmpByMode);
    mode = .ordinal_desc;
    list_sort.listSort(&mode, &ladders[2], cmpByMode);
    mode = .key_asc;
    list_sort.listSort(&mode, &ladders[3], cmpByMode);

    try std.testing.expectEqualSlices(usize, &.{ 6, 1 }, try collectOrdinals(&ladders[0], &ladder0_buf));
    try std.testing.expectEqualSlices(usize, &.{ 8, 7, 9, 12 }, try collectOrdinals(&ladders[1], &ladder1_buf));
    try std.testing.expectEqualSlices(usize, &.{ 13, 11, 10, 4, 3, 2 }, try collectOrdinals(&ladders[2], &ladder2_buf));
    try std.testing.expectEqualSlices(usize, &.{ 5, 0 }, try collectOrdinals(&ladders[3], &ladder3_buf));

    const turnstile_pattern = [_]struct { ladder: usize, back: bool }{
        .{ .ladder = 0, .back = false },
        .{ .ladder = 2, .back = true },
        .{ .ladder = 1, .back = false },
        .{ .ladder = 3, .back = true },
        .{ .ladder = 2, .back = false },
        .{ .ladder = 1, .back = true },
        .{ .ladder = 2, .back = true },
        .{ .ladder = 1, .back = false },
        .{ .ladder = 3, .back = false },
        .{ .ladder = 2, .back = false },
        .{ .ladder = 1, .back = true },
        .{ .ladder = 0, .back = true },
        .{ .ladder = 2, .back = false },
        .{ .ladder = 2, .back = true },
    };

    for (turnstile_pattern, 0..) |slot, step| {
        const detached = if (slot.back) popBack(&ladders[slot.ladder]) else popFront(&ladders[slot.ladder]);
        try expectDetached(detached);
        if ((step % 4) == 0 or (step % 4) == 3) {
            list_sort.listAdd(detached, &head);
        } else {
            list_sort.listAddTail(detached, &head);
        }
    }

    for (&ladders) |*ladder| {
        try std.testing.expect(list_sort.listEmpty(ladder));
    }

    const rebuilt = try collectOrdinals(&head, &ord_buf);
    try std.testing.expectEqualSlices(usize, &.{ 10, 1, 5, 7, 13, 0, 6, 2, 8, 12, 3, 11, 9, 4 }, rebuilt);

    mode = .all_tie;
    list_sort.listSort(&mode, &head, cmpByMode);
    try std.testing.expectEqualSlices(usize, rebuilt, try collectOrdinals(&head, &ord_buf));
    try std.testing.expect(head.next == &entries[rebuilt[0]].node);
    try std.testing.expect(head.prev == &entries[rebuilt[rebuilt.len - 1]].node);
}
