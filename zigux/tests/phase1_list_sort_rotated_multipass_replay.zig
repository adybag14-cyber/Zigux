const std = @import("std");
const list_sort = @import("list_sort");

const Entry = struct {
    group: i32,
    slot: i32,
    ordinal: usize,
    node: list_sort.ListHead = .{},
};

fn cmpSlot(_: ?*anyopaque, a: *const list_sort.ListHead, b: *const list_sort.ListHead) i32 {
    const lhs: *const Entry = @fieldParentPtr("node", a);
    const rhs: *const Entry = @fieldParentPtr("node", b);
    if (lhs.slot < rhs.slot) return -1;
    if (lhs.slot > rhs.slot) return 1;
    return 0;
}

fn cmpGroup(_: ?*anyopaque, a: *const list_sort.ListHead, b: *const list_sort.ListHead) i32 {
    const lhs: *const Entry = @fieldParentPtr("node", a);
    const rhs: *const Entry = @fieldParentPtr("node", b);
    if (lhs.group < rhs.group) return -1;
    if (lhs.group > rhs.group) return 1;
    return 0;
}

fn collectOrdinals(head: *list_sort.ListHead, out: []usize) !usize {
    var idx: usize = 0;
    var current = head.next;
    while (current != head) : (current = current.?.next) {
        const entry: *const Entry = @fieldParentPtr("node", current.?);
        out[idx] = entry.ordinal;
        try std.testing.expect(current.?.next.?.prev == current.?);
        try std.testing.expect(current.?.prev.?.next == current.?);
        idx += 1;
    }
    return idx;
}

test "phase1 list_sort replay preserves rotated multipass grouping order" {
    var head: list_sort.ListHead = .{};
    head.init();

    var entries = [_]Entry{
        .{ .group = 2, .slot = 1, .ordinal = 0 },
        .{ .group = 0, .slot = 2, .ordinal = 1 },
        .{ .group = 1, .slot = 0, .ordinal = 2 },
        .{ .group = 0, .slot = 0, .ordinal = 3 },
        .{ .group = 2, .slot = 0, .ordinal = 4 },
        .{ .group = 1, .slot = 2, .ordinal = 5 },
        .{ .group = 0, .slot = 1, .ordinal = 6 },
        .{ .group = 2, .slot = 2, .ordinal = 7 },
        .{ .group = 1, .slot = 1, .ordinal = 8 },
    };

    for (&entries) |*entry| list_sort.listAddTail(&entry.node, &head);

    list_sort.listSort(null, &head, cmpSlot);

    var ordinals: [entries.len]usize = undefined;
    var count = try collectOrdinals(&head, &ordinals);
    try std.testing.expectEqual(entries.len, count);
    try std.testing.expectEqualSlices(usize, &.{ 2, 3, 4, 0, 6, 8, 1, 5, 7 }, ordinals[0..count]);

    var rotations: usize = 0;
    while (rotations < 4) : (rotations += 1) {
        const node = head.next.?;
        list_sort.listDel(node);
        list_sort.listAddTail(node, &head);
    }

    count = try collectOrdinals(&head, &ordinals);
    try std.testing.expectEqualSlices(usize, &.{ 6, 8, 1, 5, 7, 2, 3, 4, 0 }, ordinals[0..count]);
    try std.testing.expect(head.next == &entries[6].node);
    try std.testing.expect(head.prev == &entries[0].node);

    list_sort.listSort(null, &head, cmpGroup);

    count = try collectOrdinals(&head, &ordinals);
    try std.testing.expectEqual(entries.len, count);
    try std.testing.expectEqualSlices(usize, &.{ 6, 1, 3, 8, 5, 2, 7, 4, 0 }, ordinals[0..count]);
    try std.testing.expect(head.next == &entries[6].node);
    try std.testing.expect(head.prev == &entries[0].node);
}
