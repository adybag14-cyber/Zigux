const std = @import("std");
const list_sort = @import("list_sort");

const ListHead = list_sort.ListHead;
const listAddTail = list_sort.listAddTail;
const listSort = list_sort.listSort;

test "phase1 list_sort context replay preserves descending order and stable ties" {
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
    for (&entries) |*entry| listAddTail(&entry.node, &head);

    var mode = SortMode.descending;
    listSort(&mode, &head, cmp);

    var keys: [5]i32 = undefined;
    var ordinals: [5]usize = undefined;
    var idx: usize = 0;
    var current = head.next;
    while (current != &head) : (current = current.?.next) {
        const entry: *const Entry = @fieldParentPtr("node", current.?);
        keys[idx] = entry.key;
        ordinals[idx] = entry.ordinal;
        try std.testing.expect(current.?.next.?.prev == current.?);
        try std.testing.expect(current.?.prev.?.next == current.?);
        idx += 1;
    }

    try std.testing.expectEqualSlices(i32, &.{ 3, 3, 2, 1, 1 }, keys[0..idx]);
    try std.testing.expectEqualSlices(usize, &.{ 2, 4, 0, 1, 3 }, ordinals[0..idx]);
    try std.testing.expect(head.next == &entries[2].node);
    try std.testing.expect(head.prev == &entries[3].node);
    try std.testing.expect(entries[2].node.prev == &head);
    try std.testing.expect(entries[3].node.next == &head);
}
