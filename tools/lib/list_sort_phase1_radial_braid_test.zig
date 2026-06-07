const std = @import("std");
const list_sort = @import("list_sort");

const ListHead = list_sort.ListHead;

const Entry = struct {
    key: i32,
    ordinal: usize,
    node: ListHead = .{},
};

const SortMode = enum { ascending, descending, ties };

fn entryFromNode(node: *const ListHead) *const Entry {
    return @fieldParentPtr("node", node);
}

fn cmpByMode(priv: ?*anyopaque, a: *const ListHead, b: *const ListHead) i32 {
    const mode: *const SortMode = @ptrCast(@alignCast(priv.?));
    const lhs = entryFromNode(a);
    const rhs = entryFromNode(b);

    if (mode.* == .ties or lhs.key == rhs.key) return 0;

    const ascending = lhs.key < rhs.key;
    return if (mode.* == .ascending)
        (if (ascending) -5 else 7)
    else
        (if (ascending) 11 else -13);
}

fn expectDetached(node: *const ListHead) !void {
    try std.testing.expect(node.next == null);
    try std.testing.expect(node.prev == null);
}

fn expectCircular(head: *ListHead, expected: []const usize) !void {
    var idx: usize = 0;
    var current = head.next;
    while (current != head) : (current = current.?.next) {
        const entry = entryFromNode(current.?);
        try std.testing.expectEqual(expected[idx], entry.ordinal);
        try std.testing.expect(current.?.next.?.prev == current.?);
        try std.testing.expect(current.?.prev.?.next == current.?);
        idx += 1;
    }
    try std.testing.expectEqual(expected.len, idx);

    idx = expected.len;
    current = head.prev;
    while (current != head) : (current = current.?.prev) {
        idx -= 1;
        const entry = entryFromNode(current.?);
        try std.testing.expectEqual(expected[idx], entry.ordinal);
    }
    try std.testing.expectEqual(@as(usize, 0), idx);
}

fn popFront(source: *ListHead) !?*ListHead {
    if (list_sort.listEmpty(source)) return null;
    const node = source.next.?;
    list_sort.listDel(node);
    try expectDetached(node);
    return node;
}

fn popBack(source: *ListHead) !?*ListHead {
    if (list_sort.listEmpty(source)) return null;
    const node = source.prev.?;
    list_sort.listDel(node);
    try expectDetached(node);
    return node;
}

fn appendIfPresent(target: *ListHead, maybe_node: ?*ListHead) void {
    if (maybe_node) |node| {
        list_sort.listAddTail(node, target);
    }
}

test "list_sort radial braid staging preserves links and all-ties order" {
    var entries = [_]Entry{
        .{ .key = 5, .ordinal = 0 },
        .{ .key = 1, .ordinal = 1 },
        .{ .key = 4, .ordinal = 2 },
        .{ .key = 1, .ordinal = 3 },
        .{ .key = 3, .ordinal = 4 },
        .{ .key = 2, .ordinal = 5 },
        .{ .key = 5, .ordinal = 6 },
        .{ .key = 0, .ordinal = 7 },
        .{ .key = 3, .ordinal = 8 },
        .{ .key = 2, .ordinal = 9 },
        .{ .key = 4, .ordinal = 10 },
        .{ .key = 0, .ordinal = 11 },
        .{ .key = 6, .ordinal = 12 },
        .{ .key = 1, .ordinal = 13 },
        .{ .key = 6, .ordinal = 14 },
    };

    var head: ListHead = .{};
    head.init();
    for (&entries) |*entry| list_sort.listAddTail(&entry.node, &head);

    var mode = SortMode.ascending;
    list_sort.listSort(&mode, &head, cmpByMode);
    try expectCircular(&head, &.{ 7, 11, 1, 3, 13, 5, 9, 4, 8, 2, 10, 0, 6, 12, 14 });

    var spokes = [_]ListHead{ .{}, .{}, .{} };
    for (&spokes) |*spoke| spoke.init();

    var rank: usize = 0;
    while (!list_sort.listEmpty(&head)) : (rank += 1) {
        const node = (try popFront(&head)).?;
        list_sort.listAddTail(node, &spokes[rank % spokes.len]);
    }
    try std.testing.expectEqual(@as(usize, entries.len), rank);
    try std.testing.expect(list_sort.listEmpty(&head));
    try expectCircular(&spokes[0], &.{ 7, 3, 9, 2, 6 });
    try expectCircular(&spokes[1], &.{ 11, 13, 4, 10, 12 });
    try expectCircular(&spokes[2], &.{ 1, 5, 8, 0, 14 });

    mode = .descending;
    for (&spokes) |*spoke| list_sort.listSort(&mode, spoke, cmpByMode);
    try expectCircular(&spokes[0], &.{ 6, 2, 9, 3, 7 });
    try expectCircular(&spokes[1], &.{ 12, 10, 4, 13, 11 });
    try expectCircular(&spokes[2], &.{ 14, 0, 8, 5, 1 });

    while (!list_sort.listEmpty(&spokes[0]) or !list_sort.listEmpty(&spokes[1]) or !list_sort.listEmpty(&spokes[2])) {
        appendIfPresent(&head, try popFront(&spokes[0]));
        appendIfPresent(&head, try popBack(&spokes[1]));
        appendIfPresent(&head, try popFront(&spokes[2]));
        appendIfPresent(&head, try popFront(&spokes[1]));
        appendIfPresent(&head, try popBack(&spokes[2]));
        appendIfPresent(&head, try popBack(&spokes[0]));
    }
    try expectCircular(&head, &.{ 6, 11, 14, 12, 1, 7, 2, 13, 0, 10, 5, 3, 9, 4, 8 });
    for (&spokes) |*spoke| try std.testing.expect(list_sort.listEmpty(spoke));

    mode = .ties;
    list_sort.listSort(&mode, &head, cmpByMode);
    try expectCircular(&head, &.{ 6, 11, 14, 12, 1, 7, 2, 13, 0, 10, 5, 3, 9, 4, 8 });
    try std.testing.expect(head.next == &entries[6].node);
    try std.testing.expect(head.prev == &entries[8].node);
}
