const std = @import("std");
const list_sort = @import("list_sort");

const Entry = struct {
    key: i32,
    ordinal: usize,
    node: list_sort.ListHead = .{},
};

const SortMode = enum {
    key_ascending,
    key_descending,
    ordinal_descending,
    all_ties,
};

fn compare(priv: ?*anyopaque, a: *const list_sort.ListHead, b: *const list_sort.ListHead) i32 {
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
        .ordinal_descending => {
            if (lhs.ordinal > rhs.ordinal) return -13;
            if (lhs.ordinal < rhs.ordinal) return 17;
            return 0;
        },
        .all_ties => return 0,
    }
}

fn detachFront(head: *list_sort.ListHead) !*list_sort.ListHead {
    const node = head.next.?;
    list_sort.listDel(node);
    try std.testing.expect(node.next == null);
    try std.testing.expect(node.prev == null);
    return node;
}

fn detachBack(head: *list_sort.ListHead) !*list_sort.ListHead {
    const node = head.prev.?;
    list_sort.listDel(node);
    try std.testing.expect(node.next == null);
    try std.testing.expect(node.prev == null);
    return node;
}

fn collectOrdinals(head: *const list_sort.ListHead, out: []usize) !usize {
    var idx: usize = 0;
    var current = head.next;
    while (current != head) : (current = current.?.next) {
        const entry: *const Entry = @fieldParentPtr("node", current.?);
        out[idx] = entry.ordinal;
        try std.testing.expect(current.?.next.?.prev == current.?);
        try std.testing.expect(current.?.prev.?.next == current.?);
        idx += 1;
    }
    return idx;
}

test "list sort ring fold rebuild preserves staged traversal through all ties" {
    var entries = [_]Entry{
        .{ .key = 8, .ordinal = 0 },
        .{ .key = 1, .ordinal = 1 },
        .{ .key = 6, .ordinal = 2 },
        .{ .key = 3, .ordinal = 3 },
        .{ .key = 10, .ordinal = 4 },
        .{ .key = 5, .ordinal = 5 },
        .{ .key = 2, .ordinal = 6 },
        .{ .key = 9, .ordinal = 7 },
        .{ .key = 4, .ordinal = 8 },
        .{ .key = 7, .ordinal = 9 },
        .{ .key = 0, .ordinal = 10 },
        .{ .key = 11, .ordinal = 11 },
        .{ .key = 6, .ordinal = 12 },
        .{ .key = 3, .ordinal = 13 },
        .{ .key = 8, .ordinal = 14 },
        .{ .key = 1, .ordinal = 15 },
    };

    var head: list_sort.ListHead = .{};
    head.init();
    for (&entries) |*entry| list_sort.listAddTail(&entry.node, &head);

    var mode = SortMode.key_ascending;
    list_sort.listSort(&mode, &head, compare);

    var sorted_ordinals: [entries.len]usize = undefined;
    const sorted_count = try collectOrdinals(&head, &sorted_ordinals);
    try std.testing.expectEqualSlices(usize, &.{ 10, 1, 15, 6, 3, 13, 8, 5, 2, 12, 9, 0, 14, 7, 4, 11 }, sorted_ordinals[0..sorted_count]);

    var stages: [4]list_sort.ListHead = undefined;
    for (&stages) |*stage| stage.init();

    var rank: usize = 0;
    while (!list_sort.listEmpty(&head)) : (rank += 1) {
        const node = try detachFront(&head);
        list_sort.listAddTail(node, &stages[rank % stages.len]);
    }

    mode = .key_descending;
    list_sort.listSort(&mode, &stages[0], compare);
    mode = .key_ascending;
    list_sort.listSort(&mode, &stages[1], compare);
    mode = .ordinal_descending;
    list_sort.listSort(&mode, &stages[2], compare);
    mode = .all_ties;
    list_sort.listSort(&mode, &stages[3], compare);

    while (!list_sort.listEmpty(&stages[0])) {
        list_sort.listAddTail(try detachBack(&stages[0]), &head);
        list_sort.listAddTail(try detachFront(&stages[1]), &head);
        list_sort.listAddTail(try detachBack(&stages[2]), &head);
        list_sort.listAddTail(try detachFront(&stages[3]), &head);
    }

    var folded_ordinals: [entries.len]usize = undefined;
    const folded_count = try collectOrdinals(&head, &folded_ordinals);
    try std.testing.expectEqualSlices(usize, &.{ 10, 1, 4, 6, 3, 13, 8, 5, 2, 12, 9, 0, 14, 7, 15, 11 }, folded_ordinals[0..folded_count]);

    list_sort.listSort(&mode, &head, compare);

    var final_ordinals: [entries.len]usize = undefined;
    const final_count = try collectOrdinals(&head, &final_ordinals);
    try std.testing.expectEqualSlices(usize, folded_ordinals[0..folded_count], final_ordinals[0..final_count]);
    try std.testing.expect(head.next == &entries[10].node);
    try std.testing.expect(head.prev == &entries[11].node);
}
