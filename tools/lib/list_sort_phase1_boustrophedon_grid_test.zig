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
    all_equal,
};

fn compareEntries(priv: ?*anyopaque, a: *const ListHead, b: *const ListHead) i32 {
    const mode: *const SortMode = @ptrCast(@alignCast(priv.?));
    const lhs: *const Entry = @fieldParentPtr("node", a);
    const rhs: *const Entry = @fieldParentPtr("node", b);

    if (mode.* == .all_equal or lhs.key == rhs.key) return 0;

    const lhs_before_rhs = lhs.key < rhs.key;
    return switch (mode.*) {
        .key_ascending => if (lhs_before_rhs) -23 else 29,
        .key_descending => if (lhs_before_rhs) 29 else -23,
        .all_equal => unreachable,
    };
}

fn expectOrder(head: *ListHead, expected: []const usize) !void {
    var idx: usize = 0;
    var current = head.next;
    while (current != head) : (current = current.?.next) {
        const entry: *const Entry = @fieldParentPtr("node", current.?);
        try std.testing.expectEqual(expected[idx], entry.ordinal);
        try std.testing.expect(current.?.next.?.prev == current.?);
        try std.testing.expect(current.?.prev.?.next == current.?);
        idx += 1;
    }
    try std.testing.expectEqual(expected.len, idx);
}

fn detachFront(from: *ListHead) !*ListHead {
    const node = from.next.?;
    list_sort.listDel(node);
    try std.testing.expect(node.next == null);
    try std.testing.expect(node.prev == null);
    return node;
}

fn detachBack(from: *ListHead) !*ListHead {
    const node = from.prev.?;
    list_sort.listDel(node);
    try std.testing.expect(node.next == null);
    try std.testing.expect(node.prev == null);
    return node;
}

test "list sort preserves boustrophedon grid rebuild stability" {
    var head: ListHead = .{};
    head.init();
    var rows = [_]ListHead{.{}} ** 4;
    for (&rows) |*row| row.init();

    var entries = [_]Entry{
        .{ .key = 5, .ordinal = 0 },
        .{ .key = 2, .ordinal = 1 },
        .{ .key = 4, .ordinal = 2 },
        .{ .key = 1, .ordinal = 3 },
        .{ .key = 3, .ordinal = 4 },
        .{ .key = 5, .ordinal = 5 },
        .{ .key = 0, .ordinal = 6 },
        .{ .key = 2, .ordinal = 7 },
        .{ .key = 4, .ordinal = 8 },
        .{ .key = 1, .ordinal = 9 },
        .{ .key = 3, .ordinal = 10 },
        .{ .key = 0, .ordinal = 11 },
    };

    for (&entries) |*entry| {
        if ((entry.ordinal & 1) == 0) {
            list_sort.listAddTail(&entry.node, &head);
        } else {
            list_sort.listAdd(&entry.node, &head);
        }
    }

    var mode = SortMode.key_ascending;
    list_sort.listSort(&mode, &head, compareEntries);
    try expectOrder(&head, &.{ 11, 6, 9, 3, 7, 1, 4, 10, 2, 8, 5, 0 });

    var rank: usize = 0;
    while (!list_sort.listEmpty(&head)) : (rank += 1) {
        const row_index = rank % rows.len;
        list_sort.listAddTail(try detachFront(&head), &rows[row_index]);
    }
    try std.testing.expectEqual(@as(usize, entries.len), rank);
    try std.testing.expect(list_sort.listEmpty(&head));

    mode = .key_ascending;
    list_sort.listSort(&mode, &rows[0], compareEntries);
    try expectOrder(&rows[0], &.{ 11, 7, 2 });

    mode = .key_descending;
    list_sort.listSort(&mode, &rows[1], compareEntries);
    try expectOrder(&rows[1], &.{ 8, 1, 6 });

    mode = .key_ascending;
    list_sort.listSort(&mode, &rows[2], compareEntries);
    try expectOrder(&rows[2], &.{ 9, 4, 5 });

    mode = .key_descending;
    list_sort.listSort(&mode, &rows[3], compareEntries);
    try expectOrder(&rows[3], &.{ 0, 10, 3 });

    for (&rows, 0..) |*row, row_index| {
        while (!list_sort.listEmpty(row)) {
            const node = if ((row_index & 1) == 0)
                try detachFront(row)
            else
                try detachBack(row);
            list_sort.listAddTail(node, &head);
        }
    }
    try expectOrder(&head, &.{ 11, 7, 2, 6, 1, 8, 9, 4, 5, 3, 10, 0 });

    mode = .all_equal;
    list_sort.listSort(&mode, &head, compareEntries);
    try expectOrder(&head, &.{ 11, 7, 2, 6, 1, 8, 9, 4, 5, 3, 10, 0 });

    mode = .key_descending;
    list_sort.listSort(&mode, &head, compareEntries);
    try expectOrder(&head, &.{ 5, 0, 2, 8, 4, 10, 7, 1, 9, 3, 11, 6 });

    try std.testing.expect(head.next == &entries[5].node);
    try std.testing.expect(head.prev == &entries[6].node);
}
