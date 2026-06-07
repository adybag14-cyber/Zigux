const std = @import("std");
const list_sort = @import("list_sort");

const ListHead = list_sort.ListHead;

const Entry = struct {
    key: i32,
    ordinal: usize,
    node: ListHead = .{},
};

const SortMode = enum {
    key_ascending,
    key_descending,
    ordinal_ascending,
};

fn cmp(priv: ?*anyopaque, a: *const ListHead, b: *const ListHead) i32 {
    const mode: *const SortMode = @ptrCast(@alignCast(priv.?));
    const lhs: *const Entry = @fieldParentPtr("node", a);
    const rhs: *const Entry = @fieldParentPtr("node", b);

    switch (mode.*) {
        .key_ascending => {
            if (lhs.key < rhs.key) return -5;
            if (lhs.key > rhs.key) return 7;
            return 0;
        },
        .key_descending => {
            if (lhs.key > rhs.key) return -5;
            if (lhs.key < rhs.key) return 7;
            return 0;
        },
        .ordinal_ascending => {
            if (lhs.ordinal < rhs.ordinal) return -3;
            if (lhs.ordinal > rhs.ordinal) return 3;
            return 0;
        },
    }
}

fn allTies(_: ?*anyopaque, _: *const ListHead, _: *const ListHead) i32 {
    return 0;
}

fn expectDetached(entry: *const Entry) !void {
    try std.testing.expect(entry.node.next == null);
    try std.testing.expect(entry.node.prev == null);
}

fn expectCircularLinks(head: *ListHead) !void {
    var current = head.next;
    while (current != head) : (current = current.?.next) {
        try std.testing.expect(current.?.next.?.prev == current.?);
        try std.testing.expect(current.?.prev.?.next == current.?);
    }
}

fn expectOrder(head: *ListHead, expected_ordinals: []const usize, expected_keys: []const i32) !void {
    var idx: usize = 0;
    var current = head.next;
    while (current != head) : (current = current.?.next) {
        const entry: *const Entry = @fieldParentPtr("node", current.?);
        try std.testing.expect(idx < expected_ordinals.len);
        try std.testing.expectEqual(expected_ordinals[idx], entry.ordinal);
        try std.testing.expectEqual(expected_keys[idx], entry.key);
        idx += 1;
    }

    try std.testing.expectEqual(expected_ordinals.len, idx);
    try expectCircularLinks(head);
}

fn popFront(head: *ListHead) *ListHead {
    const node = head.next.?;
    list_sort.listDel(node);
    return node;
}

test "list sort octa-bucket split rebuild preserves stable links" {
    var source: ListHead = .{};
    source.init();
    var buckets: [8]ListHead = undefined;
    for (&buckets) |*bucket| bucket.init();

    var entries = [_]Entry{
        .{ .key = 42, .ordinal = 0 },
        .{ .key = -7, .ordinal = 1 },
        .{ .key = 13, .ordinal = 2 },
        .{ .key = 42, .ordinal = 3 },
        .{ .key = 0, .ordinal = 4 },
        .{ .key = -7, .ordinal = 5 },
        .{ .key = 21, .ordinal = 6 },
        .{ .key = 5, .ordinal = 7 },
        .{ .key = 21, .ordinal = 8 },
        .{ .key = -3, .ordinal = 9 },
        .{ .key = 13, .ordinal = 10 },
        .{ .key = 34, .ordinal = 11 },
        .{ .key = 5, .ordinal = 12 },
        .{ .key = 0, .ordinal = 13 },
        .{ .key = 34, .ordinal = 14 },
        .{ .key = -3, .ordinal = 15 },
        .{ .key = 55, .ordinal = 16 },
        .{ .key = 8, .ordinal = 17 },
        .{ .key = 55, .ordinal = 18 },
        .{ .key = 8, .ordinal = 19 },
        .{ .key = 2, .ordinal = 20 },
        .{ .key = 2, .ordinal = 21 },
        .{ .key = 1, .ordinal = 22 },
        .{ .key = 1, .ordinal = 23 },
    };

    for (&entries, 0..) |*entry, idx| {
        if ((idx & 1) == 0) {
            list_sort.listAddTail(&entry.node, &source);
        } else {
            list_sort.listAdd(&entry.node, &source);
        }
    }

    var mode = SortMode.key_ascending;
    list_sort.listSort(&mode, &source, cmp);
    try expectOrder(&source, &.{
        5,  1,  15, 9,  13, 4, 23, 22, 21, 20, 7,  12,
        19, 17, 2,  10, 6,  8, 11, 14, 3,  0,  16, 18,
    }, &.{
        -7, -7, -3, -3, 0,  0,  1,  1,  2,  2,  5,  5,
        8,  8,  13, 13, 21, 21, 34, 34, 42, 42, 55, 55,
    });

    var rank: usize = 0;
    while (!list_sort.listEmpty(&source)) : (rank += 1) {
        const node = popFront(&source);
        const entry: *Entry = @fieldParentPtr("node", node);
        try expectDetached(entry);

        const bucket_id = rank % buckets.len;
        if ((rank & 2) == 0) {
            list_sort.listAddTail(node, &buckets[bucket_id]);
        } else {
            list_sort.listAdd(node, &buckets[bucket_id]);
        }
    }

    for (&buckets, 0..) |*bucket, idx| {
        mode = if ((idx & 1) == 0) .ordinal_ascending else .key_descending;
        list_sort.listSort(&mode, bucket, cmp);
        try expectCircularLinks(bucket);
    }

    const bucket_order = [_]usize{ 6, 1, 4, 7, 0, 3, 2, 5 };
    var rebuilt: ListHead = .{};
    rebuilt.init();
    for (bucket_order) |bucket_id| {
        while (!list_sort.listEmpty(&buckets[bucket_id])) {
            const node = popFront(&buckets[bucket_id]);
            const entry: *Entry = @fieldParentPtr("node", node);
            try expectDetached(entry);
            if (((bucket_id + entry.ordinal) & 1) == 0) {
                list_sort.listAddTail(node, &rebuilt);
            } else {
                list_sort.listAdd(node, &rebuilt);
            }
        }
    }

    try expectOrder(&rebuilt, &.{
        4,  0,  15, 11, 7, 12, 14, 21, 5, 22, 10, 18,
        19, 13, 3,  20, 8, 23, 2,  16, 1, 6,  9,  17,
    }, &.{
        0, 42, -3, 34, 5,  5, 34, 2,  -7, 1,  13, 55,
        8, 0,  42, 2,  21, 1, 13, 55, -7, 21, -3, 8,
    });

    list_sort.listSort(null, &rebuilt, allTies);
    try expectOrder(&rebuilt, &.{
        4,  0,  15, 11, 7, 12, 14, 21, 5, 22, 10, 18,
        19, 13, 3,  20, 8, 23, 2,  16, 1, 6,  9,  17,
    }, &.{
        0, 42, -3, 34, 5,  5, 34, 2,  -7, 1,  13, 55,
        8, 0,  42, 2,  21, 1, 13, 55, -7, 21, -3, 8,
    });

    try std.testing.expect(rebuilt.next == &entries[4].node);
    try std.testing.expect(rebuilt.prev == &entries[17].node);
}
