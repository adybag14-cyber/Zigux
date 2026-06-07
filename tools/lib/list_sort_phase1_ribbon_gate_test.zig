const std = @import("std");
const list_sort = @import("list_sort");

const ListHead = list_sort.ListHead;

const Entry = struct {
    key: i32,
    ordinal: usize,
    node: ListHead = .{},
};

const SortMode = enum { ascending, descending };

fn compareByMode(priv: ?*anyopaque, a: *const ListHead, b: *const ListHead) i32 {
    const mode: *const SortMode = @ptrCast(@alignCast(priv.?));
    const lhs: *const Entry = @fieldParentPtr("node", a);
    const rhs: *const Entry = @fieldParentPtr("node", b);

    if (lhs.key == rhs.key) return 0;
    const ascending = lhs.key < rhs.key;
    return if (mode.* == .ascending)
        (if (ascending) -5 else 7)
    else
        (if (ascending) 7 else -5);
}

fn compareAllTies(_: ?*anyopaque, _: *const ListHead, _: *const ListHead) i32 {
    return 0;
}

fn popFront(head: *ListHead) ?*ListHead {
    if (list_sort.listEmpty(head)) return null;
    const node = head.next.?;
    list_sort.listDel(node);
    return node;
}

fn popBack(head: *ListHead) ?*ListHead {
    if (list_sort.listEmpty(head)) return null;
    const node = head.prev.?;
    list_sort.listDel(node);
    return node;
}

fn expectDetached(node: *const ListHead) !void {
    try std.testing.expect(node.next == null);
    try std.testing.expect(node.prev == null);
}

fn expectCircularLinks(head: *const ListHead) !void {
    var current = head.next;
    while (current != head) : (current = current.?.next) {
        try std.testing.expect(current.?.next.?.prev == current.?);
        try std.testing.expect(current.?.prev.?.next == current.?);
    }
}

fn collectOrdinals(comptime len: usize, head: *const ListHead) ![len]usize {
    var ordinals: [len]usize = undefined;
    var idx: usize = 0;
    var current = head.next;
    while (current != head) : (current = current.?.next) {
        const entry: *const Entry = @fieldParentPtr("node", current.?);
        ordinals[idx] = entry.ordinal;
        idx += 1;
    }
    try std.testing.expectEqual(len, idx);
    return ordinals;
}

fn collectKeys(comptime len: usize, head: *const ListHead) ![len]i32 {
    var keys: [len]i32 = undefined;
    var idx: usize = 0;
    var current = head.next;
    while (current != head) : (current = current.?.next) {
        const entry: *const Entry = @fieldParentPtr("node", current.?);
        keys[idx] = entry.key;
        idx += 1;
    }
    try std.testing.expectEqual(len, idx);
    return keys;
}

