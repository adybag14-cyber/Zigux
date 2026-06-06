const std = @import("std");
const list_sort = @import("list_sort");

const Entry = struct {
    key: i32,
    ordinal: usize,
    node: list_sort.ListHead = .{},
};

const SortMode = enum { ascending, descending };

fn compareByMode(priv: ?*anyopaque, a: *const list_sort.ListHead, b: *const list_sort.ListHead) i32 {
    const mode: *const SortMode = @ptrCast(@alignCast(priv.?));
    const lhs: *const Entry = @fieldParentPtr("node", a);
    const rhs: *const Entry = @fieldParentPtr("node", b);

    if (lhs.key == rhs.key) return 0;
    const ascending = lhs.key < rhs.key;
    return if (mode.* == .ascending)
        (if (ascending) -1 else 1)
    else
        (if (ascending) 1 else -1);
}

fn compareAllTies(_: ?*anyopaque, _: *const list_sort.ListHead, _: *const list_sort.ListHead) i32 {
    return 0;
}

fn appendAll(head: *list_sort.ListHead, entries: []Entry) void {
    for (entries) |*entry| {
        list_sort.listAddTail(&entry.node, head);
    }
}

fn popFront(head: *list_sort.ListHead) ?*list_sort.ListHead {
    if (list_sort.listEmpty(head)) return null;
    const node = head.next.?;
    list_sort.listDel(node);
    return node;
}

fn collectOrdinals(head: *list_sort.ListHead, out: []usize) !usize {
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

fn collectKeys(head: *list_sort.ListHead, out: []i32) !usize {
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

fn expectOrdinals(head: *list_sort.ListHead, expected: []const usize) !void {
    var ordinals: [16]usize = undefined;
    const len = try collectOrdinals(head, &ordinals);
    try std.testing.expectEqual(expected.len, len);
    try std.testing.expectEqualSlices(usize, expected, ordinals[0..len]);
}

test "phase1 list_sort rail merge replay preserves detached rail lifecycle" {
    var head: list_sort.ListHead = .{};
    var left_rail: list_sort.ListHead = .{};
    var right_rail: list_sort.ListHead = .{};
    head.init();
    left_rail.init();
    right_rail.init();

    var entries = [_]Entry{
        .{ .key = 5, .ordinal = 0 },
        .{ .key = 1, .ordinal = 1 },
        .{ .key = 7, .ordinal = 2 },
        .{ .key = 3, .ordinal = 3 },
        .{ .key = 1, .ordinal = 4 },
        .{ .key = 6, .ordinal = 5 },
        .{ .key = 4, .ordinal = 6 },
        .{ .key = 2, .ordinal = 7 },
        .{ .key = 7, .ordinal = 8 },
        .{ .key = 3, .ordinal = 9 },
    };
    appendAll(&head, &entries);

    var mode = SortMode.ascending;
    list_sort.listSort(&mode, &head, compareByMode);

    var sorted_keys: [entries.len]i32 = undefined;
    const sorted_len = try collectKeys(&head, &sorted_keys);
    try std.testing.expectEqual(entries.len, sorted_len);
    try std.testing.expectEqualSlices(i32, &.{ 1, 1, 2, 3, 3, 4, 5, 6, 7, 7 }, sorted_keys[0..sorted_len]);
    try expectOrdinals(&head, &.{ 1, 4, 7, 3, 9, 6, 0, 5, 2, 8 });

    var sorted_rank: usize = 0;
    while (popFront(&head)) |node| : (sorted_rank += 1) {
        try std.testing.expect(node.next == null);
        try std.testing.expect(node.prev == null);
        if ((sorted_rank & 1) == 0) {
            list_sort.listAddTail(node, &left_rail);
        } else {
            list_sort.listAddTail(node, &right_rail);
        }
    }
    try std.testing.expect(list_sort.listEmpty(&head));
    try expectOrdinals(&left_rail, &.{ 1, 7, 9, 0, 2 });
    try expectOrdinals(&right_rail, &.{ 4, 3, 6, 5, 8 });

    mode = .descending;
    list_sort.listSort(&mode, &left_rail, compareByMode);
    mode = .ascending;
    list_sort.listSort(&mode, &right_rail, compareByMode);
    try expectOrdinals(&left_rail, &.{ 2, 0, 9, 7, 1 });
    try expectOrdinals(&right_rail, &.{ 4, 3, 6, 5, 8 });

    while (true) {
        const right = popFront(&right_rail);
        if (right) |node| {
            try std.testing.expect(node.next == null);
            try std.testing.expect(node.prev == null);
            list_sort.listAddTail(node, &head);
        }

        const left = popFront(&left_rail);
        if (left) |node| {
            try std.testing.expect(node.next == null);
            try std.testing.expect(node.prev == null);
            list_sort.listAddTail(node, &head);
        }

        if (right == null and left == null) break;
    }
    try std.testing.expect(list_sort.listEmpty(&left_rail));
    try std.testing.expect(list_sort.listEmpty(&right_rail));
    try expectOrdinals(&head, &.{ 4, 2, 3, 0, 6, 9, 5, 7, 8, 1 });

    list_sort.listSort(null, &head, compareAllTies);
    try expectOrdinals(&head, &.{ 4, 2, 3, 0, 6, 9, 5, 7, 8, 1 });
    try std.testing.expect(head.next == &entries[4].node);
    try std.testing.expect(head.prev == &entries[1].node);
    try std.testing.expect(entries[4].node.prev == &head);
    try std.testing.expect(entries[1].node.next == &head);
}
