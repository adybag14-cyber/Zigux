const std = @import("std");
const list_sort = @import("list_sort");

const ListHead = list_sort.ListHead;

const Entry = struct {
    key: i32,
    ordinal: usize,
    node: ListHead = .{},
};

const SortMode = enum {
    key_asc,
    key_desc,
    ordinal_asc,
    all_equal,
};

const PopSide = enum { front, back };
const InsertSide = enum { front, back };

const TurnpikeStep = struct {
    lane: usize,
    pop: PopSide,
    insert: InsertSide,
};

fn cmp(priv: ?*anyopaque, a: *const ListHead, b: *const ListHead) i32 {
    const mode: *const SortMode = @ptrCast(@alignCast(priv.?));
    const lhs: *const Entry = @fieldParentPtr("node", a);
    const rhs: *const Entry = @fieldParentPtr("node", b);

    return switch (mode.*) {
        .key_asc => compareI32(lhs.key, rhs.key),
        .key_desc => compareI32(rhs.key, lhs.key),
        .ordinal_asc => compareUsize(lhs.ordinal, rhs.ordinal),
        .all_equal => 0,
    };
}

fn compareI32(lhs: i32, rhs: i32) i32 {
    if (lhs < rhs) return -5;
    if (lhs > rhs) return 7;
    return 0;
}

fn compareUsize(lhs: usize, rhs: usize) i32 {
    if (lhs < rhs) return -3;
    if (lhs > rhs) return 11;
    return 0;
}

fn popFront(head: *ListHead) !*ListHead {
    try std.testing.expect(!list_sort.listEmpty(head));
    const node = head.next.?;
    list_sort.listDel(node);
    try std.testing.expect(node.next == null);
    try std.testing.expect(node.prev == null);
    return node;
}

fn popBack(head: *ListHead) !*ListHead {
    try std.testing.expect(!list_sort.listEmpty(head));
    const node = head.prev.?;
    list_sort.listDel(node);
    try std.testing.expect(node.next == null);
    try std.testing.expect(node.prev == null);
    return node;
}

fn insertNode(node: *ListHead, head: *ListHead, side: InsertSide) void {
    switch (side) {
        .front => list_sort.listAdd(node, head),
        .back => list_sort.listAddTail(node, head),
    }
}

fn expectOrdinals(head: *ListHead, expected: []const usize) !void {
    var forward: [16]usize = undefined;
    var reverse: [16]usize = undefined;

    var forward_len: usize = 0;
    var current = head.next;
    while (current != head) : (current = current.?.next) {
        const entry: *const Entry = @fieldParentPtr("node", current.?);
        forward[forward_len] = entry.ordinal;
        try std.testing.expect(current.?.next.?.prev == current.?);
        try std.testing.expect(current.?.prev.?.next == current.?);
        forward_len += 1;
    }

    var reverse_len: usize = 0;
    current = head.prev;
    while (current != head) : (current = current.?.prev) {
        const entry: *const Entry = @fieldParentPtr("node", current.?);
        reverse[reverse_len] = entry.ordinal;
        reverse_len += 1;
    }

    try std.testing.expectEqualSlices(usize, expected, forward[0..forward_len]);
    try std.testing.expectEqual(expected.len, reverse_len);
    for (expected, 0..) |ordinal, idx| {
        try std.testing.expectEqual(ordinal, reverse[expected.len - 1 - idx]);
    }
}

