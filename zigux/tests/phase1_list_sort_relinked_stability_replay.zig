const std = @import("std");
const list_sort = @import("list_sort");

const Entry = struct {
    key: i32,
    ordinal: usize,
    node: list_sort.ListHead = .{},
};

fn triCmp(_: ?*anyopaque, a: *const list_sort.ListHead, b: *const list_sort.ListHead) i32 {
    const lhs: *const Entry = @fieldParentPtr("node", a);
    const rhs: *const Entry = @fieldParentPtr("node", b);
    if (lhs.key < rhs.key) return -1;
    if (lhs.key > rhs.key) return 1;
    return 0;
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

test "list sort stability follows relinked circular traversal" {
    var head: list_sort.ListHead = .{};
    head.init();

    var entries = [_]Entry{
        .{ .key = 4, .ordinal = 0 },
        .{ .key = 2, .ordinal = 1 },
        .{ .key = 4, .ordinal = 2 },
        .{ .key = 1, .ordinal = 3 },
        .{ .key = 2, .ordinal = 4 },
        .{ .key = 3, .ordinal = 5 },
        .{ .key = 1, .ordinal = 6 },
        .{ .key = 3, .ordinal = 7 },
    };

    for (&entries) |*entry| {
        list_sort.listAddTail(&entry.node, &head);
    }

    list_sort.listSort(null, &head, triCmp);

    var ordinals: [entries.len]usize = undefined;
    var count = try collectOrdinals(&head, &ordinals);
    try std.testing.expectEqualSlices(
        usize,
        &.{ 3, 6, 1, 4, 5, 7, 0, 2 },
        ordinals[0..count],
    );

    list_sort.listDel(&entries[4].node);
    list_sort.listDel(&entries[6].node);
    try std.testing.expect(entries[4].node.next == null);
    try std.testing.expect(entries[4].node.prev == null);
    try std.testing.expect(entries[6].node.next == null);
    try std.testing.expect(entries[6].node.prev == null);

    list_sort.listAdd(&entries[4].node, &head);
    list_sort.listAddTail(&entries[6].node, &head);

    count = try collectOrdinals(&head, &ordinals);
    try std.testing.expectEqualSlices(
        usize,
        &.{ 4, 3, 1, 5, 7, 0, 2, 6 },
        ordinals[0..count],
    );

    list_sort.listSort(null, &head, triCmp);

    count = try collectOrdinals(&head, &ordinals);
    try std.testing.expectEqualSlices(
        usize,
        &.{ 3, 6, 4, 1, 5, 7, 0, 2 },
        ordinals[0..count],
    );
    try std.testing.expect(head.next == &entries[3].node);
    try std.testing.expect(head.prev == &entries[2].node);
}
