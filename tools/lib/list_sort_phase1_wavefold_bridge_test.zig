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
    key_asc,
    key_desc,
    ordinal_asc,
    lane_asc,
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
        .lane_asc => compare(lhs.lane, rhs.lane, lhs.ordinal, rhs.ordinal, true),
        .all_tie => 0,
    };
}

fn compare(primary_lhs: anytype, primary_rhs: @TypeOf(primary_lhs), ordinal_lhs: usize, ordinal_rhs: usize, non_unit: bool) i32 {
    if (primary_lhs < primary_rhs) return if (non_unit) -9 else -1;
    if (primary_lhs > primary_rhs) return if (non_unit) 11 else 1;
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

test "phase1 list_sort wavefold bridge lifecycle" {
    var head: ListHead = .{};
    head.init();

    var entries = [_]Entry{
        .{ .key = 5, .ordinal = 0, .lane = 2 },
        .{ .key = 1, .ordinal = 1, .lane = 0 },
        .{ .key = 4, .ordinal = 2, .lane = 1 },
        .{ .key = 1, .ordinal = 3, .lane = 2 },
        .{ .key = 3, .ordinal = 4, .lane = 0 },
        .{ .key = 5, .ordinal = 5, .lane = 1 },
        .{ .key = 2, .ordinal = 6, .lane = 2 },
        .{ .key = 4, .ordinal = 7, .lane = 0 },
        .{ .key = 2, .ordinal = 8, .lane = 1 },
        .{ .key = 6, .ordinal = 9, .lane = 2 },
        .{ .key = 3, .ordinal = 10, .lane = 1 },
        .{ .key = 6, .ordinal = 11, .lane = 0 },
    };

    const seed_order = [_]usize{ 9, 0, 6, 3, 10, 1, 7, 4, 11, 2, 8, 5 };
    inline for (seed_order, 0..) |entry_idx, step| {
        if ((step & 1) == 0) {
            list_sort.listAddTail(&entries[entry_idx].node, &head);
        } else {
            list_sort.listAdd(&entries[entry_idx].node, &head);
        }
    }

    var mode = SortMode.key_asc;
    list_sort.listSort(&mode, &head, cmpByMode);

    var keys_buf: [entries.len]i32 = undefined;
    var ord_buf: [entries.len]usize = undefined;
    try std.testing.expectEqualSlices(i32, &.{ 1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6 }, try collectKeys(&head, &keys_buf));
    try std.testing.expectEqualSlices(usize, &.{ 1, 3, 6, 8, 4, 10, 2, 7, 0, 5, 9, 11 }, try collectOrdinals(&head, &ord_buf));

    var crests = [_]ListHead{ .{}, .{}, .{} };
    for (&crests) |*crest| crest.init();

    var drain_step: usize = 0;
    while (!list_sort.listEmpty(&head)) : (drain_step += 1) {
        const detached = if ((drain_step & 1) == 0) popFront(&head) else popBack(&head);
        try expectDetached(detached);

        const entry = entryFromNode(detached);
        const lane = (entry.lane + drain_step) % crests.len;
        if ((drain_step & 2) == 0) {
            list_sort.listAddTail(detached, &crests[lane]);
        } else {
            list_sort.listAdd(detached, &crests[lane]);
        }
    }

    var lane0_buf: [entries.len]usize = undefined;
    var lane1_buf: [entries.len]usize = undefined;
    var lane2_buf: [entries.len]usize = undefined;
    try std.testing.expectEqualSlices(usize, &.{ 2, 0, 1, 6, 5, 7 }, try collectOrdinals(&crests[0], &lane0_buf));
    try std.testing.expectEqualSlices(usize, &.{ 8, 3, 11 }, try collectOrdinals(&crests[1], &lane1_buf));
    try std.testing.expectEqualSlices(usize, &.{ 10, 9, 4 }, try collectOrdinals(&crests[2], &lane2_buf));

    mode = .key_desc;
    list_sort.listSort(&mode, &crests[0], cmpByMode);
    mode = .ordinal_asc;
    list_sort.listSort(&mode, &crests[1], cmpByMode);
    mode = .lane_asc;
    list_sort.listSort(&mode, &crests[2], cmpByMode);

    try std.testing.expectEqualSlices(usize, &.{ 0, 5, 2, 7, 6, 1 }, try collectOrdinals(&crests[0], &lane0_buf));
    try std.testing.expectEqualSlices(usize, &.{ 3, 8, 11 }, try collectOrdinals(&crests[1], &lane1_buf));
    try std.testing.expectEqualSlices(usize, &.{ 4, 10, 9 }, try collectOrdinals(&crests[2], &lane2_buf));

    const bridge_pattern = [_]struct { crest: usize, back: bool }{
        .{ .crest = 0, .back = false },
        .{ .crest = 1, .back = true },
        .{ .crest = 2, .back = false },
        .{ .crest = 0, .back = true },
        .{ .crest = 1, .back = false },
        .{ .crest = 2, .back = true },
        .{ .crest = 0, .back = false },
        .{ .crest = 1, .back = true },
        .{ .crest = 2, .back = false },
        .{ .crest = 0, .back = true },
        .{ .crest = 0, .back = false },
        .{ .crest = 0, .back = true },
    };

    for (bridge_pattern) |slot| {
        const detached = if (slot.back) popBack(&crests[slot.crest]) else popFront(&crests[slot.crest]);
        try expectDetached(detached);
        if (entryFromNode(detached).ordinal % 2 == 0) {
            list_sort.listAdd(detached, &head);
        } else {
            list_sort.listAddTail(detached, &head);
        }
    }

    const bridged = try collectOrdinals(&head, &ord_buf);
    try std.testing.expectEqualSlices(usize, &.{ 2, 6, 10, 8, 4, 0, 11, 1, 3, 9, 5, 7 }, bridged);

    mode = .all_tie;
    list_sort.listSort(&mode, &head, cmpByMode);
    try std.testing.expectEqualSlices(usize, bridged, try collectOrdinals(&head, &ord_buf));
    try std.testing.expect(head.next == &entries[2].node);
    try std.testing.expect(head.prev == &entries[7].node);
}
