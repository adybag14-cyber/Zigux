const std = @import("std");
const list_sort = @import("list_sort");

const ListHead = list_sort.ListHead;

const Entry = struct {
    key: i32,
    ordinal: usize,
    spoke: usize,
    node: ListHead = .{},
};

const SortMode = enum {
    key_asc,
    key_desc,
    spoke_asc,
    ordinal_desc,
    all_tie,
};

fn cmpByMode(priv: ?*anyopaque, a: *const ListHead, b: *const ListHead) i32 {
    const mode: *const SortMode = @ptrCast(@alignCast(priv.?));
    const lhs: *const Entry = @fieldParentPtr("node", a);
    const rhs: *const Entry = @fieldParentPtr("node", b);

    return switch (mode.*) {
        .key_asc => compare(lhs.key, rhs.key, lhs.ordinal, rhs.ordinal),
        .key_desc => compare(rhs.key, lhs.key, lhs.ordinal, rhs.ordinal),
        .spoke_asc => compare(lhs.spoke, rhs.spoke, lhs.ordinal, rhs.ordinal),
        .ordinal_desc => compareInt(rhs.ordinal, lhs.ordinal),
        .all_tie => 0,
    };
}

fn compare(primary_lhs: anytype, primary_rhs: @TypeOf(primary_lhs), ordinal_lhs: usize, ordinal_rhs: usize) i32 {
    if (primary_lhs < primary_rhs) return -11;
    if (primary_lhs > primary_rhs) return 13;
    return compareInt(ordinal_lhs, ordinal_rhs);
}

