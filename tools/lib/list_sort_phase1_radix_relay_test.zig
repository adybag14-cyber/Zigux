const std = @import("std");
const list_sort = @import("list_sort");

const Entry = struct {
    key: i32,
    ordinal: usize,
    node: list_sort.ListHead = .{},
};

const SortMode = enum {
    key_ascending,
    key_descending,
    ordinal_ascending,
    ordinal_descending,
    all_ties,
};

const SortContext = struct {
    mode: SortMode,
    magnitude: i32,
};

fn entryFromNode(node: *const list_sort.ListHead) *const Entry {
    return @fieldParentPtr("node", node);
}

fn compare(priv: ?*anyopaque, a: *const list_sort.ListHead, b: *const list_sort.ListHead) i32 {
    const context: *const SortContext = @ptrCast(@alignCast(priv.?));
    const lhs = entryFromNode(a);
    const rhs = entryFromNode(b);

    const sign: i32 = switch (context.mode) {
        .key_ascending => if (lhs.key < rhs.key) -1 else if (lhs.key > rhs.key) 1 else 0,
        .key_descending => if (lhs.key > rhs.key) -1 else if (lhs.key < rhs.key) 1 else 0,
        .ordinal_ascending => if (lhs.ordinal < rhs.ordinal) -1 else if (lhs.ordinal > rhs.ordinal) 1 else 0,
        .ordinal_descending => if (lhs.ordinal > rhs.ordinal) -1 else if (lhs.ordinal < rhs.ordinal) 1 else 0,
        .all_ties => 0,
    };

    return sign * context.magnitude;
}

fn collectOrdinals(head: *const list_sort.ListHead, out: []usize) !usize {
    var idx: usize = 0;
    var current = head.next;
    while (current != head) : (current = current.?.next) {
        const entry = entryFromNode(current.?);
        out[idx] = entry.ordinal;
        try std.testing.expect(current.?.next.?.prev == current.?);
        try std.testing.expect(current.?.prev.?.next == current.?);
        idx += 1;
    }
    return idx;
}

fn expectOrdinals(head: *const list_sort.ListHead, expected: []const usize) !void {
    var ordinals: [16]usize = undefined;
    const count = try collectOrdinals(head, &ordinals);
    try std.testing.expectEqualSlices(usize, expected, ordinals[0..count]);
}

fn expectDetached(node: *const list_sort.ListHead) !void {
    try std.testing.expect(node.next == null);
    try std.testing.expect(node.prev == null);
}

fn popFront(head: *list_sort.ListHead) *list_sort.ListHead {
    const node = head.next.?;
    list_sort.listDel(node);
    return node;
}

fn popBack(head: *list_sort.ListHead) *list_sort.ListHead {
    const node = head.prev.?;
    list_sort.listDel(node);
    return node;
}

