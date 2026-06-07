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
            return if (lhs.key < rhs.key) -7 else 11;
        },
        .key_descending => {
            if (lhs.key == rhs.key) return 0;
            return if (lhs.key > rhs.key) -7 else 11;
        },
        .ordinal_ascending => {
            if (lhs.ordinal == rhs.ordinal) return 0;
            return if (lhs.ordinal < rhs.ordinal) -7 else 11;
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

test "list sort braid shuttle staging preserves rebuilt tie order" {
    var entries = [_]Entry{
        .{ .key = 5, .ordinal = 0 },
        .{ .key = -1, .ordinal = 1 },
        .{ .key = 8, .ordinal = 2 },
        .{ .key = 3, .ordinal = 3 },
        .{ .key = 5, .ordinal = 4 },
        .{ .key = 0, .ordinal = 5 },
        .{ .key = 7, .ordinal = 6 },
        .{ .key = -3, .ordinal = 7 },
        .{ .key = 3, .ordinal = 8 },
        .{ .key = 9, .ordinal = 9 },
        .{ .key = 1, .ordinal = 10 },
        .{ .key = 7, .ordinal = 11 },
        .{ .key = -1, .ordinal = 12 },
        .{ .key = 4, .ordinal = 13 },
        .{ .key = 9, .ordinal = 14 },
        .{ .key = 0, .ordinal = 15 },
        .{ .key = 2, .ordinal = 16 },
        .{ .key = 8, .ordinal = 17 },
        .{ .key = 4, .ordinal = 18 },
        .{ .key = 6, .ordinal = 19 },
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
        &.{ 7, 1, 12, 5, 15, 10, 16, 3, 8, 13, 18, 0, 4, 19, 6, 11, 2, 17, 9, 14 },
        try collectOrdinals(&main, &initial_ordinals),
    );

    var braid_a: list_sort.ListHead = .{};
    var braid_b: list_sort.ListHead = .{};
    var shuttle: list_sort.ListHead = .{};
    var reserve: list_sort.ListHead = .{};
    braid_a.init();
    braid_b.init();
    shuttle.init();
    reserve.init();

    var rank: usize = 0;
    while (!list_sort.listEmpty(&main)) : (rank += 1) {
        const node = popFront(&main);
        try std.testing.expect(node.next == null);
        try std.testing.expect(node.prev == null);
        switch (rank % 4) {
            0 => list_sort.listAddTail(node, &braid_a),
            1 => list_sort.listAdd(node, &shuttle),
            2 => list_sort.listAddTail(node, &braid_b),
            else => list_sort.listAdd(node, &reserve),
        }
    }

    mode = .key_descending;
    list_sort.listSort(&mode, &braid_a, compareByMode);
    mode = .ordinal_ascending;
    list_sort.listSort(&mode, &shuttle, compareByMode);
    mode = .key_ascending;
    list_sort.listSort(&mode, &braid_b, compareByMode);
    mode = .key_descending;
    list_sort.listSort(&mode, &reserve, compareByMode);

    while (!list_sort.listEmpty(&shuttle)) {
        const shuttle_node = popFront(&shuttle);
        try std.testing.expect(shuttle_node.next == null);
        try std.testing.expect(shuttle_node.prev == null);
        list_sort.listAddTail(shuttle_node, &main);

        const braid_a_node = popBack(&braid_a);
        try std.testing.expect(braid_a_node.next == null);
        try std.testing.expect(braid_a_node.prev == null);
        list_sort.listAddTail(braid_a_node, &main);

        const reserve_node = popFront(&reserve);
        try std.testing.expect(reserve_node.next == null);
        try std.testing.expect(reserve_node.prev == null);
        list_sort.listAddTail(reserve_node, &main);

        const braid_b_node = popBack(&braid_b);
        try std.testing.expect(braid_b_node.next == null);
        try std.testing.expect(braid_b_node.prev == null);
        list_sort.listAddTail(braid_b_node, &main);
    }

    var rebuilt_ordinals: [entries.len]usize = undefined;
    const rebuilt = try collectOrdinals(&main, &rebuilt_ordinals);
    try std.testing.expectEqualSlices(
        usize,
        &.{ 1, 7, 14, 9, 10, 15, 11, 6, 13, 8, 0, 18, 17, 4, 3, 16, 19, 2, 5, 12 },
        rebuilt,
    );
    try std.testing.expect(!std.mem.eql(
        usize,
        rebuilt,
        &.{ 7, 1, 12, 5, 15, 10, 16, 3, 8, 13, 18, 0, 4, 19, 6, 11, 2, 17, 9, 14 },
    ));
    try std.testing.expect(main.next == &entries[1].node);
    try std.testing.expect(main.prev == &entries[12].node);

    list_sort.listSort(null, &main, compareAllTies);

    var tied_ordinals: [entries.len]usize = undefined;
    try std.testing.expectEqualSlices(
        usize,
        rebuilt,
        try collectOrdinals(&main, &tied_ordinals),
    );
    try std.testing.expect(main.next == &entries[1].node);
    try std.testing.expect(main.prev == &entries[12].node);
}
