const std = @import("std");
const list_sort = @import("list_sort");

const Entry = struct {
    key: i32,
    ordinal: usize,
    node: list_sort.ListHead = .{},
};

const SortMode = enum { ascending, descending };

fn cmpByMode(priv: ?*anyopaque, a: *const list_sort.ListHead, b: *const list_sort.ListHead) i32 {
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

fn collectForward(head: *list_sort.ListHead, keys: []i32, ordinals: []usize) !usize {
    var idx: usize = 0;
    var current = head.next;
    while (current != head) : (current = current.?.next) {
        const entry: *const Entry = @fieldParentPtr("node", current.?);
        keys[idx] = entry.key;
        ordinals[idx] = entry.ordinal;
        try std.testing.expect(current.?.next.?.prev == current.?);
        try std.testing.expect(current.?.prev.?.next == current.?);
        idx += 1;
    }
    return idx;
}

fn collectReverse(head: *list_sort.ListHead, ordinals: []usize) !usize {
    var idx: usize = 0;
    var current = head.prev;
    while (current != head) : (current = current.?.prev) {
        const entry: *const Entry = @fieldParentPtr("node", current.?);
        ordinals[idx] = entry.ordinal;
        try std.testing.expect(current.?.next.?.prev == current.?);
        try std.testing.expect(current.?.prev.?.next == current.?);
        idx += 1;
    }
    return idx;
}

test "list_sort preserves stability after sorted tail splice and re-sort" {
    var head: list_sort.ListHead = .{};
    var tail: list_sort.ListHead = .{};
    head.init();
    tail.init();

    var entries = [_]Entry{
        .{ .key = 6, .ordinal = 0 },
        .{ .key = 1, .ordinal = 1 },
        .{ .key = 4, .ordinal = 2 },
        .{ .key = 1, .ordinal = 3 },
        .{ .key = 5, .ordinal = 4 },
        .{ .key = 2, .ordinal = 5 },
        .{ .key = 6, .ordinal = 6 },
        .{ .key = 3, .ordinal = 7 },
        .{ .key = 2, .ordinal = 8 },
    };

    for (&entries) |*entry| list_sort.listAddTail(&entry.node, &head);

    var mode = SortMode.ascending;
    list_sort.listSort(&mode, &head, cmpByMode);

    var sorted_keys: [9]i32 = undefined;
    var sorted_ordinals: [9]usize = undefined;
    const sorted_count = try collectForward(&head, &sorted_keys, &sorted_ordinals);
    try std.testing.expectEqualSlices(i32, &.{ 1, 1, 2, 2, 3, 4, 5, 6, 6 }, sorted_keys[0..sorted_count]);
    try std.testing.expectEqualSlices(usize, &.{ 1, 3, 5, 8, 7, 2, 4, 0, 6 }, sorted_ordinals[0..sorted_count]);

    const moved_tail = [_]*list_sort.ListHead{
        &entries[4].node,
        &entries[0].node,
        &entries[6].node,
    };
    for (moved_tail) |node| {
        list_sort.listDel(node);
        list_sort.listAddTail(node, &tail);
    }

    list_sort.listSort(&mode, &head, cmpByMode);
    mode = .descending;
    list_sort.listSort(&mode, &tail, cmpByMode);

    try std.testing.expect(head.prev == &entries[2].node);
    try std.testing.expect(tail.next == &entries[0].node);
    try std.testing.expect(tail.prev == &entries[4].node);

    while (!list_sort.listEmpty(&tail)) {
        const node = tail.next.?;
        list_sort.listDel(node);
        list_sort.listAddTail(node, &head);
    }

    mode = .ascending;
    list_sort.listSort(&mode, &head, cmpByMode);

    var final_keys: [9]i32 = undefined;
    var final_ordinals: [9]usize = undefined;
    const final_count = try collectForward(&head, &final_keys, &final_ordinals);
    try std.testing.expectEqualSlices(i32, &.{ 1, 1, 2, 2, 3, 4, 5, 6, 6 }, final_keys[0..final_count]);
    try std.testing.expectEqualSlices(usize, &.{ 1, 3, 5, 8, 7, 2, 4, 0, 6 }, final_ordinals[0..final_count]);

    var reverse_ordinals: [9]usize = undefined;
    const reverse_count = try collectReverse(&head, &reverse_ordinals);
    try std.testing.expectEqualSlices(usize, &.{ 6, 0, 4, 2, 7, 8, 5, 3, 1 }, reverse_ordinals[0..reverse_count]);
    try std.testing.expect(head.next == &entries[1].node);
    try std.testing.expect(head.prev == &entries[6].node);
    try std.testing.expect(list_sort.listEmpty(&tail));
}
