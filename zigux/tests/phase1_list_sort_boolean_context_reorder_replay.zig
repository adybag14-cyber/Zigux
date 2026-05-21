const std = @import("std");
const list_sort = @import("list_sort");

const Entry = struct {
    key: i32,
    ordinal: usize,
    node: list_sort.ListHead = .{},
};

const SortMode = enum { ascending, descending };

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
        try std.testing.expect(current.?.next.?.prev == current.?);
        try std.testing.expect(current.?.prev.?.next == current.?);
        count += 1;
    }
    return count;
}

test "phase1 list_sort replay reuses boolean comparator context across repeated reordering" {
    const cmp = struct {
        fn compare(priv: ?*anyopaque, a: *const list_sort.ListHead, b: *const list_sort.ListHead) i32 {
            const mode: *const SortMode = @ptrCast(@alignCast(priv.?));
            const lhs: *const Entry = @fieldParentPtr("node", a);
            const rhs: *const Entry = @fieldParentPtr("node", b);
            const ascending = lhs.key < rhs.key;
            return if (mode.* == .ascending)
                @intFromBool(!ascending)
            else
                @intFromBool(ascending);
        }
    }.compare;

    var head: list_sort.ListHead = .{};
    head.init();
    var entries = [_]Entry{
        .{ .key = 2, .ordinal = 0 },
        .{ .key = 1, .ordinal = 1 },
        .{ .key = 3, .ordinal = 2 },
        .{ .key = 1, .ordinal = 3 },
        .{ .key = 3, .ordinal = 4 },
        .{ .key = 2, .ordinal = 5 },
    };
    for (&entries) |*entry| {
        list_sort.listAddTail(&entry.node, &head);
    }

    var mode = SortMode.descending;
    list_sort.listSort(&mode, &head, cmp);

    var descending_keys: [6]i32 = undefined;
    var descending_ordinals: [6]usize = undefined;
    const descending_count = try collectSorted(&head, &descending_keys, &descending_ordinals);
    try std.testing.expectEqual(@as(usize, entries.len), descending_count);
    try std.testing.expectEqualSlices(i32, &.{ 3, 3, 2, 2, 1, 1 }, descending_keys[0..descending_count]);
    try std.testing.expectEqualSlices(usize, &.{ 2, 4, 0, 5, 1, 3 }, descending_ordinals[0..descending_count]);
    try std.testing.expect(head.next == &entries[2].node);
    try std.testing.expect(head.prev == &entries[3].node);

    mode = .ascending;
    list_sort.listSort(&mode, &head, cmp);

    var ascending_keys: [6]i32 = undefined;
    var ascending_ordinals: [6]usize = undefined;
    const ascending_count = try collectSorted(&head, &ascending_keys, &ascending_ordinals);
    try std.testing.expectEqual(@as(usize, entries.len), ascending_count);
    try std.testing.expectEqualSlices(i32, &.{ 1, 1, 2, 2, 3, 3 }, ascending_keys[0..ascending_count]);
    try std.testing.expectEqualSlices(usize, &.{ 3, 1, 5, 0, 4, 2 }, ascending_ordinals[0..ascending_count]);
    try std.testing.expect(head.next == &entries[3].node);
    try std.testing.expect(head.prev == &entries[2].node);
    try std.testing.expect(entries[3].node.prev == &head);
    try std.testing.expect(entries[2].node.next == &head);
}
