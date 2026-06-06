const std = @import("std");
const list_sort = @import("list_sort");

const Entry = struct {
    key: i32,
    ordinal: usize,
    node: list_sort.ListHead = .{},
};

const SortMode = enum {
    ascending,
    descending,
    modulo_bucket,
};

const SortContext = struct {
    mode: SortMode,
};

fn compare(priv: ?*anyopaque, a: *const list_sort.ListHead, b: *const list_sort.ListHead) i32 {
    const ctx: *const SortContext = @ptrCast(@alignCast(priv.?));
    const lhs: *const Entry = @fieldParentPtr("node", a);
    const rhs: *const Entry = @fieldParentPtr("node", b);

    switch (ctx.mode) {
        .ascending => {
            if (lhs.key < rhs.key) return -5;
            if (lhs.key > rhs.key) return 7;
            return 0;
        },
        .descending => {
            if (lhs.key > rhs.key) return -5;
            if (lhs.key < rhs.key) return 7;
            return 0;
        },
        .modulo_bucket => {
            const lhs_bucket = @mod(lhs.key, 3);
            const rhs_bucket = @mod(rhs.key, 3);
            if (lhs_bucket < rhs_bucket) return -3;
            if (lhs_bucket > rhs_bucket) return 3;
            return 0;
        },
    }
}

fn compareAllTies(_: ?*anyopaque, _: *const list_sort.ListHead, _: *const list_sort.ListHead) i32 {
    return 0;
}

fn expectDetached(node: *const list_sort.ListHead) !void {
    try std.testing.expect(node.next == null);
    try std.testing.expect(node.prev == null);
}

fn expectCircular(head: *list_sort.ListHead) !void {
    var current = head.next.?;
    while (current != head) : (current = current.next.?) {
        try std.testing.expect(current.next.?.prev == current);
        try std.testing.expect(current.prev.?.next == current);
    }
}

fn collectOrdinals(head: *list_sort.ListHead, out: []usize) usize {
    var idx: usize = 0;
    var current = head.next.?;
    while (current != head) : (current = current.next.?) {
        const entry: *const Entry = @fieldParentPtr("node", current);
        out[idx] = entry.ordinal;
        idx += 1;
    }
    return idx;
}

fn popFront(head: *list_sort.ListHead) !*list_sort.ListHead {
    const node = head.next.?;
    list_sort.listDel(node);
    try expectDetached(node);
    return node;
}

fn popBack(head: *list_sort.ListHead) !*list_sort.ListHead {
    const node = head.prev.?;
    list_sort.listDel(node);
    try expectDetached(node);
    return node;
}

test "list sort preserves stability after spoke rotation rebuild" {
    var main: list_sort.ListHead = .{};
    main.init();
    var entries = [_]Entry{
        .{ .key = 6, .ordinal = 0 },
        .{ .key = 1, .ordinal = 1 },
        .{ .key = 9, .ordinal = 2 },
        .{ .key = 4, .ordinal = 3 },
        .{ .key = 7, .ordinal = 4 },
        .{ .key = 2, .ordinal = 5 },
        .{ .key = 8, .ordinal = 6 },
        .{ .key = 3, .ordinal = 7 },
        .{ .key = 5, .ordinal = 8 },
        .{ .key = 0, .ordinal = 9 },
        .{ .key = 7, .ordinal = 10 },
        .{ .key = 2, .ordinal = 11 },
    };
    for (&entries) |*entry| list_sort.listAddTail(&entry.node, &main);

    var ascending = SortContext{ .mode = .ascending };
    list_sort.listSort(&ascending, &main, compare);

    var sorted_ordinals: [entries.len]usize = undefined;
    const sorted_count = collectOrdinals(&main, &sorted_ordinals);
    try std.testing.expectEqual(entries.len, sorted_count);
    try std.testing.expectEqualSlices(
        usize,
        &.{ 9, 1, 5, 11, 7, 3, 8, 0, 4, 10, 6, 2 },
        sorted_ordinals[0..sorted_count],
    );

    var spokes = [_]list_sort.ListHead{ .{}, .{}, .{} };
    for (&spokes) |*spoke| spoke.init();

    var rank: usize = 0;
    while (!list_sort.listEmpty(&main)) : (rank += 1) {
        const node = try popFront(&main);
        if ((rank & 1) == 0) {
            list_sort.listAddTail(node, &spokes[rank % spokes.len]);
        } else {
            list_sort.listAdd(node, &spokes[rank % spokes.len]);
        }
    }

    var descending = SortContext{ .mode = .descending };
    var modulo = SortContext{ .mode = .modulo_bucket };
    list_sort.listSort(&descending, &spokes[0], compare);
    list_sort.listSort(&ascending, &spokes[1], compare);
    list_sort.listSort(&modulo, &spokes[2], compare);

    var spoke0: [4]usize = undefined;
    var spoke1: [4]usize = undefined;
    var spoke2: [4]usize = undefined;
    try std.testing.expectEqualSlices(usize, &.{ 10, 8, 11, 9 }, spoke0[0..collectOrdinals(&spokes[0], &spoke0)]);
    try std.testing.expectEqualSlices(usize, &.{ 1, 7, 0, 6 }, spoke1[0..collectOrdinals(&spokes[1], &spoke1)]);
    try std.testing.expectEqualSlices(usize, &.{ 2, 3, 4, 5 }, spoke2[0..collectOrdinals(&spokes[2], &spoke2)]);

    while (!list_sort.listEmpty(&spokes[0]) or !list_sort.listEmpty(&spokes[1]) or !list_sort.listEmpty(&spokes[2])) {
        if (!list_sort.listEmpty(&spokes[2])) list_sort.listAddTail(try popBack(&spokes[2]), &main);
        if (!list_sort.listEmpty(&spokes[0])) list_sort.listAddTail(try popFront(&spokes[0]), &main);
        if (!list_sort.listEmpty(&spokes[1])) list_sort.listAddTail(try popBack(&spokes[1]), &main);
    }

    try expectCircular(&main);

    var rotated_ordinals: [entries.len]usize = undefined;
    const rotated_count = collectOrdinals(&main, &rotated_ordinals);
    try std.testing.expectEqualSlices(
        usize,
        &.{ 5, 10, 6, 4, 8, 0, 3, 11, 7, 2, 9, 1 },
        rotated_ordinals[0..rotated_count],
    );

    list_sort.listSort(null, &main, compareAllTies);
    try expectCircular(&main);

    var tied_ordinals: [entries.len]usize = undefined;
    const tied_count = collectOrdinals(&main, &tied_ordinals);
    try std.testing.expectEqual(rotated_count, tied_count);
    try std.testing.expectEqualSlices(usize, rotated_ordinals[0..rotated_count], tied_ordinals[0..tied_count]);
    try std.testing.expect(main.next == &entries[5].node);
    try std.testing.expect(main.prev == &entries[1].node);
}
