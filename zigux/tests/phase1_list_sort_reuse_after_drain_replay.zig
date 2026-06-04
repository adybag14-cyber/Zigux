const std = @import("std");
const list_sort = @import("list_sort");

const ListHead = list_sort.ListHead;

const Entry = struct {
    key: i32,
    ordinal: usize,
    node: ListHead = .{},
};

fn ascendingCmp(_: ?*anyopaque, a: *const ListHead, b: *const ListHead) i32 {
    const lhs: *const Entry = @fieldParentPtr("node", a);
    const rhs: *const Entry = @fieldParentPtr("node", b);
    if (lhs.key < rhs.key) return -1;
    if (lhs.key > rhs.key) return 1;
    return 0;
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

test "list_sort head can be drained and reused for a new sorted list" {
    var head: ListHead = .{};
    head.init();

    var first = [_]Entry{
        .{ .key = 4, .ordinal = 0 },
        .{ .key = 1, .ordinal = 1 },
        .{ .key = 3, .ordinal = 2 },
        .{ .key = 1, .ordinal = 3 },
        .{ .key = 2, .ordinal = 4 },
    };
    for (&first) |*entry| list_sort.listAddTail(&entry.node, &head);

    list_sort.listSort(null, &head, ascendingCmp);

    var ordinals: [5]usize = undefined;
    const first_len = try collectOrdinals(&head, &ordinals);
    try std.testing.expectEqualSlices(usize, &.{ 1, 3, 4, 2, 0 }, ordinals[0..first_len]);
    try std.testing.expect(head.next == &first[1].node);
    try std.testing.expect(head.prev == &first[0].node);

    while (!list_sort.listEmpty(&head)) {
        const node = head.next.?;
        list_sort.listDel(node);
        try std.testing.expect(node.next == null);
        try std.testing.expect(node.prev == null);
    }
    try std.testing.expect(head.next == &head);
    try std.testing.expect(head.prev == &head);

    var second = [_]Entry{
        .{ .key = 0, .ordinal = 10 },
        .{ .key = -3, .ordinal = 11 },
        .{ .key = 8, .ordinal = 12 },
        .{ .key = -3, .ordinal = 13 },
    };
    for (&second) |*entry| list_sort.listAddTail(&entry.node, &head);

    list_sort.listSort(null, &head, ascendingCmp);

    var reused_ordinals: [4]usize = undefined;
    const second_len = try collectOrdinals(&head, &reused_ordinals);
    try std.testing.expectEqualSlices(usize, &.{ 11, 13, 10, 12 }, reused_ordinals[0..second_len]);
    try std.testing.expect(head.next == &second[1].node);
    try std.testing.expect(head.prev == &second[2].node);

    for (&first) |*entry| {
        try std.testing.expect(entry.node.next == null);
        try std.testing.expect(entry.node.prev == null);
    }
}
