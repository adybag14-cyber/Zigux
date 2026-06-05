const std = @import("std");
const list_sort = @import("list_sort");

const Entry = struct {
    key: i32,
    ordinal: usize,
    node: list_sort.ListHead = .{},
};

const ascending_cmp = struct {
    fn compare(_: ?*anyopaque, a: *const list_sort.ListHead, b: *const list_sort.ListHead) i32 {
        const lhs: *const Entry = @fieldParentPtr("node", a);
        const rhs: *const Entry = @fieldParentPtr("node", b);
        if (lhs.key < rhs.key) return -1;
        if (lhs.key > rhs.key) return 1;
        return 0;
    }
}.compare;

const modulo_cmp = struct {
    fn compare(_: ?*anyopaque, a: *const list_sort.ListHead, b: *const list_sort.ListHead) i32 {
        const lhs: *const Entry = @fieldParentPtr("node", a);
        const rhs: *const Entry = @fieldParentPtr("node", b);
        const lhs_bucket = @mod(lhs.key, 3);
        const rhs_bucket = @mod(rhs.key, 3);
        if (lhs_bucket == rhs_bucket) return 0;
        return if (lhs_bucket < rhs_bucket) -1 else 1;
    }
}.compare;

fn expectForward(head: *const list_sort.ListHead, expected_keys: []const i32, expected_ordinals: []const usize) !void {
    var keys: [16]i32 = undefined;
    var ordinals: [16]usize = undefined;
    var idx: usize = 0;
    var current = head.next;

    while (current != head) : (current = current.?.next) {
        const entry: *const Entry = @fieldParentPtr("node", current.?);
        keys[idx] = entry.key;
        ordinals[idx] = entry.ordinal;
        try std.testing.expect(current.?.next.?.prev == current.?);
        try std.testing.expect(current.?.prev.?.next == current.?);
        idx += 1;
    }

    try std.testing.expectEqualSlices(i32, expected_keys, keys[0..idx]);
    try std.testing.expectEqualSlices(usize, expected_ordinals, ordinals[0..idx]);
}

fn expectBackward(head: *const list_sort.ListHead, expected_ordinals: []const usize) !void {
    var ordinals: [16]usize = undefined;
    var idx: usize = 0;
    var current = head.prev;

    while (current != head) : (current = current.?.prev) {
        const entry: *const Entry = @fieldParentPtr("node", current.?);
        ordinals[idx] = entry.ordinal;
        idx += 1;
    }

    try std.testing.expectEqualSlices(usize, expected_ordinals, ordinals[0..idx]);
}

test "phase1 list_sort replay preserves order after rotating a sorted window" {
    var head: list_sort.ListHead = .{};
    head.init();
    var staging: list_sort.ListHead = .{};
    staging.init();

    var entries = [_]Entry{
        .{ .key = 9, .ordinal = 0 },
        .{ .key = 1, .ordinal = 1 },
        .{ .key = 7, .ordinal = 2 },
        .{ .key = 3, .ordinal = 3 },
        .{ .key = 5, .ordinal = 4 },
        .{ .key = 2, .ordinal = 5 },
        .{ .key = 8, .ordinal = 6 },
        .{ .key = 4, .ordinal = 7 },
        .{ .key = 6, .ordinal = 8 },
        .{ .key = 0, .ordinal = 9 },
    };
    for (&entries) |*entry| list_sort.listAddTail(&entry.node, &head);

    list_sort.listSort(null, &head, ascending_cmp);
    try expectForward(
        &head,
        &.{ 0, 1, 2, 3, 4, 5, 6, 7, 8, 9 },
        &.{ 9, 1, 5, 3, 7, 4, 8, 2, 6, 0 },
    );

    var cursor = head.next.?.next.?.next.?.next;
    for (0..3) |_| {
        const node = cursor.?;
        cursor = node.next;
        list_sort.listDel(node);
        try std.testing.expect(node.next == null);
        try std.testing.expect(node.prev == null);
        list_sort.listAddTail(node, &staging);
    }

    try expectForward(
        &head,
        &.{ 0, 1, 2, 6, 7, 8, 9 },
        &.{ 9, 1, 5, 8, 2, 6, 0 },
    );
    try expectForward(&staging, &.{ 3, 4, 5 }, &.{ 3, 7, 4 });

    while (!list_sort.listEmpty(&staging)) {
        const node = staging.next.?;
        list_sort.listDel(node);
        list_sort.listAddTail(node, &head);
    }
    try std.testing.expect(list_sort.listEmpty(&staging));
    try expectForward(
        &head,
        &.{ 0, 1, 2, 6, 7, 8, 9, 3, 4, 5 },
        &.{ 9, 1, 5, 8, 2, 6, 0, 3, 7, 4 },
    );

    list_sort.listSort(null, &head, modulo_cmp);
    try expectForward(
        &head,
        &.{ 0, 6, 9, 3, 1, 7, 4, 2, 8, 5 },
        &.{ 9, 8, 0, 3, 1, 2, 7, 5, 6, 4 },
    );
    try expectBackward(&head, &.{ 4, 6, 5, 7, 2, 1, 3, 0, 8, 9 });
    try std.testing.expect(head.next == &entries[9].node);
    try std.testing.expect(head.prev == &entries[4].node);
}
