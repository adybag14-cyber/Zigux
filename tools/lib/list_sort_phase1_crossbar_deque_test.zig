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
    ordinal_desc,
    all_equal,
};

const SortContext = struct {
    mode: SortMode,
    magnitude: i32,
};

const Side = enum { front, back };

const CrossbarStep = struct {
    deck: usize,
    pop: Side,
    insert: Side,
};

fn cmp(priv: ?*anyopaque, a: *const ListHead, b: *const ListHead) i32 {
    const context: *const SortContext = @ptrCast(@alignCast(priv.?));
    const lhs: *const Entry = @fieldParentPtr("node", a);
    const rhs: *const Entry = @fieldParentPtr("node", b);

    const order = switch (context.mode) {
        .key_asc => compareI32(lhs.key, rhs.key),
        .key_desc => compareI32(rhs.key, lhs.key),
        .ordinal_desc => compareUsize(rhs.ordinal, lhs.ordinal),
        .all_equal => 0,
    };

    if (order < 0) return -context.magnitude;
    if (order > 0) return context.magnitude;
    return 0;
}

fn compareI32(lhs: i32, rhs: i32) i32 {
    if (lhs < rhs) return -1;
    if (lhs > rhs) return 1;
    return 0;
}

fn compareUsize(lhs: usize, rhs: usize) i32 {
    if (lhs < rhs) return -1;
    if (lhs > rhs) return 1;
    return 0;
}

fn popNode(head: *ListHead, side: Side) !*ListHead {
    try std.testing.expect(!list_sort.listEmpty(head));
    const node = switch (side) {
        .front => head.next.?,
        .back => head.prev.?,
    };
    list_sort.listDel(node);
    try std.testing.expect(node.next == null);
    try std.testing.expect(node.prev == null);
    return node;
}

fn insertNode(node: *ListHead, head: *ListHead, side: Side) void {
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

test "list sort preserves crossbar deque rebuild and stability" {
    var entries = [_]Entry{
        .{ .key = 4, .ordinal = 0 },
        .{ .key = 1, .ordinal = 1 },
        .{ .key = 6, .ordinal = 2 },
        .{ .key = 2, .ordinal = 3 },
        .{ .key = 5, .ordinal = 4 },
        .{ .key = 1, .ordinal = 5 },
        .{ .key = 3, .ordinal = 6 },
        .{ .key = 0, .ordinal = 7 },
        .{ .key = 6, .ordinal = 8 },
        .{ .key = 2, .ordinal = 9 },
        .{ .key = 4, .ordinal = 10 },
        .{ .key = 0, .ordinal = 11 },
        .{ .key = 5, .ordinal = 12 },
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

    var context = SortContext{ .mode = .key_asc, .magnitude = 3 };
    list_sort.listSort(&context, &head, cmp);
    try expectOrdinals(&head, &.{ 11, 7, 1, 5, 3, 9, 6, 13, 0, 10, 12, 4, 8, 2 });

    var decks = [_]ListHead{ .{}, .{}, .{}, .{} };
    for (&decks) |*deck| deck.init();

    var rank: usize = 0;
    while (!list_sort.listEmpty(&head)) : (rank += 1) {
        const node = try popNode(&head, .front);
        const deck_idx = (rank * 3 + 1) % decks.len;
        insertNode(node, &decks[deck_idx], if (rank % 2 == 0) .back else .front);
    }

    try std.testing.expect(list_sort.listEmpty(&head));
    try expectOrdinals(&decks[0], &.{ 2, 10, 9, 7 });
    try expectOrdinals(&decks[1], &.{ 11, 3, 0, 8 });
    try expectOrdinals(&decks[2], &.{ 4, 13, 5 });
    try expectOrdinals(&decks[3], &.{ 1, 6, 12 });

    context = .{ .mode = .key_desc, .magnitude = 5 };
    list_sort.listSort(&context, &decks[0], cmp);
    context = .{ .mode = .ordinal_desc, .magnitude = 7 };
    list_sort.listSort(&context, &decks[1], cmp);
    context = .{ .mode = .key_asc, .magnitude = 11 };
    list_sort.listSort(&context, &decks[2], cmp);
    context = .{ .mode = .key_desc, .magnitude = 13 };
    list_sort.listSort(&context, &decks[3], cmp);

    try expectOrdinals(&decks[0], &.{ 2, 10, 9, 7 });
    try expectOrdinals(&decks[1], &.{ 11, 8, 3, 0 });
    try expectOrdinals(&decks[2], &.{ 5, 13, 4 });
    try expectOrdinals(&decks[3], &.{ 12, 6, 1 });

    const steps = [_]CrossbarStep{
        .{ .deck = 1, .pop = .front, .insert = .back },
        .{ .deck = 0, .pop = .back, .insert = .front },
        .{ .deck = 3, .pop = .front, .insert = .back },
        .{ .deck = 2, .pop = .back, .insert = .front },
        .{ .deck = 0, .pop = .front, .insert = .back },
        .{ .deck = 1, .pop = .back, .insert = .back },
        .{ .deck = 2, .pop = .front, .insert = .front },
        .{ .deck = 3, .pop = .back, .insert = .back },
        .{ .deck = 0, .pop = .front, .insert = .front },
        .{ .deck = 1, .pop = .front, .insert = .back },
        .{ .deck = 2, .pop = .front, .insert = .back },
        .{ .deck = 3, .pop = .front, .insert = .front },
        .{ .deck = 0, .pop = .front, .insert = .back },
        .{ .deck = 1, .pop = .front, .insert = .front },
    };

    for (steps) |step| {
        const node = try popNode(&decks[step.deck], step.pop);
        insertNode(node, &head, step.insert);
    }

    for (&decks) |*deck| try std.testing.expect(list_sort.listEmpty(deck));
    try expectOrdinals(&head, &.{ 3, 6, 10, 5, 4, 7, 11, 12, 2, 0, 1, 8, 13, 9 });
    try std.testing.expect(head.next == &entries[3].node);
    try std.testing.expect(head.prev == &entries[9].node);

    context = .{ .mode = .all_equal, .magnitude = 17 };
    list_sort.listSort(&context, &head, cmp);
    try expectOrdinals(&head, &.{ 3, 6, 10, 5, 4, 7, 11, 12, 2, 0, 1, 8, 13, 9 });

    context = .{ .mode = .key_desc, .magnitude = 19 };
    list_sort.listSort(&context, &head, cmp);
    try expectOrdinals(&head, &.{ 2, 8, 4, 12, 10, 0, 6, 13, 3, 9, 5, 1, 7, 11 });
    try std.testing.expect(head.next == &entries[2].node);
    try std.testing.expect(head.prev == &entries[11].node);
}
