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
    ordinal_descending,
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
            return if (lhs.key < rhs.key) -5 else 7;
        },
        .key_descending => {
            if (lhs.key == rhs.key) return 0;
            return if (lhs.key > rhs.key) -5 else 7;
        },
        .ordinal_descending => {
            if (lhs.ordinal == rhs.ordinal) return 0;
            return if (lhs.ordinal > rhs.ordinal) -5 else 7;
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

test "list sort compass rose staging preserves rebuilt tie order" {
    var entries = [_]Entry{
        .{ .key = 8, .ordinal = 0 },
        .{ .key = 3, .ordinal = 1 },
        .{ .key = 6, .ordinal = 2 },
        .{ .key = 1, .ordinal = 3 },
        .{ .key = 7, .ordinal = 4 },
        .{ .key = 3, .ordinal = 5 },
        .{ .key = 5, .ordinal = 6 },
        .{ .key = 2, .ordinal = 7 },
        .{ .key = 8, .ordinal = 8 },
        .{ .key = 4, .ordinal = 9 },
        .{ .key = 6, .ordinal = 10 },
        .{ .key = 0, .ordinal = 11 },
        .{ .key = 5, .ordinal = 12 },
        .{ .key = 1, .ordinal = 13 },
        .{ .key = 7, .ordinal = 14 },
        .{ .key = 4, .ordinal = 15 },
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
        &.{ 11, 3, 13, 7, 1, 5, 9, 15, 6, 12, 2, 10, 4, 14, 0, 8 },
        try collectOrdinals(&main, &initial_ordinals),
    );

    var north: list_sort.ListHead = .{};
    var east: list_sort.ListHead = .{};
    var south: list_sort.ListHead = .{};
    var west: list_sort.ListHead = .{};
    north.init();
    east.init();
    south.init();
    west.init();

    var rank: usize = 0;
    while (!list_sort.listEmpty(&main)) : (rank += 1) {
        const node = popFront(&main);
        try std.testing.expect(node.next == null);
        try std.testing.expect(node.prev == null);
        switch (rank % 4) {
            0 => list_sort.listAddTail(node, &north),
            1 => list_sort.listAddTail(node, &east),
            2 => list_sort.listAddTail(node, &south),
            else => list_sort.listAddTail(node, &west),
        }
    }

    mode = .key_ascending;
    list_sort.listSort(&mode, &north, compareByMode);
    mode = .key_descending;
    list_sort.listSort(&mode, &east, compareByMode);
    mode = .ordinal_descending;
    list_sort.listSort(&mode, &south, compareByMode);
    mode = .key_ascending;
    list_sort.listSort(&mode, &west, compareByMode);

    while (!list_sort.listEmpty(&north)) {
        list_sort.listAddTail(popFront(&north), &main);
        list_sort.listAddTail(popBack(&east), &main);
        list_sort.listAddTail(popFront(&south), &main);
        list_sort.listAddTail(popBack(&west), &main);
    }

    var rebuilt_ordinals: [entries.len]usize = undefined;
    const rebuilt = try collectOrdinals(&main, &rebuilt_ordinals);
    try std.testing.expectEqualSlices(
        usize,
        &.{ 11, 3, 13, 8, 1, 5, 9, 10, 6, 12, 2, 15, 4, 14, 0, 7 },
        rebuilt,
    );
    try std.testing.expect(!std.mem.eql(usize, rebuilt, &.{ 11, 3, 13, 7, 1, 5, 9, 15, 6, 12, 2, 10, 4, 14, 0, 8 }));
    try std.testing.expect(main.next == &entries[11].node);
    try std.testing.expect(main.prev == &entries[7].node);

    list_sort.listSort(null, &main, compareAllTies);

    var tied_ordinals: [entries.len]usize = undefined;
    try std.testing.expectEqualSlices(
        usize,
        rebuilt,
        try collectOrdinals(&main, &tied_ordinals),
    );
    try std.testing.expect(main.next == &entries[11].node);
    try std.testing.expect(main.prev == &entries[7].node);
}
