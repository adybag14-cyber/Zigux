const std = @import("std");
const list_sort = @import("list_sort");

const Entry = struct {
    key: i32,
    ordinal: usize,
    node: list_sort.ListHead = .{},
};

fn cmpByKey(_: ?*anyopaque, a: *const list_sort.ListHead, b: *const list_sort.ListHead) i32 {
    const lhs: *const Entry = @fieldParentPtr("node", a);
    const rhs: *const Entry = @fieldParentPtr("node", b);
    if (lhs.key < rhs.key) return -1;
    if (lhs.key > rhs.key) return 1;
    return 0;
}

fn collectForward(head: *const list_sort.ListHead, keys: []i32, ordinals: []usize) !usize {
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

fn collectReverse(head: *const list_sort.ListHead, ordinals: []usize) usize {
    var idx: usize = 0;
    var current = head.prev;
    while (current != head) : (current = current.?.prev) {
        const entry: *const Entry = @fieldParentPtr("node", current.?);
        ordinals[idx] = entry.ordinal;
        idx += 1;
    }
    return idx;
}

test "list_sort preserves stable order after mixed head and tail insertion" {
    var head: list_sort.ListHead = .{};
    head.init();

    var entries = [_]Entry{
        .{ .key = 4, .ordinal = 0 },
        .{ .key = 1, .ordinal = 1 },
        .{ .key = 3, .ordinal = 2 },
        .{ .key = 1, .ordinal = 3 },
        .{ .key = 2, .ordinal = 4 },
        .{ .key = 4, .ordinal = 5 },
        .{ .key = 2, .ordinal = 6 },
        .{ .key = 3, .ordinal = 7 },
    };

    list_sort.listAddTail(&entries[0].node, &head);
    list_sort.listAdd(&entries[1].node, &head);
    list_sort.listAddTail(&entries[2].node, &head);
    list_sort.listAdd(&entries[3].node, &head);
    list_sort.listAddTail(&entries[4].node, &head);
    list_sort.listAdd(&entries[5].node, &head);
    list_sort.listAddTail(&entries[6].node, &head);
    list_sort.listAdd(&entries[7].node, &head);

    var pre_keys: [entries.len]i32 = undefined;
    var pre_ordinals: [entries.len]usize = undefined;
    const pre_count = try collectForward(&head, &pre_keys, &pre_ordinals);
    try std.testing.expectEqualSlices(usize, &.{ 7, 5, 3, 1, 0, 2, 4, 6 }, pre_ordinals[0..pre_count]);
    try std.testing.expect(head.next == &entries[7].node);
    try std.testing.expect(head.prev == &entries[6].node);

    list_sort.listSort(null, &head, cmpByKey);

    var keys: [entries.len]i32 = undefined;
    var ordinals: [entries.len]usize = undefined;
    const count = try collectForward(&head, &keys, &ordinals);

    try std.testing.expectEqualSlices(i32, &.{ 1, 1, 2, 2, 3, 3, 4, 4 }, keys[0..count]);
    try std.testing.expectEqualSlices(usize, &.{ 3, 1, 4, 6, 7, 2, 5, 0 }, ordinals[0..count]);
    try std.testing.expect(head.next == &entries[3].node);
    try std.testing.expect(head.prev == &entries[0].node);

    var reverse_ordinals: [entries.len]usize = undefined;
    const reverse_count = collectReverse(&head, &reverse_ordinals);
    try std.testing.expectEqualSlices(usize, &.{ 0, 5, 2, 7, 6, 4, 1, 3 }, reverse_ordinals[0..reverse_count]);
}
