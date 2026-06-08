const std = @import("std");
const list_sort = @import("list_sort");

const ListHead = list_sort.ListHead;

const Entry = struct {
    key: i32,
    ordinal: usize,
    prism: u8,
    node: ListHead = .{},
};

const SortMode = enum {
    key_ascending,
    key_descending,
    ordinal_ascending,
    ordinal_descending,
    prism_then_ordinal,
    ties,
};

fn entryFromNode(node: *const ListHead) *const Entry {
    return @fieldParentPtr("node", node);
}

fn cmpByMode(priv: ?*anyopaque, a: *const ListHead, b: *const ListHead) i32 {
    const mode: *const SortMode = @ptrCast(@alignCast(priv.?));
    const lhs = entryFromNode(a);
    const rhs = entryFromNode(b);

    switch (mode.*) {
        .key_ascending => {
            if (lhs.key < rhs.key) return -3;
            if (lhs.key > rhs.key) return 5;
            return 0;
        },
        .key_descending => {
            if (lhs.key > rhs.key) return -7;
            if (lhs.key < rhs.key) return 11;
            return 0;
        },
        .ordinal_ascending => {
            if (lhs.ordinal < rhs.ordinal) return -13;
            if (lhs.ordinal > rhs.ordinal) return 17;
            return 0;
        },
        .ordinal_descending => {
            if (lhs.ordinal > rhs.ordinal) return -19;
            if (lhs.ordinal < rhs.ordinal) return 23;
            return 0;
        },
        .prism_then_ordinal => {
            if (lhs.prism < rhs.prism) return -29;
            if (lhs.prism > rhs.prism) return 31;
            if (lhs.ordinal < rhs.ordinal) return -37;
            if (lhs.ordinal > rhs.ordinal) return 41;
            return 0;
        },
        .ties => return 0,
    }
}

fn expectLinks(head: *const ListHead, expected_len: usize) !void {
    var count: usize = 0;
    var current = head.next;
    while (current != head) : (current = current.?.next) {
        try std.testing.expect(current.?.next.?.prev == current.?);
        try std.testing.expect(current.?.prev.?.next == current.?);
        count += 1;
    }
    try std.testing.expectEqual(expected_len, count);

    count = 0;
    current = head.prev;
    while (current != head) : (current = current.?.prev) {
        count += 1;
    }
    try std.testing.expectEqual(expected_len, count);
}

fn collectOrdinals(head: *const ListHead, out: []usize) !void {
    var idx: usize = 0;
    var current = head.next;
    while (current != head) : (current = current.?.next) {
        try std.testing.expect(idx < out.len);
        out[idx] = entryFromNode(current.?).ordinal;
        idx += 1;
    }
    try std.testing.expectEqual(out.len, idx);
}

