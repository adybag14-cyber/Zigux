const std = @import("std");
const list_sort = @import("list_sort");

const Entry = struct {
    key: i32,
    node: list_sort.ListHead = .{},
};

const ComparatorState = struct {
    calls: usize = 0,
};

fn countingCompare(
    priv: ?*anyopaque,
    a: *const list_sort.ListHead,
    b: *const list_sort.ListHead,
) i32 {
    const state: *ComparatorState = @ptrCast(@alignCast(priv.?));
    state.calls += 1;

    const lhs: *const Entry = @fieldParentPtr("node", a);
    const rhs: *const Entry = @fieldParentPtr("node", b);
    if (lhs.key < rhs.key) return -1;
    if (lhs.key > rhs.key) return 1;
    return 0;
}

test "phase1 list_sort trivial replay skips comparator for empty and singleton lists" {
    var state = ComparatorState{};

    var empty_head: list_sort.ListHead = .{};
    empty_head.init();
    list_sort.listSort(&state, &empty_head, countingCompare);

    try std.testing.expectEqual(@as(usize, 0), state.calls);
    try std.testing.expect(list_sort.listEmpty(&empty_head));
    try std.testing.expect(empty_head.next == &empty_head);
    try std.testing.expect(empty_head.prev == &empty_head);

    var singleton_head: list_sort.ListHead = .{};
    singleton_head.init();
    var entry = Entry{ .key = 7 };
    list_sort.listAddTail(&entry.node, &singleton_head);

    list_sort.listSort(&state, &singleton_head, countingCompare);

    try std.testing.expectEqual(@as(usize, 0), state.calls);
    try std.testing.expect(!list_sort.listEmpty(&singleton_head));
    try std.testing.expect(singleton_head.next == &entry.node);
    try std.testing.expect(singleton_head.prev == &entry.node);
    try std.testing.expect(entry.node.next == &singleton_head);
    try std.testing.expect(entry.node.prev == &singleton_head);
}
