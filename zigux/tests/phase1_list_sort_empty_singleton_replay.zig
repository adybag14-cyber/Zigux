const std = @import("std");
const list_sort = @import("list_sort");

const ListHead = list_sort.ListHead;

const Entry = struct {
    key: i32,
    ordinal: usize,
    node: ListHead = .{},
};

fn cmpAscending(_: ?*anyopaque, a: *const ListHead, b: *const ListHead) i32 {
    const lhs: *const Entry = @fieldParentPtr("node", a);
    const rhs: *const Entry = @fieldParentPtr("node", b);
    if (lhs.key < rhs.key) return -1;
    if (lhs.key > rhs.key) return 1;
    return 0;
}

fn cmpAllTies(_: ?*anyopaque, _: *const ListHead, _: *const ListHead) i32 {
    return 0;
}

fn collectOrdinals(head: *ListHead, out: []usize) ![]usize {
    var idx: usize = 0;
    var current = head.next;
    while (current != head) : (current = current.?.next) {
        try std.testing.expect(idx < out.len);
        const entry: *const Entry = @fieldParentPtr("node", current.?);
        out[idx] = entry.ordinal;
        try std.testing.expect(current.?.next.?.prev == current.?);
        try std.testing.expect(current.?.prev.?.next == current.?);
        idx += 1;
    }
    return out[0..idx];
}

test "empty and singleton list sort keep circular sentinels intact" {
    var empty_head: ListHead = .{};
    empty_head.init();
    list_sort.listSort(null, &empty_head, cmpAscending);
    try std.testing.expect(list_sort.listEmpty(&empty_head));
    try std.testing.expect(empty_head.next == &empty_head);
    try std.testing.expect(empty_head.prev == &empty_head);

    var singleton_head: ListHead = .{};
    singleton_head.init();
    var entry = Entry{ .key = 42, .ordinal = 0 };
    list_sort.listAddTail(&entry.node, &singleton_head);

    list_sort.listSort(null, &singleton_head, cmpAscending);
    try std.testing.expect(singleton_head.next == &entry.node);
    try std.testing.expect(singleton_head.prev == &entry.node);
    try std.testing.expect(entry.node.next == &singleton_head);
    try std.testing.expect(entry.node.prev == &singleton_head);

    list_sort.listSort(null, &singleton_head, cmpAllTies);
    try std.testing.expect(singleton_head.next == &entry.node);
    try std.testing.expect(singleton_head.prev == &entry.node);
    try std.testing.expect(entry.node.next == &singleton_head);
    try std.testing.expect(entry.node.prev == &singleton_head);
}

test "delete and reinsert after singleton sort remains reusable" {
    var head: ListHead = .{};
    head.init();

    var entries = [_]Entry{
        .{ .key = 3, .ordinal = 0 },
        .{ .key = 1, .ordinal = 1 },
        .{ .key = 2, .ordinal = 2 },
    };

    list_sort.listAddTail(&entries[0].node, &head);
    list_sort.listSort(null, &head, cmpAscending);
    try std.testing.expect(head.next == &entries[0].node);
    try std.testing.expect(head.prev == &entries[0].node);

    list_sort.listDel(&entries[0].node);
    try std.testing.expect(list_sort.listEmpty(&head));
    try std.testing.expect(entries[0].node.next == null);
    try std.testing.expect(entries[0].node.prev == null);

    list_sort.listAddTail(&entries[0].node, &head);
    list_sort.listAddTail(&entries[1].node, &head);
    list_sort.listAddTail(&entries[2].node, &head);
    list_sort.listSort(null, &head, cmpAscending);

    var ordinals: [3]usize = undefined;
    try std.testing.expectEqualSlices(
        usize,
        &.{ 1, 2, 0 },
        try collectOrdinals(&head, &ordinals),
    );
    try std.testing.expect(head.next == &entries[1].node);
    try std.testing.expect(head.prev == &entries[0].node);
}
