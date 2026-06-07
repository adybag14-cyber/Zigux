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
};

fn entryFromNode(node: *const list_sort.ListHead) *const Entry {
    return @fieldParentPtr("node", node);
}

fn compareByMode(priv: ?*anyopaque, a: *const list_sort.ListHead, b: *const list_sort.ListHead) i32 {
    const mode: *const SortMode = @ptrCast(@alignCast(priv.?));
    const lhs = entryFromNode(a);
    const rhs = entryFromNode(b);

    switch (mode.*) {
        .key_ascending => {
            if (lhs.key == rhs.key) return 0;
            return if (lhs.key < rhs.key) -3 else 5;
        },
        .key_descending => {
            if (lhs.key == rhs.key) return 0;
            return if (lhs.key > rhs.key) -3 else 5;
        },
        .ordinal_ascending => {
            if (lhs.ordinal == rhs.ordinal) return 0;
            return if (lhs.ordinal < rhs.ordinal) -3 else 5;
        },
    }
}

fn compareAllTies(_: ?*anyopaque, _: *const list_sort.ListHead, _: *const list_sort.ListHead) i32 {
    return 0;
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

fn collectOrdinals(head: *const list_sort.ListHead, out: []usize) ![]usize {
    var idx: usize = 0;
    var current = head.next;
    while (current != head) : (current = current.?.next) {
        const entry = entryFromNode(current.?);
        out[idx] = entry.ordinal;
        try std.testing.expect(current.?.next.?.prev == current.?);
        try std.testing.expect(current.?.prev.?.next == current.?);
        idx += 1;
    }
    return out[0..idx];
}

test "list sort delta fan staging preserves rebuilt tie order" {
    var entries = [_]Entry{
        .{ .key = 9, .ordinal = 0 },
        .{ .key = 2, .ordinal = 1 },
        .{ .key = 7, .ordinal = 2 },
        .{ .key = 4, .ordinal = 3 },
        .{ .key = 2, .ordinal = 4 },
        .{ .key = 8, .ordinal = 5 },
        .{ .key = 1, .ordinal = 6 },
        .{ .key = 6, .ordinal = 7 },
        .{ .key = 3, .ordinal = 8 },
        .{ .key = 9, .ordinal = 9 },
        .{ .key = 5, .ordinal = 10 },
        .{ .key = 0, .ordinal = 11 },
        .{ .key = 6, .ordinal = 12 },
        .{ .key = 4, .ordinal = 13 },
        .{ .key = 8, .ordinal = 14 },
        .{ .key = 1, .ordinal = 15 },
        .{ .key = 7, .ordinal = 16 },
        .{ .key = 5, .ordinal = 17 },
    };

    var main: list_sort.ListHead = .{};
    main.init();
    for (&entries) |*entry| {
        list_sort.listAddTail(&entry.node, &main);
    }

    var mode = SortMode.key_ascending;
    list_sort.listSort(&mode, &main, compareByMode);

    var initial_ordinals: [entries.len]usize = undefined;
    try std.testing.expectEqualSlices(
        usize,
        &.{ 11, 6, 15, 1, 4, 8, 3, 13, 10, 17, 7, 12, 2, 16, 5, 14, 0, 9 },
        try collectOrdinals(&main, &initial_ordinals),
    );

    var left: list_sort.ListHead = .{};
    var center: list_sort.ListHead = .{};
    var right: list_sort.ListHead = .{};
    left.init();
    center.init();
    right.init();

    var rank: usize = 0;
    while (!list_sort.listEmpty(&main)) : (rank += 1) {
        const node = popFront(&main);
        try std.testing.expect(node.next == null);
        try std.testing.expect(node.prev == null);
        switch (rank % 3) {
            0 => list_sort.listAddTail(node, &left),
            1 => list_sort.listAdd(node, &center),
            else => list_sort.listAddTail(node, &right),
        }
    }

    mode = .key_descending;
    list_sort.listSort(&mode, &left, compareByMode);
    mode = .ordinal_ascending;
    list_sort.listSort(&mode, &center, compareByMode);
    mode = .key_ascending;
    list_sort.listSort(&mode, &right, compareByMode);

    while (!list_sort.listEmpty(&left)) {
        const left_node = popBack(&left);
        try std.testing.expect(left_node.next == null);
        try std.testing.expect(left_node.prev == null);
        list_sort.listAddTail(left_node, &main);

        const center_node = popFront(&center);
        try std.testing.expect(center_node.next == null);
        try std.testing.expect(center_node.prev == null);
        list_sort.listAddTail(center_node, &main);

        const right_node = popBack(&right);
        try std.testing.expect(right_node.next == null);
        try std.testing.expect(right_node.prev == null);
        list_sort.listAddTail(right_node, &main);
    }

    var rebuilt_ordinals: [entries.len]usize = undefined;
    const rebuilt = try collectOrdinals(&main, &rebuilt_ordinals);
    try std.testing.expectEqualSlices(
        usize,
        &.{ 11, 0, 9, 1, 4, 5, 3, 6, 12, 17, 7, 10, 2, 13, 8, 14, 16, 15 },
        rebuilt,
    );
    try std.testing.expect(!std.mem.eql(usize, rebuilt, &.{ 11, 6, 15, 1, 4, 8, 3, 13, 10, 17, 7, 12, 2, 16, 5, 14, 0, 9 }));
    try std.testing.expect(main.next == &entries[11].node);
    try std.testing.expect(main.prev == &entries[15].node);

    list_sort.listSort(null, &main, compareAllTies);

    var tied_ordinals: [entries.len]usize = undefined;
    try std.testing.expectEqualSlices(
        usize,
        rebuilt,
        try collectOrdinals(&main, &tied_ordinals),
    );
    try std.testing.expect(main.next == &entries[11].node);
    try std.testing.expect(main.prev == &entries[15].node);
}
