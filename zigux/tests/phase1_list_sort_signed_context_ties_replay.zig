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

test "phase1 list_sort replay keeps signed ascending order stable across a later all-ties pass" {
    const signed_cmp = struct {
        fn compare(priv: ?*anyopaque, a: *const list_sort.ListHead, b: *const list_sort.ListHead) i32 {
            const mode: *const SortMode = @ptrCast(@alignCast(priv.?));
            const lhs: *const Entry = @fieldParentPtr("node", a);
            const rhs: *const Entry = @fieldParentPtr("node", b);
            const delta = lhs.key - rhs.key;
            return if (mode.* == .ascending) delta else -delta;
        }
    }.compare;

    const ties_cmp = struct {
        fn compare(_: ?*anyopaque, _: *const list_sort.ListHead, _: *const list_sort.ListHead) i32 {
            return 0;
        }
    }.compare;

    var head: list_sort.ListHead = .{};
    head.init();
    var entries = [_]Entry{
        .{ .key = -3, .ordinal = 0 },
        .{ .key = 7, .ordinal = 1 },
        .{ .key = -1, .ordinal = 2 },
        .{ .key = 7, .ordinal = 3 },
        .{ .key = 0, .ordinal = 4 },
        .{ .key = -3, .ordinal = 5 },
        .{ .key = 5, .ordinal = 6 },
    };
    for (&entries) |*entry| {
        list_sort.listAddTail(&entry.node, &head);
    }

    var mode = SortMode.descending;
    list_sort.listSort(&mode, &head, signed_cmp);

    var descending_keys: [7]i32 = undefined;
    var descending_ordinals: [7]usize = undefined;
    const descending_count = try collectSorted(&head, &descending_keys, &descending_ordinals);
    try std.testing.expectEqual(@as(usize, entries.len), descending_count);
    try std.testing.expectEqualSlices(i32, &.{ 7, 7, 5, 0, -1, -3, -3 }, descending_keys[0..descending_count]);
    try std.testing.expectEqualSlices(usize, &.{ 1, 3, 6, 4, 2, 0, 5 }, descending_ordinals[0..descending_count]);
    try std.testing.expect(head.next == &entries[1].node);
    try std.testing.expect(head.prev == &entries[5].node);

    mode = .ascending;
    list_sort.listSort(&mode, &head, signed_cmp);

    var ascending_keys: [7]i32 = undefined;
    var ascending_ordinals: [7]usize = undefined;
    const ascending_count = try collectSorted(&head, &ascending_keys, &ascending_ordinals);
    try std.testing.expectEqual(@as(usize, entries.len), ascending_count);
    try std.testing.expectEqualSlices(i32, &.{ -3, -3, -1, 0, 5, 7, 7 }, ascending_keys[0..ascending_count]);
    try std.testing.expectEqualSlices(usize, &.{ 0, 5, 2, 4, 6, 1, 3 }, ascending_ordinals[0..ascending_count]);
    try std.testing.expect(head.next == &entries[0].node);
    try std.testing.expect(head.prev == &entries[3].node);

    list_sort.listSort(null, &head, ties_cmp);

    var tied_keys: [7]i32 = undefined;
    var tied_ordinals: [7]usize = undefined;
    const tied_count = try collectSorted(&head, &tied_keys, &tied_ordinals);
    try std.testing.expectEqual(@as(usize, entries.len), tied_count);
    try std.testing.expectEqualSlices(i32, &.{ -3, -3, -1, 0, 5, 7, 7 }, tied_keys[0..tied_count]);
    try std.testing.expectEqualSlices(usize, &.{ 0, 5, 2, 4, 6, 1, 3 }, tied_ordinals[0..tied_count]);
    try std.testing.expect(head.next == &entries[0].node);
    try std.testing.expect(head.prev == &entries[3].node);
    try std.testing.expect(entries[0].node.prev == &head);
    try std.testing.expect(entries[3].node.next == &head);
}
