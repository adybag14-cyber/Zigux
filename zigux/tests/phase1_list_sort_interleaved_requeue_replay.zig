const std = @import("std");
const list_sort = @import("list_sort");

const Entry = struct {
    bucket: i32,
    weight: i32,
    ordinal: usize,
    node: list_sort.ListHead = .{},
};

fn cmpWeight(_: ?*anyopaque, a: *const list_sort.ListHead, b: *const list_sort.ListHead) i32 {
    const lhs: *const Entry = @fieldParentPtr("node", a);
    const rhs: *const Entry = @fieldParentPtr("node", b);
    if (lhs.weight < rhs.weight) return -1;
    if (lhs.weight > rhs.weight) return 1;
    return 0;
}

fn cmpBucketAscending(_: ?*anyopaque, a: *const list_sort.ListHead, b: *const list_sort.ListHead) i32 {
    const lhs: *const Entry = @fieldParentPtr("node", a);
    const rhs: *const Entry = @fieldParentPtr("node", b);
    if (lhs.bucket < rhs.bucket) return -1;
    if (lhs.bucket > rhs.bucket) return 1;
    return 0;
}

fn cmpBucketDescending(_: ?*anyopaque, a: *const list_sort.ListHead, b: *const list_sort.ListHead) i32 {
    return -cmpBucketAscending(null, a, b);
}

fn collectOrdinals(head: *list_sort.ListHead, out: []usize) !usize {
    var count: usize = 0;
    var current = head.next;
    while (current != head) : (current = current.?.next) {
        const entry: *const Entry = @fieldParentPtr("node", current.?);
        out[count] = entry.ordinal;
        try std.testing.expect(current.?.next.?.prev == current.?);
        try std.testing.expect(current.?.prev.?.next == current.?);
        count += 1;
    }
    return count;
}

fn drainOddPositions(source: *list_sort.ListHead, staging: *list_sort.ListHead) !void {
    var index: usize = 0;
    var current = source.next;
    while (current != source) : (index += 1) {
        const node = current.?;
        current = node.next;
        if ((index & 1) == 0) continue;

        list_sort.listDel(node);
        try std.testing.expect(node.next == null);
        try std.testing.expect(node.prev == null);
        list_sort.listAddTail(node, staging);
    }
}

fn requeueStagingAtFront(source: *list_sort.ListHead, staging: *list_sort.ListHead) !void {
    while (!list_sort.listEmpty(staging)) {
        const node = staging.next.?;
        list_sort.listDel(node);
        try std.testing.expect(node.next == null);
        try std.testing.expect(node.prev == null);
        list_sort.listAdd(node, source);
    }
}

test "phase1 list_sort replay preserves stable order after interleaved requeue" {
    var head: list_sort.ListHead = .{};
    head.init();
    var staging: list_sort.ListHead = .{};
    staging.init();

    var entries = [_]Entry{
        .{ .bucket = 2, .weight = 5, .ordinal = 0 },
        .{ .bucket = 0, .weight = 1, .ordinal = 1 },
        .{ .bucket = 1, .weight = 4, .ordinal = 2 },
        .{ .bucket = 2, .weight = 2, .ordinal = 3 },
        .{ .bucket = 0, .weight = 6, .ordinal = 4 },
        .{ .bucket = 1, .weight = 3, .ordinal = 5 },
        .{ .bucket = 2, .weight = 0, .ordinal = 6 },
        .{ .bucket = 0, .weight = 7, .ordinal = 7 },
        .{ .bucket = 1, .weight = 8, .ordinal = 8 },
        .{ .bucket = 2, .weight = 9, .ordinal = 9 },
    };

    for (&entries) |*entry| list_sort.listAddTail(&entry.node, &head);

    list_sort.listSort(null, &head, cmpWeight);

    var ordinals: [entries.len]usize = undefined;
    var count = try collectOrdinals(&head, &ordinals);
    try std.testing.expectEqual(entries.len, count);
    try std.testing.expectEqualSlices(usize, &.{ 6, 1, 3, 5, 2, 0, 4, 7, 8, 9 }, ordinals[0..count]);

    try drainOddPositions(&head, &staging);

    count = try collectOrdinals(&head, &ordinals);
    try std.testing.expectEqualSlices(usize, &.{ 6, 3, 2, 4, 8 }, ordinals[0..count]);

    var staged_ordinals: [entries.len]usize = undefined;
    var staged_count = try collectOrdinals(&staging, &staged_ordinals);
    try std.testing.expectEqualSlices(usize, &.{ 1, 5, 0, 7, 9 }, staged_ordinals[0..staged_count]);

    list_sort.listSort(null, &staging, cmpBucketDescending);
    staged_count = try collectOrdinals(&staging, &staged_ordinals);
    try std.testing.expectEqualSlices(usize, &.{ 0, 9, 5, 1, 7 }, staged_ordinals[0..staged_count]);

    try requeueStagingAtFront(&head, &staging);
    try std.testing.expect(list_sort.listEmpty(&staging));

    count = try collectOrdinals(&head, &ordinals);
    try std.testing.expectEqualSlices(usize, &.{ 7, 1, 5, 9, 0, 6, 3, 2, 4, 8 }, ordinals[0..count]);
    try std.testing.expect(head.next == &entries[7].node);
    try std.testing.expect(head.prev == &entries[8].node);

    list_sort.listSort(null, &head, cmpBucketAscending);

    count = try collectOrdinals(&head, &ordinals);
    try std.testing.expectEqual(entries.len, count);
    try std.testing.expectEqualSlices(usize, &.{ 7, 1, 4, 5, 2, 8, 9, 0, 6, 3 }, ordinals[0..count]);
    try std.testing.expect(head.next == &entries[7].node);
    try std.testing.expect(head.prev == &entries[3].node);
}
