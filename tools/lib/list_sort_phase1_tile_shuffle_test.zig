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
};

fn cmpByKey(_: ?*anyopaque, a: *const ListHead, b: *const ListHead) i32 {
    const lhs: *const Entry = @fieldParentPtr("node", a);
    const rhs: *const Entry = @fieldParentPtr("node", b);
    if (lhs.key < rhs.key) return -1;
    if (lhs.key > rhs.key) return 1;
    return 0;
}

fn cmpWithMode(priv: ?*anyopaque, a: *const ListHead, b: *const ListHead) i32 {
    const mode: *const SortMode = @ptrCast(@alignCast(priv.?));
    const lhs: *const Entry = @fieldParentPtr("node", a);
    const rhs: *const Entry = @fieldParentPtr("node", b);

    switch (mode.*) {
        .key_ascending => {
            if (lhs.key < rhs.key) return -3;
            if (lhs.key > rhs.key) return 5;
        },
        .key_descending => {
            if (lhs.key > rhs.key) return -3;
            if (lhs.key < rhs.key) return 5;
        },
        .ordinal_ascending => {
            if (lhs.ordinal < rhs.ordinal) return -3;
            if (lhs.ordinal > rhs.ordinal) return 5;
        },
    }
    return 0;
}

fn cmpAllTies(_: ?*anyopaque, _: *const ListHead, _: *const ListHead) i32 {
    return 0;
}

fn popFront(head: *ListHead) *ListHead {
    const node = head.next.?;
    list_sort.listDel(node);
    return node;
}

fn popBack(head: *ListHead) *ListHead {
    const node = head.prev.?;
    list_sort.listDel(node);
    return node;
}

fn expectDetached(node: *const ListHead) !void {
    try std.testing.expect(node.next == null);
    try std.testing.expect(node.prev == null);
}

fn expectForward(head: *ListHead, expected: []const usize) !void {
    var current = head.next;
    var idx: usize = 0;
    while (current != head) : (current = current.?.next) {
        const entry: *const Entry = @fieldParentPtr("node", current.?);
        try std.testing.expect(idx < expected.len);
        try std.testing.expectEqual(expected[idx], entry.ordinal);
        try std.testing.expect(current.?.next.?.prev == current.?);
        try std.testing.expect(current.?.prev.?.next == current.?);
        idx += 1;
    }
    try std.testing.expectEqual(expected.len, idx);
}

fn expectBackward(head: *ListHead, expected: []const usize) !void {
    var current = head.prev;
    var idx: usize = 0;
    while (current != head) : (current = current.?.prev) {
        const entry: *const Entry = @fieldParentPtr("node", current.?);
        try std.testing.expect(idx < expected.len);
        try std.testing.expectEqual(expected[idx], entry.ordinal);
        idx += 1;
    }
    try std.testing.expectEqual(expected.len, idx);
}

test "list sort tile shuffle split rebuild preserves links and ties" {
    var main: ListHead = .{};
    main.init();

    var entries = [_]Entry{
        .{ .key = 7, .ordinal = 0 },
        .{ .key = 2, .ordinal = 1 },
        .{ .key = 5, .ordinal = 2 },
        .{ .key = 2, .ordinal = 3 },
        .{ .key = 9, .ordinal = 4 },
        .{ .key = 1, .ordinal = 5 },
        .{ .key = 5, .ordinal = 6 },
        .{ .key = 3, .ordinal = 7 },
        .{ .key = 7, .ordinal = 8 },
        .{ .key = 1, .ordinal = 9 },
        .{ .key = 4, .ordinal = 10 },
        .{ .key = 3, .ordinal = 11 },
    };

    for (&entries) |*entry| {
        if ((entry.ordinal % 3) == 0) {
            list_sort.listAdd(&entry.node, &main);
        } else {
            list_sort.listAddTail(&entry.node, &main);
        }
    }

    try expectForward(&main, &.{ 9, 6, 3, 0, 1, 2, 4, 5, 7, 8, 10, 11 });

    list_sort.listSort(null, &main, cmpByKey);
    try expectForward(&main, &.{ 9, 5, 3, 1, 7, 11, 10, 6, 2, 0, 8, 4 });
    try expectBackward(&main, &.{ 4, 8, 0, 2, 6, 10, 11, 7, 1, 3, 5, 9 });

    var tiles = [_]ListHead{ .{}, .{}, .{}, .{} };
    for (&tiles) |*tile| tile.init();

    var sorted_rank: usize = 0;
    while (!list_sort.listEmpty(&main)) : (sorted_rank += 1) {
        const node = popFront(&main);
        try expectDetached(node);

        const tile_index = sorted_rank % tiles.len;
        if ((tile_index % 2) == 0) {
            list_sort.listAddTail(node, &tiles[tile_index]);
        } else {
            list_sort.listAdd(node, &tiles[tile_index]);
        }
    }
    try std.testing.expect(list_sort.listEmpty(&main));

    try expectForward(&tiles[0], &.{ 9, 7, 2 });
    try expectForward(&tiles[1], &.{ 0, 11, 5 });
    try expectForward(&tiles[2], &.{ 3, 10, 8 });
    try expectForward(&tiles[3], &.{ 4, 6, 1 });

    var tile0_mode = SortMode.key_ascending;
    var tile1_mode = SortMode.key_descending;
    var tile2_mode = SortMode.ordinal_ascending;
    var tile3_mode = SortMode.key_ascending;

    list_sort.listSort(&tile0_mode, &tiles[0], cmpWithMode);
    list_sort.listSort(&tile1_mode, &tiles[1], cmpWithMode);
    list_sort.listSort(&tile2_mode, &tiles[2], cmpWithMode);
    list_sort.listSort(&tile3_mode, &tiles[3], cmpWithMode);

    try expectForward(&tiles[0], &.{ 9, 7, 2 });
    try expectForward(&tiles[1], &.{ 0, 11, 5 });
    try expectForward(&tiles[2], &.{ 3, 8, 10 });
    try expectForward(&tiles[3], &.{ 1, 6, 4 });

    const TileStep = struct {
        tile: usize,
        back: bool,
    };
    const steps = [_]TileStep{
        .{ .tile = 0, .back = false },
        .{ .tile = 1, .back = true },
        .{ .tile = 2, .back = false },
        .{ .tile = 3, .back = true },
        .{ .tile = 0, .back = true },
        .{ .tile = 1, .back = false },
        .{ .tile = 2, .back = true },
        .{ .tile = 3, .back = false },
        .{ .tile = 0, .back = false },
        .{ .tile = 1, .back = false },
        .{ .tile = 2, .back = false },
        .{ .tile = 3, .back = false },
    };

    for (steps) |step| {
        const node = if (step.back) popBack(&tiles[step.tile]) else popFront(&tiles[step.tile]);
        try expectDetached(node);
        list_sort.listAddTail(node, &main);
    }

    for (&tiles) |*tile| try std.testing.expect(list_sort.listEmpty(tile));

    try expectForward(&main, &.{ 9, 5, 3, 4, 2, 0, 10, 1, 7, 11, 8, 6 });
    try expectBackward(&main, &.{ 6, 8, 11, 7, 1, 10, 0, 2, 4, 3, 5, 9 });

    list_sort.listSort(null, &main, cmpAllTies);
    try expectForward(&main, &.{ 9, 5, 3, 4, 2, 0, 10, 1, 7, 11, 8, 6 });
    try std.testing.expect(main.next == &entries[9].node);
    try std.testing.expect(main.prev == &entries[6].node);
}
