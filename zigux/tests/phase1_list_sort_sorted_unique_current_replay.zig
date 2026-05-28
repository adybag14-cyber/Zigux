const std = @import("std");
const list_sort = @import("list_sort");

const Entry = struct {
    key: i32,
    ordinal: usize,
    node: list_sort.ListHead = .{},
};

test "phase1 list_sort keeps sorted unique input unchanged after one pass" {
    const cmp = struct {
        fn compare(_: ?*anyopaque, a: *const list_sort.ListHead, b: *const list_sort.ListHead) i32 {
            const lhs: *const Entry = @fieldParentPtr("node", a);
            const rhs: *const Entry = @fieldParentPtr("node", b);
            if (lhs.key < rhs.key) return -1;
            if (lhs.key > rhs.key) return 1;
            return 0;
        }
    }.compare;

    var head: list_sort.ListHead = .{};
    head.init();
    var entries = [_]Entry{
        .{ .key = 1, .ordinal = 0 },
        .{ .key = 2, .ordinal = 1 },
        .{ .key = 3, .ordinal = 2 },
        .{ .key = 4, .ordinal = 3 },
        .{ .key = 5, .ordinal = 4 },
        .{ .key = 6, .ordinal = 5 },
    };
    for (&entries) |*entry| {
        list_sort.listAddTail(&entry.node, &head);
    }

    list_sort.listSort(null, &head, cmp);

    var keys: [entries.len]i32 = undefined;
    var ordinals: [entries.len]usize = undefined;
    var count: usize = 0;
    var current = head.next;
    while (current != &head) : (current = current.?.next) {
        const entry: *const Entry = @fieldParentPtr("node", current.?);
        keys[count] = entry.key;
        ordinals[count] = entry.ordinal;
        try std.testing.expect(current.?.next.?.prev == current.?);
        try std.testing.expect(current.?.prev.?.next == current.?);
        count += 1;
    }

    try std.testing.expectEqual(@as(usize, entries.len), count);
    try std.testing.expectEqualSlices(i32, &.{ 1, 2, 3, 4, 5, 6 }, keys[0..count]);
    try std.testing.expectEqualSlices(usize, &.{ 0, 1, 2, 3, 4, 5 }, ordinals[0..count]);
    try std.testing.expect(head.next == &entries[0].node);
    try std.testing.expect(head.prev == &entries[5].node);
    try std.testing.expect(entries[0].node.prev == &head);
    try std.testing.expect(entries[5].node.next == &head);
}
