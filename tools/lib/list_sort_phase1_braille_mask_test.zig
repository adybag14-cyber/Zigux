const std = @import("std");
const list_sort = @import("list_sort");

const ListHead = list_sort.ListHead;

const Entry = struct {
    key: i32,
    ordinal: usize,
    node: ListHead = .{},
};

const SortMode = enum {
    key_asc,
    key_desc,
    ordinal_asc,
    ordinal_desc,
};

const SortContext = struct {
    mode: SortMode,
};

fn compare(_: ?*anyopaque, a: *const ListHead, b: *const ListHead) i32 {
    const lhs: *const Entry = @fieldParentPtr("node", a);
    const rhs: *const Entry = @fieldParentPtr("node", b);
    if (lhs.key < rhs.key) return -1;
    if (lhs.key > rhs.key) return 1;
    return 0;
}

fn compareWithContext(priv: ?*anyopaque, a: *const ListHead, b: *const ListHead) i32 {
    const context: *const SortContext = @ptrCast(@alignCast(priv.?));
    const lhs: *const Entry = @fieldParentPtr("node", a);
    const rhs: *const Entry = @fieldParentPtr("node", b);

    return switch (context.mode) {
        .key_asc => compare(null, a, b),
        .key_desc => compare(null, b, a),
        .ordinal_asc => order(lhs.ordinal, rhs.ordinal),
        .ordinal_desc => order(rhs.ordinal, lhs.ordinal),
    };
}

fn order(lhs: usize, rhs: usize) i32 {
    if (lhs < rhs) return -1;
    if (lhs > rhs) return 1;
    return 0;
}

fn tieCompare(_: ?*anyopaque, _: *const ListHead, _: *const ListHead) i32 {
    return 0;
}

fn entryFromNode(node: *const ListHead) *const Entry {
    return @fieldParentPtr("node", node);
}

fn assertDetached(entry: *const Entry) !void {
    try std.testing.expect(entry.node.next == null);
    try std.testing.expect(entry.node.prev == null);
}

fn expectTraversal(head: *ListHead, expected: []const usize) !void {
    try std.testing.expectEqual(expected.len == 0, list_sort.listEmpty(head));

    var forward_index: usize = 0;
    var current = head.next;
    while (current != head) : (current = current.?.next) {
        try std.testing.expect(forward_index < expected.len);
        const entry = entryFromNode(current.?);
        try std.testing.expectEqual(expected[forward_index], entry.ordinal);
        try std.testing.expect(current.?.next.?.prev == current.?);
        try std.testing.expect(current.?.prev.?.next == current.?);
        forward_index += 1;
    }
    try std.testing.expectEqual(expected.len, forward_index);

    var reverse_index = expected.len;
    current = head.prev;
    while (current != head) : (current = current.?.prev) {
        try std.testing.expect(reverse_index > 0);
        reverse_index -= 1;
        const entry = entryFromNode(current.?);
        try std.testing.expectEqual(expected[reverse_index], entry.ordinal);
    }
    try std.testing.expectEqual(@as(usize, 0), reverse_index);
}

fn popFront(head: *ListHead) ?*ListHead {
    if (list_sort.listEmpty(head)) return null;
    const node = head.next.?;
    list_sort.listDel(node);
    return node;
}

fn popBack(head: *ListHead) ?*ListHead {
    if (list_sort.listEmpty(head)) return null;
    const node = head.prev.?;
    list_sort.listDel(node);
    return node;
}

