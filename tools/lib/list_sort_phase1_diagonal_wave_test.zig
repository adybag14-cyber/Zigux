const std = @import("std");
const list_sort = @import("list_sort");

const ListHead = list_sort.ListHead;

const entry_count = 18;
const stage_count = 5;

const SortMode = enum {
    key_asc,
    key_desc,
    diagonal_asc,
    ordinal_desc,
    all_ties,
};

const SortContext = struct {
    mode: SortMode,
    magnitude: i32,
};

const Entry = struct {
    key: i32,
    ordinal: usize,
    diagonal: usize = 0,
    node: ListHead = .{},
};

fn compare(priv: ?*anyopaque, a: *const ListHead, b: *const ListHead) i32 {
    const context: *const SortContext = @ptrCast(@alignCast(priv.?));
    const lhs: *const Entry = @fieldParentPtr("node", a);
    const rhs: *const Entry = @fieldParentPtr("node", b);

    const result: i32 = switch (context.mode) {
        .key_asc => compareInts(lhs.key, rhs.key),
        .key_desc => compareInts(rhs.key, lhs.key),
        .diagonal_asc => compareUsize(lhs.diagonal, rhs.diagonal),
        .ordinal_desc => compareUsize(rhs.ordinal, lhs.ordinal),
        .all_ties => 0,
    };

    if (result == 0) return 0;
    return result * context.magnitude;
}

fn compareInts(lhs: i32, rhs: i32) i32 {
    if (lhs < rhs) return -1;
    if (lhs > rhs) return 1;
    return 0;
}

fn compareUsize(lhs: usize, rhs: usize) i32 {
    if (lhs < rhs) return -1;
    if (lhs > rhs) return 1;
    return 0;
}

fn expectOrder(head: *const ListHead, expected: []const usize) !void {
    var actual: [entry_count]usize = undefined;
    var idx: usize = 0;
    var current = head.next;
    while (current != head) : (current = current.?.next) {
        try std.testing.expect(idx < actual.len);
        const entry: *const Entry = @fieldParentPtr("node", current.?);
        actual[idx] = entry.ordinal;
        idx += 1;
    }

    try std.testing.expectEqualSlices(usize, expected, actual[0..idx]);
}

fn expectReverseOrder(head: *const ListHead, expected: []const usize) !void {
    var actual: [entry_count]usize = undefined;
    var idx: usize = 0;
    var current = head.prev;
    while (current != head) : (current = current.?.prev) {
        try std.testing.expect(idx < actual.len);
        const entry: *const Entry = @fieldParentPtr("node", current.?);
        actual[idx] = entry.ordinal;
        idx += 1;
    }

    try std.testing.expectEqual(idx, expected.len);
    for (expected, 0..) |ordinal, pos| {
        try std.testing.expectEqual(ordinal, actual[expected.len - 1 - pos]);
    }
}

fn expectCircular(head: *const ListHead, expected_len: usize) !void {
    var current = head.next;
    var previous: *const ListHead = head;
    var seen: usize = 0;

    while (current != head) {
        try std.testing.expect(current.?.prev == previous);
        previous = current.?;
        current = current.?.next;
        seen += 1;
        try std.testing.expect(seen <= expected_len);
    }

    try std.testing.expectEqual(expected_len, seen);
    try std.testing.expect(head.prev == previous);
}

fn popFront(head: *ListHead) !?*ListHead {
    if (list_sort.listEmpty(head)) return null;
    const node = head.next.?;
    list_sort.listDel(node);
    try std.testing.expect(node.next == null);
    try std.testing.expect(node.prev == null);
    return node;
}

fn popBack(head: *ListHead) !?*ListHead {
    if (list_sort.listEmpty(head)) return null;
    const node = head.prev.?;
    list_sort.listDel(node);
    try std.testing.expect(node.next == null);
    try std.testing.expect(node.prev == null);
    return node;
}

