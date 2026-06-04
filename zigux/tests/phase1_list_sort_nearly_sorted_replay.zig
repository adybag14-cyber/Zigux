const std = @import("std");
const list_sort = @import("list_sort");

const ListHead = list_sort.ListHead;

const Entry = struct {
    key: i32,
    ordinal: usize,
    node: ListHead = .{},
};

fn collect(head: *const ListHead, keys: []i32, ordinals: []usize) !usize {
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

fn keyCmp(_: ?*anyopaque, a: *const ListHead, b: *const ListHead) i32 {
    const lhs: *const Entry = @fieldParentPtr("node", a);
    const rhs: *const Entry = @fieldParentPtr("node", b);
    if (lhs.key < rhs.key) return -1;
    if (lhs.key > rhs.key) return 1;
    return 0;
}

fn parityCmp(_: ?*anyopaque, a: *const ListHead, b: *const ListHead) i32 {
    const lhs: *const Entry = @fieldParentPtr("node", a);
    const rhs: *const Entry = @fieldParentPtr("node", b);
    const lhs_even = @mod(lhs.key, 2) == 0;
    const rhs_even = @mod(rhs.key, 2) == 0;
    if (lhs_even == rhs_even) return 0;
    return if (lhs_even) -1 else 1;
}

test "list_sort replays nearly sorted local inversions with stable duplicate carryover" {
    var head: ListHead = .{};
    head.init();

    var entries = [_]Entry{
        .{ .key = 0, .ordinal = 0 },
        .{ .key = 1, .ordinal = 1 },
        .{ .key = 3, .ordinal = 2 },
        .{ .key = 2, .ordinal = 3 },
        .{ .key = 2, .ordinal = 4 },
        .{ .key = 5, .ordinal = 5 },
        .{ .key = 4, .ordinal = 6 },
        .{ .key = 4, .ordinal = 7 },
        .{ .key = 7, .ordinal = 8 },
        .{ .key = 6, .ordinal = 9 },
        .{ .key = 8, .ordinal = 10 },
        .{ .key = 8, .ordinal = 11 },
        .{ .key = 9, .ordinal = 12 },
    };
    for (&entries) |*entry| list_sort.listAddTail(&entry.node, &head);

    list_sort.listSort(null, &head, keyCmp);

    var keys: [entries.len]i32 = undefined;
    var ordinals: [entries.len]usize = undefined;
    const first_len = try collect(&head, &keys, &ordinals);

    try std.testing.expectEqualSlices(i32, &.{ 0, 1, 2, 2, 3, 4, 4, 5, 6, 7, 8, 8, 9 }, keys[0..first_len]);
    try std.testing.expectEqualSlices(usize, &.{ 0, 1, 3, 4, 2, 6, 7, 5, 9, 8, 10, 11, 12 }, ordinals[0..first_len]);
    try std.testing.expect(head.next == &entries[0].node);
    try std.testing.expect(head.prev == &entries[12].node);

    list_sort.listSort(null, &head, parityCmp);

    const second_len = try collect(&head, &keys, &ordinals);
    try std.testing.expectEqualSlices(i32, &.{ 0, 2, 2, 4, 4, 6, 8, 8, 1, 3, 5, 7, 9 }, keys[0..second_len]);
    try std.testing.expectEqualSlices(usize, &.{ 0, 3, 4, 6, 7, 9, 10, 11, 1, 2, 5, 8, 12 }, ordinals[0..second_len]);
    try std.testing.expect(head.next == &entries[0].node);
    try std.testing.expect(head.prev == &entries[12].node);
}
