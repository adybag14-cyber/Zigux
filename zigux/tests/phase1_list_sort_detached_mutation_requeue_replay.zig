const std = @import("std");
const list_sort = @import("list_sort");

const ListHead = list_sort.ListHead;

const Entry = struct {
    key: i32,
    ordinal: usize,
    node: ListHead = .{},
};

fn ascending(_: ?*anyopaque, a: *const ListHead, b: *const ListHead) i32 {
    const lhs: *const Entry = @fieldParentPtr("node", a);
    const rhs: *const Entry = @fieldParentPtr("node", b);

    if (lhs.key < rhs.key) return -1;
    if (lhs.key > rhs.key) return 1;
    return 0;
}

fn collectForward(head: *ListHead, keys: []i32, ordinals: []usize) !usize {
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

fn collectReverse(head: *ListHead, ordinals: []usize) !usize {
    var idx: usize = 0;
    var current = head.prev;
    while (current != head) : (current = current.?.prev) {
        const entry: *const Entry = @fieldParentPtr("node", current.?);
        ordinals[idx] = entry.ordinal;
        idx += 1;
    }
    return idx;
}

test "list sort accepts detached key mutation before alternating-end requeue" {
    var head: ListHead = .{};
    head.init();

    var entries = [_]Entry{
        .{ .key = 5, .ordinal = 0 },
        .{ .key = -2, .ordinal = 1 },
        .{ .key = 8, .ordinal = 2 },
        .{ .key = 5, .ordinal = 3 },
        .{ .key = 0, .ordinal = 4 },
        .{ .key = -2, .ordinal = 5 },
        .{ .key = 3, .ordinal = 6 },
        .{ .key = 8, .ordinal = 7 },
        .{ .key = 1, .ordinal = 8 },
        .{ .key = 3, .ordinal = 9 },
        .{ .key = 6, .ordinal = 10 },
        .{ .key = 1, .ordinal = 11 },
    };

    for (&entries) |*entry| list_sort.listAddTail(&entry.node, &head);

    list_sort.listSort(null, &head, ascending);

    var keys: [entries.len]i32 = undefined;
    var ordinals: [entries.len]usize = undefined;
    const first_count = try collectForward(&head, &keys, &ordinals);
    try std.testing.expectEqual(entries.len, first_count);
    try std.testing.expectEqualSlices(i32, &.{ -2, -2, 0, 1, 1, 3, 3, 5, 5, 6, 8, 8 }, keys[0..first_count]);
    try std.testing.expectEqualSlices(usize, &.{ 1, 5, 4, 8, 11, 6, 9, 0, 3, 10, 2, 7 }, ordinals[0..first_count]);

    var detached: [4]*Entry = undefined;
    var detached_count: usize = 0;
    var current = head.next;
    while (current != &head) {
        const next = current.?.next;
        const entry: *Entry = @fieldParentPtr("node", current.?);
        if (entry.ordinal % 3 == 1) {
            list_sort.listDel(&entry.node);
            try std.testing.expect(entry.node.next == null);
            try std.testing.expect(entry.node.prev == null);
            detached[detached_count] = entry;
            detached_count += 1;
        }
        current = next;
    }

    try std.testing.expectEqual(@as(usize, 4), detached_count);
    try std.testing.expectEqual(@as(usize, 1), detached[0].ordinal);
    try std.testing.expectEqual(@as(usize, 4), detached[1].ordinal);
    try std.testing.expectEqual(@as(usize, 10), detached[2].ordinal);
    try std.testing.expectEqual(@as(usize, 7), detached[3].ordinal);

    entries[1].key = 7;
    entries[4].key = -3;
    entries[7].key = 4;
    entries[10].key = -1;

    for (detached[0..detached_count], 0..) |entry, idx| {
        if ((idx & 1) == 0) {
            list_sort.listAdd(&entry.node, &head);
        } else {
            list_sort.listAddTail(&entry.node, &head);
        }
    }

    list_sort.listSort(null, &head, ascending);

    const final_count = try collectForward(&head, &keys, &ordinals);
    try std.testing.expectEqual(entries.len, final_count);
    try std.testing.expectEqualSlices(i32, &.{ -3, -2, -1, 1, 1, 3, 3, 4, 5, 5, 7, 8 }, keys[0..final_count]);
    try std.testing.expectEqualSlices(usize, &.{ 4, 5, 10, 8, 11, 6, 9, 7, 0, 3, 1, 2 }, ordinals[0..final_count]);
    try std.testing.expect(head.next == &entries[4].node);
    try std.testing.expect(head.prev == &entries[2].node);

    var reverse_ordinals: [entries.len]usize = undefined;
    const reverse_count = try collectReverse(&head, &reverse_ordinals);
    try std.testing.expectEqual(entries.len, reverse_count);
    try std.testing.expectEqualSlices(usize, &.{ 2, 1, 3, 0, 7, 9, 6, 11, 8, 10, 5, 4 }, reverse_ordinals[0..reverse_count]);
}
