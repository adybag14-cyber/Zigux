const std = @import("std");
const list_sort = @import("list_sort");

const Entry = struct {
    key: i32,
    ordinal: usize,
    node: list_sort.ListHead = .{},
};

fn ascending(_: ?*anyopaque, a: *const list_sort.ListHead, b: *const list_sort.ListHead) i32 {
    const lhs: *const Entry = @fieldParentPtr("node", a);
    const rhs: *const Entry = @fieldParentPtr("node", b);
    if (lhs.key < rhs.key) return -1;
    if (lhs.key > rhs.key) return 1;
    return 0;
}

fn expectOrder(head: *const list_sort.ListHead, expected_keys: []const i32, expected_ordinals: []const usize) !void {
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
}

test "list sort preserves sorted prefix stability after tail appends" {
    var head: list_sort.ListHead = .{};
    head.init();

    var entries = [_]Entry{
        .{ .key = 2, .ordinal = 0 },
        .{ .key = 4, .ordinal = 1 },
        .{ .key = 1, .ordinal = 2 },
        .{ .key = 3, .ordinal = 3 },
        .{ .key = 2, .ordinal = 4 },
        .{ .key = 0, .ordinal = 5 },
        .{ .key = 4, .ordinal = 6 },
        .{ .key = 3, .ordinal = 7 },
    };

    for (entries[0..4]) |*entry| list_sort.listAddTail(&entry.node, &head);
    list_sort.listSort(null, &head, ascending);
    try expectOrder(&head, &.{ 1, 2, 3, 4 }, &.{ 2, 0, 3, 1 });
    try std.testing.expect(head.next == &entries[2].node);
    try std.testing.expect(head.prev == &entries[1].node);

    for (entries[4..]) |*entry| list_sort.listAddTail(&entry.node, &head);
    list_sort.listSort(null, &head, ascending);
    try expectOrder(&head, &.{ 0, 1, 2, 2, 3, 3, 4, 4 }, &.{ 5, 2, 0, 4, 3, 7, 1, 6 });
    try std.testing.expect(head.next == &entries[5].node);
    try std.testing.expect(head.prev == &entries[6].node);
}
