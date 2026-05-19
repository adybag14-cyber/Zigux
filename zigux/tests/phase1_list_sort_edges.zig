const std = @import("std");
const list_sort = @import("list_sort");

const Entry = struct {
    key: i32,
    ordinal: usize,
    node: list_sort.ListHead = .{},
};

fn appendEntries(head: *list_sort.ListHead, entries: []Entry) void {
    for (entries) |*entry| {
        list_sort.listAddTail(&entry.node, head);
    }
}

fn expectOrder(
    head: *const list_sort.ListHead,
    expected_keys: []const i32,
    expected_ordinals: []const usize,
) !void {
    var keys: [32]i32 = undefined;
    var ordinals: [32]usize = undefined;
    var idx: usize = 0;
    var current = head.next;
    while (current != head) : (current = current.?.next) {
        const entry: *const Entry = @fieldParentPtr("node", current.?);
        keys[idx] = entry.key;
        ordinals[idx] = entry.ordinal;
        try std.testing.expect(current.?.next.?.prev == current.?);
        try std.testing.expect(current.?.prev.?.next == current.?);
        idx += 1;
    }

    try std.testing.expectEqual(expected_keys.len, idx);
    try std.testing.expectEqualSlices(i32, expected_keys, keys[0..idx]);
    try std.testing.expectEqualSlices(usize, expected_ordinals, ordinals[0..idx]);
}

test "phase1 list_sort edges keep add tail delete and singleton routes circular" {
    var head: list_sort.ListHead = .{};
    head.init();
    try std.testing.expect(list_sort.listEmpty(&head));

    var first = Entry{ .key = 7, .ordinal = 0 };
    var second = Entry{ .key = 4, .ordinal = 1 };
    list_sort.listAdd(&first.node, &head);
    try std.testing.expect(!list_sort.listEmpty(&head));
    try std.testing.expect(head.next == &first.node);
    try std.testing.expect(head.prev == &first.node);

    list_sort.listAddTail(&second.node, &head);
    try std.testing.expect(head.next == &first.node);
    try std.testing.expect(head.prev == &second.node);
    try std.testing.expect(first.node.next == &second.node);
    try std.testing.expect(second.node.prev == &first.node);

    const cmp = struct {
        fn less(_: ?*anyopaque, a: *const list_sort.ListHead, b: *const list_sort.ListHead) i32 {
            const lhs: *const Entry = @fieldParentPtr("node", a);
            const rhs: *const Entry = @fieldParentPtr("node", b);
            if (lhs.key < rhs.key) return -1;
            if (lhs.key > rhs.key) return 1;
            return 0;
        }
    }.less;

    list_sort.listSort(null, &head, cmp);
    try expectOrder(&head, &.{ 4, 7 }, &.{ 1, 0 });

    list_sort.listDel(&second.node);
    try std.testing.expect(head.next == &first.node);
    try std.testing.expect(head.prev == &first.node);
    try std.testing.expect(second.node.next == null);
    try std.testing.expect(second.node.prev == null);

    list_sort.listDel(&first.node);
    try std.testing.expect(list_sort.listEmpty(&head));
    try std.testing.expect(first.node.next == null);
    try std.testing.expect(first.node.prev == null);
}

test "phase1 list_sort edges preserve stable duplicate order across parity buckets" {
    const cmp = struct {
        fn less(_: ?*anyopaque, a: *const list_sort.ListHead, b: *const list_sort.ListHead) i32 {
            const lhs: *const Entry = @fieldParentPtr("node", a);
            const rhs: *const Entry = @fieldParentPtr("node", b);
            const lhs_is_odd = @mod(lhs.key, 2) != 0;
            const rhs_is_odd = @mod(rhs.key, 2) != 0;
            if (lhs_is_odd == rhs_is_odd) return 0;
            return if (lhs_is_odd) -1 else 1;
        }
    }.less;

    var head: list_sort.ListHead = .{};
    head.init();
    var entries = [_]Entry{
        .{ .key = 4, .ordinal = 0 },
        .{ .key = 1, .ordinal = 1 },
        .{ .key = 6, .ordinal = 2 },
        .{ .key = 3, .ordinal = 3 },
        .{ .key = 2, .ordinal = 4 },
        .{ .key = 5, .ordinal = 5 },
        .{ .key = 8, .ordinal = 6 },
        .{ .key = 7, .ordinal = 7 },
    };
    appendEntries(&head, &entries);

    list_sort.listSort(null, &head, cmp);

    try expectOrder(
        &head,
        &.{ 1, 3, 5, 7, 4, 6, 2, 8 },
        &.{ 1, 3, 5, 7, 0, 2, 4, 6 },
    );
    try std.testing.expect(head.next == &entries[1].node);
    try std.testing.expect(head.prev == &entries[6].node);
}

test "phase1 list_sort edges reuse context across repeated reordering" {
    const SortMode = enum { ascending, descending };

    const cmp = struct {
        fn less(priv: ?*anyopaque, a: *const list_sort.ListHead, b: *const list_sort.ListHead) i32 {
            const mode: *const SortMode = @ptrCast(@alignCast(priv.?));
            const lhs: *const Entry = @fieldParentPtr("node", a);
            const rhs: *const Entry = @fieldParentPtr("node", b);
            if (lhs.key == rhs.key) return 0;
            const ascending = lhs.key < rhs.key;
            return if (mode.* == .ascending)
                (if (ascending) -11 else 13)
            else
                (if (ascending) 13 else -11);
        }
    }.less;

    var head: list_sort.ListHead = .{};
    head.init();
    var entries = [_]Entry{
        .{ .key = 2, .ordinal = 0 },
        .{ .key = 5, .ordinal = 1 },
        .{ .key = 1, .ordinal = 2 },
        .{ .key = 5, .ordinal = 3 },
        .{ .key = 4, .ordinal = 4 },
        .{ .key = 1, .ordinal = 5 },
    };
    appendEntries(&head, &entries);

    var mode = SortMode.descending;
    list_sort.listSort(&mode, &head, cmp);
    try expectOrder(&head, &.{ 5, 5, 4, 2, 1, 1 }, &.{ 1, 3, 4, 0, 2, 5 });

    mode = .ascending;
    list_sort.listSort(&mode, &head, cmp);
    try expectOrder(&head, &.{ 1, 1, 2, 4, 5, 5 }, &.{ 2, 5, 0, 4, 1, 3 });
    try std.testing.expect(head.next == &entries[2].node);
    try std.testing.expect(head.prev == &entries[3].node);
}
