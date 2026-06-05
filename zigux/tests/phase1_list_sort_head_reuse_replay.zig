const std = @import("std");
const list_sort = @import("list_sort");

const Entry = struct {
    key: i32,
    priority: i32,
    serial: usize,
    node: list_sort.ListHead = .{},
};

const SortMode = enum {
    key_ascending,
    priority_descending,
};

const SortContext = struct {
    mode: SortMode,
};

fn compare(ctx_ptr: ?*anyopaque, a: *const list_sort.ListHead, b: *const list_sort.ListHead) i32 {
    const ctx: *const SortContext = @ptrCast(@alignCast(ctx_ptr.?));
    const lhs: *const Entry = @fieldParentPtr("node", a);
    const rhs: *const Entry = @fieldParentPtr("node", b);

    switch (ctx.mode) {
        .key_ascending => {
            if (lhs.key < rhs.key) return -1;
            if (lhs.key > rhs.key) return 1;
            return 0;
        },
        .priority_descending => {
            if (lhs.priority > rhs.priority) return -1;
            if (lhs.priority < rhs.priority) return 1;
            return 0;
        },
    }
}

fn expectForward(comptime count: usize, head: *const list_sort.ListHead, expected: *const [count]usize) !void {
    var observed: [count]usize = undefined;
    var idx: usize = 0;
    var current = head.next;

    while (current != head) : (current = current.?.next) {
        try std.testing.expect(idx < count);
        const entry: *const Entry = @fieldParentPtr("node", current.?);
        observed[idx] = entry.serial;
        idx += 1;
    }

    try std.testing.expectEqual(count, idx);
    try std.testing.expectEqualSlices(usize, expected, &observed);
}

fn expectReverse(comptime count: usize, head: *const list_sort.ListHead, expected: *const [count]usize) !void {
    var observed: [count]usize = undefined;
    var idx: usize = 0;
    var current = head.prev;

    while (current != head) : (current = current.?.prev) {
        try std.testing.expect(idx < count);
        const entry: *const Entry = @fieldParentPtr("node", current.?);
        observed[idx] = entry.serial;
        idx += 1;
    }

    try std.testing.expectEqual(count, idx);
    try std.testing.expectEqualSlices(usize, expected, &observed);
}

test "phase1 list_sort replay reuses an emptied head after full drain" {
    var head: list_sort.ListHead = .{};
    head.init();

    var entries = [_]Entry{
        .{ .key = 5, .priority = 1, .serial = 0 },
        .{ .key = 2, .priority = 3, .serial = 1 },
        .{ .key = 7, .priority = 2, .serial = 2 },
        .{ .key = 2, .priority = 1, .serial = 3 },
        .{ .key = 5, .priority = 4, .serial = 4 },
        .{ .key = 7, .priority = 0, .serial = 5 },
        .{ .key = 3, .priority = 9, .serial = 6 },
    };

    for (&entries) |*entry| list_sort.listAddTail(&entry.node, &head);

    var ctx = SortContext{ .mode = .key_ascending };
    list_sort.listSort(&ctx, &head, compare);
    try expectForward(entries.len, &head, &.{ 1, 3, 6, 0, 4, 2, 5 });
    try expectReverse(entries.len, &head, &.{ 5, 2, 4, 0, 6, 3, 1 });

    var drained: [entries.len]*list_sort.ListHead = undefined;
    var drained_count: usize = 0;
    while (!list_sort.listEmpty(&head)) {
        const node = head.next.?;
        list_sort.listDel(node);
        try std.testing.expect(node.next == null);
        try std.testing.expect(node.prev == null);
        drained[drained_count] = node;
        drained_count += 1;
    }

    try std.testing.expectEqual(entries.len, drained_count);
    try std.testing.expect(head.next == &head);
    try std.testing.expect(head.prev == &head);

    for (0..drained_count) |idx| {
        const node = drained[drained_count - 1 - idx];
        list_sort.listAddTail(node, &head);
    }
    try expectForward(entries.len, &head, &.{ 5, 2, 4, 0, 6, 3, 1 });

    ctx.mode = .priority_descending;
    list_sort.listSort(&ctx, &head, compare);
    try expectForward(entries.len, &head, &.{ 6, 4, 1, 2, 0, 3, 5 });
    try expectReverse(entries.len, &head, &.{ 5, 3, 0, 2, 1, 4, 6 });
}
