const std = @import("std");
const list_sort = @import("list_sort");

const Entry = struct {
    key: i32,
    ordinal: usize,
    node: list_sort.ListHead = .{},
};

fn ascendingCmp(_: ?*anyopaque, a: *const list_sort.ListHead, b: *const list_sort.ListHead) i32 {
    const lhs: *const Entry = @fieldParentPtr("node", a);
    const rhs: *const Entry = @fieldParentPtr("node", b);
    if (lhs.key < rhs.key) return -1;
    if (lhs.key > rhs.key) return 1;
    return 0;
}

fn readList(head: *const list_sort.ListHead, comptime field: enum { key, ordinal }, out: anytype) !usize {
    var idx: usize = 0;
    var current = head.next;
    while (current != head) : (current = current.?.next) {
        const entry: *const Entry = @fieldParentPtr("node", current.?);
        out[idx] = switch (field) {
            .key => entry.key,
            .ordinal => entry.ordinal,
        };
        try std.testing.expect(current.?.next.?.prev == current.?);
        try std.testing.expect(current.?.prev.?.next == current.?);
        idx += 1;
    }
    return idx;
}

test "phase1 list_sort head tail rotation replay" {
    var head: list_sort.ListHead = .{};
    head.init();

    var entries = [_]Entry{
        .{ .key = 6, .ordinal = 0 },
        .{ .key = 2, .ordinal = 1 },
        .{ .key = 6, .ordinal = 2 },
        .{ .key = 4, .ordinal = 3 },
        .{ .key = 2, .ordinal = 4 },
        .{ .key = 5, .ordinal = 5 },
        .{ .key = 4, .ordinal = 6 },
        .{ .key = 1, .ordinal = 7 },
        .{ .key = 5, .ordinal = 8 },
    };

    for (&entries) |*entry| list_sort.listAddTail(&entry.node, &head);

    list_sort.listDel(&entries[0].node);
    list_sort.listDel(&entries[7].node);
    list_sort.listDel(&entries[4].node);
    list_sort.listAddTail(&entries[0].node, &head);
    list_sort.listAdd(&entries[7].node, &head);
    list_sort.listAddTail(&entries[4].node, &head);

    var presort_ordinals: [entries.len]usize = undefined;
    const presort_len = try readList(&head, .ordinal, &presort_ordinals);
    try std.testing.expectEqual(entries.len, presort_len);
    try std.testing.expectEqualSlices(usize, &.{ 7, 1, 2, 3, 5, 6, 8, 0, 4 }, presort_ordinals[0..presort_len]);
    try std.testing.expect(head.next == &entries[7].node);
    try std.testing.expect(head.prev == &entries[4].node);

    list_sort.listSort(null, &head, ascendingCmp);

    var keys: [entries.len]i32 = undefined;
    var ordinals: [entries.len]usize = undefined;
    const key_len = try readList(&head, .key, &keys);
    const ordinal_len = try readList(&head, .ordinal, &ordinals);

    try std.testing.expectEqual(entries.len, key_len);
    try std.testing.expectEqual(entries.len, ordinal_len);
    try std.testing.expectEqualSlices(i32, &.{ 1, 2, 2, 4, 4, 5, 5, 6, 6 }, keys[0..key_len]);
    try std.testing.expectEqualSlices(usize, &.{ 7, 1, 4, 3, 6, 5, 8, 2, 0 }, ordinals[0..ordinal_len]);
    try std.testing.expect(head.next == &entries[7].node);
    try std.testing.expect(head.prev == &entries[0].node);
    try std.testing.expect(entries[7].node.prev == &head);
    try std.testing.expect(entries[0].node.next == &head);
}
