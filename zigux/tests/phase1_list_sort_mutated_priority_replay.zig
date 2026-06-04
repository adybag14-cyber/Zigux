const std = @import("std");
const list_sort = @import("list_sort");

const ListHead = list_sort.ListHead;

const Entry = struct {
    priority: i32,
    ordinal: usize,
    node: ListHead = .{},
};

fn priorityCmp(_: ?*anyopaque, a: *const ListHead, b: *const ListHead) i32 {
    const lhs: *const Entry = @fieldParentPtr("node", a);
    const rhs: *const Entry = @fieldParentPtr("node", b);
    if (lhs.priority == rhs.priority) return 0;
    return if (lhs.priority < rhs.priority) -1 else 1;
}

fn collectOrdinals(head: *ListHead, comptime len: usize) ![len]usize {
    var ordinals: [len]usize = undefined;
    var idx: usize = 0;
    var current = head.next;
    while (current != head) : (current = current.?.next) {
        const entry: *const Entry = @fieldParentPtr("node", current.?);
        ordinals[idx] = entry.ordinal;
        try std.testing.expect(current.?.next.?.prev == current.?);
        try std.testing.expect(current.?.prev.?.next == current.?);
        idx += 1;
    }
    try std.testing.expectEqual(len, idx);
    return ordinals;
}

fn collectPriorities(head: *ListHead, comptime len: usize) ![len]i32 {
    var priorities: [len]i32 = undefined;
    var idx: usize = 0;
    var current = head.next;
    while (current != head) : (current = current.?.next) {
        const entry: *const Entry = @fieldParentPtr("node", current.?);
        priorities[idx] = entry.priority;
        idx += 1;
    }
    try std.testing.expectEqual(len, idx);
    return priorities;
}

test "list sort preserves current traversal order after in-place priority mutation" {
    var head: ListHead = .{};
    head.init();

    var entries = [_]Entry{
        .{ .priority = 40, .ordinal = 0 },
        .{ .priority = 10, .ordinal = 1 },
        .{ .priority = 30, .ordinal = 2 },
        .{ .priority = 20, .ordinal = 3 },
        .{ .priority = 50, .ordinal = 4 },
        .{ .priority = 15, .ordinal = 5 },
        .{ .priority = 35, .ordinal = 6 },
        .{ .priority = 25, .ordinal = 7 },
        .{ .priority = 45, .ordinal = 8 },
        .{ .priority = 5, .ordinal = 9 },
        .{ .priority = 30, .ordinal = 10 },
        .{ .priority = 20, .ordinal = 11 },
    };

    for (&entries) |*entry| {
        list_sort.listAddTail(&entry.node, &head);
    }

    list_sort.listSort(null, &head, priorityCmp);
    const first_ordinals = try collectOrdinals(&head, entries.len);
    try std.testing.expectEqualSlices(usize, &.{
        9, 1, 5, 3, 11, 7, 2, 10, 6, 0, 8, 4,
    }, &first_ordinals);
    try std.testing.expect(head.next == &entries[9].node);
    try std.testing.expect(head.prev == &entries[4].node);

    const mutated_priorities = [_]i32{
        2, 1, 0, 1, 0, 2, 0, 2, 1, 2, 1, 0,
    };
    for (&entries, mutated_priorities) |*entry, priority| {
        entry.priority = priority;
    }

    list_sort.listSort(null, &head, priorityCmp);

    const second_priorities = try collectPriorities(&head, entries.len);
    try std.testing.expectEqualSlices(i32, &.{
        0, 0, 0, 0, 1, 1, 1, 1, 2, 2, 2, 2,
    }, &second_priorities);

    const second_ordinals = try collectOrdinals(&head, entries.len);
    try std.testing.expectEqualSlices(usize, &.{
        11, 2, 6, 4, 1, 3, 10, 8, 9, 5, 7, 0,
    }, &second_ordinals);
    try std.testing.expect(head.next == &entries[11].node);
    try std.testing.expect(head.prev == &entries[0].node);
    try std.testing.expect(entries[11].node.prev == &head);
    try std.testing.expect(entries[0].node.next == &head);

    var reverse_ordinals: [entries.len]usize = undefined;
    var idx: usize = 0;
    var current = head.prev;
    while (current != &head) : (current = current.?.prev) {
        const entry: *const Entry = @fieldParentPtr("node", current.?);
        reverse_ordinals[idx] = entry.ordinal;
        idx += 1;
    }
    try std.testing.expectEqualSlices(usize, &.{
        0, 7, 5, 9, 8, 10, 3, 1, 4, 6, 2, 11,
    }, reverse_ordinals[0..idx]);
}
