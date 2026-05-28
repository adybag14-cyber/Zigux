const std = @import("std");
const list_sort = @import("list_sort");

const Entry = struct {
    key: i32,
    ordinal: usize,
    node: list_sort.ListHead = .{},
};

test "phase1 list_sort parity-bucket replay preserves stable bucket order" {
    const cmp = struct {
        fn less(_: ?*anyopaque, a: *const list_sort.ListHead, b: *const list_sort.ListHead) i32 {
            const lhs: *const Entry = @fieldParentPtr("node", a);
            const rhs: *const Entry = @fieldParentPtr("node", b);
            const lhs_is_odd = @mod(lhs.key, 2) != 0;
            const rhs_is_odd = @mod(rhs.key, 2) != 0;
            if (lhs_is_odd == rhs_is_odd) return 0;
            return if (lhs_is_odd) -1 else 1;
        }
    }.less;

    var head: list_sort.ListHead = .{};
    head.init();
    var entries = [_]Entry{
        .{ .key = 4, .ordinal = 0 },
        .{ .key = 1, .ordinal = 1 },
        .{ .key = 6, .ordinal = 2 },
        .{ .key = 3, .ordinal = 3 },
        .{ .key = 2, .ordinal = 4 },
        .{ .key = 5, .ordinal = 5 },
        .{ .key = 8, .ordinal = 6 },
        .{ .key = 7, .ordinal = 7 },
    };
    for (&entries) |*entry| list_sort.listAddTail(&entry.node, &head);

    list_sort.listSort(null, &head, cmp);

    var keys: [entries.len]i32 = undefined;
    var ordinals: [entries.len]usize = undefined;
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
    try std.testing.expectEqualSlices(i32, &.{ 1, 3, 5, 7, 4, 6, 2, 8 }, keys[0..idx]);
    try std.testing.expectEqualSlices(usize, &.{ 1, 3, 5, 7, 0, 2, 4, 6 }, ordinals[0..idx]);
    try std.testing.expect(head.next == &entries[1].node);
    try std.testing.expect(head.prev == &entries[6].node);
}
