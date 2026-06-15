const std = @import("std");
const core = @import("list_sort.zig");

pub const ListHead = core.ListHead;
pub const CmpFn = core.CmpFn;

pub fn list_empty(head: *const ListHead) bool {
    return core.listEmpty(head);
}

pub fn list_add(new: *ListHead, head: *ListHead) void {
    core.listAdd(new, head);
}

pub fn list_add_tail(new: *ListHead, head: *ListHead) void {
    core.listAddTail(new, head);
}

pub fn list_del(entry: *ListHead) void {
    core.listDel(entry);
}

pub fn list_sort(priv: ?*anyopaque, head: *ListHead, cmp: CmpFn) void {
    core.listSort(priv, head, cmp);
}

test "Linux-style list_sort wrappers mirror helper behavior" {
    const Entry = struct {
        key: i32,
        ordinal: usize,
        node: ListHead = .{},
    };

    const cmp = struct {
        fn less(_: ?*anyopaque, a: *const ListHead, b: *const ListHead) i32 {
            const lhs: *const Entry = @fieldParentPtr("node", a);
            const rhs: *const Entry = @fieldParentPtr("node", b);
            if (lhs.key < rhs.key) return -1;
            if (lhs.key > rhs.key) return 1;
            return 0;
        }
    }.less;

    var head: ListHead = .{};
    head.init();
    try std.testing.expect(list_empty(&head));

    var entries = [_]Entry{
        .{ .key = 3, .ordinal = 0 },
        .{ .key = 1, .ordinal = 1 },
        .{ .key = 3, .ordinal = 2 },
        .{ .key = 2, .ordinal = 3 },
    };

    list_add(&entries[0].node, &head);
    list_add_tail(&entries[1].node, &head);
    list_add_tail(&entries[2].node, &head);
    list_add(&entries[3].node, &head);
    try std.testing.expect(!list_empty(&head));

    list_del(&entries[3].node);
    try std.testing.expect(entries[3].node.next == null);
    try std.testing.expect(entries[3].node.prev == null);

    list_sort(null, &head, cmp);

    var keys: [3]i32 = undefined;
    var ordinals: [3]usize = undefined;
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

    try std.testing.expectEqualSlices(i32, &.{ 1, 3, 3 }, keys[0..idx]);
    try std.testing.expectEqualSlices(usize, &.{ 1, 0, 2 }, ordinals[0..idx]);
    try std.testing.expect(head.next == &entries[1].node);
    try std.testing.expect(head.prev == &entries[2].node);
}
