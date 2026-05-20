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

test "phase1 list_sort replay preserves input order when every comparison ties" {
    const ties_cmp = struct {
        fn compare(_: ?*anyopaque, _: *const list_sort.ListHead, _: *const list_sort.ListHead) i32 {
            return 0;
        }
    }.compare;

    var head: list_sort.ListHead = .{};
    head.init();
    var entries = [_]Entry{
        .{ .key = 4, .ordinal = 0 },
        .{ .key = -1, .ordinal = 1 },
        .{ .key = 4, .ordinal = 2 },
        .{ .key = 0, .ordinal = 3 },
        .{ .key = -1, .ordinal = 4 },
        .{ .key = 7, .ordinal = 5 },
    };
    for (&entries) |*entry| {
        list_sort.listAddTail(&entry.node, &head);
    }

    list_sort.listSort(null, &head, ties_cmp);

    var keys: [6]i32 = undefined;
    var ordinals: [6]usize = undefined;
    const count = try collectSorted(&head, &keys, &ordinals);
    try std.testing.expectEqual(@as(usize, entries.len), count);
    try std.testing.expectEqualSlices(i32, &.{ 4, -1, 4, 0, -1, 7 }, keys[0..count]);
    try std.testing.expectEqualSlices(usize, &.{ 0, 1, 2, 3, 4, 5 }, ordinals[0..count]);
    try std.testing.expect(head.next == &entries[0].node);
    try std.testing.expect(head.prev == &entries[5].node);
    try std.testing.expect(entries[0].node.prev == &head);
    try std.testing.expect(entries[5].node.next == &head);

    var current = head.next;
    while (current != &head) : (current = current.?.next) {
        try std.testing.expect(current.?.next.?.prev == current.?);
        try std.testing.expect(current.?.prev.?.next == current.?);
    }
}
