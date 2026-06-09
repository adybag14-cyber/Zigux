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
    all_equal,
};

fn compareEntries(priv: ?*anyopaque, a: *const ListHead, b: *const ListHead) i32 {
    const mode: *const SortMode = @ptrCast(@alignCast(priv.?));
    const lhs: *const Entry = @fieldParentPtr("node", a);
    const rhs: *const Entry = @fieldParentPtr("node", b);

    return switch (mode.*) {
        .all_equal => 0,
        .key_ascending => compareScalar(lhs.key, rhs.key, -31, 37),
        .key_descending => compareScalar(lhs.key, rhs.key, 37, -31),
        .ordinal_ascending => compareScalar(lhs.ordinal, rhs.ordinal, -43, 47),
        .ordinal_descending => compareScalar(lhs.ordinal, rhs.ordinal, 47, -43),
    };
}

fn compareScalar(lhs: anytype, rhs: @TypeOf(lhs), less_value: i32, greater_value: i32) i32 {
    if (lhs < rhs) return less_value;
    if (lhs > rhs) return greater_value;
    return 0;
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

test "list sort preserves zipper switchback rebuild stability" {
    var head: ListHead = .{};
    head.init();
    var lanes = [_]ListHead{.{}} ** 6;
    for (&lanes) |*lane| lane.init();

    var entries = [_]Entry{
        .{ .key = 4, .ordinal = 0 },
        .{ .key = 1, .ordinal = 1 },
        .{ .key = 3, .ordinal = 2 },
        .{ .key = 0, .ordinal = 3 },
        .{ .key = 2, .ordinal = 4 },
        .{ .key = 4, .ordinal = 5 },
        .{ .key = 1, .ordinal = 6 },
        .{ .key = 3, .ordinal = 7 },
        .{ .key = 2, .ordinal = 8 },
        .{ .key = 5, .ordinal = 9 },
        .{ .key = 0, .ordinal = 10 },
        .{ .key = 5, .ordinal = 11 },
        .{ .key = 1, .ordinal = 12 },
        .{ .key = 4, .ordinal = 13 },
    };

    for (&entries) |*entry| {
        if (@mod(entry.ordinal, 3) == 1) {
            list_sort.listAdd(&entry.node, &head);
        } else {
            list_sort.listAddTail(&entry.node, &head);
        }
    }

    var mode = SortMode.key_ascending;
    list_sort.listSort(&mode, &head, compareEntries);
    try expectOrder(&head, &.{ 10, 3, 1, 6, 12, 4, 8, 7, 2, 13, 0, 5, 9, 11 });

    var rank: usize = 0;
    while (!list_sort.listEmpty(&head)) : (rank += 1) {
        const lane_index = switch (@mod(rank / 3, 2)) {
            0 => rank % 3,
            else => 5 - (rank % 3),
        };
        list_sort.listAddTail(try detachFront(&head), &lanes[lane_index]);
    }
    try std.testing.expectEqual(@as(usize, entries.len), rank);
    try std.testing.expect(list_sort.listEmpty(&head));

    mode = .key_descending;
    list_sort.listSort(&mode, &lanes[0], compareEntries);
    try expectOrder(&lanes[0], &.{ 9, 8, 10 });

    mode = .ordinal_descending;
    list_sort.listSort(&mode, &lanes[1], compareEntries);
    try expectOrder(&lanes[1], &.{ 11, 7, 3 });

    mode = .key_ascending;
    list_sort.listSort(&mode, &lanes[2], compareEntries);
    try expectOrder(&lanes[2], &.{ 1, 2 });

    mode = .ordinal_ascending;
    list_sort.listSort(&mode, &lanes[3], compareEntries);
    try expectOrder(&lanes[3], &.{ 4, 5 });

    mode = .key_descending;
    list_sort.listSort(&mode, &lanes[4], compareEntries);
    try expectOrder(&lanes[4], &.{ 0, 12 });

    mode = .key_ascending;
    list_sort.listSort(&mode, &lanes[5], compareEntries);
    try expectOrder(&lanes[5], &.{ 6, 13 });

    const zipper_order = [_]usize{ 0, 5, 1, 4, 2, 3 };
    for (zipper_order, 0..) |lane_index, order_index| {
        while (!list_sort.listEmpty(&lanes[lane_index])) {
            const node = if ((order_index & 1) == 0)
                try detachFront(&lanes[lane_index])
            else
                try detachBack(&lanes[lane_index]);
            list_sort.listAddTail(node, &head);
        }
    }
    try expectOrder(&head, &.{ 9, 8, 10, 13, 6, 11, 7, 3, 12, 0, 1, 2, 5, 4 });

    mode = .all_equal;
    list_sort.listSort(&mode, &head, compareEntries);
    try expectOrder(&head, &.{ 9, 8, 10, 13, 6, 11, 7, 3, 12, 0, 1, 2, 5, 4 });

    mode = .key_descending;
    list_sort.listSort(&mode, &head, compareEntries);
    try expectOrder(&head, &.{ 9, 11, 13, 0, 5, 7, 2, 8, 4, 6, 12, 1, 10, 3 });

    try std.testing.expect(head.next == &entries[9].node);
    try std.testing.expect(head.prev == &entries[3].node);
}
