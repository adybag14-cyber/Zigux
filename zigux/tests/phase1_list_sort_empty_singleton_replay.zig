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

test "phase1 list_sort empty and singleton replay preserves sentinel links" {
    const cmp = struct {
        fn compare(_: ?*anyopaque, a: *const list_sort.ListHead, b: *const list_sort.ListHead) i32 {
            const lhs: *const Entry = @fieldParentPtr("node", a);
            const rhs: *const Entry = @fieldParentPtr("node", b);
            return @intCast(@intFromBool(lhs.key > rhs.key));
        }
    }.compare;

    var empty_head: list_sort.ListHead = .{};
    empty_head.init();
    list_sort.listSort(null, &empty_head, cmp);

    try std.testing.expect(list_sort.listEmpty(&empty_head));
    try std.testing.expect(empty_head.next == &empty_head);
    try std.testing.expect(empty_head.prev == &empty_head);
    try std.testing.expect(empty_head.next.?.prev == &empty_head);
    try std.testing.expect(empty_head.prev.?.next == &empty_head);

    var single_head: list_sort.ListHead = .{};
    single_head.init();
    var entry = Entry{ .key = 7, .ordinal = 0 };
    list_sort.listAddTail(&entry.node, &single_head);
    list_sort.listSort(null, &single_head, cmp);

    var keys: [1]i32 = undefined;
    var ordinals: [1]usize = undefined;
    const count = try collectSorted(&single_head, &keys, &ordinals);
    try std.testing.expectEqual(@as(usize, 1), count);
    try std.testing.expectEqualSlices(i32, &.{7}, keys[0..count]);
    try std.testing.expectEqualSlices(usize, &.{0}, ordinals[0..count]);
    try std.testing.expect(single_head.next == &entry.node);
    try std.testing.expect(single_head.prev == &entry.node);
    try std.testing.expect(entry.node.next == &single_head);
    try std.testing.expect(entry.node.prev == &single_head);
    try std.testing.expect(single_head.next.?.prev == &single_head);
    try std.testing.expect(single_head.prev.?.next == &single_head);
}
