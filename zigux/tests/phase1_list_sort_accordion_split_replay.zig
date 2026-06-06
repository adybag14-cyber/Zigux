const std = @import("std");
const list_sort = @import("list_sort");

const ListHead = list_sort.ListHead;

const Entry = struct {
    key: i32,
    ordinal: usize,
    node: ListHead = .{},
};

const SortMode = enum { ascending, descending };

fn cmpByKey(priv: ?*anyopaque, a: *const ListHead, b: *const ListHead) i32 {
    const mode: *const SortMode = @ptrCast(@alignCast(priv.?));
    const lhs: *const Entry = @fieldParentPtr("node", a);
    const rhs: *const Entry = @fieldParentPtr("node", b);

    if (lhs.key == rhs.key) return 0;
    const ascending = lhs.key < rhs.key;
    return if (mode.* == .ascending)
        (if (ascending) -3 else 5)
    else
        (if (ascending) 5 else -3);
}

fn cmpAllTies(_: ?*anyopaque, _: *const ListHead, _: *const ListHead) i32 {
    return 0;
}

fn collectKeys(head: *const ListHead, out: []i32) !usize {
    var idx: usize = 0;
    var current = head.next;
    while (current != head) : (current = current.?.next) {
        const entry: *const Entry = @fieldParentPtr("node", current.?);
        out[idx] = entry.key;
        try std.testing.expect(current.?.next.?.prev == current.?);
        try std.testing.expect(current.?.prev.?.next == current.?);
        idx += 1;
    }
    return idx;
}

fn collectOrdinals(head: *const ListHead, out: []usize) !usize {
    var idx: usize = 0;
    var current = head.next;
    while (current != head) : (current = current.?.next) {
        const entry: *const Entry = @fieldParentPtr("node", current.?);
        out[idx] = entry.ordinal;
        try std.testing.expect(current.?.next.?.prev == current.?);
        try std.testing.expect(current.?.prev.?.next == current.?);
        idx += 1;
    }
    return idx;
}

fn expectEmpty(head: *const ListHead) !void {
    try std.testing.expect(list_sort.listEmpty(head));
    try std.testing.expect(head.next == head);
    try std.testing.expect(head.prev == head);
}

test "list sort accordion split replay preserves staged traversal" {
    var head: ListHead = .{};
    var lows: ListHead = .{};
    var highs: ListHead = .{};
    head.init();
    lows.init();
    highs.init();

    var entries = [_]Entry{
        .{ .key = 6, .ordinal = 0 },
        .{ .key = 1, .ordinal = 1 },
        .{ .key = 4, .ordinal = 2 },
        .{ .key = 2, .ordinal = 3 },
        .{ .key = 8, .ordinal = 4 },
        .{ .key = 3, .ordinal = 5 },
        .{ .key = 5, .ordinal = 6 },
        .{ .key = 7, .ordinal = 7 },
        .{ .key = 0, .ordinal = 8 },
        .{ .key = 9, .ordinal = 9 },
    };
    for (&entries) |*entry| list_sort.listAddTail(&entry.node, &head);

    var mode = SortMode.ascending;
    list_sort.listSort(&mode, &head, cmpByKey);

    var keys: [entries.len]i32 = undefined;
    var ordinals: [entries.len]usize = undefined;
    var len = try collectKeys(&head, &keys);
    try std.testing.expectEqualSlices(i32, &.{ 0, 1, 2, 3, 4, 5, 6, 7, 8, 9 }, keys[0..len]);

    while (!list_sort.listEmpty(&head)) {
        const low = head.next.?;
        list_sort.listDel(low);
        try std.testing.expect(low.next == null);
        try std.testing.expect(low.prev == null);
        list_sort.listAddTail(low, &lows);

        if (list_sort.listEmpty(&head)) break;

        const high = head.prev.?;
        list_sort.listDel(high);
        try std.testing.expect(high.next == null);
        try std.testing.expect(high.prev == null);
        list_sort.listAddTail(high, &highs);
    }
    try expectEmpty(&head);

    len = try collectKeys(&lows, &keys);
    try std.testing.expectEqualSlices(i32, &.{ 0, 1, 2, 3, 4 }, keys[0..len]);
    len = try collectKeys(&highs, &keys);
    try std.testing.expectEqualSlices(i32, &.{ 9, 8, 7, 6, 5 }, keys[0..len]);

    mode = .descending;
    list_sort.listSort(&mode, &lows, cmpByKey);
    mode = .ascending;
    list_sort.listSort(&mode, &highs, cmpByKey);

    len = try collectKeys(&lows, &keys);
    try std.testing.expectEqualSlices(i32, &.{ 4, 3, 2, 1, 0 }, keys[0..len]);
    len = try collectKeys(&highs, &keys);
    try std.testing.expectEqualSlices(i32, &.{ 5, 6, 7, 8, 9 }, keys[0..len]);

    while (!list_sort.listEmpty(&lows) or !list_sort.listEmpty(&highs)) {
        if (!list_sort.listEmpty(&lows)) {
            const node = lows.next.?;
            list_sort.listDel(node);
            try std.testing.expect(node.next == null);
            try std.testing.expect(node.prev == null);
            list_sort.listAddTail(node, &head);
        }
        if (!list_sort.listEmpty(&highs)) {
            const node = highs.next.?;
            list_sort.listDel(node);
            try std.testing.expect(node.next == null);
            try std.testing.expect(node.prev == null);
            list_sort.listAddTail(node, &head);
        }
    }
    try expectEmpty(&lows);
    try expectEmpty(&highs);

    len = try collectKeys(&head, &keys);
    try std.testing.expectEqualSlices(i32, &.{ 4, 5, 3, 6, 2, 7, 1, 8, 0, 9 }, keys[0..len]);
    len = try collectOrdinals(&head, &ordinals);
    try std.testing.expectEqualSlices(usize, &.{ 2, 6, 5, 0, 3, 7, 1, 4, 8, 9 }, ordinals[0..len]);

    list_sort.listSort(null, &head, cmpAllTies);
    len = try collectKeys(&head, &keys);
    try std.testing.expectEqualSlices(i32, &.{ 4, 5, 3, 6, 2, 7, 1, 8, 0, 9 }, keys[0..len]);
    len = try collectOrdinals(&head, &ordinals);
    try std.testing.expectEqualSlices(usize, &.{ 2, 6, 5, 0, 3, 7, 1, 4, 8, 9 }, ordinals[0..len]);
    try std.testing.expect(head.next == &entries[2].node);
    try std.testing.expect(head.prev == &entries[9].node);

    var reverse: [entries.len]usize = undefined;
    var reverse_len: usize = 0;
    var current = head.prev;
    while (current != &head) : (current = current.?.prev) {
        const entry: *const Entry = @fieldParentPtr("node", current.?);
        reverse[reverse_len] = entry.ordinal;
        reverse_len += 1;
    }
    try std.testing.expectEqualSlices(usize, &.{ 9, 8, 4, 1, 7, 3, 0, 5, 6, 2 }, reverse[0..reverse_len]);
}
