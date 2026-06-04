const std = @import("std");
const list_sort = @import("list_sort");

const ListHead = list_sort.ListHead;

const Entry = struct {
    key: i32,
    ordinal: usize,
    node: ListHead = .{},
};

const SortMode = enum {
    ascending,
    descending,
    bucket,
};

const ComparatorStats = struct {
    mode: SortMode,
    calls: usize = 0,
    equal_calls: usize = 0,
    reverse_bias_calls: usize = 0,
};

fn checkedCmp(priv: ?*anyopaque, a: *const ListHead, b: *const ListHead) i32 {
    const stats: *ComparatorStats = @ptrCast(@alignCast(priv.?));
    const lhs: *const Entry = @fieldParentPtr("node", a);
    const rhs: *const Entry = @fieldParentPtr("node", b);

    stats.calls += 1;

    switch (stats.mode) {
        .ascending => {
            if (lhs.key == rhs.key) {
                stats.equal_calls += 1;
                return 0;
            }
            return if (lhs.key < rhs.key) -3 else 5;
        },
        .descending => {
            if (lhs.key == rhs.key) {
                stats.equal_calls += 1;
                return 0;
            }
            stats.reverse_bias_calls += 1;
            return if (lhs.key > rhs.key) -7 else 11;
        },
        .bucket => {
            const lhs_bucket = @mod(lhs.key, 4);
            const rhs_bucket = @mod(rhs.key, 4);
            if (lhs_bucket == rhs_bucket) {
                stats.equal_calls += 1;
                return 0;
            }
            return if (lhs_bucket < rhs_bucket) -13 else 17;
        },
    }
}

fn drainOrdinals(head: *ListHead, comptime len: usize) ![len]usize {
    var ordinals: [len]usize = undefined;
    var idx: usize = 0;
    var current = head.next;
    while (current != head) : (current = current.?.next) {
        const entry: *const Entry = @fieldParentPtr("node", current.?);
        ordinals[idx] = entry.ordinal;
        try std.testing.expect(current.?.next.?.prev == current.?);
        try std.testing.expect(current.?.prev.?.next == current.?);
        idx += 1;
    }
    try std.testing.expectEqual(len, idx);
    return ordinals;
}

fn drainKeys(head: *ListHead, comptime len: usize) ![len]i32 {
    var keys: [len]i32 = undefined;
    var idx: usize = 0;
    var current = head.next;
    while (current != head) : (current = current.?.next) {
        const entry: *const Entry = @fieldParentPtr("node", current.?);
        keys[idx] = entry.key;
        idx += 1;
    }
    try std.testing.expectEqual(len, idx);
    return keys;
}

test "list sort records comparator activity across long carry and reuse passes" {
    var head: ListHead = .{};
    head.init();

    var entries = [_]Entry{
        .{ .key = 12, .ordinal = 0 },
        .{ .key = -1, .ordinal = 1 },
        .{ .key = 8, .ordinal = 2 },
        .{ .key = 5, .ordinal = 3 },
        .{ .key = 12, .ordinal = 4 },
        .{ .key = 0, .ordinal = 5 },
        .{ .key = -3, .ordinal = 6 },
        .{ .key = 5, .ordinal = 7 },
        .{ .key = 7, .ordinal = 8 },
        .{ .key = -1, .ordinal = 9 },
        .{ .key = 4, .ordinal = 10 },
        .{ .key = 9, .ordinal = 11 },
        .{ .key = -3, .ordinal = 12 },
        .{ .key = 2, .ordinal = 13 },
        .{ .key = 7, .ordinal = 14 },
        .{ .key = 0, .ordinal = 15 },
        .{ .key = 6, .ordinal = 16 },
    };

    for (&entries) |*entry| {
        list_sort.listAddTail(&entry.node, &head);
    }

    var stats = ComparatorStats{ .mode = .ascending };
    list_sort.listSort(&stats, &head, checkedCmp);
    try std.testing.expect(stats.calls > entries.len);
    try std.testing.expect(stats.equal_calls >= 4);
    try std.testing.expectEqual(@as(usize, 0), stats.reverse_bias_calls);

    const ascending_keys = try drainKeys(&head, entries.len);
    try std.testing.expectEqualSlices(i32, &.{
        -3, -3, -1, -1, 0, 0, 2, 4, 5, 5, 6, 7, 7, 8, 9, 12, 12,
    }, &ascending_keys);
    const ascending_ordinals = try drainOrdinals(&head, entries.len);
    try std.testing.expectEqualSlices(usize, &.{
        6, 12, 1, 9, 5, 15, 13, 10, 3, 7, 16, 8, 14, 2, 11, 0, 4,
    }, &ascending_ordinals);
    try std.testing.expect(head.next == &entries[6].node);
    try std.testing.expect(head.prev == &entries[4].node);

    stats = .{ .mode = .descending };
    list_sort.listSort(&stats, &head, checkedCmp);
    try std.testing.expect(stats.calls > entries.len);
    try std.testing.expect(stats.equal_calls >= 4);
    try std.testing.expect(stats.reverse_bias_calls > stats.equal_calls);

    const descending_keys = try drainKeys(&head, entries.len);
    try std.testing.expectEqualSlices(i32, &.{
        12, 12, 9, 8, 7, 7, 6, 5, 5, 4, 2, 0, 0, -1, -1, -3, -3,
    }, &descending_keys);
    const descending_ordinals = try drainOrdinals(&head, entries.len);
    try std.testing.expectEqualSlices(usize, &.{
        0, 4, 11, 2, 8, 14, 16, 3, 7, 10, 13, 5, 15, 1, 9, 6, 12,
    }, &descending_ordinals);
    try std.testing.expect(head.next == &entries[0].node);
    try std.testing.expect(head.prev == &entries[12].node);

    stats = .{ .mode = .bucket };
    list_sort.listSort(&stats, &head, checkedCmp);
    try std.testing.expect(stats.calls > entries.len);
    try std.testing.expect(stats.equal_calls > entries.len / 2);

    const bucket_keys = try drainKeys(&head, entries.len);
    try std.testing.expectEqualSlices(i32, &.{
        12, 12, 8, 4, 0, 0, 9, 5, 5, -3, -3, 6, 2, 7, 7, -1, -1,
    }, &bucket_keys);
    const bucket_ordinals = try drainOrdinals(&head, entries.len);
    try std.testing.expectEqualSlices(usize, &.{
        0, 4, 2, 10, 5, 15, 11, 3, 7, 6, 12, 16, 13, 8, 14, 1, 9,
    }, &bucket_ordinals);
    try std.testing.expect(head.next == &entries[0].node);
    try std.testing.expect(head.prev == &entries[9].node);
}
