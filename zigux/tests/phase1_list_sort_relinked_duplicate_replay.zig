const std = @import("std");
const list_sort = @import("list_sort");

const Entry = struct {
    key: i32,
    ordinal: usize,
    node: list_sort.ListHead = .{},
};

fn triStateCmp(_: ?*anyopaque, a: *const list_sort.ListHead, b: *const list_sort.ListHead) i32 {
    const lhs: *const Entry = @fieldParentPtr("node", a);
    const rhs: *const Entry = @fieldParentPtr("node", b);
    if (lhs.key < rhs.key) return -1;
    if (lhs.key > rhs.key) return 1;
    return 0;
}

test "phase1 list_sort relinked duplicate replay" {
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
    for (&entries) |*entry| {
        list_sort.listAddTail(&entry.node, &head);
    }

    list_sort.listSort(null, &head, triStateCmp);
    list_sort.listDel(&entries[5].node);
    list_sort.listDel(&entries[3].node);

    try std.testing.expect(entries[5].node.next == null);
    try std.testing.expect(entries[5].node.prev == null);
    try std.testing.expect(entries[3].node.next == null);
    try std.testing.expect(entries[3].node.prev == null);

    list_sort.listAdd(&entries[5].node, &head);
    list_sort.listAddTail(&entries[3].node, &head);
    list_sort.listSort(null, &head, triStateCmp);

    var keys: [entries.len]i32 = undefined;
    var ordinals: [entries.len]usize = undefined;
    var idx: usize = 0;
    var current = head.next;
    while (current != &head) : (current = current.?.next) {
        const entry: *const Entry = @fieldParentPtr("node", current.?);
        keys[idx] = entry.key;
        ordinals[idx] = entry.ordinal;
        try std.testing.expect(current.?.next.?.prev == current.?);
        try std.testing.expect(current.?.prev.?.next == current.?);
        idx += 1;
    }

    try std.testing.expectEqual(entries.len, idx);
    try std.testing.expectEqualSlices(i32, &.{ 1, 1, 2, 3, 3, 4, 5 }, keys[0..idx]);
    try std.testing.expectEqualSlices(usize, &.{ 1, 3, 6, 5, 2, 0, 4 }, ordinals[0..idx]);
    try std.testing.expect(head.next == &entries[1].node);
    try std.testing.expect(head.prev == &entries[4].node);
    try std.testing.expect(entries[1].node.prev == &head);
    try std.testing.expect(entries[4].node.next == &head);
}
