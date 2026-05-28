const std = @import("std");
const list_sort = @import("list_sort");

const Entry = struct {
    key: i32,
    ordinal: usize,
    node: list_sort.ListHead = .{},
};

fn collectSorted(
    head: *list_sort.ListHead,
    keys: []i32,
    ordinals: []usize,
) !usize {
    var count: usize = 0;
    var current = head.next;
    while (current != head) : (current = current.?.next) {
        const entry: *const Entry = @fieldParentPtr("node", current.?);
        keys[count] = entry.key;
        ordinals[count] = entry.ordinal;
        count += 1;
    }
    return count;
}

test "phase1 list_sort replay accepts non-unit comparator magnitudes with intact links" {
    const magnitude_cmp = struct {
        fn compare(_: ?*anyopaque, a: *const list_sort.ListHead, b: *const list_sort.ListHead) i32 {
            const lhs: *const Entry = @fieldParentPtr("node", a);
            const rhs: *const Entry = @fieldParentPtr("node", b);
            if (lhs.key < rhs.key) return -7;
            if (lhs.key > rhs.key) return 9;
            return 0;
        }
    }.compare;

    var head: list_sort.ListHead = .{};
    head.init();
    var entries = [_]Entry{
        .{ .key = 3, .ordinal = 0 },
        .{ .key = 1, .ordinal = 1 },
        .{ .key = 2, .ordinal = 2 },
        .{ .key = 1, .ordinal = 3 },
        .{ .key = 4, .ordinal = 4 },
        .{ .key = 2, .ordinal = 5 },
    };
    for (&entries) |*entry| {
        list_sort.listAddTail(&entry.node, &head);
    }

    list_sort.listSort(null, &head, magnitude_cmp);

    var keys: [6]i32 = undefined;
    var ordinals: [6]usize = undefined;
    const count = try collectSorted(&head, &keys, &ordinals);
    try std.testing.expectEqual(@as(usize, entries.len), count);
    try std.testing.expectEqualSlices(i32, &.{ 1, 1, 2, 2, 3, 4 }, keys[0..count]);
    try std.testing.expectEqualSlices(usize, &.{ 1, 3, 2, 5, 0, 4 }, ordinals[0..count]);
    try std.testing.expect(head.next == &entries[1].node);
    try std.testing.expect(head.prev == &entries[4].node);
    try std.testing.expect(entries[1].node.prev == &head);
    try std.testing.expect(entries[4].node.next == &head);

    var current = head.next;
    while (current != &head) : (current = current.?.next) {
        try std.testing.expect(current.?.next.?.prev == current.?);
        try std.testing.expect(current.?.prev.?.next == current.?);
    }
}
