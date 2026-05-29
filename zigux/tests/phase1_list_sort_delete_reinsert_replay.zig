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
    var keys: [7]i32 = undefined;
    var ordinals: [7]usize = undefined;
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

test "list sort handles delete reinsert before reverse resort" {
    var head: list_sort.ListHead = .{};
    head.init();

    var entries = [_]Entry{
        .{ .key = 4, .ordinal = 0 },
        .{ .key = 1, .ordinal = 1 },
        .{ .key = 3, .ordinal = 2 },
        .{ .key = 1, .ordinal = 3 },
        .{ .key = 5, .ordinal = 4 },
        .{ .key = 3, .ordinal = 5 },
        .{ .key = 2, .ordinal = 6 },
    };

    for (&entries) |*entry| list_sort.listAddTail(&entry.node, &head);

    var mode = SortMode.ascending;
    list_sort.listSort(&mode, &head, signedCompare);
    try expectOrder(&head, &.{ 1, 1, 2, 3, 3, 4, 5 }, &.{ 1, 3, 6, 2, 5, 0, 4 });
    try std.testing.expect(head.next == &entries[1].node);
    try std.testing.expect(head.prev == &entries[4].node);

    list_sort.listDel(&entries[3].node);
    list_sort.listDel(&entries[5].node);
    try std.testing.expect(entries[3].node.next == null);
    try std.testing.expect(entries[3].node.prev == null);
    try std.testing.expect(entries[5].node.next == null);
    try std.testing.expect(entries[5].node.prev == null);
    try expectOrder(&head, &.{ 1, 2, 3, 4, 5 }, &.{ 1, 6, 2, 0, 4 });

    list_sort.listAdd(&entries[5].node, &head);
    list_sort.listAddTail(&entries[3].node, &head);

    mode = .descending;
    list_sort.listSort(&mode, &head, signedCompare);
    try expectOrder(&head, &.{ 5, 4, 3, 3, 2, 1, 1 }, &.{ 4, 0, 5, 2, 6, 1, 3 });
    try std.testing.expect(head.next == &entries[4].node);
    try std.testing.expect(head.prev == &entries[3].node);
}
