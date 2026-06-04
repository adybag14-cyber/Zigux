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

test "reverse sorted duplicate runs sort stably and relink both directions" {
    var head: list_sort.ListHead = .{};
    head.init();

    var entries = [_]Entry{
        .{ .key = 5, .ordinal = 0 },
        .{ .key = 5, .ordinal = 1 },
        .{ .key = 4, .ordinal = 2 },
        .{ .key = 4, .ordinal = 3 },
        .{ .key = 3, .ordinal = 4 },
        .{ .key = 3, .ordinal = 5 },
        .{ .key = 2, .ordinal = 6 },
        .{ .key = 2, .ordinal = 7 },
        .{ .key = 1, .ordinal = 8 },
        .{ .key = 1, .ordinal = 9 },
    };

    for (&entries) |*entry| {
        list_sort.listAddTail(&entry.node, &head);
    }

    list_sort.listSort(null, &head, triStateCmp);

    var keys: [entries.len]i32 = undefined;
    var forward_ordinals: [entries.len]usize = undefined;
    var backward_ordinals: [entries.len]usize = undefined;

    var forward_idx: usize = 0;
    var current = head.next;
    while (current != &head) : (current = current.?.next) {
        const entry: *const Entry = @fieldParentPtr("node", current.?);
        keys[forward_idx] = entry.key;
        forward_ordinals[forward_idx] = entry.ordinal;
        try std.testing.expect(current.?.next.?.prev == current.?);
        try std.testing.expect(current.?.prev.?.next == current.?);
        forward_idx += 1;
    }

    var backward_idx: usize = 0;
    current = head.prev;
    while (current != &head) : (current = current.?.prev) {
        const entry: *const Entry = @fieldParentPtr("node", current.?);
        backward_ordinals[backward_idx] = entry.ordinal;
        backward_idx += 1;
    }

    try std.testing.expectEqualSlices(i32, &.{ 1, 1, 2, 2, 3, 3, 4, 4, 5, 5 }, keys[0..forward_idx]);
    try std.testing.expectEqualSlices(usize, &.{ 8, 9, 6, 7, 4, 5, 2, 3, 0, 1 }, forward_ordinals[0..forward_idx]);
    try std.testing.expectEqualSlices(usize, &.{ 1, 0, 3, 2, 5, 4, 7, 6, 9, 8 }, backward_ordinals[0..backward_idx]);
    try std.testing.expect(head.next == &entries[8].node);
    try std.testing.expect(head.prev == &entries[1].node);
    try std.testing.expect(entries[8].node.prev == &head);
    try std.testing.expect(entries[1].node.next == &head);
}
