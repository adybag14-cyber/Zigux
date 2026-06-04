const std = @import("std");
const list_sort = @import("list_sort");

const Entry = struct {
    key: i32,
    ordinal: usize,
    node: list_sort.ListHead = .{},
};

fn compare(_: ?*anyopaque, a: *const list_sort.ListHead, b: *const list_sort.ListHead) i32 {
    const lhs: *const Entry = @fieldParentPtr("node", a);
    const rhs: *const Entry = @fieldParentPtr("node", b);
    if (lhs.key < rhs.key) return -1;
    if (lhs.key > rhs.key) return 1;
    return 0;
}

test "phase1 list_sort replay restores order after segment reinsert" {
    var head: list_sort.ListHead = .{};
    head.init();
    var entries = [_]Entry{
        .{ .key = 4, .ordinal = 0 },
        .{ .key = 1, .ordinal = 1 },
        .{ .key = 3, .ordinal = 2 },
        .{ .key = 2, .ordinal = 3 },
        .{ .key = 3, .ordinal = 4 },
        .{ .key = 0, .ordinal = 5 },
        .{ .key = 2, .ordinal = 6 },
        .{ .key = 5, .ordinal = 7 },
        .{ .key = 1, .ordinal = 8 },
    };
    for (&entries) |*entry| {
        list_sort.listAddTail(&entry.node, &head);
    }

    list_sort.listSort(null, &head, compare);

    list_sort.listDel(&entries[3].node);
    list_sort.listDel(&entries[6].node);
    list_sort.listDel(&entries[2].node);
    list_sort.listAddTail(&entries[3].node, &head);
    list_sort.listAddTail(&entries[6].node, &head);
    list_sort.listAddTail(&entries[2].node, &head);

    list_sort.listSort(null, &head, compare);

    var keys: [9]i32 = undefined;
    var ordinals: [9]usize = undefined;
    var idx: usize = 0;
    var current = head.next;
    while (current != &head) : (current = current.?.next) {
        const entry: *const Entry = @fieldParentPtr("node", current.?);
        keys[idx] = entry.key;
        ordinals[idx] = entry.ordinal;
        try std.testing.expect(current.?.next.?.prev == current.?);
        try std.testing.expect(current.?.prev.?.next == current.?);
        idx += 1;
    }

    try std.testing.expectEqualSlices(i32, &.{ 0, 1, 1, 2, 2, 3, 3, 4, 5 }, keys[0..idx]);
    try std.testing.expectEqualSlices(usize, &.{ 5, 1, 8, 3, 6, 4, 2, 0, 7 }, ordinals[0..idx]);
    try std.testing.expect(head.next == &entries[5].node);
    try std.testing.expect(head.prev == &entries[7].node);
    try std.testing.expect(entries[5].node.prev == &head);
    try std.testing.expect(entries[7].node.next == &head);
}