fn compareInt(lhs: usize, rhs: usize) i32 {
    if (lhs < rhs) return -3;
    if (lhs > rhs) return 5;
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

test "phase1 list_sort spoke ferry lifecycle" {
    var head: ListHead = .{};
    head.init();

    var entries = [_]Entry{
        .{ .key = 5, .ordinal = 0, .spoke = 1 },
        .{ .key = 1, .ordinal = 1, .spoke = 4 },
        .{ .key = 4, .ordinal = 2, .spoke = 0 },
        .{ .key = 2, .ordinal = 3, .spoke = 3 },
        .{ .key = 3, .ordinal = 4, .spoke = 1 },
        .{ .key = 1, .ordinal = 5, .spoke = 2 },
        .{ .key = 5, .ordinal = 6, .spoke = 4 },
        .{ .key = 2, .ordinal = 7, .spoke = 0 },
        .{ .key = 4, .ordinal = 8, .spoke = 3 },
        .{ .key = 3, .ordinal = 9, .spoke = 2 },
        .{ .key = 6, .ordinal = 10, .spoke = 1 },
        .{ .key = 0, .ordinal = 11, .spoke = 3 },
    };

    const seed_order = [_]usize{ 10, 0, 5, 8, 1, 11, 4, 7, 2, 9, 6, 3 };
    inline for (seed_order, 0..) |entry_idx, step| {
        if ((step % 4) == 0 or (step % 4) == 3) {
            list_sort.listAdd(&entries[entry_idx].node, &head);
        } else {
            list_sort.listAddTail(&entries[entry_idx].node, &head);
        }
    }

    var mode = SortMode.key_asc;
    list_sort.listSort(&mode, &head, cmpByMode);

    var keys_buf: [entries.len]i32 = undefined;
    var ord_buf: [entries.len]usize = undefined;
    try std.testing.expectEqualSlices(i32, &.{ 0, 1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6 }, try collectKeys(&head, &keys_buf));
    try std.testing.expectEqualSlices(usize, &.{ 11, 1, 5, 3, 7, 4, 9, 2, 8, 0, 6, 10 }, try collectOrdinals(&head, &ord_buf));

    var spokes = [_]ListHead{ .{}, .{}, .{}, .{}, .{} };
    for (&spokes) |*spoke| spoke.init();

    var drain_step: usize = 0;
    while (!list_sort.listEmpty(&head)) : (drain_step += 1) {
        const detached = if ((drain_step % 3) == 2) popBack(&head) else popFront(&head);
        try expectDetached(detached);

        const entry = entryFromNode(detached);
        const spoke = (entry.spoke * 2 + drain_step) % spokes.len;
        if ((drain_step & 1) == 0) {
            list_sort.listAddTail(detached, &spokes[spoke]);
        } else {
            list_sort.listAdd(detached, &spokes[spoke]);
        }
    }

    var spoke0_buf: [entries.len]usize = undefined;
    var spoke1_buf: [entries.len]usize = undefined;
    var spoke2_buf: [entries.len]usize = undefined;
    var spoke3_buf: [entries.len]usize = undefined;
    var spoke4_buf: [entries.len]usize = undefined;
    try std.testing.expectEqualSlices(usize, &.{ 3, 0, 2 }, try collectOrdinals(&spokes[0], &spoke0_buf));
    try std.testing.expectEqualSlices(usize, &.{ 11, 7 }, try collectOrdinals(&spokes[1], &spoke1_buf));
    try std.testing.expectEqualSlices(usize, &.{ 8, 5 }, try collectOrdinals(&spokes[2], &spoke2_buf));
    try std.testing.expectEqualSlices(usize, &.{ 9, 6 }, try collectOrdinals(&spokes[3], &spoke3_buf));
    try std.testing.expectEqualSlices(usize, &.{ 4, 1, 10 }, try collectOrdinals(&spokes[4], &spoke4_buf));

    mode = .spoke_asc;
    list_sort.listSort(&mode, &spokes[0], cmpByMode);
    mode = .key_desc;
    list_sort.listSort(&mode, &spokes[1], cmpByMode);
    mode = .ordinal_desc;
    list_sort.listSort(&mode, &spokes[2], cmpByMode);
    mode = .key_asc;
    list_sort.listSort(&mode, &spokes[3], cmpByMode);
    mode = .spoke_asc;
    list_sort.listSort(&mode, &spokes[4], cmpByMode);

    try std.testing.expectEqualSlices(usize, &.{ 2, 0, 3 }, try collectOrdinals(&spokes[0], &spoke0_buf));
    try std.testing.expectEqualSlices(usize, &.{ 7, 11 }, try collectOrdinals(&spokes[1], &spoke1_buf));
    try std.testing.expectEqualSlices(usize, &.{ 8, 5 }, try collectOrdinals(&spokes[2], &spoke2_buf));
    try std.testing.expectEqualSlices(usize, &.{ 9, 6 }, try collectOrdinals(&spokes[3], &spoke3_buf));
    try std.testing.expectEqualSlices(usize, &.{ 4, 10, 1 }, try collectOrdinals(&spokes[4], &spoke4_buf));

    const ferry_pattern = [_]struct { spoke: usize, back: bool }{
        .{ .spoke = 0, .back = false },
        .{ .spoke = 4, .back = true },
        .{ .spoke = 1, .back = false },
        .{ .spoke = 3, .back = true },
        .{ .spoke = 2, .back = false },
        .{ .spoke = 0, .back = true },
        .{ .spoke = 4, .back = false },
        .{ .spoke = 1, .back = true },
        .{ .spoke = 3, .back = false },
        .{ .spoke = 2, .back = true },
        .{ .spoke = 0, .back = false },
        .{ .spoke = 4, .back = false },
    };

    for (ferry_pattern, 0..) |slot, step| {
        const detached = if (slot.back) popBack(&spokes[slot.spoke]) else popFront(&spokes[slot.spoke]);
        try expectDetached(detached);
        if ((step % 3) == 1) {
            list_sort.listAdd(detached, &head);
        } else {
            list_sort.listAddTail(detached, &head);
        }
    }

    const ferried = try collectOrdinals(&head, &ord_buf);
    try std.testing.expectEqualSlices(usize, &.{ 0, 11, 8, 1, 2, 7, 6, 3, 4, 9, 5, 10 }, ferried);

    mode = .all_tie;
    list_sort.listSort(&mode, &head, cmpByMode);
    try std.testing.expectEqualSlices(usize, ferried, try collectOrdinals(&head, &ord_buf));
    try std.testing.expect(head.next == &entries[ferried[0]].node);
    try std.testing.expect(head.prev == &entries[ferried[ferried.len - 1]].node);
}
