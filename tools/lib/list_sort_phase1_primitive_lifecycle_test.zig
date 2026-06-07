const std = @import("std");
const list_sort = @import("list_sort");

const Entry = struct {
    ordinal: usize,
    node: list_sort.ListHead = .{},
};

fn expectForward(head: *const list_sort.ListHead, expected: []const usize) !void {
    var idx: usize = 0;
    var current = head.next;
    while (current != head) : (current = current.?.next) {
        const entry: *const Entry = @fieldParentPtr("node", current.?);
        try std.testing.expect(idx < expected.len);
        try std.testing.expectEqual(expected[idx], entry.ordinal);
        try std.testing.expect(current.?.next.?.prev == current.?);
        try std.testing.expect(current.?.prev.?.next == current.?);
        idx += 1;
    }
    try std.testing.expectEqual(expected.len, idx);
}

fn expectReverse(head: *const list_sort.ListHead, expected: []const usize) !void {
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

fn expectDetached(entry: *const Entry) !void {
    try std.testing.expect(entry.node.next == null);
    try std.testing.expect(entry.node.prev == null);
}

test "list primitives preserve circular links through detach and reuse" {
    var head: list_sort.ListHead = .{};
    head.init();
    try std.testing.expect(list_sort.listEmpty(&head));

    var entries = [_]Entry{
        .{ .ordinal = 0 },
        .{ .ordinal = 1 },
        .{ .ordinal = 2 },
        .{ .ordinal = 3 },
    };

    list_sort.listAddTail(&entries[1].node, &head);
    list_sort.listAdd(&entries[0].node, &head);
    list_sort.listAddTail(&entries[2].node, &head);
    list_sort.listAdd(&entries[3].node, &entries[1].node);

    try expectForward(&head, &.{ 0, 1, 3, 2 });
    try expectReverse(&head, &.{ 2, 3, 1, 0 });
    try std.testing.expect(!list_sort.listEmpty(&head));

    list_sort.listDel(&entries[1].node);
    try expectDetached(&entries[1]);
    try expectForward(&head, &.{ 0, 3, 2 });
    try expectReverse(&head, &.{ 2, 3, 0 });

    list_sort.listDel(&entries[0].node);
    list_sort.listDel(&entries[3].node);
    list_sort.listDel(&entries[2].node);
    try std.testing.expect(list_sort.listEmpty(&head));
    for (&entries) |*entry| {
        try expectDetached(entry);
    }

    list_sort.listAddTail(&entries[2].node, &head);
    list_sort.listAddTail(&entries[1].node, &head);
    list_sort.listAdd(&entries[0].node, &head);
    list_sort.listAddTail(&entries[3].node, &head);

    try expectForward(&head, &.{ 0, 2, 1, 3 });
    try expectReverse(&head, &.{ 3, 1, 2, 0 });
}
