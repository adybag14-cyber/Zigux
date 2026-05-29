const std = @import("std");
const list_sort = @import("list_sort");

const Entry = struct {
    key: i32,
    node: list_sort.ListHead = .{},
};

const CompareContext = struct {
    calls: usize = 0,
};

fn countingCmp(priv: ?*anyopaque, a: *const list_sort.ListHead, b: *const list_sort.ListHead) i32 {
    const context: *CompareContext = @ptrCast(@alignCast(priv.?));
    const lhs: *const Entry = @fieldParentPtr("node", a);
    const rhs: *const Entry = @fieldParentPtr("node", b);
    context.calls += 1;
    if (lhs.key < rhs.key) return -1;
    if (lhs.key > rhs.key) return 1;
    return 0;
}

test "phase1 list_sort leaves trivial rings without comparator calls" {
    var context = CompareContext{};

    var empty_head: list_sort.ListHead = .{};
    empty_head.init();
    list_sort.listSort(&context, &empty_head, countingCmp);
    try std.testing.expectEqual(@as(usize, 0), context.calls);
    try std.testing.expect(list_sort.listEmpty(&empty_head));
    try std.testing.expect(empty_head.next == &empty_head);
    try std.testing.expect(empty_head.prev == &empty_head);

    var singleton_head: list_sort.ListHead = .{};
    singleton_head.init();
    var entry = Entry{ .key = 42 };
    list_sort.listAddTail(&entry.node, &singleton_head);

    list_sort.listSort(&context, &singleton_head, countingCmp);
    try std.testing.expectEqual(@as(usize, 0), context.calls);
    try std.testing.expect(singleton_head.next == &entry.node);
    try std.testing.expect(singleton_head.prev == &entry.node);
    try std.testing.expect(entry.node.next == &singleton_head);
    try std.testing.expect(entry.node.prev == &singleton_head);
}
