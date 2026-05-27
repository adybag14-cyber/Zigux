const std = @import("std");
const list_sort = @import("list_sort");

const Entry = struct {
    key: i32,
    ordinal: usize,
    node: list_sort.ListHead = .{},
};

const SortMode = enum { ascending, descending };

fn cmpWithMode(priv: ?*anyopaque, a: *const list_sort.ListHead, b: *const list_sort.ListHead) i32 {
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

test "phase1 list_sort preserves list lifecycle through sort delete and reinsertion" {
    var head: list_sort.ListHead = .{};
    head.init();
    try std.testing.expect(list_sort.listEmpty(&head));

    var entries = [_]Entry{
        .{ .key = 4, .ordinal = 0 },
        .{ .key = 1, .ordinal = 1 },
        .{ .key = 3, .ordinal = 2 },
        .{ .key = 3, .ordinal = 3 },
        .{ .key = 2, .ordinal = 4 },
    };

    list_sort.listAdd(&entries[0].node, &head);
    list_sort.listAddTail(&entries[1].node, &head);
    list_sort.listAdd(&entries[2].node, &head);
    list_sort.listAddTail(&entries[3].node, &head);
    list_sort.listAddTail(&entries[4].node, &head);
    try std.testing.expect(!list_sort.listEmpty(&head));

    var mode = SortMode.ascending;
    list_sort.listSort(&mode, &head, cmpWithMode);

    var first_keys: [entries.len]i32 = undefined;
    var first_ordinals: [entries.len]usize = undefined;
    var idx: usize = 0;
    var current = head.next;
    while (current != &head) : (current = current.?.next) {
        const entry: *const Entry = @fieldParentPtr("node", current.?);
        first_keys[idx] = entry.key;
        first_ordinals[idx] = entry.ordinal;
        try std.testing.expect(current.?.next.?.prev == current.?);
        try std.testing.expect(current.?.prev.?.next == current.?);
        idx += 1;
    }

    try std.testing.expectEqual(@as(usize, entries.len), idx);
    try std.testing.expectEqualSlices(i32, &.{ 1, 2, 3, 3, 4 }, first_keys[0..idx]);
    try std.testing.expectEqualSlices(usize, &.{ 1, 4, 2, 3, 0 }, first_ordinals[0..idx]);
    try std.testing.expect(head.next == &entries[1].node);
    try std.testing.expect(head.prev == &entries[0].node);

    list_sort.listDel(&entries[4].node);
    try std.testing.expect(entries[4].node.next == null);
    try std.testing.expect(entries[4].node.prev == null);
    try std.testing.expect(head.next == &entries[1].node);
    try std.testing.expect(head.prev == &entries[0].node);

    list_sort.listAdd(&entries[4].node, &head);
    try std.testing.expect(head.next == &entries[4].node);
    try std.testing.expect(entries[4].node.prev == &head);
    try std.testing.expect(entries[4].node.next == &entries[1].node);

    mode = .descending;
    list_sort.listSort(&mode, &head, cmpWithMode);

    var second_keys: [entries.len]i32 = undefined;
    var second_ordinals: [entries.len]usize = undefined;
    idx = 0;
    current = head.next;
    while (current != &head) : (current = current.?.next) {
        const entry: *const Entry = @fieldParentPtr("node", current.?);
        second_keys[idx] = entry.key;
        second_ordinals[idx] = entry.ordinal;
        try std.testing.expect(current.?.next.?.prev == current.?);
        try std.testing.expect(current.?.prev.?.next == current.?);
        idx += 1;
    }

    try std.testing.expectEqual(@as(usize, entries.len), idx);
    try std.testing.expectEqualSlices(i32, &.{ 4, 3, 3, 2, 1 }, second_keys[0..idx]);
    try std.testing.expectEqualSlices(usize, &.{ 0, 2, 3, 4, 1 }, second_ordinals[0..idx]);
    try std.testing.expect(head.next == &entries[0].node);
    try std.testing.expect(head.prev == &entries[1].node);

    current = head.next;
    while (current != &head) {
        const next = current.?.next.?;
        list_sort.listDel(current.?);
        current = next;
    }

    try std.testing.expect(list_sort.listEmpty(&head));
    try std.testing.expect(head.next == &head);
    try std.testing.expect(head.prev == &head);
    for (&entries) |*entry| {
        try std.testing.expect(entry.node.next == null);
        try std.testing.expect(entry.node.prev == null);
    }
}
