const std = @import("std");
const list_sort = @import("list_sort");

const Entry = struct {
    key: i32,
    ordinal: usize,
    node: list_sort.ListHead = .{},
};

fn ascendingKey(_: ?*anyopaque, a: *const list_sort.ListHead, b: *const list_sort.ListHead) i32 {
    const lhs: *const Entry = @fieldParentPtr("node", a);
    const rhs: *const Entry = @fieldParentPtr("node", b);
    if (lhs.key < rhs.key) return -1;
    if (lhs.key > rhs.key) return 1;
    return 0;
}

fn moduloBucket(_: ?*anyopaque, a: *const list_sort.ListHead, b: *const list_sort.ListHead) i32 {
    const lhs: *const Entry = @fieldParentPtr("node", a);
    const rhs: *const Entry = @fieldParentPtr("node", b);
    const lhs_bucket = @mod(lhs.key, 3);
    const rhs_bucket = @mod(rhs.key, 3);
    if (lhs_bucket == rhs_bucket) return 0;
    return if (lhs_bucket < rhs_bucket) -1 else 1;
}

fn collectForward(head: *const list_sort.ListHead, keys: []i32, ordinals: []usize) !usize {
    var count: usize = 0;
    var current = head.next;
    while (current != head) : (current = current.?.next) {
        const entry: *const Entry = @fieldParentPtr("node", current.?);
        keys[count] = entry.key;
        ordinals[count] = entry.ordinal;
        try std.testing.expect(current.?.next.?.prev == current.?);
        try std.testing.expect(current.?.prev.?.next == current.?);
        count += 1;
    }
    return count;
}

fn collectBackward(head: *const list_sort.ListHead, ordinals: []usize) !usize {
    var count: usize = 0;
    var current = head.prev;
    while (current != head) : (current = current.?.prev) {
        const entry: *const Entry = @fieldParentPtr("node", current.?);
        ordinals[count] = entry.ordinal;
        count += 1;
    }
    return count;
}

test "list_sort keeps bucket stability after sorted tail splice" {
    var head: list_sort.ListHead = .{};
    head.init();
    var entries = [_]Entry{
        .{ .key = 4, .ordinal = 4 },
        .{ .key = 1, .ordinal = 1 },
        .{ .key = 8, .ordinal = 8 },
        .{ .key = 0, .ordinal = 0 },
        .{ .key = 6, .ordinal = 6 },
        .{ .key = 3, .ordinal = 3 },
        .{ .key = 9, .ordinal = 9 },
        .{ .key = 2, .ordinal = 2 },
        .{ .key = 7, .ordinal = 7 },
        .{ .key = 5, .ordinal = 5 },
    };

    for (&entries) |*entry| list_sort.listAddTail(&entry.node, &head);
    list_sort.listSort(null, &head, ascendingKey);

    list_sort.listDel(&entries[6].node);
    try std.testing.expect(entries[6].node.next == null);
    try std.testing.expect(entries[6].node.prev == null);
    list_sort.listAdd(&entries[6].node, &head);

    list_sort.listDel(&entries[2].node);
    try std.testing.expect(entries[2].node.next == null);
    try std.testing.expect(entries[2].node.prev == null);
    list_sort.listAdd(&entries[2].node, &head);

    list_sort.listDel(&entries[8].node);
    try std.testing.expect(entries[8].node.next == null);
    try std.testing.expect(entries[8].node.prev == null);
    list_sort.listAdd(&entries[8].node, &head);

    var keys: [10]i32 = undefined;
    var ordinals: [10]usize = undefined;
    var idx = try collectForward(&head, &keys, &ordinals);
    try std.testing.expectEqualSlices(i32, &.{ 7, 8, 9, 0, 1, 2, 3, 4, 5, 6 }, keys[0..idx]);
    try std.testing.expectEqualSlices(usize, &.{ 7, 8, 9, 0, 1, 2, 3, 4, 5, 6 }, ordinals[0..idx]);

    list_sort.listSort(null, &head, moduloBucket);

    idx = try collectForward(&head, &keys, &ordinals);
    try std.testing.expectEqualSlices(i32, &.{ 9, 0, 3, 6, 7, 1, 4, 8, 2, 5 }, keys[0..idx]);
    try std.testing.expectEqualSlices(usize, &.{ 9, 0, 3, 6, 7, 1, 4, 8, 2, 5 }, ordinals[0..idx]);
    try std.testing.expect(head.next == &entries[6].node);
    try std.testing.expect(head.prev == &entries[9].node);

    var reverse_ordinals: [10]usize = undefined;
    const reverse_idx = try collectBackward(&head, &reverse_ordinals);
    try std.testing.expectEqualSlices(usize, &.{ 5, 2, 8, 4, 1, 7, 6, 3, 0, 9 }, reverse_ordinals[0..reverse_idx]);
}
