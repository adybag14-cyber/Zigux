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
    all_tie,
};

fn entryFromNode(node: *const ListHead) *const Entry {
    return @fieldParentPtr("node", node);
}

fn compare(priv: ?*anyopaque, a: *const ListHead, b: *const ListHead) i32 {
    const mode: *const SortMode = @ptrCast(@alignCast(priv.?));
    const lhs = entryFromNode(a);
    const rhs = entryFromNode(b);

    return switch (mode.*) {
        .key_ascending => order(lhs.key, rhs.key),
        .key_descending => order(rhs.key, lhs.key),
        .ordinal_ascending => orderInt(lhs.ordinal, rhs.ordinal),
        .all_tie => 0,
    };
}

fn order(lhs: i32, rhs: i32) i32 {
    if (lhs < rhs) return -5;
    if (lhs > rhs) return 7;
    return 0;
}

fn orderInt(lhs: usize, rhs: usize) i32 {
    if (lhs < rhs) return -3;
    if (lhs > rhs) return 11;
    return 0;
}

fn popFront(head: *ListHead) *ListHead {
    const node = head.next.?;
    list_sort.listDel(node);
    return node;
}

fn expectDetached(node: *const ListHead) !void {
    try std.testing.expect(node.next == null);
    try std.testing.expect(node.prev == null);
}

fn collectOrdinals(head: *const ListHead, out: []usize) !usize {
    var idx: usize = 0;
    var current = head.next;
    while (current != head) : (current = current.?.next) {
        const node = current.?;
        const entry = entryFromNode(node);
        try std.testing.expect(idx < out.len);
        out[idx] = entry.ordinal;
        try std.testing.expect(node.next.?.prev == node);
        try std.testing.expect(node.prev.?.next == node);
        idx += 1;
    }
    return idx;
}

fn expectOrder(head: *const ListHead, expected: []const usize) !void {
    var actual: [16]usize = undefined;
    const count = try collectOrdinals(head, &actual);
    try std.testing.expectEqualSlices(usize, expected, actual[0..count]);
}

test "list sort supports rank accordion staging and tie replay" {
    var source: ListHead = .{};
    source.init();

    var entries = [_]Entry{
        .{ .key = 9, .ordinal = 0 },
        .{ .key = 2, .ordinal = 1 },
        .{ .key = 7, .ordinal = 2 },
        .{ .key = 2, .ordinal = 3 },
        .{ .key = 5, .ordinal = 4 },
        .{ .key = 8, .ordinal = 5 },
        .{ .key = 3, .ordinal = 6 },
        .{ .key = 5, .ordinal = 7 },
        .{ .key = 1, .ordinal = 8 },
        .{ .key = 6, .ordinal = 9 },
        .{ .key = 4, .ordinal = 10 },
        .{ .key = 7, .ordinal = 11 },
    };

    for (&entries, 0..) |*entry, idx| {
        if (idx % 3 == 0) {
            list_sort.listAdd(&entry.node, &source);
        } else {
            list_sort.listAddTail(&entry.node, &source);
        }
    }

    try expectOrder(&source, &.{ 9, 6, 3, 0, 1, 2, 4, 5, 7, 8, 10, 11 });

    var mode = SortMode.key_ascending;
    list_sort.listSort(&mode, &source, compare);
    try expectOrder(&source, &.{ 8, 3, 1, 6, 10, 4, 7, 9, 2, 11, 5, 0 });

    var stages = [_]ListHead{ .{}, .{}, .{} };
    for (&stages) |*stage| stage.init();

    var rank: usize = 0;
    while (!list_sort.listEmpty(&source)) : (rank += 1) {
        const node = popFront(&source);
        try expectDetached(node);

        switch (rank % 3) {
            0 => list_sort.listAddTail(node, &stages[0]),
            1 => list_sort.listAdd(node, &stages[1]),
            else => if ((rank / 3) % 2 == 0)
                list_sort.listAddTail(node, &stages[2])
            else
                list_sort.listAdd(node, &stages[2]),
        }
    }

    try expectOrder(&stages[0], &.{ 8, 6, 7, 11 });
    try expectOrder(&stages[1], &.{ 5, 9, 10, 3 });
    try expectOrder(&stages[2], &.{ 0, 4, 1, 2 });

    mode = .key_descending;
    list_sort.listSort(&mode, &stages[0], compare);
    try expectOrder(&stages[0], &.{ 11, 7, 6, 8 });

    mode = .ordinal_ascending;
    list_sort.listSort(&mode, &stages[1], compare);
    try expectOrder(&stages[1], &.{ 3, 5, 9, 10 });

    mode = .key_ascending;
    list_sort.listSort(&mode, &stages[2], compare);
    try expectOrder(&stages[2], &.{ 1, 4, 2, 0 });

    const rebuild_stages = [_]usize{ 0, 2, 1, 0, 2, 1, 0, 2, 1, 0, 2, 1 };
    for (rebuild_stages, 0..) |stage_idx, step| {
        const node = popFront(&stages[stage_idx]);
        try expectDetached(node);
        if (step % 2 == 0) {
            list_sort.listAddTail(node, &source);
        } else {
            list_sort.listAdd(node, &source);
        }
    }

    for (&stages) |*stage| try std.testing.expect(list_sort.listEmpty(stage));
    try expectOrder(&source, &.{ 10, 8, 2, 5, 7, 1, 11, 3, 4, 6, 9, 0 });

    mode = .all_tie;
    list_sort.listSort(&mode, &source, compare);
    try expectOrder(&source, &.{ 10, 8, 2, 5, 7, 1, 11, 3, 4, 6, 9, 0 });
    try std.testing.expect(source.next == &entries[10].node);
    try std.testing.expect(source.prev == &entries[0].node);
}
