const std = @import("std");
const list_sort = @import("list_sort");

const ListHead = list_sort.ListHead;

test "phase1 list_sort replay can reorder the same circular list twice with comparator context" {
    const Entry = struct {
        key: i32,
        ordinal: usize,
        node: ListHead = .{},
    };

    const SortMode = enum { ascending, descending };

    const cmp = struct {
        fn less(priv: ?*anyopaque, a: *const ListHead, b: *const ListHead) i32 {
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
    }.less;

    var head: ListHead = .{};
    head.init();
    var entries = [_]Entry{
        .{ .key = 2, .ordinal = 0 },
        .{ .key = 1, .ordinal = 1 },
        .{ .key = 3, .ordinal = 2 },
        .{ .key = 1, .ordinal = 3 },
        .{ .key = 3, .ordinal = 4 },
    };
    for (&entries) |*entry| list_sort.listAddTail(&entry.node, &head);

    var mode = SortMode.descending;
    list_sort.listSort(&mode, &head, cmp);

    var descending_keys: [5]i32 = undefined;
    var descending_ordinals: [5]usize = undefined;
    var descending_idx: usize = 0;
    var current = head.next;
    while (current != &head) : (current = current.?.next) {
        const entry: *const Entry = @fieldParentPtr("node", current.?);
        descending_keys[descending_idx] = entry.key;
        descending_ordinals[descending_idx] = entry.ordinal;
        try std.testing.expect(current.?.next.?.prev == current.?);
        try std.testing.expect(current.?.prev.?.next == current.?);
        descending_idx += 1;
    }

    try std.testing.expectEqualSlices(i32, &.{ 3, 3, 2, 1, 1 }, descending_keys[0..descending_idx]);
    try std.testing.expectEqualSlices(usize, &.{ 2, 4, 0, 1, 3 }, descending_ordinals[0..descending_idx]);
    try std.testing.expect(head.next == &entries[2].node);
    try std.testing.expect(head.prev == &entries[3].node);

    mode = .ascending;
    list_sort.listSort(&mode, &head, cmp);

    var ascending_keys: [5]i32 = undefined;
    var ascending_ordinals: [5]usize = undefined;
    var ascending_idx: usize = 0;
    current = head.next;
    while (current != &head) : (current = current.?.next) {
        const entry: *const Entry = @fieldParentPtr("node", current.?);
        ascending_keys[ascending_idx] = entry.key;
        ascending_ordinals[ascending_idx] = entry.ordinal;
        try std.testing.expect(current.?.next.?.prev == current.?);
        try std.testing.expect(current.?.prev.?.next == current.?);
        ascending_idx += 1;
    }

    try std.testing.expectEqualSlices(i32, &.{ 1, 1, 2, 3, 3 }, ascending_keys[0..ascending_idx]);
    try std.testing.expectEqualSlices(usize, &.{ 1, 3, 0, 2, 4 }, ascending_ordinals[0..ascending_idx]);
    try std.testing.expect(head.next == &entries[1].node);
    try std.testing.expect(head.prev == &entries[4].node);
    try std.testing.expect(entries[1].node.prev == &head);
    try std.testing.expect(entries[4].node.next == &head);
}
