const std = @import("std");
const list_sort = @import("list_sort");

const Entry = struct {
    key: i32,
    ordinal: usize,
    node: list_sort.ListHead = .{},
};

fn cmp(_: ?*anyopaque, a: *const list_sort.ListHead, b: *const list_sort.ListHead) i32 {
    const lhs: *const Entry = @fieldParentPtr("node", a);
    const rhs: *const Entry = @fieldParentPtr("node", b);

    if (lhs.key < rhs.key) return -1;
    if (lhs.key > rhs.key) return 1;
    return 0;
}

fn expectOrder(head: *list_sort.ListHead, expected_keys: []const i32, expected_ordinals: []const usize) !void {
    var keys: [8]i32 = undefined;
    var ordinals: [8]usize = undefined;

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

    try std.testing.expectEqual(expected_keys.len, idx);
    try std.testing.expectEqualSlices(i32, expected_keys, keys[0..idx]);
    try std.testing.expectEqualSlices(usize, expected_ordinals, ordinals[0..idx]);

    var reverse_idx = expected_ordinals.len;
    current = head.prev;
    while (current != head) : (current = current.?.prev) {
        reverse_idx -= 1;
        const entry: *const Entry = @fieldParentPtr("node", current.?);
        try std.testing.expectEqual(expected_ordinals[reverse_idx], entry.ordinal);
    }
    try std.testing.expectEqual(@as(usize, 0), reverse_idx);
}

test "list_sort keeps stable order after endpoint rotation and resort" {
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

    for (&entries) |*entry| list_sort.listAddTail(&entry.node, &head);
    list_sort.listSort(null, &head, cmp);

    try expectOrder(
        &head,
        &.{ 1, 1, 2, 2, 3, 3, 4, 4 },
        &.{ 1, 3, 4, 6, 2, 7, 0, 5 },
    );

    list_sort.listDel(head.next.?);
    list_sort.listDel(head.prev.?);
    list_sort.listAdd(&entries[1].node, &head);
    list_sort.listAddTail(&entries[5].node, &head);

    try expectOrder(
        &head,
        &.{ 1, 1, 2, 2, 3, 3, 4, 4 },
        &.{ 1, 3, 4, 6, 2, 7, 0, 5 },
    );

    list_sort.listDel(head.prev.?);
    list_sort.listAdd(&entries[5].node, &head);
    list_sort.listSort(null, &head, cmp);

    try expectOrder(
        &head,
        &.{ 1, 1, 2, 2, 3, 3, 4, 4 },
        &.{ 1, 3, 4, 6, 2, 7, 5, 0 },
    );
    try std.testing.expect(head.next == &entries[1].node);
    try std.testing.expect(head.prev == &entries[0].node);
}
