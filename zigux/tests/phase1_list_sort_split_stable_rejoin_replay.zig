const std = @import("std");
const list_sort = @import("list_sort");

const Entry = struct {
    key: i32,
    ordinal: usize,
    node: list_sort.ListHead = .{},
};

fn triCmp(_: ?*anyopaque, a: *const list_sort.ListHead, b: *const list_sort.ListHead) i32 {
    const lhs: *const Entry = @fieldParentPtr("node", a);
    const rhs: *const Entry = @fieldParentPtr("node", b);
    if (lhs.key < rhs.key) return -1;
    if (lhs.key > rhs.key) return 1;
    return 0;
}

fn collect(head: *list_sort.ListHead, keys: []i32, ordinals: []usize) !usize {
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
    return idx;
}

fn moveToTail(entry: *Entry, to: *list_sort.ListHead) !void {
    list_sort.listDel(&entry.node);
    try std.testing.expect(entry.node.next == null);
    try std.testing.expect(entry.node.prev == null);
    list_sort.listAddTail(&entry.node, to);
}

test "list sort stability follows split and rejoined traversal order" {
    var primary: list_sort.ListHead = .{};
    var staging: list_sort.ListHead = .{};
    primary.init();
    staging.init();

    var entries = [_]Entry{
        .{ .key = 3, .ordinal = 0 },
        .{ .key = 1, .ordinal = 1 },
        .{ .key = 4, .ordinal = 2 },
        .{ .key = 2, .ordinal = 3 },
        .{ .key = 3, .ordinal = 4 },
        .{ .key = 1, .ordinal = 5 },
        .{ .key = 4, .ordinal = 6 },
        .{ .key = 2, .ordinal = 7 },
        .{ .key = 3, .ordinal = 8 },
    };

    for (&entries) |*entry| {
        list_sort.listAddTail(&entry.node, &primary);
    }

    list_sort.listSort(null, &primary, triCmp);

    var keys: [entries.len]i32 = undefined;
    var ordinals: [entries.len]usize = undefined;
    var count = try collect(&primary, &keys, &ordinals);
    try std.testing.expectEqualSlices(i32, &.{ 1, 1, 2, 2, 3, 3, 3, 4, 4 }, keys[0..count]);
    try std.testing.expectEqualSlices(usize, &.{ 1, 5, 3, 7, 0, 4, 8, 2, 6 }, ordinals[0..count]);

    try moveToTail(&entries[5], &staging);
    try moveToTail(&entries[7], &staging);
    try moveToTail(&entries[4], &staging);
    try std.testing.expect(staging.next == &entries[5].node);
    try std.testing.expect(staging.prev == &entries[4].node);

    list_sort.listSort(null, &staging, triCmp);

    count = try collect(&staging, &keys, &ordinals);
    try std.testing.expectEqualSlices(i32, &.{ 1, 2, 3 }, keys[0..count]);
    try std.testing.expectEqualSlices(usize, &.{ 5, 7, 4 }, ordinals[0..count]);

    while (!list_sort.listEmpty(&staging)) {
        const node = staging.next.?;
        const entry: *Entry = @fieldParentPtr("node", node);
        list_sort.listDel(node);
        try std.testing.expect(node.next == null);
        try std.testing.expect(node.prev == null);
        list_sort.listAddTail(&entry.node, &primary);
    }
    try std.testing.expect(list_sort.listEmpty(&staging));

    count = try collect(&primary, &keys, &ordinals);
    try std.testing.expectEqualSlices(i32, &.{ 1, 2, 3, 3, 4, 4, 1, 2, 3 }, keys[0..count]);
    try std.testing.expectEqualSlices(usize, &.{ 1, 3, 0, 8, 2, 6, 5, 7, 4 }, ordinals[0..count]);

    list_sort.listSort(null, &primary, triCmp);

    count = try collect(&primary, &keys, &ordinals);
    try std.testing.expectEqualSlices(i32, &.{ 1, 1, 2, 2, 3, 3, 3, 4, 4 }, keys[0..count]);
    try std.testing.expectEqualSlices(usize, &.{ 1, 5, 3, 7, 0, 8, 4, 2, 6 }, ordinals[0..count]);
    try std.testing.expect(primary.next == &entries[1].node);
    try std.testing.expect(primary.prev == &entries[6].node);
}
