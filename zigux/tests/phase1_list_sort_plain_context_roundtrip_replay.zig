const std = @import("std");
const list_sort = @import("list_sort");

const Entry = struct {
    key: i32,
    ordinal: usize,
    node: list_sort.ListHead = .{},
};

const SortMode = enum { ascending, descending };

fn contextCmp(priv: ?*anyopaque, a: *const list_sort.ListHead, b: *const list_sort.ListHead) i32 {
    const mode: *const SortMode = @ptrCast(@alignCast(priv.?));
    const lhs: *const Entry = @fieldParentPtr("node", a);
    const rhs: *const Entry = @fieldParentPtr("node", b);

    if (lhs.key == rhs.key) return 0;
    const ascending = lhs.key < rhs.key;
    return if (mode.* == .ascending)
        (if (ascending) -1 else 1)
    else
        (if (ascending) 1 else -1);
}

fn expectRing(head: *list_sort.ListHead, expected_keys: []const i32, expected_ordinals: []const usize, expected_first: *list_sort.ListHead, expected_last: *list_sort.ListHead) !void {
    var keys: [9]i32 = undefined;
    var ordinals: [9]usize = undefined;
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
    try std.testing.expect(head.next == expected_first);
    try std.testing.expect(head.prev == expected_last);
    try std.testing.expect(expected_first.prev == head);
    try std.testing.expect(expected_last.next == head);
}

test "phase1 list_sort plain-context roundtrip replay preserves ring integrity" {
    var head: list_sort.ListHead = .{};
    head.init();
    var entries = [_]Entry{
        .{ .key = 3, .ordinal = 0 },
        .{ .key = 1, .ordinal = 1 },
        .{ .key = 4, .ordinal = 2 },
        .{ .key = 1, .ordinal = 3 },
        .{ .key = 5, .ordinal = 4 },
        .{ .key = 9, .ordinal = 5 },
        .{ .key = 2, .ordinal = 6 },
        .{ .key = 6, .ordinal = 7 },
        .{ .key = 5, .ordinal = 8 },
    };
    for (&entries) |*entry| {
        list_sort.listAddTail(&entry.node, &head);
    }

    var mode = SortMode.descending;
    list_sort.listSort(&mode, &head, contextCmp);
    try expectRing(
        &head,
        &.{ 9, 6, 5, 5, 4, 3, 2, 1, 1 },
        &.{ 5, 7, 4, 8, 2, 0, 6, 1, 3 },
        &entries[5].node,
        &entries[3].node,
    );

    mode = .ascending;
    list_sort.listSort(&mode, &head, contextCmp);
    try expectRing(
        &head,
        &.{ 1, 1, 2, 3, 4, 5, 5, 6, 9 },
        &.{ 1, 3, 6, 0, 2, 4, 8, 7, 5 },
        &entries[1].node,
        &entries[5].node,
    );

    mode = .descending;
    list_sort.listSort(&mode, &head, contextCmp);
    try expectRing(
        &head,
        &.{ 9, 6, 5, 5, 4, 3, 2, 1, 1 },
        &.{ 5, 7, 4, 8, 2, 0, 6, 1, 3 },
        &entries[5].node,
        &entries[3].node,
    );
}
