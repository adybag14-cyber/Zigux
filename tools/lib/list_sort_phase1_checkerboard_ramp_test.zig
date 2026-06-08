const std = @import("std");
const list_sort = @import("list_sort");

const ListHead = list_sort.ListHead;

const Entry = struct {
    key: i32,
    ordinal: usize,
    rank: usize,
    node: ListHead = .{},
};

const SortMode = enum {
    key_ascending,
    key_descending,
    ordinal_ascending,
    rank_then_key,
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
        .rank_then_key => rankThenKey(lhs, rhs),
        .all_tie => 0,
    };
}

fn order(lhs: i32, rhs: i32) i32 {
    if (lhs < rhs) return -13;
    if (lhs > rhs) return 17;
    return 0;
}

fn orderInt(lhs: usize, rhs: usize) i32 {
    if (lhs < rhs) return -7;
    if (lhs > rhs) return 19;
    return 0;
}

fn rankThenKey(lhs: *const Entry, rhs: *const Entry) i32 {
    const rank_order = orderInt(lhs.rank, rhs.rank);
    if (rank_order != 0) return rank_order;
    return order(lhs.key, rhs.key);
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
    var actual: [20]usize = undefined;
    const count = try collectOrdinals(head, &actual);
    try std.testing.expectEqualSlices(usize, expected, actual[0..count]);
}

test "list sort supports checkerboard ramp staging and tie replay" {
    var source: ListHead = .{};
    source.init();

    var entries = [_]Entry{
        .{ .key = 10, .ordinal = 0, .rank = 3 },
        .{ .key = 4, .ordinal = 1, .rank = 0 },
        .{ .key = 8, .ordinal = 2, .rank = 2 },
        .{ .key = 4, .ordinal = 3, .rank = 1 },
        .{ .key = 7, .ordinal = 4, .rank = 3 },
        .{ .key = 2, .ordinal = 5, .rank = 2 },
        .{ .key = 9, .ordinal = 6, .rank = 0 },
        .{ .key = 2, .ordinal = 7, .rank = 1 },
        .{ .key = 6, .ordinal = 8, .rank = 2 },
        .{ .key = 5, .ordinal = 9, .rank = 0 },
        .{ .key = 1, .ordinal = 10, .rank = 3 },
        .{ .key = 6, .ordinal = 11, .rank = 1 },
        .{ .key = 3, .ordinal = 12, .rank = 0 },
        .{ .key = 8, .ordinal = 13, .rank = 1 },
        .{ .key = 5, .ordinal = 14, .rank = 2 },
        .{ .key = 1, .ordinal = 15, .rank = 0 },
    };

    for (&entries, 0..) |*entry, idx| {
        if (idx % 4 == 0 or idx % 4 == 3) {
            list_sort.listAdd(&entry.node, &source);
        } else {
            list_sort.listAddTail(&entry.node, &source);
        }
    }

    try expectOrder(&source, &.{ 15, 12, 11, 8, 7, 4, 3, 0, 1, 2, 5, 6, 9, 10, 13, 14 });

    var mode = SortMode.key_ascending;
    list_sort.listSort(&mode, &source, compare);
    try expectOrder(&source, &.{ 15, 10, 7, 5, 12, 3, 1, 9, 14, 11, 8, 4, 2, 13, 6, 0 });

    var boards = [_]ListHead{ .{}, .{}, .{}, .{} };
    for (&boards) |*board| board.init();

    var position: usize = 0;
    while (!list_sort.listEmpty(&source)) : (position += 1) {
        const node = popFront(&source);
        try expectDetached(node);

        const entry = entryFromNode(node);
        const board_idx = (position + entry.rank) % boards.len;
        if (((position / boards.len) + board_idx) % 2 == 0) {
            list_sort.listAdd(node, &boards[board_idx]);
        } else {
            list_sort.listAddTail(node, &boards[board_idx]);
        }
    }

    try expectOrder(&boards[0], &.{ 8, 10, 15, 12 });
    try expectOrder(&boards[1], &.{5});
    try expectOrder(&boards[2], &.{ 4, 11, 14, 3, 1, 2, 13, 6, 0 });
    try expectOrder(&boards[3], &.{ 9, 7 });

    mode = .key_descending;
    list_sort.listSort(&mode, &boards[0], compare);
    try expectOrder(&boards[0], &.{ 8, 12, 10, 15 });

    mode = .ordinal_ascending;
    list_sort.listSort(&mode, &boards[1], compare);
    try expectOrder(&boards[1], &.{5});

    mode = .rank_then_key;
    list_sort.listSort(&mode, &boards[2], compare);
    try expectOrder(&boards[2], &.{ 1, 6, 3, 11, 13, 14, 2, 4, 0 });

    mode = .key_ascending;
    list_sort.listSort(&mode, &boards[3], compare);
    try expectOrder(&boards[3], &.{ 7, 9 });

    const rebuild_boards = [_]usize{ 0, 1, 2, 3, 3, 2, 0, 0, 2, 2, 0, 2, 2, 2, 2, 2 };
    for (rebuild_boards, 0..) |board_idx, step| {
        const node = popFront(&boards[board_idx]);
        try expectDetached(node);
        if (step % 3 == 1) {
            list_sort.listAdd(node, &source);
        } else {
            list_sort.listAddTail(node, &source);
        }
    }

    for (&boards) |*board| try std.testing.expect(list_sort.listEmpty(board));
    try expectOrder(&source, &.{ 2, 15, 10, 9, 5, 8, 1, 7, 6, 12, 3, 11, 13, 14, 4, 0 });

    mode = .all_tie;
    list_sort.listSort(&mode, &source, compare);
    try expectOrder(&source, &.{ 2, 15, 10, 9, 5, 8, 1, 7, 6, 12, 3, 11, 13, 14, 4, 0 });
    try std.testing.expect(source.next == &entries[2].node);
    try std.testing.expect(source.prev == &entries[0].node);
}
