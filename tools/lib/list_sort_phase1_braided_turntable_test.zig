const std = @import("std");
const list_sort = @import("list_sort");

const ListHead = list_sort.ListHead;

const Entry = struct {
    key: i32,
    ordinal: usize,
    lane: usize,
    node: ListHead = .{},
};

const SortMode = enum {
    key_stable,
    key_asc,
    key_desc,
    lane_asc,
    lane_desc,
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
        .lane_asc => compareWithOrdinal(lhs.lane, rhs.lane, lhs.ordinal, rhs.ordinal),
        .lane_desc => compareWithOrdinal(rhs.lane, lhs.lane, lhs.ordinal, rhs.ordinal),
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
    if (lhs < rhs) return -9;
    if (lhs > rhs) return 11;
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

test "phase1 list_sort braided turntable lifecycle" {
    var head: ListHead = .{};
    head.init();

    var entries = [_]Entry{
        .{ .key = 3, .ordinal = 0, .lane = 2 },
        .{ .key = 1, .ordinal = 1, .lane = 0 },
        .{ .key = 4, .ordinal = 2, .lane = 3 },
        .{ .key = 2, .ordinal = 3, .lane = 1 },
        .{ .key = 3, .ordinal = 4, .lane = 0 },
        .{ .key = 0, .ordinal = 5, .lane = 2 },
        .{ .key = 5, .ordinal = 6, .lane = 1 },
        .{ .key = 2, .ordinal = 7, .lane = 3 },
        .{ .key = 1, .ordinal = 8, .lane = 2 },
        .{ .key = 4, .ordinal = 9, .lane = 0 },
        .{ .key = 0, .ordinal = 10, .lane = 1 },
        .{ .key = 5, .ordinal = 11, .lane = 2 },
        .{ .key = 3, .ordinal = 12, .lane = 3 },
        .{ .key = 1, .ordinal = 13, .lane = 1 },
        .{ .key = 4, .ordinal = 14, .lane = 2 },
    };

    const seed_order = [_]usize{ 12, 2, 9, 0, 14, 5, 8, 1, 11, 4, 13, 6, 10, 3, 7 };
    inline for (seed_order, 0..) |entry_idx, step| {
        if ((step % 6) == 0 or (step % 6) == 3 or (step % 6) == 5) {
            list_sort.listAdd(&entries[entry_idx].node, &head);
        } else {
            list_sort.listAddTail(&entries[entry_idx].node, &head);
        }
    }

    var mode = SortMode.key_stable;
    list_sort.listSort(&mode, &head, cmpByMode);

    var keys_buf: [entries.len]i32 = undefined;
    var ord_buf: [entries.len]usize = undefined;
    try std.testing.expectEqualSlices(i32, &.{ 0, 0, 1, 1, 1, 2, 2, 3, 3, 3, 4, 4, 4, 5, 5 }, try collectKeys(&head, &keys_buf));
    try std.testing.expectEqualSlices(usize, &.{ 10, 5, 8, 1, 13, 3, 7, 4, 0, 12, 2, 9, 14, 6, 11 }, try collectOrdinals(&head, &ord_buf));

    var turntables = [_]ListHead{ .{}, .{}, .{}, .{}, .{} };
    for (&turntables) |*table| table.init();

    var drain_step: usize = 0;
    while (!list_sort.listEmpty(&head)) : (drain_step += 1) {
        const detached = if ((drain_step % 5) == 1 or (drain_step % 5) == 4) popBack(&head) else popFront(&head);
        try expectDetached(detached);

        const entry = entryFromNode(detached);
        const table_idx = (entry.lane * 2 + drain_step) % turntables.len;
        if ((drain_step % 3) == 0) {
            list_sort.listAdd(detached, &turntables[table_idx]);
        } else {
            list_sort.listAddTail(detached, &turntables[table_idx]);
        }
    }

    try std.testing.expect(list_sort.listEmpty(&head));

    var table0_buf: [entries.len]usize = undefined;
    var table1_buf: [entries.len]usize = undefined;
    var table2_buf: [entries.len]usize = undefined;
    var table3_buf: [entries.len]usize = undefined;
    var table4_buf: [entries.len]usize = undefined;
    try std.testing.expectEqualSlices(usize, &.{ 14, 11, 1, 3, 12 }, try collectOrdinals(&turntables[0], &table0_buf));
    try std.testing.expectEqualSlices(usize, &.{ 5, 6, 7 }, try collectOrdinals(&turntables[1], &table1_buf));
    try std.testing.expectEqualSlices(usize, &.{ 4, 8, 10, 2, 0 }, try collectOrdinals(&turntables[2], &table2_buf));
    try std.testing.expect(list_sort.listEmpty(&turntables[3]));
    try std.testing.expectEqualSlices(usize, &.{ 9, 13 }, try collectOrdinals(&turntables[4], &table4_buf));

    mode = .lane_asc;
    list_sort.listSort(&mode, &turntables[0], cmpByMode);
    mode = .key_desc;
    list_sort.listSort(&mode, &turntables[1], cmpByMode);
    mode = .ordinal_desc;
    list_sort.listSort(&mode, &turntables[2], cmpByMode);
    mode = .key_asc;
    list_sort.listSort(&mode, &turntables[3], cmpByMode);
    mode = .lane_desc;
    list_sort.listSort(&mode, &turntables[4], cmpByMode);

    try std.testing.expectEqualSlices(usize, &.{ 1, 3, 11, 14, 12 }, try collectOrdinals(&turntables[0], &table0_buf));
    try std.testing.expectEqualSlices(usize, &.{ 6, 7, 5 }, try collectOrdinals(&turntables[1], &table1_buf));
    try std.testing.expectEqualSlices(usize, &.{ 10, 8, 4, 2, 0 }, try collectOrdinals(&turntables[2], &table2_buf));
    try std.testing.expectEqualSlices(usize, &.{}, try collectOrdinals(&turntables[3], &table3_buf));
    try std.testing.expectEqualSlices(usize, &.{ 13, 9 }, try collectOrdinals(&turntables[4], &table4_buf));

    const turntable_pattern = [_]struct { table: usize, back: bool }{
        .{ .table = 0, .back = false },
        .{ .table = 2, .back = true },
        .{ .table = 1, .back = false },
        .{ .table = 4, .back = true },
        .{ .table = 2, .back = false },
        .{ .table = 0, .back = true },
        .{ .table = 1, .back = true },
        .{ .table = 2, .back = false },
        .{ .table = 4, .back = false },
        .{ .table = 0, .back = false },
        .{ .table = 2, .back = true },
        .{ .table = 0, .back = true },
        .{ .table = 1, .back = false },
        .{ .table = 2, .back = false },
        .{ .table = 0, .back = false },
    };

    for (turntable_pattern, 0..) |slot, step| {
        const detached = if (slot.back) popBack(&turntables[slot.table]) else popFront(&turntables[slot.table]);
        try expectDetached(detached);
        if ((step % 5) == 0 or (step % 5) == 2) {
            list_sort.listAdd(detached, &head);
        } else {
            list_sort.listAddTail(detached, &head);
        }
    }

    for (&turntables) |*table| {
        try std.testing.expect(list_sort.listEmpty(table));
    }

    const rebuilt = try collectOrdinals(&head, &ord_buf);
    try std.testing.expectEqualSlices(usize, &.{ 7, 2, 8, 12, 6, 1, 0, 9, 10, 5, 13, 3, 14, 4, 11 }, rebuilt);
    try std.testing.expect(head.next == &entries[rebuilt[0]].node);
    try std.testing.expect(head.prev == &entries[rebuilt[rebuilt.len - 1]].node);

    mode = .all_tie;
    list_sort.listSort(&mode, &head, cmpByMode);
    try std.testing.expectEqualSlices(usize, rebuilt, try collectOrdinals(&head, &ord_buf));
    try std.testing.expect(head.next == &entries[rebuilt[0]].node);
    try std.testing.expect(head.prev == &entries[rebuilt[rebuilt.len - 1]].node);
}
