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

test "phase1 list_sort mixed end insertion replay" {
    var head: list_sort.ListHead = .{};
    head.init();

    var entries = [_]Entry{
        .{ .key = 3, .ordinal = 0 },
        .{ .key = 1, .ordinal = 1 },
        .{ .key = 2, .ordinal = 2 },
        .{ .key = 1, .ordinal = 3 },
        .{ .key = 3, .ordinal = 4 },
        .{ .key = 2, .ordinal = 5 },
        .{ .key = 1, .ordinal = 6 },
        .{ .key = 3, .ordinal = 7 },
    };

    list_sort.listAddTail(&entries[0].node, &head);
    list_sort.listAdd(&entries[1].node, &head);
    list_sort.listAddTail(&entries[2].node, &head);
    list_sort.listAdd(&entries[3].node, &head);
    list_sort.listAddTail(&entries[4].node, &head);
    list_sort.listAdd(&entries[5].node, &head);
    list_sort.listAddTail(&entries[6].node, &head);
    list_sort.listAdd(&entries[7].node, &head);

    var presort_ordinals: [entries.len]usize = undefined;
    var presort_index: usize = 0;
    var presort_current = head.next;
    while (presort_current != &head) : (presort_current = presort_current.?.next) {
        const entry: *const Entry = @fieldParentPtr("node", presort_current.?);
        presort_ordinals[presort_index] = entry.ordinal;
        try std.testing.expect(presort_current.?.next.?.prev == presort_current.?);
        try std.testing.expect(presort_current.?.prev.?.next == presort_current.?);
        presort_index += 1;
    }

    try std.testing.expectEqual(entries.len, presort_index);
    try std.testing.expectEqualSlices(usize, &.{ 7, 5, 3, 1, 0, 2, 4, 6 }, presort_ordinals[0..presort_index]);

    list_sort.listSort(null, &head, ascendingCmp);

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
    try std.testing.expectEqualSlices(i32, &.{ 1, 1, 1, 2, 2, 3, 3, 3 }, keys[0..idx]);
    try std.testing.expectEqualSlices(usize, &.{ 3, 1, 6, 5, 2, 7, 0, 4 }, ordinals[0..idx]);
    try std.testing.expect(head.next == &entries[3].node);
    try std.testing.expect(head.prev == &entries[4].node);
    try std.testing.expect(entries[3].node.prev == &head);
    try std.testing.expect(entries[4].node.next == &head);
}
