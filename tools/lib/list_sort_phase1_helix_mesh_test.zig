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

const MeshStep = struct {
    rail: usize,
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
    if (lhs < rhs) return -1;
    if (lhs > rhs) return 1;
    return 0;
}

fn compareUsize(lhs: usize, rhs: usize) i32 {
    if (lhs < rhs) return -1;
    if (lhs > rhs) return 1;
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

test "list sort preserves helix mesh staging across independent rail reorders" {
    var entries = [_]Entry{
        .{ .key = 5, .ordinal = 0 },
        .{ .key = 1, .ordinal = 1 },
        .{ .key = 4, .ordinal = 2 },
        .{ .key = 1, .ordinal = 3 },
        .{ .key = 3, .ordinal = 4 },
        .{ .key = 2, .ordinal = 5 },
        .{ .key = 5, .ordinal = 6 },
        .{ .key = 0, .ordinal = 7 },
        .{ .key = 3, .ordinal = 8 },
        .{ .key = 2, .ordinal = 9 },
        .{ .key = 4, .ordinal = 10 },
        .{ .key = 0, .ordinal = 11 },
    };

    var head: ListHead = .{};
    head.init();
    for (&entries, 0..) |*entry, idx| {
        if (idx % 3 == 0) {
            list_sort.listAdd(&entry.node, &head);
        } else {
            list_sort.listAddTail(&entry.node, &head);
        }
    }
    try expectOrdinals(&head, &.{ 9, 6, 3, 0, 1, 2, 4, 5, 7, 8, 10, 11 });

    var mode = SortMode.key_asc;
    list_sort.listSort(&mode, &head, cmp);
    try expectOrdinals(&head, &.{ 7, 11, 3, 1, 9, 5, 4, 8, 2, 10, 6, 0 });

    var rails = [_]ListHead{ .{}, .{}, .{} };
    for (&rails) |*rail| rail.init();

    var rank: usize = 0;
    while (!list_sort.listEmpty(&head)) : (rank += 1) {
        const node = try popFront(&head);
        const rail_idx = rank % rails.len;
        insertNode(node, &rails[rail_idx], if (rank % 2 == 0) .back else .front);
    }

    try std.testing.expect(list_sort.listEmpty(&head));
    try expectOrdinals(&rails[0], &.{ 10, 1, 7, 4 });
    try expectOrdinals(&rails[1], &.{ 8, 11, 9, 6 });
    try expectOrdinals(&rails[2], &.{ 0, 5, 3, 2 });

    mode = .key_desc;
    list_sort.listSort(&mode, &rails[0], cmp);
    mode = .ordinal_asc;
    list_sort.listSort(&mode, &rails[1], cmp);
    mode = .key_asc;
    list_sort.listSort(&mode, &rails[2], cmp);

    try expectOrdinals(&rails[0], &.{ 10, 4, 1, 7 });
    try expectOrdinals(&rails[1], &.{ 6, 8, 9, 11 });
    try expectOrdinals(&rails[2], &.{ 3, 5, 2, 0 });

    const mesh_steps = [_]MeshStep{
        .{ .rail = 0, .pop = .front, .insert = .back },
        .{ .rail = 1, .pop = .back, .insert = .front },
        .{ .rail = 2, .pop = .front, .insert = .back },
        .{ .rail = 0, .pop = .back, .insert = .front },
        .{ .rail = 2, .pop = .back, .insert = .back },
        .{ .rail = 1, .pop = .front, .insert = .front },
        .{ .rail = 0, .pop = .front, .insert = .back },
        .{ .rail = 2, .pop = .front, .insert = .front },
        .{ .rail = 1, .pop = .back, .insert = .back },
        .{ .rail = 0, .pop = .back, .insert = .front },
        .{ .rail = 2, .pop = .back, .insert = .back },
        .{ .rail = 1, .pop = .front, .insert = .front },
    };

    for (mesh_steps) |step| {
        const node = switch (step.pop) {
            .front => try popFront(&rails[step.rail]),
            .back => try popBack(&rails[step.rail]),
        };
        insertNode(node, &head, step.insert);
    }

    for (&rails) |*rail| try std.testing.expect(list_sort.listEmpty(rail));
    try expectOrdinals(&head, &.{ 8, 1, 5, 6, 7, 11, 10, 3, 0, 4, 9, 2 });
    try std.testing.expect(head.next == &entries[8].node);
    try std.testing.expect(head.prev == &entries[2].node);

    mode = .all_equal;
    list_sort.listSort(&mode, &head, cmp);
    try expectOrdinals(&head, &.{ 8, 1, 5, 6, 7, 11, 10, 3, 0, 4, 9, 2 });
    try std.testing.expect(head.next == &entries[8].node);
    try std.testing.expect(head.prev == &entries[2].node);
}
