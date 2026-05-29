const std = @import("std");
const list_sort = @import("list_sort");

const Entry = struct {
    key: i32,
    ordinal: usize,
    node: list_sort.ListHead = .{},
};

const SortContext = struct {
    descending: bool = false,
    comparisons: usize = 0,
};

const entry_count = 10;

fn largeMagnitudeCmp(priv: ?*anyopaque, a: *const list_sort.ListHead, b: *const list_sort.ListHead) i32 {
    const context: *SortContext = @ptrCast(@alignCast(priv.?));
    const lhs: *const Entry = @fieldParentPtr("node", a);
    const rhs: *const Entry = @fieldParentPtr("node", b);
    context.comparisons += 1;

    if (lhs.key == rhs.key) return 0;
    const lhs_before_rhs = if (context.descending) lhs.key > rhs.key else lhs.key < rhs.key;
    return if (lhs_before_rhs) -32768 else 32767;
}

fn expectOrder(head: *const list_sort.ListHead, expected_ordinals: []const usize) !void {
    var ordinals: [entry_count]usize = undefined;
    var reverse_ordinals: [entry_count]usize = undefined;

    var forward_index: usize = 0;
    var current = head.next;
    while (current != head) : (current = current.?.next) {
        const entry: *const Entry = @fieldParentPtr("node", current.?);
        ordinals[forward_index] = entry.ordinal;
        try std.testing.expect(current.?.next.?.prev == current.?);
        try std.testing.expect(current.?.prev.?.next == current.?);
        forward_index += 1;
    }

    var reverse_index: usize = 0;
    current = head.prev;
    while (current != head) : (current = current.?.prev) {
        const entry: *const Entry = @fieldParentPtr("node", current.?);
        reverse_ordinals[reverse_index] = entry.ordinal;
        reverse_index += 1;
    }

    try std.testing.expectEqual(expected_ordinals.len, forward_index);
    try std.testing.expectEqual(expected_ordinals.len, reverse_index);
    try std.testing.expectEqualSlices(usize, expected_ordinals, ordinals[0..forward_index]);

    var expected_reverse: [entry_count]usize = undefined;
    for (expected_ordinals, 0..) |ordinal, index| {
        expected_reverse[expected_ordinals.len - 1 - index] = ordinal;
    }
    try std.testing.expectEqualSlices(usize, expected_reverse[0..expected_ordinals.len], reverse_ordinals[0..reverse_index]);
    try std.testing.expect(head.prev.?.next == head);
    try std.testing.expect(head.next.?.prev == head);
}

test "phase1 list_sort honors large comparator return magnitudes" {
    var head: list_sort.ListHead = .{};
    head.init();

    var entries = [_]Entry{
        .{ .key = 9, .ordinal = 0 },
        .{ .key = -4, .ordinal = 1 },
        .{ .key = 7, .ordinal = 2 },
        .{ .key = -4, .ordinal = 3 },
        .{ .key = 0, .ordinal = 4 },
        .{ .key = 9, .ordinal = 5 },
        .{ .key = -12, .ordinal = 6 },
        .{ .key = 7, .ordinal = 7 },
        .{ .key = 3, .ordinal = 8 },
        .{ .key = -12, .ordinal = 9 },
    };

    for (&entries) |*entry| {
        list_sort.listAddTail(&entry.node, &head);
    }

    var context = SortContext{};
    list_sort.listSort(&context, &head, largeMagnitudeCmp);
    try std.testing.expect(context.comparisons > 0);
    try expectOrder(&head, &.{ 6, 9, 1, 3, 4, 8, 2, 7, 0, 5 });
    try std.testing.expect(head.next == &entries[6].node);
    try std.testing.expect(head.prev == &entries[5].node);

    context.descending = true;
    context.comparisons = 0;
    list_sort.listSort(&context, &head, largeMagnitudeCmp);
    try std.testing.expect(context.comparisons > 0);
    try expectOrder(&head, &.{ 0, 5, 2, 7, 8, 4, 1, 3, 6, 9 });
    try std.testing.expect(head.next == &entries[0].node);
    try std.testing.expect(head.prev == &entries[9].node);
}
