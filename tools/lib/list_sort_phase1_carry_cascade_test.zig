const std = @import("std");
const list_sort = @import("list_sort");

const ListHead = list_sort.ListHead;

const Entry = struct {
    key: i32,
    ordinal: usize,
    node: ListHead = .{},
};

const SortContext = struct {
    modulo: i32,
    descending_bucket: bool,
};

fn bucketedCompare(priv: ?*anyopaque, a: *const ListHead, b: *const ListHead) i32 {
    const ctx: *const SortContext = @ptrCast(@alignCast(priv.?));
    const lhs: *const Entry = @fieldParentPtr("node", a);
    const rhs: *const Entry = @fieldParentPtr("node", b);
    const lhs_bucket = @mod(lhs.key, ctx.modulo);
    const rhs_bucket = @mod(rhs.key, ctx.modulo);

    if (lhs_bucket == rhs_bucket) return 0;
    const lhs_before_rhs = lhs_bucket < rhs_bucket;
    if (ctx.descending_bucket) {
        return if (lhs_before_rhs) 17 else -19;
    }
    return if (lhs_before_rhs) -17 else 19;
}

fn expectOrder(head: *ListHead, entries: []Entry, expected_ordinals: []const usize) !void {
    var idx: usize = 0;
    var current = head.next;
    while (current != head) : (current = current.?.next) {
        const entry: *const Entry = @fieldParentPtr("node", current.?);
        try std.testing.expectEqual(expected_ordinals[idx], entry.ordinal);
        try std.testing.expect(current.?.next.?.prev == current.?);
        try std.testing.expect(current.?.prev.?.next == current.?);
        idx += 1;
    }

    try std.testing.expectEqual(expected_ordinals.len, idx);
    try std.testing.expect(head.next == &entries[expected_ordinals[0]].node);
    try std.testing.expect(head.prev == &entries[expected_ordinals[expected_ordinals.len - 1]].node);

    var reverse_idx = expected_ordinals.len;
    current = head.prev;
    while (current != head) : (current = current.?.prev) {
        reverse_idx -= 1;
        const entry: *const Entry = @fieldParentPtr("node", current.?);
        try std.testing.expectEqual(expected_ordinals[reverse_idx], entry.ordinal);
    }
    try std.testing.expectEqual(@as(usize, 0), reverse_idx);
}

test "list sort carry cascade keeps stable buckets across long pending merges" {
    var head: ListHead = .{};
    head.init();

    var entries = [_]Entry{
        .{ .key = 34, .ordinal = 0 },
        .{ .key = 5, .ordinal = 1 },
        .{ .key = 21, .ordinal = 2 },
        .{ .key = 13, .ordinal = 3 },
        .{ .key = 8, .ordinal = 4 },
        .{ .key = 55, .ordinal = 5 },
        .{ .key = 1, .ordinal = 6 },
        .{ .key = 3, .ordinal = 7 },
        .{ .key = 89, .ordinal = 8 },
        .{ .key = 2, .ordinal = 9 },
        .{ .key = 144, .ordinal = 10 },
        .{ .key = 233, .ordinal = 11 },
        .{ .key = 377, .ordinal = 12 },
        .{ .key = 610, .ordinal = 13 },
        .{ .key = 987, .ordinal = 14 },
        .{ .key = 1597, .ordinal = 15 },
        .{ .key = 2584, .ordinal = 16 },
        .{ .key = 4181, .ordinal = 17 },
        .{ .key = 6765, .ordinal = 18 },
        .{ .key = 10946, .ordinal = 19 },
        .{ .key = 17711, .ordinal = 20 },
        .{ .key = 28657, .ordinal = 21 },
        .{ .key = 46368, .ordinal = 22 },
        .{ .key = 75025, .ordinal = 23 },
        .{ .key = 121393, .ordinal = 24 },
        .{ .key = 196418, .ordinal = 25 },
        .{ .key = 317811, .ordinal = 26 },
        .{ .key = 514229, .ordinal = 27 },
        .{ .key = 832040, .ordinal = 28 },
        .{ .key = 1346269, .ordinal = 29 },
        .{ .key = 2178309, .ordinal = 30 },
        .{ .key = 3524578, .ordinal = 31 },
        .{ .key = 5702887, .ordinal = 32 },
    };

    for (&entries) |*entry| {
        list_sort.listAddTail(&entry.node, &head);
    }

    var context = SortContext{ .modulo = 5, .descending_bucket = false };
    list_sort.listSort(&context, &head, bucketedCompare);

    const ascending_buckets = [_]usize{
        1,  5,  13, 18, 23, 28, 2,  6,
        17, 19, 20, 26, 9,  12, 14, 15,
        21, 32, 3,  4,  7,  11, 22, 24,
        25, 31, 0,  8,  10, 16, 27, 29,
        30,
    };
    try expectOrder(&head, &entries, &ascending_buckets);

    context.descending_bucket = true;
    list_sort.listSort(&context, &head, bucketedCompare);

    const descending_buckets = [_]usize{
        0,  8,  10, 16, 27, 29, 30, 3,
        4,  7,  11, 22, 24, 25, 31, 9,
        12, 14, 15, 21, 32, 2,  6,  17,
        19, 20, 26, 1,  5,  13, 18, 23,
        28,
    };
    try expectOrder(&head, &entries, &descending_buckets);
}
