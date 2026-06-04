const std = @import("std");
const list_sort = @import("list_sort");

const Entry = struct {
    key: i32,
    ordinal: usize,
    node: list_sort.ListHead = .{},
};

fn cmpAscending(_: ?*anyopaque, a: *const list_sort.ListHead, b: *const list_sort.ListHead) i32 {
    const lhs: *const Entry = @fieldParentPtr("node", a);
    const rhs: *const Entry = @fieldParentPtr("node", b);
    if (lhs.key < rhs.key) return -1;
    if (lhs.key > rhs.key) return 1;
    return 0;
}

fn cmpDescending(_: ?*anyopaque, a: *const list_sort.ListHead, b: *const list_sort.ListHead) i32 {
    return -cmpAscending(null, a, b);
}

fn expectForward(head: *const list_sort.ListHead, expected: []const usize) !void {
    var seen: [16]usize = undefined;
    var idx: usize = 0;
    var current = head.next;
    while (current != head) : (current = current.?.next) {
        const entry: *const Entry = @fieldParentPtr("node", current.?);
        seen[idx] = entry.ordinal;
        try std.testing.expect(current.?.next.?.prev == current.?);
        try std.testing.expect(current.?.prev.?.next == current.?);
        idx += 1;
    }
    try std.testing.expectEqualSlices(usize, expected, seen[0..idx]);
}

fn expectBackward(head: *const list_sort.ListHead, expected: []const usize) !void {
    var seen: [16]usize = undefined;
    var idx: usize = 0;
    var current = head.prev;
    while (current != head) : (current = current.?.prev) {
        const entry: *const Entry = @fieldParentPtr("node", current.?);
        seen[idx] = entry.ordinal;
        idx += 1;
    }
    try std.testing.expectEqualSlices(usize, expected, seen[0..idx]);
}

test "list_sort preserves stable order after delete and tail reinsertion" {
    var head: list_sort.ListHead = .{};
    head.init();

    var entries = [_]Entry{
        .{ .key = 3, .ordinal = 0 },
        .{ .key = 1, .ordinal = 1 },
        .{ .key = 2, .ordinal = 2 },
        .{ .key = 1, .ordinal = 3 },
        .{ .key = 3, .ordinal = 4 },
        .{ .key = 2, .ordinal = 5 },
        .{ .key = 4, .ordinal = 6 },
    };

    for (&entries) |*entry| list_sort.listAddTail(&entry.node, &head);
    list_sort.listSort(null, &head, cmpAscending);
    try expectForward(&head, &.{ 1, 3, 2, 5, 0, 4, 6 });
    try expectBackward(&head, &.{ 6, 4, 0, 5, 2, 3, 1 });

    list_sort.listDel(&entries[3].node);
    try std.testing.expect(entries[3].node.next == null);
    try std.testing.expect(entries[3].node.prev == null);
    try expectForward(&head, &.{ 1, 2, 5, 0, 4, 6 });

    list_sort.listAddTail(&entries[3].node, &head);
    list_sort.listSort(null, &head, cmpAscending);
    try expectForward(&head, &.{ 1, 3, 2, 5, 0, 4, 6 });
    try expectBackward(&head, &.{ 6, 4, 0, 5, 2, 3, 1 });
    try std.testing.expect(head.next == &entries[1].node);
    try std.testing.expect(head.prev == &entries[6].node);
}

test "list_sort can reinsert a detached middle node before descending resort" {
    var head: list_sort.ListHead = .{};
    head.init();

    var entries = [_]Entry{
        .{ .key = -1, .ordinal = 0 },
        .{ .key = 4, .ordinal = 1 },
        .{ .key = 0, .ordinal = 2 },
        .{ .key = 4, .ordinal = 3 },
        .{ .key = -1, .ordinal = 4 },
        .{ .key = 2, .ordinal = 5 },
    };

    for (&entries) |*entry| list_sort.listAddTail(&entry.node, &head);
    list_sort.listSort(null, &head, cmpAscending);
    try expectForward(&head, &.{ 0, 4, 2, 5, 1, 3 });

    list_sort.listDel(&entries[2].node);
    list_sort.listAdd(&entries[2].node, &head);
    list_sort.listSort(null, &head, cmpDescending);

    try expectForward(&head, &.{ 1, 3, 5, 2, 0, 4 });
    try expectBackward(&head, &.{ 4, 0, 2, 5, 3, 1 });
    try std.testing.expect(head.next == &entries[1].node);
    try std.testing.expect(head.prev == &entries[4].node);
}
