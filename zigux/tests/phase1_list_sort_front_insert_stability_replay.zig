const std = @import("std");
const list_sort = @import("list_sort");

const Entry = struct {
    key: i32,
    ordinal: usize,
    node: list_sort.ListHead = .{},
};

const entry_count = 10;

fn keyCmp(_: ?*anyopaque, a: *const list_sort.ListHead, b: *const list_sort.ListHead) i32 {
    const lhs: *const Entry = @fieldParentPtr("node", a);
    const rhs: *const Entry = @fieldParentPtr("node", b);

    if (lhs.key < rhs.key) return -1;
    if (lhs.key > rhs.key) return 1;
    return 0;
}

fn tiesCmp(_: ?*anyopaque, _: *const list_sort.ListHead, _: *const list_sort.ListHead) i32 {
    return 0;
}

fn expectOrder(head: *const list_sort.ListHead, expected_keys: []const i32, expected_ordinals: []const usize) !void {
    var keys: [entry_count]i32 = undefined;
    var ordinals: [entry_count]usize = undefined;
    var index: usize = 0;
    var current = head.next;

    while (current != head) : (current = current.?.next) {
        const entry: *const Entry = @fieldParentPtr("node", current.?);
        keys[index] = entry.key;
        ordinals[index] = entry.ordinal;
        try std.testing.expect(current.?.next.?.prev == current.?);
        try std.testing.expect(current.?.prev.?.next == current.?);
        index += 1;
    }

    try std.testing.expectEqual(expected_keys.len, index);
    try std.testing.expectEqualSlices(i32, expected_keys, keys[0..index]);
    try std.testing.expectEqualSlices(usize, expected_ordinals, ordinals[0..index]);
}

test "phase1 list_sort keeps front inserted equal keys in traversal order" {
    var head: list_sort.ListHead = .{};
    head.init();

    var entries = [_]Entry{
        .{ .key = 4, .ordinal = 0 },
        .{ .key = 1, .ordinal = 1 },
        .{ .key = 4, .ordinal = 2 },
        .{ .key = 2, .ordinal = 3 },
        .{ .key = 1, .ordinal = 4 },
        .{ .key = 3, .ordinal = 5 },
        .{ .key = 2, .ordinal = 6 },
        .{ .key = 4, .ordinal = 7 },
        .{ .key = 3, .ordinal = 8 },
        .{ .key = 1, .ordinal = 9 },
    };

    for (&entries) |*entry| list_sort.listAdd(&entry.node, &head);

    try expectOrder(
        &head,
        &.{ 1, 3, 4, 2, 3, 1, 2, 4, 1, 4 },
        &.{ 9, 8, 7, 6, 5, 4, 3, 2, 1, 0 },
    );

    list_sort.listSort(null, &head, keyCmp);
    try expectOrder(
        &head,
        &.{ 1, 1, 1, 2, 2, 3, 3, 4, 4, 4 },
        &.{ 9, 4, 1, 6, 3, 8, 5, 7, 2, 0 },
    );
    try std.testing.expect(head.next == &entries[9].node);
    try std.testing.expect(head.prev == &entries[0].node);

    list_sort.listSort(null, &head, tiesCmp);
    try expectOrder(
        &head,
        &.{ 1, 1, 1, 2, 2, 3, 3, 4, 4, 4 },
        &.{ 9, 4, 1, 6, 3, 8, 5, 7, 2, 0 },
    );
    try std.testing.expect(head.next == &entries[9].node);
    try std.testing.expect(head.prev == &entries[0].node);
}
