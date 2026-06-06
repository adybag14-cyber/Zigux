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
    all_equal,
};

fn compare(priv: ?*anyopaque, a: *const list_sort.ListHead, b: *const list_sort.ListHead) i32 {
    const mode: *const SortMode = @ptrCast(@alignCast(priv.?));
    const lhs: *const Entry = @fieldParentPtr("node", a);
    const rhs: *const Entry = @fieldParentPtr("node", b);

    return switch (mode.*) {
        .key_ascending => if (lhs.key == rhs.key) 0 else if (lhs.key < rhs.key) -3 else 3,
        .key_descending => if (lhs.key == rhs.key) 0 else if (lhs.key > rhs.key) -5 else 5,
        .all_equal => 0,
    };
}

fn expectDetached(node: *const list_sort.ListHead) !void {
    try std.testing.expect(node.next == null);
    try std.testing.expect(node.prev == null);
}

fn popFront(head: *list_sort.ListHead) *list_sort.ListHead {
    const node = head.next.?;
    list_sort.listDel(node);
    return node;
}

fn popBack(head: *list_sort.ListHead) *list_sort.ListHead {
    const node = head.prev.?;
    list_sort.listDel(node);
    return node;
}

fn expectOrder(head: *const list_sort.ListHead, expected: []const usize) !void {
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

test "phase1 list_sort helper-local braid preserves all-ties stability after staged reorders" {
    var head: list_sort.ListHead = .{};
    head.init();
    var left: list_sort.ListHead = .{};
    left.init();
    var right: list_sort.ListHead = .{};
    right.init();

    var entries = [_]Entry{
        .{ .key = 7, .ordinal = 0 },
        .{ .key = 2, .ordinal = 1 },
        .{ .key = 6, .ordinal = 2 },
        .{ .key = 2, .ordinal = 3 },
        .{ .key = 9, .ordinal = 4 },
        .{ .key = 4, .ordinal = 5 },
        .{ .key = 8, .ordinal = 6 },
        .{ .key = 1, .ordinal = 7 },
        .{ .key = 5, .ordinal = 8 },
        .{ .key = 3, .ordinal = 9 },
    };
    for (&entries) |*entry| {
        list_sort.listAddTail(&entry.node, &head);
    }

    var mode = SortMode.key_ascending;
    list_sort.listSort(&mode, &head, compare);
    try expectOrder(&head, &.{ 7, 1, 3, 9, 5, 8, 2, 0, 6, 4 });

    var rank: usize = 0;
    while (!list_sort.listEmpty(&head)) : (rank += 1) {
        const node = popFront(&head);
        try expectDetached(node);
        if ((rank & 1) == 0) {
            list_sort.listAddTail(node, &left);
        } else {
            list_sort.listAddTail(node, &right);
        }
    }
    try expectOrder(&left, &.{ 7, 3, 5, 2, 6 });
    try expectOrder(&right, &.{ 1, 9, 8, 0, 4 });

    mode = .key_descending;
    list_sort.listSort(&mode, &left, compare);
    try expectOrder(&left, &.{ 6, 2, 5, 3, 7 });

    mode = .key_ascending;
    list_sort.listSort(&mode, &right, compare);
    try expectOrder(&right, &.{ 1, 9, 8, 0, 4 });

    while (!list_sort.listEmpty(&left) or !list_sort.listEmpty(&right)) {
        if (!list_sort.listEmpty(&right)) {
            const node = popBack(&right);
            try expectDetached(node);
            list_sort.listAddTail(node, &head);
        }
        if (!list_sort.listEmpty(&left)) {
            const node = popFront(&left);
            try expectDetached(node);
            list_sort.listAddTail(node, &head);
        }
    }
    try expectOrder(&head, &.{ 4, 6, 0, 2, 8, 5, 9, 3, 1, 7 });

    mode = .all_equal;
    list_sort.listSort(&mode, &head, compare);
    try expectOrder(&head, &.{ 4, 6, 0, 2, 8, 5, 9, 3, 1, 7 });

    try std.testing.expect(head.next == &entries[4].node);
    try std.testing.expect(head.prev == &entries[7].node);
}
