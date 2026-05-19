const std = @import("std");
const list_sort = @import("list_sort");

const Entry = struct {
    key: i32,
    ordinal: usize,
    node: list_sort.ListHead = .{},
};

test "phase1 list_sort replay preserves stable modulo bucket order across a longer merge path" {
    const cmp = struct {
        fn compare(_: ?*anyopaque, a: *const list_sort.ListHead, b: *const list_sort.ListHead) i32 {
            const lhs: *const Entry = @fieldParentPtr("node", a);
            const rhs: *const Entry = @fieldParentPtr("node", b);
            const lhs_bucket = @mod(lhs.key, 3);
            const rhs_bucket = @mod(rhs.key, 3);
            if (lhs_bucket == rhs_bucket) return 0;
            return if (lhs_bucket < rhs_bucket) -1 else 1;
        }
    }.compare;

    var head: list_sort.ListHead = .{};
    head.init();
    var entries = [_]Entry{
        .{ .key = 8, .ordinal = 0 },
        .{ .key = 3, .ordinal = 1 },
        .{ .key = 10, .ordinal = 2 },
        .{ .key = 1, .ordinal = 3 },
        .{ .key = 7, .ordinal = 4 },
        .{ .key = 4, .ordinal = 5 },
        .{ .key = 6, .ordinal = 6 },
        .{ .key = 11, .ordinal = 7 },
        .{ .key = 0, .ordinal = 8 },
        .{ .key = 5, .ordinal = 9 },
        .{ .key = 9, .ordinal = 10 },
        .{ .key = 2, .ordinal = 11 },
    };
    for (&entries) |*entry| {
        list_sort.listAddTail(&entry.node, &head);
    }

    list_sort.listSort(null, &head, cmp);

    var keys: [12]i32 = undefined;
    var ordinals: [12]usize = undefined;
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

    try std.testing.expectEqual(@as(usize, entries.len), idx);
    try std.testing.expectEqualSlices(i32, &.{ 3, 6, 0, 9, 10, 1, 7, 4, 8, 11, 5, 2 }, keys[0..idx]);
    try std.testing.expectEqualSlices(usize, &.{ 1, 6, 8, 10, 2, 3, 4, 5, 0, 7, 9, 11 }, ordinals[0..idx]);
    try std.testing.expect(head.next == &entries[1].node);
    try std.testing.expect(head.prev == &entries[11].node);
    try std.testing.expect(entries[1].node.prev == &head);
    try std.testing.expect(entries[11].node.next == &head);
}
