const std = @import("std");
const list_sort = @import("list_sort");

const Entry = struct {
    key: i32,
    ordinal: usize,
    node: list_sort.ListHead = .{},
};

const entry_count = 12;

fn allEqualCmp(_: ?*anyopaque, _: *const list_sort.ListHead, _: *const list_sort.ListHead) i32 {
    return 0;
}

fn expectOrder(head: *const list_sort.ListHead, expected_ordinals: []const usize) !void {
    var ordinals: [entry_count]usize = undefined;
    var index: usize = 0;
    var current = head.next;

    while (current != head) : (current = current.?.next) {
        const entry: *const Entry = @fieldParentPtr("node", current.?);
        ordinals[index] = entry.ordinal;
        try std.testing.expect(current.?.next.?.prev == current.?);
        try std.testing.expect(current.?.prev.?.next == current.?);
        index += 1;
    }

    try std.testing.expectEqual(expected_ordinals.len, index);
    try std.testing.expectEqualSlices(usize, expected_ordinals, ordinals[0..index]);
    try std.testing.expect(head.prev.?.next == head);
    try std.testing.expect(head.next.?.prev == head);
}

test "phase1 list_sort keeps caller order when every comparison ties" {
    var head: list_sort.ListHead = .{};
    head.init();

    var entries = [_]Entry{
        .{ .key = 7, .ordinal = 0 },
        .{ .key = -2, .ordinal = 1 },
        .{ .key = 4, .ordinal = 2 },
        .{ .key = 4, .ordinal = 3 },
        .{ .key = -9, .ordinal = 4 },
        .{ .key = 1, .ordinal = 5 },
        .{ .key = 7, .ordinal = 6 },
        .{ .key = 0, .ordinal = 7 },
        .{ .key = -2, .ordinal = 8 },
        .{ .key = 5, .ordinal = 9 },
        .{ .key = 1, .ordinal = 10 },
        .{ .key = -9, .ordinal = 11 },
    };

    inline for (.{ 0, 1, 2, 3 }) |index| {
        list_sort.listAddTail(&entries[index].node, &head);
    }
    inline for (.{ 7, 6, 5, 4 }) |index| {
        list_sort.listAdd(&entries[index].node, &head);
    }
    inline for (.{ 8, 9, 10, 11 }) |index| {
        list_sort.listAddTail(&entries[index].node, &head);
    }

    try expectOrder(&head, &.{ 4, 5, 6, 7, 0, 1, 2, 3, 8, 9, 10, 11 });

    list_sort.listSort(null, &head, allEqualCmp);
    try expectOrder(&head, &.{ 4, 5, 6, 7, 0, 1, 2, 3, 8, 9, 10, 11 });

    list_sort.listSort(null, &head, allEqualCmp);
    try expectOrder(&head, &.{ 4, 5, 6, 7, 0, 1, 2, 3, 8, 9, 10, 11 });
}
