const std = @import("std");
const list_sort = @import("list_sort");

const Entry = struct {
    key: i32,
    ordinal: usize,
    node: list_sort.ListHead = .{},
};

const SortMode = enum { bucket_ascending, exact_descending };

const SortContext = struct {
    mode: SortMode,
    bucket_width: i32,
};

fn compareWithContext(priv: ?*anyopaque, a: *const list_sort.ListHead, b: *const list_sort.ListHead) i32 {
    const context: *const SortContext = @ptrCast(@alignCast(priv.?));
    const lhs: *const Entry = @fieldParentPtr("node", a);
    const rhs: *const Entry = @fieldParentPtr("node", b);

    switch (context.mode) {
        .bucket_ascending => {
            const lhs_bucket = @divFloor(lhs.key, context.bucket_width);
            const rhs_bucket = @divFloor(rhs.key, context.bucket_width);
            if (lhs_bucket < rhs_bucket) return -1;
            if (lhs_bucket > rhs_bucket) return 1;
            return 0;
        },
        .exact_descending => {
            if (lhs.key > rhs.key) return -1;
            if (lhs.key < rhs.key) return 1;
            return 0;
        },
    }
}

fn expectOrder(head: *const list_sort.ListHead, expected_keys: []const i32, expected_ordinals: []const usize) !void {
    var keys: [12]i32 = undefined;
    var ordinals: [12]usize = undefined;
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

    try std.testing.expectEqual(expected_keys.len, idx);
    try std.testing.expectEqualSlices(i32, expected_keys, keys[0..idx]);
    try std.testing.expectEqualSlices(usize, expected_ordinals, ordinals[0..idx]);
}

test "list sort honors resized comparator context buckets across repeated sorts" {
    var head: list_sort.ListHead = .{};
    head.init();

    var entries = [_]Entry{
        .{ .key = 9, .ordinal = 0 },
        .{ .key = -4, .ordinal = 1 },
        .{ .key = 2, .ordinal = 2 },
        .{ .key = 7, .ordinal = 3 },
        .{ .key = -1, .ordinal = 4 },
        .{ .key = 4, .ordinal = 5 },
        .{ .key = 12, .ordinal = 6 },
        .{ .key = 0, .ordinal = 7 },
        .{ .key = 5, .ordinal = 8 },
        .{ .key = -7, .ordinal = 9 },
        .{ .key = 3, .ordinal = 10 },
        .{ .key = 8, .ordinal = 11 },
    };

    for (&entries) |*entry| list_sort.listAddTail(&entry.node, &head);

    var context = SortContext{ .mode = .bucket_ascending, .bucket_width = 5 };
    list_sort.listSort(&context, &head, compareWithContext);
    try expectOrder(
        &head,
        &.{ -7, -4, -1, 2, 4, 0, 3, 9, 7, 5, 8, 12 },
        &.{ 9, 1, 4, 2, 5, 7, 10, 0, 3, 8, 11, 6 },
    );

    context.bucket_width = 3;
    list_sort.listSort(&context, &head, compareWithContext);
    try expectOrder(
        &head,
        &.{ -7, -4, -1, 2, 0, 4, 3, 5, 7, 8, 9, 12 },
        &.{ 9, 1, 4, 2, 7, 5, 10, 8, 3, 11, 0, 6 },
    );

    context.mode = .exact_descending;
    list_sort.listSort(&context, &head, compareWithContext);
    try expectOrder(
        &head,
        &.{ 12, 9, 8, 7, 5, 4, 3, 2, 0, -1, -4, -7 },
        &.{ 6, 0, 11, 3, 8, 5, 10, 2, 7, 4, 1, 9 },
    );

    try std.testing.expect(head.next == &entries[6].node);
    try std.testing.expect(head.prev == &entries[9].node);
}
