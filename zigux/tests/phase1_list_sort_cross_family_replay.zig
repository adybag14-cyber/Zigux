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
        try std.testing.expect(current.?.next.?.prev == current.?);
        try std.testing.expect(current.?.prev.?.next == current.?);
        count += 1;
    }
    return count;
}

test "phase1 list_sort replay reuses one circular list across signed boolean and non-unit comparator families" {
    const SortMode = enum { ascending, descending };

    const signed_cmp = struct {
        fn compare(priv: ?*anyopaque, a: *const list_sort.ListHead, b: *const list_sort.ListHead) i32 {
            const mode: *const SortMode = @ptrCast(@alignCast(priv.?));
            const lhs: *const Entry = @fieldParentPtr("node", a);
            const rhs: *const Entry = @fieldParentPtr("node", b);
            const delta = lhs.key - rhs.key;
            return if (mode.* == .ascending) delta else -delta;
        }
    }.compare;

    const bool_cmp = struct {
        fn compare(priv: ?*anyopaque, a: *const list_sort.ListHead, b: *const list_sort.ListHead) i32 {
            const mode: *const SortMode = @ptrCast(@alignCast(priv.?));
            const lhs: *const Entry = @fieldParentPtr("node", a);
            const rhs: *const Entry = @fieldParentPtr("node", b);
            if (lhs.key == rhs.key) return 0;
            return if (mode.* == .ascending)
                @intFromBool(lhs.key > rhs.key)
            else
                @intFromBool(lhs.key < rhs.key);
        }
    }.compare;

    const non_unit_cmp = struct {
        fn compare(priv: ?*anyopaque, a: *const list_sort.ListHead, b: *const list_sort.ListHead) i32 {
            const mode: *const SortMode = @ptrCast(@alignCast(priv.?));
            const lhs: *const Entry = @fieldParentPtr("node", a);
            const rhs: *const Entry = @fieldParentPtr("node", b);

            if (lhs.key == rhs.key) return 0;
            const ascending = lhs.key < rhs.key;
            return if (mode.* == .ascending)
                (if (ascending) -11 else 13)
            else
                (if (ascending) 13 else -11);
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

    mode = .ascending;
    list_sort.listSort(&mode, &head, bool_cmp);

    mode = .descending;
    list_sort.listSort(&mode, &head, non_unit_cmp);

    var keys: [7]i32 = undefined;
    var ordinals: [7]usize = undefined;
    const count = try collectSorted(&head, &keys, &ordinals);
    try std.testing.expectEqual(@as(usize, entries.len), count);
    try std.testing.expectEqualSlices(i32, &.{ 7, 7, 5, 0, -1, -3, -3 }, keys[0..count]);
    try std.testing.expectEqualSlices(usize, &.{ 1, 3, 6, 4, 2, 0, 5 }, ordinals[0..count]);
    try std.testing.expect(head.next == &entries[1].node);
    try std.testing.expect(head.prev == &entries[5].node);
    try std.testing.expect(entries[1].node.prev == &head);
    try std.testing.expect(entries[5].node.next == &head);
}
