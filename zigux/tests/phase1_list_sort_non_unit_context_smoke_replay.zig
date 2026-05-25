const std = @import("std");
const list_sort = @import("list_sort");

const Entry = struct {
    key: i32,
    ordinal: usize,
    node: list_sort.ListHead = .{},
};

test "phase1 list_sort non-unit context smoke replay keeps descending order stable" {
    const SortMode = enum { ascending, descending };

    const cmp = struct {
        fn less(priv: ?*anyopaque, a: *const list_sort.ListHead, b: *const list_sort.ListHead) i32 {
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
    }.less;

    var head: list_sort.ListHead = .{};
    head.init();
    var entries = [_]Entry{
        .{ .key = 2, .ordinal = 0 },
        .{ .key = 5, .ordinal = 1 },
        .{ .key = 1, .ordinal = 2 },
        .{ .key = 5, .ordinal = 3 },
        .{ .key = 4, .ordinal = 4 },
        .{ .key = 1, .ordinal = 5 },
    };
    for (&entries) |*entry| {
        list_sort.listAddTail(&entry.node, &head);
    }

    var mode = SortMode.descending;
    list_sort.listSort(&mode, &head, cmp);

    var sorted_keys: [6]i32 = undefined;
    var sorted_ordinals: [6]usize = undefined;
    var sorted_count: usize = 0;
    var sorted_node = head.next;
    while (sorted_node != &head) : (sorted_node = sorted_node.?.next) {
        const entry: *const Entry = @fieldParentPtr("node", sorted_node.?);
        sorted_keys[sorted_count] = entry.key;
        sorted_ordinals[sorted_count] = entry.ordinal;
        try std.testing.expect(sorted_node.?.next.?.prev == sorted_node.?);
        try std.testing.expect(sorted_node.?.prev.?.next == sorted_node.?);
        sorted_count += 1;
    }

    try std.testing.expectEqualSlices(i32, &.{ 5, 5, 4, 2, 1, 1 }, sorted_keys[0..sorted_count]);
    try std.testing.expectEqualSlices(usize, &.{ 1, 3, 4, 0, 2, 5 }, sorted_ordinals[0..sorted_count]);
    try std.testing.expect(head.next == &entries[1].node);
    try std.testing.expect(head.prev == &entries[5].node);
}