test "list_sort diagonal wave staging preserves detached lifecycle and ties" {
    var head: ListHead = .{};
    head.init();

    var entries = [_]Entry{
        .{ .key = 4, .ordinal = 0 },
        .{ .key = 1, .ordinal = 1 },
        .{ .key = 3, .ordinal = 2 },
        .{ .key = 1, .ordinal = 3 },
        .{ .key = 5, .ordinal = 4 },
        .{ .key = 2, .ordinal = 5 },
        .{ .key = 4, .ordinal = 6 },
        .{ .key = 2, .ordinal = 7 },
        .{ .key = 6, .ordinal = 8 },
        .{ .key = 3, .ordinal = 9 },
        .{ .key = 5, .ordinal = 10 },
        .{ .key = 0, .ordinal = 11 },
        .{ .key = 6, .ordinal = 12 },
        .{ .key = 0, .ordinal = 13 },
        .{ .key = 4, .ordinal = 14 },
        .{ .key = 2, .ordinal = 15 },
        .{ .key = 5, .ordinal = 16 },
        .{ .key = 3, .ordinal = 17 },
    };

    for (&entries, 0..) |*entry, idx| {
        if (idx % 3 == 0) {
            list_sort.listAdd(&entry.node, &head);
        } else {
            list_sort.listAddTail(&entry.node, &head);
        }
    }
    try expectCircular(&head, entries.len);

    var key_asc = SortContext{ .mode = .key_asc, .magnitude = 3 };
    list_sort.listSort(&key_asc, &head, compare);
    try expectOrder(&head, &.{ 11, 13, 3, 1, 15, 5, 7, 9, 2, 17, 6, 0, 14, 4, 10, 16, 12, 8 });
    try expectCircular(&head, entries.len);

    var stages: [stage_count]ListHead = undefined;
    for (&stages) |*stage| stage.init();

    var rank: usize = 0;
    while (try popFront(&head)) |node| : (rank += 1) {
        const entry: *Entry = @fieldParentPtr("node", node);
        const diagonal = (rank * 2 + if (rank % 3 == 0) @as(usize, 1) else 0) % stages.len;
        entry.diagonal = diagonal;
        if (rank % 2 == 0) {
            list_sort.listAddTail(node, &stages[diagonal]);
        } else {
            list_sort.listAdd(node, &stages[diagonal]);
        }
    }
    try std.testing.expect(list_sort.listEmpty(&head));

    var key_desc = SortContext{ .mode = .key_desc, .magnitude = 2 };
    var diagonal_asc = SortContext{ .mode = .diagonal_asc, .magnitude = 5 };
    var ordinal_desc = SortContext{ .mode = .ordinal_desc, .magnitude = 7 };
    const contexts = [_]*SortContext{ &key_desc, &diagonal_asc, &ordinal_desc, &key_asc, &diagonal_asc };

    for (&stages, 0..) |*stage, idx| {
        if (!list_sort.listEmpty(stage)) {
            list_sort.listSort(contexts[idx], stage, compare);
            try expectCircular(stage, switch (idx) {
                0 => 3,
                1 => 4,
                2 => 4,
                3 => 3,
                else => 4,
            });
        }
    }

    try expectOrder(&stages[0], &.{ 6, 14, 5 });
    try expectOrder(&stages[1], &.{ 16, 4, 11, 2 });
    try expectOrder(&stages[2], &.{ 13, 12, 1, 0 });
    try expectOrder(&stages[3], &.{ 15, 7, 10 });
    try expectOrder(&stages[4], &.{ 8, 17, 9, 3 });

    const schedule = [_]usize{ 3, 0, 4, 1, 2, 0, 3, 1, 4, 2, 1, 0, 2, 4, 1, 2, 4, 3 };
    for (schedule, 0..) |stage_idx, step| {
        const node = if (step % 2 == 0)
            try popFront(&stages[stage_idx])
        else
            try popBack(&stages[stage_idx]);
        try std.testing.expect(node != null);

        if (step % 3 == 0) {
            list_sort.listAdd(node.?, &head);
        } else {
            list_sort.listAddTail(node.?, &head);
        }
    }
    for (&stages) |*stage| try std.testing.expect(list_sort.listEmpty(stage));

    const rebuilt = [_]usize{ 1, 12, 0, 7, 2, 15, 5, 8, 13, 14, 11, 17, 16, 6, 3, 4, 9, 10 };
    try expectOrder(&head, &rebuilt);
    try expectReverseOrder(&head, &rebuilt);
    try expectCircular(&head, entries.len);

    var all_ties = SortContext{ .mode = .all_ties, .magnitude = 11 };
    list_sort.listSort(&all_ties, &head, compare);
    try expectOrder(&head, &rebuilt);
    try expectCircular(&head, entries.len);
}
