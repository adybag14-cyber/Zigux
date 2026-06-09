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
        .key_ascending => if (lhs_before_rhs) -17 else 19,
        .key_descending => if (lhs_before_rhs) 19 else -17,
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

test "list sort preserves stability through alternating rebuild lifecycle" {
    var head: ListHead = .{};
    head.init();
    var left: ListHead = .{};
    left.init();
    var right: ListHead = .{};
    right.init();

    var entries = [_]Entry{
        .{ .key = 3, .ordinal = 0 },
        .{ .key = 1, .ordinal = 1 },
        .{ .key = 4, .ordinal = 2 },
        .{ .key = 1, .ordinal = 3 },
        .{ .key = 2, .ordinal = 4 },
        .{ .key = 4, .ordinal = 5 },
        .{ .key = 3, .ordinal = 6 },
        .{ .key = 2, .ordinal = 7 },
        .{ .key = 1, .ordinal = 8 },
        .{ .key = 3, .ordinal = 9 },
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
    try expectOrder(&head, &.{ 3, 1, 8, 7, 4, 9, 0, 6, 5, 2 });

    var rank: usize = 0;
    while (!list_sort.listEmpty(&head)) : (rank += 1) {
        const node = try detachFront(&head);
        if ((rank & 1) == 0) {
            list_sort.listAddTail(node, &left);
        } else {
            list_sort.listAddTail(node, &right);
        }
    }

    mode = .key_descending;
    list_sort.listSort(&mode, &left, compareEntries);
    try expectOrder(&left, &.{ 5, 0, 4, 3, 8 });

    mode = .key_ascending;
    list_sort.listSort(&mode, &right, compareEntries);
    try expectOrder(&right, &.{ 1, 7, 9, 6, 2 });

    while (!list_sort.listEmpty(&left) or !list_sort.listEmpty(&right)) {
        if (!list_sort.listEmpty(&left)) {
            list_sort.listAddTail(try detachBack(&left), &head);
        }
        if (!list_sort.listEmpty(&right)) {
            list_sort.listAddTail(try detachFront(&right), &head);
        }
    }
    try expectOrder(&head, &.{ 8, 1, 3, 7, 4, 9, 0, 6, 5, 2 });

    mode = .all_equal;
    list_sort.listSort(&mode, &head, compareEntries);
    try expectOrder(&head, &.{ 8, 1, 3, 7, 4, 9, 0, 6, 5, 2 });

    mode = .key_descending;
    list_sort.listSort(&mode, &head, compareEntries);
    try expectOrder(&head, &.{ 5, 2, 9, 0, 6, 7, 4, 8, 1, 3 });
}
