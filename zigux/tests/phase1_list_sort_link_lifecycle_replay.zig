const std = @import("std");
const list_sort = @import("list_sort");

const ListHead = list_sort.ListHead;

const Entry = struct {
    key: i32,
    ordinal: usize,
    node: ListHead = .{},
};

fn cmpKey(_: ?*anyopaque, a: *const ListHead, b: *const ListHead) i32 {
    const lhs: *const Entry = @fieldParentPtr("node", a);
    const rhs: *const Entry = @fieldParentPtr("node", b);
    if (lhs.key < rhs.key) return -1;
    if (lhs.key > rhs.key) return 1;
    return 0;
}

fn expectForward(head: *const ListHead, expected: []const usize) !void {
    var idx: usize = 0;
    var current = head.next;
    while (current != head) : (current = current.?.next) {
        const node = current.?;
        const entry: *const Entry = @fieldParentPtr("node", node);
        try std.testing.expect(idx < expected.len);
        try std.testing.expectEqual(expected[idx], entry.ordinal);
        try std.testing.expect(node.next.?.prev == node);
        try std.testing.expect(node.prev.?.next == node);
        idx += 1;
    }
    try std.testing.expectEqual(expected.len, idx);
}

fn expectBackward(head: *const ListHead, expected: []const usize) !void {
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

test "list add and delete maintain circular links" {
    var head: ListHead = .{};
    head.init();
    var entries = [_]Entry{
        .{ .key = 3, .ordinal = 0 },
        .{ .key = 1, .ordinal = 1 },
        .{ .key = 2, .ordinal = 2 },
    };

    for (&entries) |*entry| list_sort.listAddTail(&entry.node, &head);
    try expectForward(&head, &.{ 0, 1, 2 });
    try expectBackward(&head, &.{ 2, 1, 0 });

    list_sort.listDel(&entries[1].node);
    try std.testing.expect(entries[1].node.next == null);
    try std.testing.expect(entries[1].node.prev == null);
    try expectForward(&head, &.{ 0, 2 });
    try expectBackward(&head, &.{ 2, 0 });

    list_sort.listAdd(&entries[1].node, &head);
    try expectForward(&head, &.{ 1, 0, 2 });
    try expectBackward(&head, &.{ 2, 0, 1 });
    try std.testing.expect(head.next == &entries[1].node);
    try std.testing.expect(head.prev == &entries[2].node);
}

test "single entry delete resets list to empty" {
    var head: ListHead = .{};
    head.init();
    var entry = Entry{ .key = 9, .ordinal = 0 };

    list_sort.listAddTail(&entry.node, &head);
    try expectForward(&head, &.{0});

    list_sort.listDel(&entry.node);
    try std.testing.expect(list_sort.listEmpty(&head));
    try std.testing.expect(entry.node.next == null);
    try std.testing.expect(entry.node.prev == null);
    try std.testing.expect(head.next == &head);
    try std.testing.expect(head.prev == &head);
}

test "deleted node can be reinserted before sorting" {
    var head: ListHead = .{};
    head.init();
    var entries = [_]Entry{
        .{ .key = 4, .ordinal = 0 },
        .{ .key = 1, .ordinal = 1 },
        .{ .key = 3, .ordinal = 2 },
        .{ .key = 1, .ordinal = 3 },
    };

    for (&entries) |*entry| list_sort.listAddTail(&entry.node, &head);
    list_sort.listDel(&entries[2].node);
    list_sort.listAddTail(&entries[2].node, &head);

    try expectForward(&head, &.{ 0, 1, 3, 2 });
    list_sort.listSort(null, &head, cmpKey);
    try expectForward(&head, &.{ 1, 3, 2, 0 });
    try expectBackward(&head, &.{ 0, 2, 3, 1 });
    try std.testing.expect(head.next == &entries[1].node);
    try std.testing.expect(head.prev == &entries[0].node);
}
