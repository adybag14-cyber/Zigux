const std = @import("std");
const list_sort = @import("list_sort");

const ListHead = list_sort.ListHead;

const Entry = struct {
    group: i32,
    slot: i32,
    ordinal: usize,
    node: ListHead = .{},
};

const SortKey = enum { slot, group };

fn stableProjection(priv: ?*anyopaque, a: *const ListHead, b: *const ListHead) i32 {
    const key: *const SortKey = @ptrCast(@alignCast(priv.?));
    const lhs: *const Entry = @fieldParentPtr("node", a);
    const rhs: *const Entry = @fieldParentPtr("node", b);

    const lhs_value = switch (key.*) {
        .slot => lhs.slot,
        .group => lhs.group,
    };
    const rhs_value = switch (key.*) {
        .slot => rhs.slot,
        .group => rhs.group,
    };

    if (lhs_value < rhs_value) return -1;
    if (lhs_value > rhs_value) return 1;
    return 0;
}

fn collectForward(head: *ListHead, groups: []i32, slots: []i32, ordinals: []usize) !usize {
    var idx: usize = 0;
    var current = head.next;
    while (current != head) : (current = current.?.next) {
        const entry: *const Entry = @fieldParentPtr("node", current.?);
        groups[idx] = entry.group;
        slots[idx] = entry.slot;
        ordinals[idx] = entry.ordinal;
        try std.testing.expect(current.?.next.?.prev == current.?);
        try std.testing.expect(current.?.prev.?.next == current.?);
        idx += 1;
    }
    return idx;
}

fn collectReverse(head: *ListHead, ordinals: []usize) !usize {
    var idx: usize = 0;
    var current = head.prev;
    while (current != head) : (current = current.?.prev) {
        const entry: *const Entry = @fieldParentPtr("node", current.?);
        ordinals[idx] = entry.ordinal;
        idx += 1;
    }
    return idx;
}

test "list sort preserves prior pass ordering inside later stable groups" {
    var head: ListHead = .{};
    head.init();

    var entries = [_]Entry{
        .{ .group = 2, .slot = 3, .ordinal = 0 },
        .{ .group = 1, .slot = 2, .ordinal = 1 },
        .{ .group = 3, .slot = 1, .ordinal = 2 },
        .{ .group = 2, .slot = 0, .ordinal = 3 },
        .{ .group = 1, .slot = 3, .ordinal = 4 },
        .{ .group = 3, .slot = 0, .ordinal = 5 },
        .{ .group = 2, .slot = 2, .ordinal = 6 },
        .{ .group = 1, .slot = 1, .ordinal = 7 },
        .{ .group = 3, .slot = 2, .ordinal = 8 },
        .{ .group = 2, .slot = 1, .ordinal = 9 },
        .{ .group = 1, .slot = 0, .ordinal = 10 },
        .{ .group = 3, .slot = 3, .ordinal = 11 },
    };

    for (&entries) |*entry| list_sort.listAddTail(&entry.node, &head);

    var key = SortKey.slot;
    list_sort.listSort(&key, &head, stableProjection);

    var groups: [entries.len]i32 = undefined;
    var slots: [entries.len]i32 = undefined;
    var ordinals: [entries.len]usize = undefined;
    const slot_count = try collectForward(&head, &groups, &slots, &ordinals);
    try std.testing.expectEqual(entries.len, slot_count);
    try std.testing.expectEqualSlices(i32, &.{ 0, 0, 0, 1, 1, 1, 2, 2, 2, 3, 3, 3 }, slots[0..slot_count]);
    try std.testing.expectEqualSlices(usize, &.{ 3, 5, 10, 2, 7, 9, 1, 6, 8, 0, 4, 11 }, ordinals[0..slot_count]);

    key = .group;
    list_sort.listSort(&key, &head, stableProjection);

    const group_count = try collectForward(&head, &groups, &slots, &ordinals);
    try std.testing.expectEqual(entries.len, group_count);
    try std.testing.expectEqualSlices(i32, &.{ 1, 1, 1, 1, 2, 2, 2, 2, 3, 3, 3, 3 }, groups[0..group_count]);
    try std.testing.expectEqualSlices(i32, &.{ 0, 1, 2, 3, 0, 1, 2, 3, 0, 1, 2, 3 }, slots[0..group_count]);
    try std.testing.expectEqualSlices(usize, &.{ 10, 7, 1, 4, 3, 9, 6, 0, 5, 2, 8, 11 }, ordinals[0..group_count]);
    try std.testing.expect(head.next == &entries[10].node);
    try std.testing.expect(head.prev == &entries[11].node);

    var reverse_ordinals: [entries.len]usize = undefined;
    const reverse_count = try collectReverse(&head, &reverse_ordinals);
    try std.testing.expectEqual(entries.len, reverse_count);
    try std.testing.expectEqualSlices(usize, &.{ 11, 8, 2, 5, 0, 6, 9, 3, 4, 1, 7, 10 }, reverse_ordinals[0..reverse_count]);
}