fn collectKeys(head: *const ListHead, out: []i32) !void {
    var idx: usize = 0;
    var current = head.next;
    while (current != head) : (current = current.?.next) {
        try std.testing.expect(idx < out.len);
        out[idx] = entryFromNode(current.?).key;
        idx += 1;
    }
    try std.testing.expectEqual(out.len, idx);
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

test "list sort prism switchback rebuild preserves staged traversal through ties" {
    var source: ListHead = .{};
    source.init();

    var entries = [_]Entry{
        .{ .key = 6, .ordinal = 0, .prism = 2 },
        .{ .key = -3, .ordinal = 1, .prism = 0 },
        .{ .key = 4, .ordinal = 2, .prism = 1 },
        .{ .key = 9, .ordinal = 3, .prism = 2 },
        .{ .key = 0, .ordinal = 4, .prism = 0 },
        .{ .key = 4, .ordinal = 5, .prism = 1 },
        .{ .key = -3, .ordinal = 6, .prism = 0 },
        .{ .key = 8, .ordinal = 7, .prism = 2 },
        .{ .key = 2, .ordinal = 8, .prism = 1 },
        .{ .key = 6, .ordinal = 9, .prism = 2 },
        .{ .key = 1, .ordinal = 10, .prism = 0 },
        .{ .key = 8, .ordinal = 11, .prism = 2 },
    };

    const insertion_order = [_]usize{ 3, 1, 10, 5, 8, 0, 11, 4, 2, 9, 6, 7 };
    for (insertion_order, 0..) |entry_idx, step| {
        if ((step & 1) == 0) {
            list_sort.listAddTail(&entries[entry_idx].node, &source);
        } else {
            list_sort.listAdd(&entries[entry_idx].node, &source);
        }
    }
    try expectLinks(&source, entries.len);

    var mode = SortMode.key_ascending;
    list_sort.listSort(&mode, &source, cmpByMode);

    var sorted_keys: [entries.len]i32 = undefined;
    var sorted_ordinals: [entries.len]usize = undefined;
    try collectKeys(&source, &sorted_keys);
    try collectOrdinals(&source, &sorted_ordinals);
    try std.testing.expectEqualSlices(i32, &.{ -3, -3, 0, 1, 2, 4, 4, 6, 6, 8, 8, 9 }, &sorted_keys);
    try std.testing.expectEqualSlices(usize, &.{ 1, 6, 4, 10, 8, 5, 2, 9, 0, 7, 11, 3 }, &sorted_ordinals);

    var low: ListHead = .{};
    var mid: ListHead = .{};
    var high: ListHead = .{};
    low.init();
    mid.init();
    high.init();

    var rank: usize = 0;
    while (!list_sort.listEmpty(&source)) : (rank += 1) {
        const node = try popFront(&source);
        switch (rank % 3) {
            0 => list_sort.listAddTail(node, &low),
            1 => list_sort.listAdd(node, &mid),
            else => list_sort.listAddTail(node, &high),
        }
    }
    try std.testing.expect(list_sort.listEmpty(&source));

    mode = .ordinal_descending;
    list_sort.listSort(&mode, &low, cmpByMode);
    mode = .key_descending;
    list_sort.listSort(&mode, &mid, cmpByMode);
    mode = .prism_then_ordinal;
    list_sort.listSort(&mode, &high, cmpByMode);

    var staged: [4]usize = undefined;
    try collectOrdinals(&low, &staged);
    try std.testing.expectEqualSlices(usize, &.{ 10, 7, 2, 1 }, &staged);
    try collectOrdinals(&mid, &staged);
    try std.testing.expectEqualSlices(usize, &.{ 11, 9, 8, 6 }, &staged);
    try collectOrdinals(&high, &staged);
    try std.testing.expectEqualSlices(usize, &.{ 4, 5, 0, 3 }, &staged);

    var rebuilt: ListHead = .{};
    rebuilt.init();
    const switchback = [_]struct { head: *ListHead, back: bool, tail: bool }{
        .{ .head = &mid, .back = false, .tail = true },
        .{ .head = &low, .back = true, .tail = false },
        .{ .head = &high, .back = false, .tail = true },
        .{ .head = &mid, .back = true, .tail = false },
        .{ .head = &low, .back = false, .tail = true },
        .{ .head = &high, .back = true, .tail = false },
        .{ .head = &mid, .back = false, .tail = true },
        .{ .head = &low, .back = true, .tail = false },
        .{ .head = &high, .back = false, .tail = true },
        .{ .head = &mid, .back = true, .tail = false },
        .{ .head = &low, .back = false, .tail = true },
        .{ .head = &high, .back = true, .tail = false },
    };

    for (switchback) |step| {
        const node = if (step.back) try popBack(step.head) else try popFront(step.head);
        if (step.tail) {
            list_sort.listAddTail(node, &rebuilt);
        } else {
            list_sort.listAdd(node, &rebuilt);
        }
    }
    try std.testing.expect(list_sort.listEmpty(&low));
    try std.testing.expect(list_sort.listEmpty(&mid));
    try std.testing.expect(list_sort.listEmpty(&high));
    try expectLinks(&rebuilt, entries.len);

    var rebuilt_ordinals: [entries.len]usize = undefined;
    try collectOrdinals(&rebuilt, &rebuilt_ordinals);
    try std.testing.expectEqualSlices(usize, &.{ 0, 8, 2, 3, 6, 1, 11, 4, 10, 9, 5, 7 }, &rebuilt_ordinals);

    mode = .ties;
    list_sort.listSort(&mode, &rebuilt, cmpByMode);
    try expectLinks(&rebuilt, entries.len);

    var tied_ordinals: [entries.len]usize = undefined;
    try collectOrdinals(&rebuilt, &tied_ordinals);
    try std.testing.expectEqualSlices(usize, &rebuilt_ordinals, &tied_ordinals);
    try std.testing.expect(rebuilt.next == &entries[0].node);
    try std.testing.expect(rebuilt.prev == &entries[7].node);
}
