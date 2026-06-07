const std = @import("std");
const list_sort = @import("list_sort");

const ListHead = list_sort.ListHead;

const Entry = struct {
    key: i32,
    ordinal: usize,
    node: ListHead = .{},
};

const SortMode = enum {
    key_ascending,
    key_descending,
    ordinal_ascending,
    ordinal_descending,
    all_ties,
};

fn compare(priv: ?*anyopaque, a: *const ListHead, b: *const ListHead) i32 {
    const mode: *const SortMode = @ptrCast(@alignCast(priv.?));
    const lhs: *const Entry = @fieldParentPtr("node", a);
    const rhs: *const Entry = @fieldParentPtr("node", b);

    switch (mode.*) {
        .key_ascending => {
            if (lhs.key < rhs.key) return -3;
            if (lhs.key > rhs.key) return 5;
            return 0;
        },
        .key_descending => {
            if (lhs.key > rhs.key) return -7;
            if (lhs.key < rhs.key) return 11;
            return 0;
        },
        .ordinal_ascending => {
            if (lhs.ordinal < rhs.ordinal) return -13;
            if (lhs.ordinal > rhs.ordinal) return 17;
            return 0;
        },
        .ordinal_descending => {
            if (lhs.ordinal > rhs.ordinal) return -19;
            if (lhs.ordinal < rhs.ordinal) return 23;
            return 0;
        },
        .all_ties => return 0,
    }
}

fn entryFromNode(node: *const ListHead) *const Entry {
    return @fieldParentPtr("node", node);
}

fn collectOrdinals(head: *const ListHead, out: []usize) !usize {
    var count: usize = 0;
    var current = head.next;
    while (current != head) : (current = current.?.next) {
        try std.testing.expect(count < out.len);
        const entry = entryFromNode(current.?);
        out[count] = entry.ordinal;
        try std.testing.expect(current.?.next.?.prev == current.?);
        try std.testing.expect(current.?.prev.?.next == current.?);
        count += 1;
    }
    return count;
}

fn collectKeys(head: *const ListHead, out: []i32) !usize {
    var count: usize = 0;
    var current = head.next;
    while (current != head) : (current = current.?.next) {
        try std.testing.expect(count < out.len);
        const entry = entryFromNode(current.?);
        out[count] = entry.key;
        try std.testing.expect(current.?.next.?.prev == current.?);
        try std.testing.expect(current.?.prev.?.next == current.?);
        count += 1;
    }
    return count;
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

test "list sort grid shuttle preserves staged lifecycle and all-ties order" {
    var head: ListHead = .{};
    head.init();

    var entries = [_]Entry{
        .{ .key = 5, .ordinal = 0 },
        .{ .key = 2, .ordinal = 1 },
        .{ .key = 8, .ordinal = 2 },
        .{ .key = 2, .ordinal = 3 },
        .{ .key = 6, .ordinal = 4 },
        .{ .key = 1, .ordinal = 5 },
        .{ .key = 7, .ordinal = 6 },
        .{ .key = 3, .ordinal = 7 },
        .{ .key = 6, .ordinal = 8 },
        .{ .key = 4, .ordinal = 9 },
        .{ .key = 1, .ordinal = 10 },
        .{ .key = 5, .ordinal = 11 },
    };

    for (&entries, 0..) |*entry, index| {
        if (index % 3 == 0) {
            list_sort.listAdd(&entry.node, &head);
        } else {
            list_sort.listAddTail(&entry.node, &head);
        }
    }

    var mode = SortMode.key_ascending;
    list_sort.listSort(&mode, &head, compare);

    var sorted_keys: [entries.len]i32 = undefined;
    var sorted_ordinals: [entries.len]usize = undefined;
    const sorted_count = try collectKeys(&head, &sorted_keys);
    _ = try collectOrdinals(&head, &sorted_ordinals);
    try std.testing.expectEqual(entries.len, sorted_count);
    try std.testing.expectEqualSlices(i32, &.{ 1, 1, 2, 2, 3, 4, 5, 5, 6, 6, 7, 8 }, sorted_keys[0..sorted_count]);
    try std.testing.expectEqualSlices(usize, &.{ 5, 10, 3, 1, 7, 9, 0, 11, 4, 8, 6, 2 }, sorted_ordinals[0..sorted_count]);

    var grid: [9]ListHead = undefined;
    for (&grid) |*cell| cell.init();

    var rank: usize = 0;
    while (!list_sort.listEmpty(&head)) : (rank += 1) {
        const node = popFront(&head);
        try std.testing.expect(node.next == null);
        try std.testing.expect(node.prev == null);

        const cell_index = (rank % 3) * 3 + (rank / 3) % 3;
        if ((rank & 1) == 0) {
            list_sort.listAddTail(node, &grid[cell_index]);
        } else {
            list_sort.listAdd(node, &grid[cell_index]);
        }
    }
    try std.testing.expectEqual(entries.len, rank);
    try std.testing.expect(list_sort.listEmpty(&head));

    const cell_modes = [_]SortMode{
        .key_descending,
        .ordinal_ascending,
        .ordinal_descending,
        .key_ascending,
        .ordinal_descending,
        .key_descending,
        .ordinal_ascending,
        .key_ascending,
        .ordinal_descending,
    };
    for (&grid, cell_modes) |*cell, cell_mode| {
        mode = cell_mode;
        list_sort.listSort(&mode, cell, compare);
    }

    const shuttle = [_]struct { cell: usize, back: bool }{
        .{ .cell = 0, .back = false },
        .{ .cell = 4, .back = true },
        .{ .cell = 8, .back = false },
        .{ .cell = 2, .back = true },
        .{ .cell = 6, .back = false },
        .{ .cell = 1, .back = true },
        .{ .cell = 5, .back = false },
        .{ .cell = 3, .back = true },
        .{ .cell = 7, .back = false },
    };

    var rebuilt: usize = 0;
    while (rebuilt < entries.len) {
        for (shuttle) |step| {
            if (list_sort.listEmpty(&grid[step.cell])) continue;
            const node = if (step.back) popBack(&grid[step.cell]) else popFront(&grid[step.cell]);
            try std.testing.expect(node.next == null);
            try std.testing.expect(node.prev == null);

            if ((rebuilt & 1) == 0) {
                list_sort.listAddTail(node, &head);
            } else {
                list_sort.listAdd(node, &head);
            }
            rebuilt += 1;
        }
    }
    try std.testing.expectEqual(entries.len, rebuilt);
    for (&grid) |*cell| try std.testing.expect(list_sort.listEmpty(cell));

    var rebuilt_ordinals: [entries.len]usize = undefined;
    const rebuilt_count = try collectOrdinals(&head, &rebuilt_ordinals);
    try std.testing.expectEqual(entries.len, rebuilt_count);
    try std.testing.expect(!std.mem.eql(usize, sorted_ordinals[0..sorted_count], rebuilt_ordinals[0..rebuilt_count]));

    mode = .all_ties;
    list_sort.listSort(&mode, &head, compare);

    var tied_ordinals: [entries.len]usize = undefined;
    const tied_count = try collectOrdinals(&head, &tied_ordinals);
    try std.testing.expectEqualSlices(usize, rebuilt_ordinals[0..rebuilt_count], tied_ordinals[0..tied_count]);
    try std.testing.expect(head.next == &entries[tied_ordinals[0]].node);
    try std.testing.expect(head.prev == &entries[tied_ordinals[tied_count - 1]].node);
}