test "list sort ribbon gate split rebuild preserves detach and tie stability" {
    var head: ListHead = .{};
    head.init();

    var entries = [_]Entry{
        .{ .key = 7, .ordinal = 0 },
        .{ .key = 2, .ordinal = 1 },
        .{ .key = 5, .ordinal = 2 },
        .{ .key = 2, .ordinal = 3 },
        .{ .key = 9, .ordinal = 4 },
        .{ .key = 4, .ordinal = 5 },
        .{ .key = 7, .ordinal = 6 },
        .{ .key = 1, .ordinal = 7 },
        .{ .key = 6, .ordinal = 8 },
        .{ .key = 4, .ordinal = 9 },
        .{ .key = 8, .ordinal = 10 },
        .{ .key = 1, .ordinal = 11 },
    };

    for (&entries) |*entry| {
        list_sort.listAddTail(&entry.node, &head);
    }

    var ascending = SortMode.ascending;
    list_sort.listSort(&ascending, &head, compareByMode);

    const sorted_keys = try collectKeys(entries.len, &head);
    const sorted_ordinals = try collectOrdinals(entries.len, &head);
    try std.testing.expectEqualSlices(i32, &.{ 1, 1, 2, 2, 4, 4, 5, 6, 7, 7, 8, 9 }, &sorted_keys);
    try std.testing.expectEqualSlices(usize, &.{ 7, 11, 1, 3, 5, 9, 2, 8, 0, 6, 10, 4 }, &sorted_ordinals);

    var gates = [_]ListHead{ .{}, .{}, .{}, .{} };
    for (&gates) |*gate| gate.init();

    var sorted_rank: usize = 0;
    while (popFront(&head)) |node| : (sorted_rank += 1) {
        try expectDetached(node);
        switch (sorted_rank % gates.len) {
            0 => list_sort.listAddTail(node, &gates[0]),
            1 => list_sort.listAdd(node, &gates[1]),
            2 => list_sort.listAddTail(node, &gates[2]),
            else => list_sort.listAdd(node, &gates[3]),
        }
    }
    try std.testing.expect(list_sort.listEmpty(&head));
    try std.testing.expectEqual(entries.len, sorted_rank);

    list_sort.listSort(&ascending, &gates[0], compareByMode);
    var descending = SortMode.descending;
    list_sort.listSort(&descending, &gates[1], compareByMode);
    list_sort.listSort(&ascending, &gates[2], compareByMode);
    list_sort.listSort(&descending, &gates[3], compareByMode);

    try std.testing.expectEqualSlices(usize, &.{ 7, 5, 0 }, &(try collectOrdinals(3, &gates[0])));
    try std.testing.expectEqualSlices(usize, &.{ 6, 9, 11 }, &(try collectOrdinals(3, &gates[1])));
    try std.testing.expectEqualSlices(usize, &.{ 1, 2, 10 }, &(try collectOrdinals(3, &gates[2])));
    try std.testing.expectEqualSlices(usize, &.{ 4, 8, 3 }, &(try collectOrdinals(3, &gates[3])));

    const ribbon_steps = [_]struct {
        gate: usize,
        back: bool,
    }{
        .{ .gate = 1, .back = false },
        .{ .gate = 0, .back = true },
        .{ .gate = 3, .back = false },
        .{ .gate = 2, .back = true },
        .{ .gate = 1, .back = true },
        .{ .gate = 0, .back = false },
        .{ .gate = 3, .back = true },
        .{ .gate = 2, .back = false },
        .{ .gate = 1, .back = false },
        .{ .gate = 0, .back = false },
        .{ .gate = 3, .back = false },
        .{ .gate = 2, .back = false },
    };

    for (ribbon_steps) |step| {
        const node = if (step.back) popBack(&gates[step.gate]).? else popFront(&gates[step.gate]).?;
        try expectDetached(node);
        list_sort.listAddTail(node, &head);
    }
    for (&gates) |*gate| {
        try std.testing.expect(list_sort.listEmpty(gate));
    }

    try expectCircularLinks(&head);
    const rebuilt_ordinals = try collectOrdinals(entries.len, &head);
    const rebuilt_keys = try collectKeys(entries.len, &head);
    try std.testing.expectEqualSlices(usize, &.{ 6, 0, 4, 10, 11, 7, 3, 1, 9, 5, 8, 2 }, &rebuilt_ordinals);
    try std.testing.expectEqualSlices(i32, &.{ 7, 7, 9, 8, 1, 1, 2, 2, 4, 4, 6, 5 }, &rebuilt_keys);
    try std.testing.expect(head.next == &entries[6].node);
    try std.testing.expect(head.prev == &entries[2].node);

    list_sort.listSort(null, &head, compareAllTies);
    try expectCircularLinks(&head);
    const tied_ordinals = try collectOrdinals(entries.len, &head);
    const tied_keys = try collectKeys(entries.len, &head);
    try std.testing.expectEqualSlices(usize, &.{ 6, 0, 4, 10, 11, 7, 3, 1, 9, 5, 8, 2 }, &tied_ordinals);
    try std.testing.expectEqualSlices(i32, &.{ 7, 7, 9, 8, 1, 1, 2, 2, 4, 4, 6, 5 }, &tied_keys);
    try std.testing.expect(head.next == &entries[6].node);
    try std.testing.expect(head.prev == &entries[2].node);
}
