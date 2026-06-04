const std = @import("std");
const list_sort = @import("list_sort");

const ListHead = list_sort.ListHead;

const Entry = struct {
    key: i32,
    node: ListHead = .{},
};

fn forbiddenCmp(priv: ?*anyopaque, a: *const ListHead, b: *const ListHead) i32 {
    const calls: *usize = @ptrCast(@alignCast(priv.?));
    calls.* += 1;

    const lhs: *const Entry = @fieldParentPtr("node", a);
    const rhs: *const Entry = @fieldParentPtr("node", b);
    if (lhs.key < rhs.key) return -1;
    if (lhs.key > rhs.key) return 1;
    return 0;
}

test "list_sort returns before comparator for empty and singleton inputs" {
    var calls: usize = 0;

    var empty_head: ListHead = .{};
    empty_head.init();
    list_sort.listSort(&calls, &empty_head, forbiddenCmp);
    try std.testing.expect(list_sort.listEmpty(&empty_head));
    try std.testing.expectEqual(@as(usize, 0), calls);

    var singleton_head: ListHead = .{};
    singleton_head.init();
    var entry = Entry{ .key = 7 };
    list_sort.listAddTail(&entry.node, &singleton_head);

    list_sort.listSort(&calls, &singleton_head, forbiddenCmp);
    try std.testing.expectEqual(@as(usize, 0), calls);
    try std.testing.expect(singleton_head.next == &entry.node);
    try std.testing.expect(singleton_head.prev == &entry.node);
    try std.testing.expect(entry.node.next == &singleton_head);
    try std.testing.expect(entry.node.prev == &singleton_head);
}
