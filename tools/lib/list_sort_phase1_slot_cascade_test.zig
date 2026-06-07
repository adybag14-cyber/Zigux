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

fn entryOf(node: *const ListHead) *const Entry {
    return @fieldParentPtr("node", node);
}

fn mutableEntryOf(node: *ListHead) *Entry {
    return @fieldParentPtr("node", node);
}

fn cmp(priv: ?*anyopaque, a: *const ListHead, b: *const ListHead) i32 {
    const mode: *const SortMode = @ptrCast(@alignCast(priv.?));
    const lhs = entryOf(a);
    const rhs = entryOf(b);

    return switch (mode.*) {
        .key_asc => compareI32(lhs.key, rhs.key),
        .key_desc => compareI32(rhs.key, lhs.key),
        .ordinal_asc => compareUsize(lhs.ordinal, rhs.ordinal),
        .ordinal_desc => compareUsize(rhs.ordinal, lhs.ordinal),
        .all_ties => 0,
    };
}

fn compareI32(lhs: i32, rhs: i32) i32 {
    if (lhs < rhs) return -1;
    if (lhs > rhs) return 1;
    return 0;
}

fn compareUsize(lhs: usize, rhs: usize) i32 {
    if (lhs < rhs) return -1;
    if (lhs > rhs) return 1;
    return 0;
}

fn popFront(head: *ListHead) !?*Entry {
    if (list_sort.listEmpty(head)) return null;
    const node = head.next.?;
    const entry = mutableEntryOf(node);
    list_sort.listDel(node);
    try std.testing.expect(node.next == null and node.prev == null);
    return entry;
}

fn popBack(head: *ListHead) !?*Entry {
    if (list_sort.listEmpty(head)) return null;
    const node = head.prev.?;
    const entry = mutableEntryOf(node);
    list_sort.listDel(node);
    try std.testing.expect(node.next == null and node.prev == null);
    return entry;
}

fn collectOrdinals(head: *const ListHead, out: []usize) !usize {
    var idx: usize = 0;
    var current = head.next;
    while (current != head) : (current = current.?.next) {
        const entry = entryOf(current.?);
        out[idx] = entry.ordinal;
        try std.testing.expect(current.?.next.?.prev == current.?);
        try std.testing.expect(current.?.prev.?.next == current.?);
        idx += 1;
    }
    return idx;
}

test "list sort survives slot cascade staging and all-ties replay" {
    var head: ListHead = .{};
    head.init();
    var entries = [_]Entry{
        .{ .key = 7, .ordinal = 0 },
        .{ .key = -1, .ordinal = 1 },
        .{ .key = 4, .ordinal = 2 },
        .{ .key = 7, .ordinal = 3 },
        .{ .key = 2, .ordinal = 4 },
        .{ .key = -1, .ordinal = 5 },
        .{ .key = 9, .ordinal = 6 },
        .{ .key = 4, .ordinal = 7 },
        .{ .key = 0, .ordinal = 8 },
        .{ .key = 2, .ordinal = 9 },
        .{ .key = 9, .ordinal = 10 },
        .{ .key = 5, .ordinal = 11 },
    };

    for (&entries, 0..) |*entry, index| {
        if ((index & 1) == 0) {
            list_sort.listAddTail(&entry.node, &head);
        } else {
            list_sort.listAdd(&entry.node, &head);
        }
    }

    var mode = SortMode.key_asc;
    list_sort.listSort(&mode, &head, cmp);

    var sorted_ordinals: [entries.len]usize = undefined;
    const sorted_len = try collectOrdinals(&head, &sorted_ordinals);
    try std.testing.expectEqualSlices(
        usize,
        &.{ 5, 1, 8, 9, 4, 7, 2, 11, 3, 0, 6, 10 },
        sorted_ordinals[0..sorted_len],
    );

    var slots = [_]ListHead{ .{}, .{}, .{}, .{} };
    for (&slots) |*slot| slot.init();

    var rank: usize = 0;
    while (try popFront(&head)) |entry| : (rank += 1) {
        const slot_index = rank % slots.len;
        if ((rank & 1) == 0) {
            list_sort.listAddTail(&entry.node, &slots[slot_index]);
        } else {
            list_sort.listAdd(&entry.node, &slots[slot_index]);
        }
    }
    try std.testing.expect(list_sort.listEmpty(&head));

    const slot_modes = [_]SortMode{ .key_desc, .ordinal_asc, .key_asc, .ordinal_desc };
    for (&slots, slot_modes) |*slot, slot_mode| {
        mode = slot_mode;
        list_sort.listSort(&mode, slot, cmp);
    }

    var slot0_ordinals: [3]usize = undefined;
    var slot1_ordinals: [3]usize = undefined;
    var slot2_ordinals: [3]usize = undefined;
    var slot3_ordinals: [3]usize = undefined;
    try std.testing.expectEqualSlices(usize, &.{ 3, 4, 5 }, slot0_ordinals[0..try collectOrdinals(&slots[0], &slot0_ordinals)]);
    try std.testing.expectEqualSlices(usize, &.{ 0, 1, 7 }, slot1_ordinals[0..try collectOrdinals(&slots[1], &slot1_ordinals)]);
    try std.testing.expectEqualSlices(usize, &.{ 8, 2, 6 }, slot2_ordinals[0..try collectOrdinals(&slots[2], &slot2_ordinals)]);
    try std.testing.expectEqualSlices(usize, &.{ 11, 10, 9 }, slot3_ordinals[0..try collectOrdinals(&slots[3], &slot3_ordinals)]);

    const cascade = [_]struct { slot: usize, from_back: bool }{
        .{ .slot = 0, .from_back = false },
        .{ .slot = 3, .from_back = true },
        .{ .slot = 1, .from_back = false },
        .{ .slot = 2, .from_back = true },
        .{ .slot = 0, .from_back = true },
        .{ .slot = 1, .from_back = true },
        .{ .slot = 2, .from_back = false },
        .{ .slot = 3, .from_back = false },
    };

    while (true) {
        var moved = false;
        for (cascade) |step| {
            const maybe_entry = try (if (step.from_back)
                popBack(&slots[step.slot])
            else
                popFront(&slots[step.slot]));
            if (maybe_entry) |entry| {
                list_sort.listAddTail(&entry.node, &head);
                moved = true;
            }
        }
        if (!moved) break;
    }
    for (&slots) |*slot| try std.testing.expect(list_sort.listEmpty(slot));

    var rebuilt_ordinals: [entries.len]usize = undefined;
    const rebuilt_len = try collectOrdinals(&head, &rebuilt_ordinals);
    try std.testing.expectEqualSlices(
        usize,
        &.{ 3, 9, 0, 6, 5, 7, 8, 11, 4, 10, 1, 2 },
        rebuilt_ordinals[0..rebuilt_len],
    );
    try std.testing.expect(head.next == &entries[3].node);
    try std.testing.expect(head.prev == &entries[2].node);

    mode = .all_ties;
    list_sort.listSort(&mode, &head, cmp);

    var tied_ordinals: [entries.len]usize = undefined;
    const tied_len = try collectOrdinals(&head, &tied_ordinals);
    try std.testing.expectEqualSlices(usize, rebuilt_ordinals[0..rebuilt_len], tied_ordinals[0..tied_len]);
    try std.testing.expect(head.next == &entries[3].node);
    try std.testing.expect(head.prev == &entries[2].node);
}
