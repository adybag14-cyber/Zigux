const std = @import("std");
const list_sort = @import("list_sort");

const Entry = struct {
    key: i32,
    ordinal: usize,
    node: list_sort.ListHead = .{},
};

const Direction = enum { ascending, descending };

fn appendAll(head: *list_sort.ListHead, entries: []Entry) void {
    for (entries) |*entry| {
        list_sort.listAddTail(&entry.node, head);
    }
}

fn expectForwardOrder(
    head: *list_sort.ListHead,
    expected_keys: []const i32,
    expected_ordinals: []const usize,
) !void {
    try std.testing.expectEqual(expected_keys.len, expected_ordinals.len);

    var idx: usize = 0;
    var current = head.next;
    while (current != head) : (current = current.?.next) {
        const entry: *const Entry = @fieldParentPtr("node", current.?);
        try std.testing.expect(idx < expected_keys.len);
        try std.testing.expectEqual(expected_keys[idx], entry.key);
        try std.testing.expectEqual(expected_ordinals[idx], entry.ordinal);
        try std.testing.expect(current.?.next.?.prev == current.?);
        try std.testing.expect(current.?.prev.?.next == current.?);
        idx += 1;
    }

    try std.testing.expectEqual(expected_keys.len, idx);
}

fn expectBackwardOrdinals(head: *list_sort.ListHead, expected: []const usize) !void {
    var idx: usize = 0;
    var current = head.prev;
    while (current != head) : (current = current.?.prev) {
        const entry: *const Entry = @fieldParentPtr("node", current.?);
        try std.testing.expect(idx < expected.len);
        try std.testing.expectEqual(expected[idx], entry.ordinal);
        idx += 1;
    }

    try std.testing.expectEqual(expected.len, idx);
}

fn directionalCmp(priv: ?*anyopaque, a: *const list_sort.ListHead, b: *const list_sort.ListHead) i32 {
    const direction: *const Direction = @ptrCast(@alignCast(priv.?));
    const lhs: *const Entry = @fieldParentPtr("node", a);
    const rhs: *const Entry = @fieldParentPtr("node", b);
    if (lhs.key == rhs.key) return 0;
    const ascending = lhs.key < rhs.key;
    return if (direction.* == .ascending)
        (if (ascending) -17 else 23)
    else
        (if (ascending) 23 else -17);
}

fn booleanEvenFirst(_: ?*anyopaque, a: *const list_sort.ListHead, b: *const list_sort.ListHead) i32 {
    const lhs: *const Entry = @fieldParentPtr("node", a);
    const rhs: *const Entry = @fieldParentPtr("node", b);
    return @intFromBool(@mod(lhs.key, 2) > @mod(rhs.key, 2));
}

test "list sort keeps stability across mixed repeated comparator passes" {
    var head: list_sort.ListHead = .{};
    head.init();
    var entries = [_]Entry{
        .{ .key = 4, .ordinal = 0 },
        .{ .key = 1, .ordinal = 1 },
        .{ .key = 6, .ordinal = 2 },
        .{ .key = 3, .ordinal = 3 },
        .{ .key = 2, .ordinal = 4 },
        .{ .key = 5, .ordinal = 5 },
        .{ .key = 4, .ordinal = 6 },
        .{ .key = 7, .ordinal = 7 },
        .{ .key = 0, .ordinal = 8 },
        .{ .key = 5, .ordinal = 9 },
    };
    appendAll(&head, &entries);

    var direction = Direction.descending;
    list_sort.listSort(&direction, &head, directionalCmp);
    try expectForwardOrder(
        &head,
        &.{ 7, 6, 5, 5, 4, 4, 3, 2, 1, 0 },
        &.{ 7, 2, 5, 9, 0, 6, 3, 4, 1, 8 },
    );

    list_sort.listSort(null, &head, booleanEvenFirst);
    try expectForwardOrder(
        &head,
        &.{ 6, 4, 4, 2, 0, 7, 5, 5, 3, 1 },
        &.{ 2, 0, 6, 4, 8, 7, 5, 9, 3, 1 },
    );

    direction = .ascending;
    list_sort.listSort(&direction, &head, directionalCmp);
    try expectForwardOrder(
        &head,
        &.{ 0, 1, 2, 3, 4, 4, 5, 5, 6, 7 },
        &.{ 8, 1, 4, 3, 0, 6, 5, 9, 2, 7 },
    );
    try expectBackwardOrdinals(&head, &.{ 7, 2, 9, 5, 6, 0, 3, 4, 1, 8 });
    try std.testing.expect(head.next == &entries[8].node);
    try std.testing.expect(head.prev == &entries[7].node);
}

test "list sort reuses relinked nodes after delete and tail insert" {
    var head: list_sort.ListHead = .{};
    head.init();
    var entries = [_]Entry{
        .{ .key = 10, .ordinal = 0 },
        .{ .key = -2, .ordinal = 1 },
        .{ .key = 4, .ordinal = 2 },
        .{ .key = 10, .ordinal = 3 },
        .{ .key = 0, .ordinal = 4 },
        .{ .key = -2, .ordinal = 5 },
    };
    appendAll(&head, &entries);

    var direction = Direction.ascending;
    list_sort.listSort(&direction, &head, directionalCmp);
    try expectForwardOrder(
        &head,
        &.{ -2, -2, 0, 4, 10, 10 },
        &.{ 1, 5, 4, 2, 0, 3 },
    );

    list_sort.listDel(&entries[4].node);
    list_sort.listAddTail(&entries[4].node, &head);

    direction = .descending;
    list_sort.listSort(&direction, &head, directionalCmp);
    try expectForwardOrder(
        &head,
        &.{ 10, 10, 4, 0, -2, -2 },
        &.{ 0, 3, 2, 4, 1, 5 },
    );
    try expectBackwardOrdinals(&head, &.{ 5, 1, 4, 2, 3, 0 });
    try std.testing.expect(head.next == &entries[0].node);
    try std.testing.expect(head.prev == &entries[5].node);
}
