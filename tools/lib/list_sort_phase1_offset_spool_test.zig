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
    ordinal_ascending,
    ordinal_descending,
    all_equal,
};

const SortContext = struct {
    mode: SortMode,
    negative: i32,
    positive: i32,
};

fn compareValues(context: *const SortContext, lhs: i32, rhs: i32) i32 {
    if (lhs == rhs) return 0;
    return if (lhs < rhs) context.negative else context.positive;
}

fn cmp(context_ptr: ?*anyopaque, a: *const list_sort.ListHead, b: *const list_sort.ListHead) i32 {
    const context: *const SortContext = @ptrCast(@alignCast(context_ptr.?));
    if (context.mode == .all_equal) return 0;

    const lhs: *const Entry = @fieldParentPtr("node", a);
    const rhs: *const Entry = @fieldParentPtr("node", b);

    return switch (context.mode) {
        .key_ascending => compareValues(context, lhs.key, rhs.key),
        .key_descending => compareValues(context, rhs.key, lhs.key),
        .ordinal_ascending => compareValues(context, @intCast(lhs.ordinal), @intCast(rhs.ordinal)),
        .ordinal_descending => compareValues(context, @intCast(rhs.ordinal), @intCast(lhs.ordinal)),
        .all_equal => 0,
    };
}

fn popFront(head: *list_sort.ListHead) !*Entry {
    try std.testing.expect(!list_sort.listEmpty(head));
    const node = head.next.?;
    list_sort.listDel(node);
    try std.testing.expect(node.next == null);
    try std.testing.expect(node.prev == null);
    return @fieldParentPtr("node", node);
}

fn expectOrder(head: *list_sort.ListHead, expected: []const usize) !void {
    var idx: usize = 0;
    var current = head.next;
    while (current != head) : (current = current.?.next) {
        const entry: *const Entry = @fieldParentPtr("node", current.?);
        try std.testing.expect(idx < expected.len);
        try std.testing.expectEqual(expected[idx], entry.ordinal);
        try std.testing.expect(current.?.next.?.prev == current.?);
        try std.testing.expect(current.?.prev.?.next == current.?);
        idx += 1;
    }
    try std.testing.expectEqual(expected.len, idx);

    idx = 0;
    current = head.prev;
    while (current != head) : (current = current.?.prev) {
        const entry: *const Entry = @fieldParentPtr("node", current.?);
        try std.testing.expect(idx < expected.len);
        try std.testing.expectEqual(expected[expected.len - idx - 1], entry.ordinal);
        idx += 1;
    }
    try std.testing.expectEqual(expected.len, idx);
}

fn drainSpool(spool: *list_sort.ListHead, head: *list_sort.ListHead) !void {
    while (!list_sort.listEmpty(spool)) {
        const entry = try popFront(spool);
        list_sort.listAddTail(&entry.node, head);
    }
}

test "list sort survives offset spool staging and rebuild passes" {
    var head: list_sort.ListHead = .{};
    head.init();

    var entries = [_]Entry{
        .{ .key = 6, .ordinal = 0 },
        .{ .key = 2, .ordinal = 1 },
        .{ .key = 5, .ordinal = 2 },
        .{ .key = 2, .ordinal = 3 },
        .{ .key = 7, .ordinal = 4 },
        .{ .key = 1, .ordinal = 5 },
        .{ .key = 4, .ordinal = 6 },
        .{ .key = 6, .ordinal = 7 },
        .{ .key = 3, .ordinal = 8 },
        .{ .key = 5, .ordinal = 9 },
        .{ .key = 1, .ordinal = 10 },
        .{ .key = 4, .ordinal = 11 },
        .{ .key = 8, .ordinal = 12 },
        .{ .key = 3, .ordinal = 13 },
    };

    for (&entries, 0..) |*entry, idx| {
        if ((idx & 1) == 0) {
            list_sort.listAddTail(&entry.node, &head);
        } else {
            list_sort.listAdd(&entry.node, &head);
        }
    }

    var key_ascending = SortContext{ .mode = .key_ascending, .negative = -23, .positive = 29 };
    list_sort.listSort(&key_ascending, &head, cmp);
    try expectOrder(&head, &.{ 5, 10, 3, 1, 13, 8, 11, 6, 9, 2, 7, 0, 4, 12 });

    var spools = [_]list_sort.ListHead{ .{}, .{}, .{}, .{} };
    for (&spools) |*spool| spool.init();

    for (0..entries.len) |rank| {
        const entry = try popFront(&head);
        const spool_idx = (rank * 3 + 1) % spools.len;
        list_sort.listAddTail(&entry.node, &spools[spool_idx]);
    }
    try std.testing.expect(list_sort.listEmpty(&head));

    var spool0_by_ordinal_desc = SortContext{ .mode = .ordinal_descending, .negative = -31, .positive = 37 };
    var spool1_by_key_desc = SortContext{ .mode = .key_descending, .negative = -41, .positive = 43 };
    var spool2_by_key_asc = SortContext{ .mode = .key_ascending, .negative = -47, .positive = 53 };
    var spool3_by_ordinal_asc = SortContext{ .mode = .ordinal_ascending, .negative = -59, .positive = 61 };

    list_sort.listSort(&spool0_by_ordinal_desc, &spools[0], cmp);
    list_sort.listSort(&spool1_by_key_desc, &spools[1], cmp);
    list_sort.listSort(&spool2_by_key_asc, &spools[2], cmp);
    list_sort.listSort(&spool3_by_ordinal_asc, &spools[3], cmp);

    try expectOrder(&spools[0], &.{ 12, 10, 8, 2 });
    try expectOrder(&spools[1], &.{ 4, 9, 13, 5 });
    try expectOrder(&spools[2], &.{ 1, 6, 0 });
    try expectOrder(&spools[3], &.{ 3, 7, 11 });

    try drainSpool(&spools[2], &head);
    try drainSpool(&spools[0], &head);
    try drainSpool(&spools[3], &head);
    try drainSpool(&spools[1], &head);
    try expectOrder(&head, &.{ 1, 6, 0, 12, 10, 8, 2, 3, 7, 11, 4, 9, 13, 5 });

    var all_equal = SortContext{ .mode = .all_equal, .negative = -67, .positive = 71 };
    list_sort.listSort(&all_equal, &head, cmp);
    try expectOrder(&head, &.{ 1, 6, 0, 12, 10, 8, 2, 3, 7, 11, 4, 9, 13, 5 });

    var key_descending = SortContext{ .mode = .key_descending, .negative = -73, .positive = 79 };
    list_sort.listSort(&key_descending, &head, cmp);
    try expectOrder(&head, &.{ 12, 4, 0, 7, 2, 9, 6, 11, 8, 13, 1, 3, 10, 5 });
    try std.testing.expect(head.next == &entries[12].node);
    try std.testing.expect(head.prev == &entries[5].node);
}
