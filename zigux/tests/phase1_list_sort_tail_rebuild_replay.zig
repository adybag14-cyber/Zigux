const std = @import("std");
const list_sort = @import("list_sort");

const Entry = struct {
    key: i32,
    band: i32,
    serial: usize,
    node: list_sort.ListHead = .{},
};

const SortMode = enum {
    key_ascending,
    band_descending,
    all_equal,
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
        .band_descending => {
            if (lhs.band > rhs.band) return -1;
            if (lhs.band < rhs.band) return 1;
            return 0;
        },
        .all_equal => return 0,
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
        try std.testing.expect(current.?.next.?.prev == current.?);
        try std.testing.expect(current.?.prev.?.next == current.?);
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

test "phase1 list_sort replay rebuilds from tail-drained staging" {
    var head: list_sort.ListHead = .{};
    var staging: list_sort.ListHead = .{};
    head.init();
    staging.init();

    var entries = [_]Entry{
        .{ .key = 4, .band = 1, .serial = 0 },
        .{ .key = 2, .band = 3, .serial = 1 },
        .{ .key = 5, .band = 2, .serial = 2 },
        .{ .key = 1, .band = 3, .serial = 3 },
        .{ .key = 4, .band = 0, .serial = 4 },
        .{ .key = 3, .band = 2, .serial = 5 },
        .{ .key = 2, .band = 1, .serial = 6 },
        .{ .key = 5, .band = 3, .serial = 7 },
        .{ .key = 1, .band = 0, .serial = 8 },
    };

    for (&entries) |*entry| list_sort.listAddTail(&entry.node, &head);

    var ctx = SortContext{ .mode = .key_ascending };
    list_sort.listSort(&ctx, &head, compare);
    try expectForward(entries.len, &head, &.{ 3, 8, 1, 6, 5, 0, 4, 2, 7 });
    try expectReverse(entries.len, &head, &.{ 7, 2, 4, 0, 5, 6, 1, 8, 3 });

    while (!list_sort.listEmpty(&head)) {
        const node = head.prev.?;
        list_sort.listDel(node);
        try std.testing.expect(node.next == null);
        try std.testing.expect(node.prev == null);
        list_sort.listAddTail(node, &staging);
    }

    try std.testing.expect(head.next == &head);
    try std.testing.expect(head.prev == &head);
    try expectForward(entries.len, &staging, &.{ 7, 2, 4, 0, 5, 6, 1, 8, 3 });

    ctx.mode = .band_descending;
    list_sort.listSort(&ctx, &staging, compare);
    try expectForward(entries.len, &staging, &.{ 7, 1, 3, 2, 5, 0, 6, 4, 8 });

    while (!list_sort.listEmpty(&staging)) {
        const node = staging.next.?;
        list_sort.listDel(node);
        try std.testing.expect(node.next == null);
        try std.testing.expect(node.prev == null);
        list_sort.listAddTail(node, &head);
    }

    try std.testing.expect(staging.next == &staging);
    try std.testing.expect(staging.prev == &staging);
    try expectForward(entries.len, &head, &.{ 7, 1, 3, 2, 5, 0, 6, 4, 8 });

    ctx.mode = .all_equal;
    list_sort.listSort(&ctx, &head, compare);
    try expectForward(entries.len, &head, &.{ 7, 1, 3, 2, 5, 0, 6, 4, 8 });
    try expectReverse(entries.len, &head, &.{ 8, 4, 6, 0, 5, 2, 3, 1, 7 });
    try std.testing.expect(head.next == &entries[7].node);
    try std.testing.expect(head.prev == &entries[8].node);
}