test "list sort radix relay preserves staged stability and links" {
    var entries = [_]Entry{
        .{ .key = 14, .ordinal = 0 },
        .{ .key = 3, .ordinal = 1 },
        .{ .key = 11, .ordinal = 2 },
        .{ .key = 6, .ordinal = 3 },
        .{ .key = 3, .ordinal = 4 },
        .{ .key = 9, .ordinal = 5 },
        .{ .key = 0, .ordinal = 6 },
        .{ .key = 14, .ordinal = 7 },
        .{ .key = 6, .ordinal = 8 },
        .{ .key = 12, .ordinal = 9 },
        .{ .key = 1, .ordinal = 10 },
        .{ .key = 9, .ordinal = 11 },
        .{ .key = 5, .ordinal = 12 },
        .{ .key = 12, .ordinal = 13 },
        .{ .key = 1, .ordinal = 14 },
        .{ .key = 5, .ordinal = 15 },
    };

    var source: list_sort.ListHead = .{};
    source.init();
    const source_order = [_]usize{ 9, 1, 14, 4, 12, 0, 7, 3, 10, 15, 6, 11, 2, 8, 5, 13 };
    for (source_order, 0..) |entry_idx, insert_idx| {
        if ((insert_idx & 1) == 0) {
            list_sort.listAddTail(&entries[entry_idx].node, &source);
        } else {
            list_sort.listAdd(&entries[entry_idx].node, &source);
        }
    }
    try expectOrdinals(&source, &.{ 13, 8, 11, 15, 3, 0, 4, 1, 9, 14, 12, 7, 10, 6, 2, 5 });

    var ascending = SortContext{ .mode = .key_ascending, .magnitude = 17 };
    list_sort.listSort(&ascending, &source, compare);
    try expectOrdinals(&source, &.{ 6, 14, 10, 4, 1, 15, 12, 8, 3, 11, 5, 2, 13, 9, 0, 7 });

    var buckets = [_]list_sort.ListHead{ .{}, .{}, .{}, .{} };
    for (&buckets) |*bucket| bucket.init();

    var rank: usize = 0;
    while (!list_sort.listEmpty(&source)) : (rank += 1) {
        const node = if ((rank & 1) == 0) popFront(&source) else popBack(&source);
        try expectDetached(node);
        const entry = entryFromNode(node);
        const bucket_idx = ((entry.key & 3) ^ @as(i32, @intCast(rank & 1))) & 3;
        if ((rank & 2) == 0) {
            list_sort.listAddTail(node, &buckets[@intCast(bucket_idx)]);
        } else {
            list_sort.listAdd(node, &buckets[@intCast(bucket_idx)]);
        }
    }
    try std.testing.expect(list_sort.listEmpty(&source));
    try expectOrdinals(&buckets[0], &.{ 5, 6, 11 });
    try expectOrdinals(&buckets[1], &.{ 15, 13, 14, 10, 9, 12 });
    try expectOrdinals(&buckets[2], &.{ 8, 2 });
    try expectOrdinals(&buckets[3], &.{ 3, 4, 0, 7, 1 });

    var bucket_modes = [_]SortContext{
        .{ .mode = .ordinal_descending, .magnitude = 5 },
        .{ .mode = .key_descending, .magnitude = 7 },
        .{ .mode = .ordinal_ascending, .magnitude = 11 },
        .{ .mode = .key_ascending, .magnitude = 13 },
    };
    for (&buckets, &bucket_modes) |*bucket, *mode| {
        list_sort.listSort(mode, bucket, compare);
    }
    try expectOrdinals(&buckets[0], &.{ 11, 6, 5 });
    try expectOrdinals(&buckets[1], &.{ 13, 9, 15, 12, 14, 10 });
    try expectOrdinals(&buckets[2], &.{ 2, 8 });
    try expectOrdinals(&buckets[3], &.{ 4, 1, 3, 0, 7 });

    const relay = [_]struct {
        bucket: usize,
        from_back: bool,
        to_front: bool,
    }{
        .{ .bucket = 1, .from_back = false, .to_front = false },
        .{ .bucket = 3, .from_back = true, .to_front = true },
        .{ .bucket = 0, .from_back = false, .to_front = false },
        .{ .bucket = 2, .from_back = true, .to_front = true },
        .{ .bucket = 1, .from_back = true, .to_front = false },
        .{ .bucket = 3, .from_back = false, .to_front = true },
        .{ .bucket = 1, .from_back = false, .to_front = false },
        .{ .bucket = 0, .from_back = true, .to_front = true },
        .{ .bucket = 3, .from_back = true, .to_front = false },
        .{ .bucket = 1, .from_back = false, .to_front = true },
        .{ .bucket = 2, .from_back = false, .to_front = false },
        .{ .bucket = 3, .from_back = false, .to_front = false },
        .{ .bucket = 1, .from_back = true, .to_front = true },
        .{ .bucket = 0, .from_back = false, .to_front = false },
        .{ .bucket = 3, .from_back = false, .to_front = true },
        .{ .bucket = 1, .from_back = false, .to_front = false },
    };

    var rebuilt: list_sort.ListHead = .{};
    rebuilt.init();
    for (relay) |step| {
        const node = if (step.from_back) popBack(&buckets[step.bucket]) else popFront(&buckets[step.bucket]);
        try expectDetached(node);
        if (step.to_front) {
            list_sort.listAdd(node, &rebuilt);
        } else {
            list_sort.listAddTail(node, &rebuilt);
        }
    }
    for (&buckets) |*bucket| try std.testing.expect(list_sort.listEmpty(bucket));
    try expectOrdinals(&rebuilt, &.{ 3, 14, 15, 5, 4, 8, 7, 13, 11, 10, 9, 0, 2, 1, 6, 12 });

    var ties = SortContext{ .mode = .all_ties, .magnitude = 19 };
    list_sort.listSort(&ties, &rebuilt, compare);
    try expectOrdinals(&rebuilt, &.{ 3, 14, 15, 5, 4, 8, 7, 13, 11, 10, 9, 0, 2, 1, 6, 12 });
    try std.testing.expect(rebuilt.next == &entries[3].node);
    try std.testing.expect(rebuilt.prev == &entries[12].node);
}