test "list sort braille-mask bucket rebuild preserves link integrity and tie order" {
    var head: ListHead = .{};
    head.init();
    var buckets = [_]ListHead{.{}} ** 8;
    for (&buckets) |*bucket| bucket.init();

    var entries = [_]Entry{
        .{ .key = 9, .ordinal = 0 },
        .{ .key = 4, .ordinal = 1 },
        .{ .key = 9, .ordinal = 2 },
        .{ .key = 1, .ordinal = 3 },
        .{ .key = 7, .ordinal = 4 },
        .{ .key = 4, .ordinal = 5 },
        .{ .key = 8, .ordinal = 6 },
        .{ .key = 2, .ordinal = 7 },
        .{ .key = 7, .ordinal = 8 },
        .{ .key = 3, .ordinal = 9 },
        .{ .key = 6, .ordinal = 10 },
        .{ .key = 2, .ordinal = 11 },
    };

    const construction = [_]usize{ 4, 0, 10, 2, 8, 6, 1, 3, 5, 7, 9, 11 };
    for (construction, 0..) |entry_index, step| {
        if ((step & 1) == 0) {
            list_sort.listAdd(&entries[entry_index].node, &head);
        } else {
            list_sort.listAddTail(&entries[entry_index].node, &head);
        }
    }

    list_sort.listSort(null, &head, compare);
    try expectTraversal(&head, &.{ 3, 7, 11, 9, 5, 1, 10, 8, 4, 6, 0, 2 });

    var rank: usize = 0;
    while (popFront(&head)) |node| : (rank += 1) {
        const entry: *Entry = @constCast(entryFromNode(node));
        try assertDetached(entry);

        const bucket_index = ((rank & 1) << 2) | ((rank & 2) << 0) | ((rank & 4) >> 2);
        if ((rank & 1) == 0) {
            list_sort.listAddTail(&entry.node, &buckets[bucket_index]);
        } else {
            list_sort.listAdd(&entry.node, &buckets[bucket_index]);
        }
    }
    try std.testing.expectEqual(@as(usize, entries.len), rank);
    try std.testing.expect(list_sort.listEmpty(&head));

    const contexts = [_]SortContext{
        .{ .mode = .ordinal_desc },
        .{ .mode = .key_asc },
        .{ .mode = .ordinal_asc },
        .{ .mode = .key_desc },
        .{ .mode = .key_asc },
        .{ .mode = .ordinal_desc },
        .{ .mode = .key_desc },
        .{ .mode = .ordinal_asc },
    };

    for (&buckets, 0..) |*bucket, bucket_index| {
        list_sort.listSort(@constCast(&contexts[bucket_index]), bucket, compareWithContext);
    }

    try expectTraversal(&buckets[0], &.{ 4, 3 });
    try expectTraversal(&buckets[1], &.{5});
    try expectTraversal(&buckets[2], &.{ 0, 11 });
    try expectTraversal(&buckets[3], &.{10});
    try expectTraversal(&buckets[4], &.{ 7, 6 });
    try expectTraversal(&buckets[5], &.{1});
    try expectTraversal(&buckets[6], &.{ 2, 9 });
    try expectTraversal(&buckets[7], &.{8});

    const rebuild = [_]struct {
        bucket: usize,
        back: bool,
    }{
        .{ .bucket = 5, .back = false },
        .{ .bucket = 1, .back = true },
        .{ .bucket = 6, .back = false },
        .{ .bucket = 0, .back = true },
        .{ .bucket = 4, .back = false },
        .{ .bucket = 2, .back = true },
        .{ .bucket = 7, .back = false },
        .{ .bucket = 3, .back = false },
        .{ .bucket = 0, .back = false },
        .{ .bucket = 6, .back = true },
        .{ .bucket = 4, .back = true },
        .{ .bucket = 2, .back = false },
    };

    for (rebuild) |move| {
        const node = if (move.back) popBack(&buckets[move.bucket]) else popFront(&buckets[move.bucket]);
        try std.testing.expect(node != null);
        const entry: *Entry = @constCast(entryFromNode(node.?));
        try assertDetached(entry);
        if (move.back) {
            list_sort.listAdd(&entry.node, &head);
        } else {
            list_sort.listAddTail(&entry.node, &head);
        }
    }

    for (&buckets) |*bucket| try std.testing.expect(list_sort.listEmpty(bucket));

    try expectTraversal(&head, &.{ 6, 9, 11, 3, 5, 1, 2, 7, 8, 10, 4, 0 });
    list_sort.listSort(null, &head, tieCompare);
    try expectTraversal(&head, &.{ 6, 9, 11, 3, 5, 1, 2, 7, 8, 10, 4, 0 });
}
