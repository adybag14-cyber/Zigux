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

fn cmpBucket(_: ?*anyopaque, a: *const list_sort.ListHead, b: *const list_sort.ListHead) i32 {
    const lhs: *const Entry = @fieldParentPtr("node", a);
    const rhs: *const Entry = @fieldParentPtr("node", b);
    if (lhs.bucket < rhs.bucket) return -1;
    if (lhs.bucket > rhs.bucket) return 1;
    return 0;
}

fn cmpBucketDescending(_: ?*anyopaque, a: *const list_sort.ListHead, b: *const list_sort.ListHead) i32 {
    return -cmpBucket(null, a, b);
}

fn collectOrdinals(head: *list_sort.ListHead, out: []usize) !usize {
    var idx: usize = 0;
    var current = head.next;
    while (current != head) : (current = current.?.next) {
        const entry: *const Entry = @fieldParentPtr("node", current.?);
        out[idx] = entry.ordinal;
        try std.testing.expect(current.?.next.?.prev == current.?);
        try std.testing.expect(current.?.prev.?.next == current.?);
        idx += 1;
    }
    return idx;
}

test "phase1 list_sort replay preserves detached sublist stable order" {
    var main: list_sort.ListHead = .{};
    var detached: list_sort.ListHead = .{};
    main.init();
    detached.init();

    var entries = [_]Entry{
        .{ .bucket = 2, .weight = 40, .ordinal = 0 },
        .{ .bucket = 1, .weight = 10, .ordinal = 1 },
        .{ .bucket = 0, .weight = 30, .ordinal = 2 },
        .{ .bucket = 2, .weight = 20, .ordinal = 3 },
        .{ .bucket = 0, .weight = 10, .ordinal = 4 },
        .{ .bucket = 1, .weight = 30, .ordinal = 5 },
        .{ .bucket = 1, .weight = 20, .ordinal = 6 },
        .{ .bucket = 0, .weight = 40, .ordinal = 7 },
        .{ .bucket = 2, .weight = 25, .ordinal = 8 },
        .{ .bucket = 0, .weight = 15, .ordinal = 9 },
    };

    for (&entries) |*entry| list_sort.listAddTail(&entry.node, &main);

    list_sort.listSort(null, &main, cmpWeight);

    var ordinals: [entries.len]usize = undefined;
    var count = try collectOrdinals(&main, &ordinals);
    try std.testing.expectEqual(entries.len, count);
    try std.testing.expectEqualSlices(usize, &.{ 1, 4, 9, 3, 6, 8, 2, 5, 0, 7 }, ordinals[0..count]);

    var detached_count: usize = 0;
    while (detached_count < 4) : (detached_count += 1) {
        const node = main.next.?.next.?.next.?;
        list_sort.listDel(node);
        list_sort.listAddTail(node, &detached);
    }

    count = try collectOrdinals(&main, &ordinals);
    try std.testing.expectEqualSlices(usize, &.{ 1, 4, 2, 5, 0, 7 }, ordinals[0..count]);
    try std.testing.expect(main.next == &entries[1].node);
    try std.testing.expect(main.prev == &entries[7].node);

    count = try collectOrdinals(&detached, &ordinals);
    try std.testing.expectEqualSlices(usize, &.{ 9, 3, 6, 8 }, ordinals[0..count]);
    try std.testing.expect(detached.next == &entries[9].node);
    try std.testing.expect(detached.prev == &entries[8].node);

    list_sort.listSort(null, &detached, cmpBucketDescending);

    count = try collectOrdinals(&detached, &ordinals);
    try std.testing.expectEqualSlices(usize, &.{ 3, 8, 6, 9 }, ordinals[0..count]);
    try std.testing.expect(detached.next == &entries[3].node);
    try std.testing.expect(detached.prev == &entries[9].node);

    while (!list_sort.listEmpty(&detached)) {
        const node = detached.next.?;
        list_sort.listDel(node);
        list_sort.listAddTail(node, &main);
    }
    try std.testing.expect(list_sort.listEmpty(&detached));

    count = try collectOrdinals(&main, &ordinals);
    try std.testing.expectEqualSlices(usize, &.{ 1, 4, 2, 5, 0, 7, 3, 8, 6, 9 }, ordinals[0..count]);

    list_sort.listSort(null, &main, cmpBucket);

    count = try collectOrdinals(&main, &ordinals);
    try std.testing.expectEqual(entries.len, count);
    try std.testing.expectEqualSlices(usize, &.{ 4, 2, 7, 9, 1, 5, 6, 0, 3, 8 }, ordinals[0..count]);
    try std.testing.expect(main.next == &entries[4].node);
    try std.testing.expect(main.prev == &entries[8].node);
}
