const std = @import("std");
const list_sort = @import("list_sort");

const ListHead = list_sort.ListHead;

const Entry = struct {
    key: i32,
    ordinal: usize,
    rail: usize,
    node: ListHead = .{},
};

const SortMode = enum {
    key_asc,
    key_desc,
    ordinal_asc,
    rail_desc,
    all_tie,
};

fn cmpByMode(priv: ?*anyopaque, a: *const ListHead, b: *const ListHead) i32 {
    const mode: *const SortMode = @ptrCast(@alignCast(priv.?));
    const lhs: *const Entry = @fieldParentPtr("node", a);
    const rhs: *const Entry = @fieldParentPtr("node", b);

    return switch (mode.*) {
        .key_asc => compare(lhs.key, rhs.key, lhs.ordinal, rhs.ordinal, false),
        .key_desc => compare(rhs.key, lhs.key, lhs.ordinal, rhs.ordinal, false),
        .ordinal_asc => compareInt(lhs.ordinal, rhs.ordinal),
        .rail_desc => compare(rhs.rail, lhs.rail, lhs.ordinal, rhs.ordinal, true),
        .all_tie => 0,
    };
}

fn compare(primary_lhs: anytype, primary_rhs: @TypeOf(primary_lhs), ordinal_lhs: usize, ordinal_rhs: usize, non_unit: bool) i32 {
    if (primary_lhs < primary_rhs) return if (non_unit) -13 else -1;
    if (primary_lhs > primary_rhs) return if (non_unit) 17 else 1;
    return compareInt(ordinal_lhs, ordinal_rhs);
}

fn compareInt(lhs: usize, rhs: usize) i32 {
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

test "phase1 list_sort counterflow braid lifecycle" {
    var head: ListHead = .{};
    head.init();

    var entries = [_]Entry{
        .{ .key = 4, .ordinal = 0, .rail = 0 },
        .{ .key = 2, .ordinal = 1, .rail = 1 },
        .{ .key = 5, .ordinal = 2, .rail = 2 },
        .{ .key = 1, .ordinal = 3, .rail = 3 },
        .{ .key = 3, .ordinal = 4, .rail = 0 },
        .{ .key = 2, .ordinal = 5, .rail = 2 },
        .{ .key = 6, .ordinal = 6, .rail = 1 },
        .{ .key = 1, .ordinal = 7, .rail = 0 },
        .{ .key = 4, .ordinal = 8, .rail = 3 },
        .{ .key = 3, .ordinal = 9, .rail = 2 },
    };

    const seed_order = [_]usize{ 6, 0, 3, 8, 1, 9, 4, 2, 7, 5 };
    inline for (seed_order, 0..) |entry_idx, step| {
        if ((step % 3) == 1) {
            list_sort.listAdd(&entries[entry_idx].node, &head);
        } else {
            list_sort.listAddTail(&entries[entry_idx].node, &head);
        }
    }

    var mode = SortMode.key_asc;
    list_sort.listSort(&mode, &head, cmpByMode);

    var keys_buf: [entries.len]i32 = undefined;
    var ord_buf: [entries.len]usize = undefined;
    try std.testing.expectEqualSlices(i32, &.{ 1, 1, 2, 2, 3, 3, 4, 4, 5, 6 }, try collectKeys(&head, &keys_buf));
    try std.testing.expectEqualSlices(usize, &.{ 3, 7, 1, 5, 4, 9, 0, 8, 2, 6 }, try collectOrdinals(&head, &ord_buf));

    var rails = [_]ListHead{ .{}, .{}, .{}, .{} };
    for (&rails) |*rail| rail.init();

    var drain_step: usize = 0;
    while (!list_sort.listEmpty(&head)) : (drain_step += 1) {
        const detached = if ((drain_step & 1) == 0) popFront(&head) else popBack(&head);
        try expectDetached(detached);

        const entry = entryFromNode(detached);
        const rail = (entry.rail + drain_step + (drain_step / 2)) % rails.len;
        if ((drain_step & 2) == 0) {
            list_sort.listAddTail(detached, &rails[rail]);
        } else {
            list_sort.listAdd(detached, &rails[rail]);
        }
    }

    var rail0_buf: [entries.len]usize = undefined;
    var rail1_buf: [entries.len]usize = undefined;
    var rail2_buf: [entries.len]usize = undefined;
    var rail3_buf: [entries.len]usize = undefined;
    try std.testing.expectEqualSlices(usize, &.{4}, try collectOrdinals(&rails[0], &rail0_buf));
    try std.testing.expectEqualSlices(usize, &.{}, try collectOrdinals(&rails[1], &rail1_buf));
    try std.testing.expectEqualSlices(usize, &.{ 0, 2, 6, 8 }, try collectOrdinals(&rails[2], &rail2_buf));
    try std.testing.expectEqualSlices(usize, &.{ 5, 7, 3, 1, 9 }, try collectOrdinals(&rails[3], &rail3_buf));

    mode = .key_desc;
    list_sort.listSort(&mode, &rails[0], cmpByMode);
    mode = .ordinal_asc;
    list_sort.listSort(&mode, &rails[1], cmpByMode);
    mode = .rail_desc;
    list_sort.listSort(&mode, &rails[2], cmpByMode);
    mode = .key_asc;
    list_sort.listSort(&mode, &rails[3], cmpByMode);

    try std.testing.expectEqualSlices(usize, &.{4}, try collectOrdinals(&rails[0], &rail0_buf));
    try std.testing.expectEqualSlices(usize, &.{}, try collectOrdinals(&rails[1], &rail1_buf));
    try std.testing.expectEqualSlices(usize, &.{ 8, 2, 6, 0 }, try collectOrdinals(&rails[2], &rail2_buf));
    try std.testing.expectEqualSlices(usize, &.{ 3, 7, 1, 5, 9 }, try collectOrdinals(&rails[3], &rail3_buf));

    const braid_pattern = [_]struct { rail: usize, back: bool }{
        .{ .rail = 3, .back = false },
        .{ .rail = 2, .back = true },
        .{ .rail = 3, .back = true },
        .{ .rail = 2, .back = false },
        .{ .rail = 3, .back = false },
        .{ .rail = 2, .back = true },
        .{ .rail = 3, .back = true },
        .{ .rail = 2, .back = false },
        .{ .rail = 3, .back = false },
        .{ .rail = 0, .back = false },
    };

    for (braid_pattern, 0..) |slot, step| {
        const detached = if (slot.back) popBack(&rails[slot.rail]) else popFront(&rails[slot.rail]);
        try expectDetached(detached);
        if ((step & 1) == 0) {
            list_sort.listAdd(detached, &head);
        } else {
            list_sort.listAddTail(detached, &head);
        }
    }

    const braided = try collectOrdinals(&head, &ord_buf);
    try std.testing.expectEqualSlices(usize, &.{ 1, 5, 7, 9, 3, 0, 8, 6, 2, 4 }, braided);

    mode = .all_tie;
    list_sort.listSort(&mode, &head, cmpByMode);
    try std.testing.expectEqualSlices(usize, braided, try collectOrdinals(&head, &ord_buf));
    try std.testing.expect(head.next == &entries[1].node);
    try std.testing.expect(head.prev == &entries[4].node);
}
