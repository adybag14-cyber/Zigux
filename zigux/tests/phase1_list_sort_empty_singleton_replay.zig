const std = @import("std");
const list_sort = @import("list_sort");

const Entry = struct {
    key: i32,
    ordinal: usize,
    node: list_sort.ListHead = .{},
};

fn descendingCmp(_: ?*anyopaque, a: *const list_sort.ListHead, b: *const list_sort.ListHead) i32 {
    const lhs: *const Entry = @fieldParentPtr("node", a);
    const rhs: *const Entry = @fieldParentPtr("node", b);
    if (lhs.key == rhs.key) return 0;
    return if (lhs.key > rhs.key) -1 else 1;
}

fn tiesCmp(_: ?*anyopaque, _: *const list_sort.ListHead, _: *const list_sort.ListHead) i32 {
    return 0;
}

test "phase1 list_sort empty and singleton replay keeps sentinels stable across repeated sorts" {
    var empty_head: list_sort.ListHead = .{};
    empty_head.init();

    list_sort.listSort(null, &empty_head, tiesCmp);
    try std.testing.expect(list_sort.listEmpty(&empty_head));
    try std.testing.expect(empty_head.next == &empty_head);
    try std.testing.expect(empty_head.prev == &empty_head);

    var single_head: list_sort.ListHead = .{};
    single_head.init();
    var entry = Entry{ .key = 7, .ordinal = 0 };
    list_sort.listAddTail(&entry.node, &single_head);

    list_sort.listSort(null, &single_head, descendingCmp);
    list_sort.listSort(null, &single_head, tiesCmp);

    try std.testing.expect(!list_sort.listEmpty(&single_head));
    try std.testing.expect(single_head.next == &entry.node);
    try std.testing.expect(single_head.prev == &entry.node);
    try std.testing.expect(entry.node.next == &single_head);
    try std.testing.expect(entry.node.prev == &single_head);

    const replayed: *const Entry = @fieldParentPtr("node", single_head.next.?);
    try std.testing.expectEqual(@as(i32, 7), replayed.key);
    try std.testing.expectEqual(@as(usize, 0), replayed.ordinal);
}
