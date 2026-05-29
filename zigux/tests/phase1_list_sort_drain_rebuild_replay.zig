const std = @import("std");
const list_sort = @import("list_sort");

const Entry = struct {
    key: i32,
    ordinal: usize,
    node: list_sort.ListHead = .{},
};

const SortMode = enum { ascending, descending };

fn signedCompare(priv: ?*anyopaque, a: *const list_sort.ListHead, b: *const list_sort.ListHead) i32 {
    const mode: *const SortMode = @ptrCast(@alignCast(priv.?));
    const lhs: *const Entry = @fieldParentPtr("node", a);
    const rhs: *const Entry = @fieldParentPtr("node", b);

    if (lhs.key < rhs.key) return if (mode.* == .ascending) -1 else 1;
    if (lhs.key > rhs.key) return if (mode.* == .ascending) 1 else -1;
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

test "list sort handles drain rebuild and reverse resort" {
    var head: list_sort.ListHead = .{};
    head.init();

    var entries = [_]Entry{
        .{ .key = 6, .ordinal = 0 },
        .{ .key = -1, .ordinal = 1 },
        .{ .key = 4, .ordinal = 2 },
        .{ .key = -1, .ordinal = 3 },
        .{ .key = 8, .ordinal = 4 },
        .{ .key = 4, .ordinal = 5 },
        .{ .key = 0, .ordinal = 6 },
        .{ .key = 8, .ordinal = 7 },
    };

    for (&entries) |*entry| list_sort.listAddTail(&entry.node, &head);

    var mode = SortMode.ascending;
    list_sort.listSort(&mode, &head, signedCompare);
    try expectOrder(&head, &.{ -1, -1, 0, 4, 4, 6, 8, 8 }, &.{ 1, 3, 6, 2, 5, 0, 4, 7 });
    try std.testing.expect(head.next == &entries[1].node);
    try std.testing.expect(head.prev == &entries[7].node);

    while (!list_sort.listEmpty(&head)) {
        const node = head.next.?;
        list_sort.listDel(node);
        try std.testing.expect(node.next == null);
        try std.testing.expect(node.prev == null);
    }
    try std.testing.expect(head.next == &head);
    try std.testing.expect(head.prev == &head);

    const rebuild_order = [_]usize{ 7, 3, 0, 5, 1, 4, 6, 2 };
    for (rebuild_order) |entry_idx| list_sort.listAddTail(&entries[entry_idx].node, &head);

    mode = .descending;
    list_sort.listSort(&mode, &head, signedCompare);
    try expectOrder(&head, &.{ 8, 8, 6, 4, 4, 0, -1, -1 }, &.{ 7, 4, 0, 5, 2, 6, 3, 1 });
    try std.testing.expect(head.next == &entries[7].node);
    try std.testing.expect(head.prev == &entries[1].node);
}
