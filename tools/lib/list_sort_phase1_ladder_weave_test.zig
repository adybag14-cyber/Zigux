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
    ordinal_descending,
    ties,
};

fn cmp(priv: ?*anyopaque, a: *const ListHead, b: *const ListHead) i32 {
    const mode: *const SortMode = @ptrCast(@alignCast(priv.?));
    const lhs: *const Entry = @fieldParentPtr("node", a);
    const rhs: *const Entry = @fieldParentPtr("node", b);

    return switch (mode.*) {
        .key_ascending => order(lhs.key, rhs.key),
        .key_descending => order(rhs.key, lhs.key),
        .ordinal_ascending => order(lhs.ordinal, rhs.ordinal),
        .ordinal_descending => order(rhs.ordinal, lhs.ordinal),
        .ties => 0,
    };
}

fn order(lhs: anytype, rhs: @TypeOf(lhs)) i32 {
    if (lhs < rhs) return -1;
    if (lhs > rhs) return 1;
    return 0;
}

fn appendOrdinal(out: []usize, idx: *usize, node: *ListHead) void {
    const entry: *const Entry = @fieldParentPtr("node", node);
    out[idx.*] = entry.ordinal;
    idx.* += 1;
}

fn collectOrdinals(head: *ListHead, out: []usize) ![]usize {
    var idx: usize = 0;
    var current = head.next;
    while (current != head) : (current = current.?.next) {
        try std.testing.expect(current.?.next.?.prev == current.?);
        try std.testing.expect(current.?.prev.?.next == current.?);
        appendOrdinal(out, &idx, current.?);
    }
    return out[0..idx];
}

fn popFront(head: *ListHead) *ListHead {
    const node = head.next.?;
    list_sort.listDel(node);
    std.testing.expect(node.next == null and node.prev == null) catch unreachable;
    return node;
}

fn popBack(head: *ListHead) *ListHead {
    const node = head.prev.?;
    list_sort.listDel(node);
    std.testing.expect(node.next == null and node.prev == null) catch unreachable;
    return node;
}

test "list sort ladder weave preserves rebuilt traversal through staged resorts" {
    var source: ListHead = .{};
    source.init();
    var left_rail: ListHead = .{};
    left_rail.init();
    var right_rail: ListHead = .{};
    right_rail.init();
    var center_rung: ListHead = .{};
    center_rung.init();
    var shadow_rung: ListHead = .{};
    shadow_rung.init();

    var entries = [_]Entry{
        .{ .key = 6, .ordinal = 0 },
        .{ .key = 1, .ordinal = 1 },
        .{ .key = 4, .ordinal = 2 },
        .{ .key = 1, .ordinal = 3 },
        .{ .key = 7, .ordinal = 4 },
        .{ .key = 2, .ordinal = 5 },
        .{ .key = 5, .ordinal = 6 },
        .{ .key = 2, .ordinal = 7 },
        .{ .key = 3, .ordinal = 8 },
        .{ .key = 6, .ordinal = 9 },
        .{ .key = 4, .ordinal = 10 },
        .{ .key = 5, .ordinal = 11 },
    };

    for (&entries, 0..) |*entry, idx| {
        if ((idx & 1) == 0) {
            list_sort.listAddTail(&entry.node, &source);
        } else {
            list_sort.listAdd(&entry.node, &source);
        }
    }

    var mode = SortMode.key_ascending;
    list_sort.listSort(&mode, &source, cmp);

    var sorted_ordinals: [12]usize = undefined;
    try std.testing.expectEqualSlices(
        usize,
        &.{ 3, 1, 7, 5, 8, 2, 10, 11, 6, 9, 0, 4 },
        try collectOrdinals(&source, &sorted_ordinals),
    );

    var rank: usize = 0;
    while (!list_sort.listEmpty(&source)) : (rank += 1) {
        const node = popFront(&source);
        switch (rank % 4) {
            0 => list_sort.listAddTail(node, &left_rail),
            1 => list_sort.listAdd(node, &right_rail),
            2 => list_sort.listAddTail(node, &center_rung),
            else => list_sort.listAdd(node, &shadow_rung),
        }
    }

    try std.testing.expect(list_sort.listEmpty(&source));

    mode = .key_descending;
    list_sort.listSort(&mode, &left_rail, cmp);
    mode = .ordinal_ascending;
    list_sort.listSort(&mode, &right_rail, cmp);
    mode = .key_ascending;
    list_sort.listSort(&mode, &center_rung, cmp);
    mode = .ordinal_descending;
    list_sort.listSort(&mode, &shadow_rung, cmp);

    var left_ordinals: [3]usize = undefined;
    try std.testing.expectEqualSlices(usize, &.{ 6, 8, 3 }, try collectOrdinals(&left_rail, &left_ordinals));
    var right_ordinals: [3]usize = undefined;
    try std.testing.expectEqualSlices(usize, &.{ 1, 2, 9 }, try collectOrdinals(&right_rail, &right_ordinals));
    var center_ordinals: [3]usize = undefined;
    try std.testing.expectEqualSlices(usize, &.{ 7, 10, 0 }, try collectOrdinals(&center_rung, &center_ordinals));
    var shadow_ordinals: [3]usize = undefined;
    try std.testing.expectEqualSlices(usize, &.{ 11, 5, 4 }, try collectOrdinals(&shadow_rung, &shadow_ordinals));

    list_sort.listAddTail(popFront(&left_rail), &source);
    list_sort.listAddTail(popBack(&right_rail), &source);
    list_sort.listAddTail(popFront(&center_rung), &source);
    list_sort.listAddTail(popBack(&shadow_rung), &source);
    list_sort.listAddTail(popBack(&left_rail), &source);
    list_sort.listAddTail(popFront(&right_rail), &source);
    list_sort.listAddTail(popBack(&center_rung), &source);
    list_sort.listAddTail(popFront(&shadow_rung), &source);
    list_sort.listAddTail(popFront(&left_rail), &source);
    list_sort.listAddTail(popBack(&right_rail), &source);
    list_sort.listAddTail(popFront(&center_rung), &source);
    list_sort.listAddTail(popBack(&shadow_rung), &source);

    try std.testing.expect(list_sort.listEmpty(&left_rail));
    try std.testing.expect(list_sort.listEmpty(&right_rail));
    try std.testing.expect(list_sort.listEmpty(&center_rung));
    try std.testing.expect(list_sort.listEmpty(&shadow_rung));

    const expected_rebuilt = &.{ 6, 9, 7, 4, 3, 1, 0, 11, 8, 2, 10, 5 };
    var rebuilt_ordinals: [12]usize = undefined;
    try std.testing.expectEqualSlices(usize, expected_rebuilt, try collectOrdinals(&source, &rebuilt_ordinals));
    try std.testing.expect(source.next == &entries[6].node);
    try std.testing.expect(source.prev == &entries[5].node);

    mode = .ties;
    list_sort.listSort(&mode, &source, cmp);

    var tied_ordinals: [12]usize = undefined;
    try std.testing.expectEqualSlices(usize, expected_rebuilt, try collectOrdinals(&source, &tied_ordinals));
    try std.testing.expect(source.next == &entries[6].node);
    try std.testing.expect(source.prev == &entries[5].node);
}
