const std = @import("std");
const list_sort = @import("list_sort");

const Entry = struct {
    key: i32,
    ordinal: usize,
    node: list_sort.ListHead = .{},
};

const SortMode = enum { ascending, descending };

fn signedCmp(priv: ?*anyopaque, a: *const list_sort.ListHead, b: *const list_sort.ListHead) i32 {
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

fn tiesCmp(_: ?*anyopaque, _: *const list_sort.ListHead, _: *const list_sort.ListHead) i32 {
    return 0;
}

fn expectCircular(head: *const list_sort.ListHead, expected_len: usize) !void {
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

fn collectOrdinals(head: *const list_sort.ListHead, out: []usize) !usize {
    var idx: usize = 0;
    var current = head.next;
    while (current != head) : (current = current.?.next) {
        const entry: *const Entry = @fieldParentPtr("node", current.?);
        out[idx] = entry.ordinal;
        idx += 1;
    }
    return idx;
}

fn collectKeys(head: *const list_sort.ListHead, out: []i32) !usize {
    var idx: usize = 0;
    var current = head.next;
    while (current != head) : (current = current.?.next) {
        const entry: *const Entry = @fieldParentPtr("node", current.?);
        out[idx] = entry.key;
        idx += 1;
    }
    return idx;
}

fn popFront(head: *list_sort.ListHead) ?*list_sort.ListHead {
    if (list_sort.listEmpty(head)) return null;
    const node = head.next.?;
    list_sort.listDel(node);
    return node;
}

fn popBack(head: *list_sort.ListHead) ?*list_sort.ListHead {
    if (list_sort.listEmpty(head)) return null;
    const node = head.prev.?;
    list_sort.listDel(node);
    return node;
}

test "list sort mirror runway rebuild preserves all-ties order" {
    var entries = [_]Entry{
        .{ .key = 4, .ordinal = 0 },
        .{ .key = -1, .ordinal = 1 },
        .{ .key = 7, .ordinal = 2 },
        .{ .key = 4, .ordinal = 3 },
        .{ .key = -3, .ordinal = 4 },
        .{ .key = 9, .ordinal = 5 },
        .{ .key = 0, .ordinal = 6 },
        .{ .key = 7, .ordinal = 7 },
        .{ .key = -1, .ordinal = 8 },
        .{ .key = 5, .ordinal = 9 },
        .{ .key = 9, .ordinal = 10 },
        .{ .key = 2, .ordinal = 11 },
        .{ .key = -3, .ordinal = 12 },
        .{ .key = 5, .ordinal = 13 },
        .{ .key = 8, .ordinal = 14 },
        .{ .key = 0, .ordinal = 15 },
        .{ .key = 6, .ordinal = 16 },
        .{ .key = 2, .ordinal = 17 },
        .{ .key = 8, .ordinal = 18 },
        .{ .key = 4, .ordinal = 19 },
    };

    var source: list_sort.ListHead = .{};
    source.init();
    for (&entries) |*entry| list_sort.listAddTail(&entry.node, &source);

    var mode = SortMode.descending;
    list_sort.listSort(&mode, &source, signedCmp);
    try expectCircular(&source, entries.len);

    var keys: [entries.len]i32 = undefined;
    var ordinals: [entries.len]usize = undefined;
    try std.testing.expectEqual(entries.len, try collectKeys(&source, &keys));
    try std.testing.expectEqual(entries.len, try collectOrdinals(&source, &ordinals));
    try std.testing.expectEqualSlices(i32, &.{ 9, 9, 8, 8, 7, 7, 6, 5, 5, 4, 4, 4, 2, 2, 0, 0, -1, -1, -3, -3 }, &keys);
    try std.testing.expectEqualSlices(usize, &.{ 5, 10, 14, 18, 2, 7, 16, 9, 13, 0, 3, 19, 11, 17, 6, 15, 1, 8, 4, 12 }, &ordinals);

    var left: list_sort.ListHead = .{};
    var right: list_sort.ListHead = .{};
    left.init();
    right.init();

    var rank: usize = 0;
    while (popFront(&source)) |node| : (rank += 1) {
        try std.testing.expect(node.next == null);
        try std.testing.expect(node.prev == null);
        if ((rank & 1) == 0) {
            list_sort.listAddTail(node, &left);
        } else {
            list_sort.listAdd(node, &right);
        }
    }
    try std.testing.expect(list_sort.listEmpty(&source));
    try expectCircular(&left, 10);
    try expectCircular(&right, 10);

    mode = .ascending;
    list_sort.listSort(&mode, &left, signedCmp);
    mode = .descending;
    list_sort.listSort(&mode, &right, signedCmp);

    var rebuilt: [entries.len]usize = undefined;
    var rebuilt_len: usize = 0;
    while (!list_sort.listEmpty(&left) or !list_sort.listEmpty(&right)) {
        if (popFront(&left)) |node| {
            const entry: *const Entry = @fieldParentPtr("node", node);
            rebuilt[rebuilt_len] = entry.ordinal;
            rebuilt_len += 1;
            try std.testing.expect(node.next == null);
            try std.testing.expect(node.prev == null);
            list_sort.listAddTail(node, &source);
        }
        if (popBack(&right)) |node| {
            const entry: *const Entry = @fieldParentPtr("node", node);
            rebuilt[rebuilt_len] = entry.ordinal;
            rebuilt_len += 1;
            try std.testing.expect(node.next == null);
            try std.testing.expect(node.prev == null);
            list_sort.listAddTail(node, &source);
        }
    }

    try std.testing.expectEqualSlices(usize, &.{ 4, 12, 1, 8, 6, 15, 11, 17, 3, 0, 13, 19, 16, 9, 2, 7, 14, 18, 5, 10 }, rebuilt[0..rebuilt_len]);
    try expectCircular(&source, entries.len);
    try std.testing.expect(source.next == &entries[4].node);
    try std.testing.expect(source.prev == &entries[10].node);

    list_sort.listSort(null, &source, tiesCmp);

    var after_ties: [entries.len]usize = undefined;
    try std.testing.expectEqual(entries.len, try collectOrdinals(&source, &after_ties));
    try std.testing.expectEqualSlices(usize, rebuilt[0..rebuilt_len], &after_ties);
    try expectCircular(&source, entries.len);
    try std.testing.expect(source.next == &entries[4].node);
    try std.testing.expect(source.prev == &entries[10].node);
}
