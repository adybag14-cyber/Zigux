const std = @import("std");
const list_sort = @import("list_sort");

const ListHead = list_sort.ListHead;

const Entry = struct {
    key: i32,
    ordinal: usize,
    node: ListHead = .{},
};

const SortMode = enum {
    ascending,
    descending,
    all_ties,
};

const SortContext = struct {
    mode: SortMode,
};

fn compare(priv: ?*anyopaque, a: *const ListHead, b: *const ListHead) i32 {
    const context: *const SortContext = @ptrCast(@alignCast(priv.?));
    const lhs: *const Entry = @fieldParentPtr("node", a);
    const rhs: *const Entry = @fieldParentPtr("node", b);

    if (context.mode == .all_ties or lhs.key == rhs.key) return 0;
    const lhs_before_rhs = lhs.key < rhs.key;
    return switch (context.mode) {
        .ascending => if (lhs_before_rhs) -5 else 7,
        .descending => if (lhs_before_rhs) 7 else -5,
        .all_ties => 0,
    };
}

fn expectTraversal(head: *const ListHead, expected_ordinals: []const usize, entries: []const Entry) !void {
    var actual_ordinals: [20]usize = undefined;
    var actual_keys: [20]i32 = undefined;
    var idx: usize = 0;
    var current = head.next;

    while (current != head) : (current = current.?.next) {
        const entry: *const Entry = @fieldParentPtr("node", current.?);
        actual_ordinals[idx] = entry.ordinal;
        actual_keys[idx] = entry.key;
        try std.testing.expect(current.?.next.?.prev == current.?);
        try std.testing.expect(current.?.prev.?.next == current.?);
        idx += 1;
    }

    try std.testing.expectEqual(expected_ordinals.len, idx);
    try std.testing.expectEqualSlices(usize, expected_ordinals, actual_ordinals[0..idx]);
    for (expected_ordinals, actual_keys[0..idx]) |ordinal, key| {
        try std.testing.expectEqual(entries[ordinal].key, key);
    }
}

fn moveFront(from: *ListHead, to: *ListHead) !void {
    const node = from.next.?;
    try std.testing.expect(node != from);
    list_sort.listDel(node);
    try std.testing.expect(node.next == null);
    try std.testing.expect(node.prev == null);
    list_sort.listAddTail(node, to);
}

fn moveBack(from: *ListHead, to: *ListHead) !void {
    const node = from.prev.?;
    try std.testing.expect(node != from);
    list_sort.listDel(node);
    try std.testing.expect(node.next == null);
    try std.testing.expect(node.prev == null);
    list_sort.listAddTail(node, to);
}

test "list sort preserves pendulum lattice rebuild through all ties" {
    var head: ListHead = .{};
    head.init();
    var upper: ListHead = .{};
    upper.init();
    var lower: ListHead = .{};
    lower.init();

    var entries = [_]Entry{
        .{ .key = 17, .ordinal = 0 },
        .{ .key = -3, .ordinal = 1 },
        .{ .key = 12, .ordinal = 2 },
        .{ .key = 5, .ordinal = 3 },
        .{ .key = -8, .ordinal = 4 },
        .{ .key = 0, .ordinal = 5 },
        .{ .key = 23, .ordinal = 6 },
        .{ .key = 7, .ordinal = 7 },
        .{ .key = -1, .ordinal = 8 },
        .{ .key = 14, .ordinal = 9 },
        .{ .key = 2, .ordinal = 10 },
        .{ .key = 19, .ordinal = 11 },
        .{ .key = -6, .ordinal = 12 },
        .{ .key = 10, .ordinal = 13 },
        .{ .key = 4, .ordinal = 14 },
        .{ .key = 21, .ordinal = 15 },
        .{ .key = -4, .ordinal = 16 },
        .{ .key = 8, .ordinal = 17 },
        .{ .key = 15, .ordinal = 18 },
        .{ .key = 1, .ordinal = 19 },
    };

    for (&entries, 0..) |*entry, idx| {
        if ((idx & 1) == 0) {
            list_sort.listAddTail(&entry.node, &head);
        } else {
            list_sort.listAdd(&entry.node, &head);
        }
    }

    var context = SortContext{ .mode = .ascending };
    list_sort.listSort(&context, &head, compare);
    try expectTraversal(&head, &.{ 4, 12, 16, 1, 8, 5, 19, 10, 14, 3, 7, 17, 13, 2, 9, 18, 0, 11, 15, 6 }, &entries);

    var rank: usize = 0;
    while (!list_sort.listEmpty(&head)) : (rank += 1) {
        const node = head.next.?;
        list_sort.listDel(node);
        try std.testing.expect(node.next == null);
        try std.testing.expect(node.prev == null);

        if ((rank & 1) == 0) {
            list_sort.listAdd(node, &upper);
        } else {
            list_sort.listAddTail(node, &lower);
        }
    }
    try std.testing.expect(list_sort.listEmpty(&head));

    context.mode = .descending;
    list_sort.listSort(&context, &upper, compare);
    try expectTraversal(&upper, &.{ 15, 0, 9, 13, 7, 14, 19, 8, 16, 4 }, &entries);

    context.mode = .ascending;
    list_sort.listSort(&context, &lower, compare);
    try expectTraversal(&lower, &.{ 12, 1, 5, 10, 3, 17, 2, 18, 11, 6 }, &entries);

    while (!list_sort.listEmpty(&upper) or !list_sort.listEmpty(&lower)) {
        if (!list_sort.listEmpty(&upper)) try moveFront(&upper, &head);
        if (!list_sort.listEmpty(&lower)) try moveBack(&lower, &head);
    }

    const pendulum_ordinals = &.{ 15, 6, 0, 11, 9, 18, 13, 2, 7, 17, 14, 3, 19, 10, 8, 5, 16, 1, 4, 12 };
    try expectTraversal(&head, pendulum_ordinals, &entries);

    context.mode = .all_ties;
    list_sort.listSort(&context, &head, compare);
    try expectTraversal(&head, pendulum_ordinals, &entries);
    try std.testing.expect(head.next == &entries[15].node);
    try std.testing.expect(head.prev == &entries[12].node);
}
