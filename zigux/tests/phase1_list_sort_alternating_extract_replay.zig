const std = @import("std");
const list_sort = @import("list_sort");

const ListHead = list_sort.ListHead;

const Entry = struct {
    key: i32,
    ordinal: usize,
    node: ListHead = .{},
};

fn compareByKey(_: ?*anyopaque, a: *const ListHead, b: *const ListHead) i32 {
    const lhs: *const Entry = @fieldParentPtr("node", a);
    const rhs: *const Entry = @fieldParentPtr("node", b);
    if (lhs.key < rhs.key) return -1;
    if (lhs.key > rhs.key) return 1;
    return 0;
}

fn expectOrder(head: *ListHead, expected_keys: []const i32, expected_ordinals: []const usize) !void {
    try std.testing.expectEqual(expected_keys.len, expected_ordinals.len);

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

    try std.testing.expectEqual(expected_keys.len, idx);
    try std.testing.expectEqualSlices(i32, expected_keys, keys[0..idx]);
    try std.testing.expectEqualSlices(usize, expected_ordinals, ordinals[0..idx]);

    var reverse_idx = idx;
    current = head.prev;
    while (current != head) : (current = current.?.prev) {
        reverse_idx -= 1;
        const entry: *const Entry = @fieldParentPtr("node", current.?);
        try std.testing.expectEqual(expected_ordinals[reverse_idx], entry.ordinal);
    }
    try std.testing.expectEqual(@as(usize, 0), reverse_idx);
}

test "list sort survives alternating endpoint extraction and final reassembly" {
    var main: ListHead = .{};
    main.init();
    var staging: ListHead = .{};
    staging.init();

    var entries = [_]Entry{
        .{ .key = 6, .ordinal = 0 },
        .{ .key = 1, .ordinal = 1 },
        .{ .key = 4, .ordinal = 2 },
        .{ .key = 1, .ordinal = 3 },
        .{ .key = 7, .ordinal = 4 },
        .{ .key = 2, .ordinal = 5 },
        .{ .key = 5, .ordinal = 6 },
        .{ .key = 2, .ordinal = 7 },
        .{ .key = 3, .ordinal = 8 },
        .{ .key = 6, .ordinal = 9 },
    };

    for (&entries) |*entry| list_sort.listAddTail(&entry.node, &main);
    list_sort.listSort(null, &main, compareByKey);
    try expectOrder(
        &main,
        &.{ 1, 1, 2, 2, 3, 4, 5, 6, 6, 7 },
        &.{ 1, 3, 5, 7, 8, 2, 6, 0, 9, 4 },
    );

    while (!list_sort.listEmpty(&main)) {
        const front = main.next.?;
        list_sort.listDel(front);
        list_sort.listAddTail(front, &staging);

        if (!list_sort.listEmpty(&main)) {
            const back = main.prev.?;
            list_sort.listDel(back);
            list_sort.listAddTail(back, &staging);
        }
    }
    try std.testing.expect(list_sort.listEmpty(&main));

    try expectOrder(
        &staging,
        &.{ 1, 7, 1, 6, 2, 6, 2, 5, 3, 4 },
        &.{ 1, 4, 3, 9, 5, 0, 7, 6, 8, 2 },
    );

    list_sort.listSort(null, &staging, compareByKey);
    try expectOrder(
        &staging,
        &.{ 1, 1, 2, 2, 3, 4, 5, 6, 6, 7 },
        &.{ 1, 3, 5, 7, 8, 2, 6, 9, 0, 4 },
    );

    while (!list_sort.listEmpty(&staging)) {
        const node = staging.prev.?;
        list_sort.listDel(node);
        list_sort.listAddTail(node, &main);
    }
    try expectOrder(
        &main,
        &.{ 7, 6, 6, 5, 4, 3, 2, 2, 1, 1 },
        &.{ 4, 0, 9, 6, 2, 8, 7, 5, 3, 1 },
    );

    list_sort.listSort(null, &main, compareByKey);
    try expectOrder(
        &main,
        &.{ 1, 1, 2, 2, 3, 4, 5, 6, 6, 7 },
        &.{ 3, 1, 7, 5, 8, 2, 6, 0, 9, 4 },
    );
    try std.testing.expect(list_sort.listEmpty(&staging));
}