test "list sort preserves staggered turnpike rebuild across lane reorders" {
    var entries = [_]Entry{
        .{ .key = 4, .ordinal = 0 },
        .{ .key = 1, .ordinal = 1 },
        .{ .key = 6, .ordinal = 2 },
        .{ .key = 2, .ordinal = 3 },
        .{ .key = 5, .ordinal = 4 },
        .{ .key = 1, .ordinal = 5 },
        .{ .key = 3, .ordinal = 6 },
        .{ .key = 6, .ordinal = 7 },
        .{ .key = 0, .ordinal = 8 },
        .{ .key = 4, .ordinal = 9 },
        .{ .key = 2, .ordinal = 10 },
        .{ .key = 5, .ordinal = 11 },
        .{ .key = 0, .ordinal = 12 },
        .{ .key = 3, .ordinal = 13 },
    };

    var head: ListHead = .{};
    head.init();
    for (&entries, 0..) |*entry, idx| {
        if (idx % 4 == 0 or idx % 4 == 3) {
            list_sort.listAdd(&entry.node, &head);
        } else {
            list_sort.listAddTail(&entry.node, &head);
        }
    }
    try expectOrdinals(&head, &.{ 12, 11, 8, 7, 4, 3, 0, 1, 2, 5, 6, 9, 10, 13 });

    var mode = SortMode.key_asc;
    list_sort.listSort(&mode, &head, cmp);
    try expectOrdinals(&head, &.{ 12, 8, 1, 5, 3, 10, 6, 13, 0, 9, 11, 4, 7, 2 });

    var lanes = [_]ListHead{ .{}, .{}, .{}, .{} };
    for (&lanes) |*lane| lane.init();

    var rank: usize = 0;
    while (!list_sort.listEmpty(&head)) : (rank += 1) {
        const node = try popFront(&head);
        const lane_idx = (rank * 3 + 1) % lanes.len;
        const side: InsertSide = if (rank % 3 == 0) .front else .back;
        insertNode(node, &lanes[lane_idx], side);
    }

    try std.testing.expect(list_sort.listEmpty(&head));
    try expectOrdinals(&lanes[0], &.{ 9, 8, 10, 2 });
    try expectOrdinals(&lanes[1], &.{ 7, 12, 3, 0 });
    try expectOrdinals(&lanes[2], &.{ 5, 13, 4 });
    try expectOrdinals(&lanes[3], &.{ 6, 1, 11 });

    mode = .key_desc;
    list_sort.listSort(&mode, &lanes[0], cmp);
    mode = .ordinal_asc;
    list_sort.listSort(&mode, &lanes[1], cmp);
    mode = .key_asc;
    list_sort.listSort(&mode, &lanes[2], cmp);
    mode = .key_desc;
    list_sort.listSort(&mode, &lanes[3], cmp);

    try expectOrdinals(&lanes[0], &.{ 2, 9, 10, 8 });
    try expectOrdinals(&lanes[1], &.{ 0, 3, 7, 12 });
    try expectOrdinals(&lanes[2], &.{ 5, 13, 4 });
    try expectOrdinals(&lanes[3], &.{ 11, 6, 1 });

    const turnpike_steps = [_]TurnpikeStep{
        .{ .lane = 1, .pop = .front, .insert = .back },
        .{ .lane = 0, .pop = .front, .insert = .front },
        .{ .lane = 3, .pop = .front, .insert = .back },
        .{ .lane = 2, .pop = .back, .insert = .front },
        .{ .lane = 1, .pop = .back, .insert = .back },
        .{ .lane = 0, .pop = .back, .insert = .front },
        .{ .lane = 2, .pop = .front, .insert = .back },
        .{ .lane = 3, .pop = .back, .insert = .front },
        .{ .lane = 1, .pop = .front, .insert = .back },
        .{ .lane = 0, .pop = .front, .insert = .front },
        .{ .lane = 2, .pop = .front, .insert = .back },
        .{ .lane = 3, .pop = .front, .insert = .front },
        .{ .lane = 1, .pop = .front, .insert = .back },
        .{ .lane = 0, .pop = .front, .insert = .front },
    };

    for (turnpike_steps) |step| {
        const node = switch (step.pop) {
            .front => try popFront(&lanes[step.lane]),
            .back => try popBack(&lanes[step.lane]),
        };
        insertNode(node, &head, step.insert);
    }

    for (&lanes) |*lane| try std.testing.expect(list_sort.listEmpty(lane));
    try expectOrdinals(&head, &.{ 10, 6, 9, 1, 8, 4, 2, 0, 11, 12, 5, 3, 13, 7 });
    try std.testing.expect(head.next == &entries[10].node);
    try std.testing.expect(head.prev == &entries[7].node);

    mode = .all_equal;
    list_sort.listSort(&mode, &head, cmp);
    try expectOrdinals(&head, &.{ 10, 6, 9, 1, 8, 4, 2, 0, 11, 12, 5, 3, 13, 7 });
    try std.testing.expect(head.next == &entries[10].node);
    try std.testing.expect(head.prev == &entries[7].node);
}
