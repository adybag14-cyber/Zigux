const std = @import("std");
const list_sort = @import("list_sort");

const Entry = struct {
    key: i32,
    ordinal: usize,
    node: list_sort.ListHead = .{},
};

fn keyAscending(_: ?*anyopaque, a: *const list_sort.ListHead, b: *const list_sort.ListHead) i32 {
    const lhs: *const Entry = @fieldParentPtr("node", a);
    const rhs: *const Entry = @fieldParentPtr("node", b);
    if (lhs.key < rhs.key) return -1;
    if (lhs.key > rhs.key) return 1;
    return 0;
}

fn keyDescending(_: ?*anyopaque, a: *const list_sort.ListHead, b: *const list_sort.ListHead) i32 {
    return -keyAscending(null, a, b);
}

fn moduloFourBucket(_: ?*anyopaque, a: *const list_sort.ListHead, b: *const list_sort.ListHead) i32 {
    const lhs: *const Entry = @fieldParentPtr("node", a);
    const rhs: *const Entry = @fieldParentPtr("node", b);
    const lhs_bucket = @mod(lhs.key, 4);
    const rhs_bucket = @mod(rhs.key, 4);
    if (lhs_bucket < rhs_bucket) return -1;
    if (lhs_bucket > rhs_bucket) return 1;
    return 0;
}

fn collectKeys(head: *const list_sort.ListHead, out: []i32) ![]const i32 {
    var idx: usize = 0;
    var current = head.next;
    while (current != head) : (current = current.?.next) {
        const entry: *const Entry = @fieldParentPtr("node", current.?);
        out[idx] = entry.key;
        try std.testing.expect(current.?.next.?.prev == current.?);
        try std.testing.expect(current.?.prev.?.next == current.?);
        idx += 1;
    }
    return out[0..idx];
}

fn collectOrdinals(head: *const list_sort.ListHead, out: []usize) ![]const usize {
    var idx: usize = 0;
    var current = head.next;
    while (current != head) : (current = current.?.next) {
        const entry: *const Entry = @fieldParentPtr("node", current.?);
        out[idx] = entry.ordinal;
        try std.testing.expect(current.?.next.?.prev == current.?);
        try std.testing.expect(current.?.prev.?.next == current.?);
        idx += 1;
    }
    return out[0..idx];
}

fn moveFrontToTail(src: *list_sort.ListHead, dst: *list_sort.ListHead) void {
    const node = src.next.?;
    list_sort.listDel(node);
    std.debug.assert(node.next == null);
    std.debug.assert(node.prev == null);
    list_sort.listAddTail(node, dst);
}

fn drainByPartition(src: *list_sort.ListHead, low: *list_sort.ListHead, high: *list_sort.ListHead) void {
    while (!list_sort.listEmpty(src)) {
        const node = src.next.?;
        const entry: *const Entry = @fieldParentPtr("node", node);
        list_sort.listDel(node);
        std.debug.assert(node.next == null);
        std.debug.assert(node.prev == null);
        if (entry.key < 6) {
            list_sort.listAddTail(node, low);
        } else {
            list_sort.listAddTail(node, high);
        }
    }
}

fn appendAll(src: *list_sort.ListHead, dst: *list_sort.ListHead) void {
    while (!list_sort.listEmpty(src)) {
        moveFrontToTail(src, dst);
    }
}

test "list_sort survives partition staging swapped before stable bucket replay" {
    var main: list_sort.ListHead = .{};
    var low_staging: list_sort.ListHead = .{};
    var high_staging: list_sort.ListHead = .{};
    main.init();
    low_staging.init();
    high_staging.init();

    var entries = [_]Entry{
        .{ .key = 6, .ordinal = 0 },
        .{ .key = 1, .ordinal = 1 },
        .{ .key = 10, .ordinal = 2 },
        .{ .key = 3, .ordinal = 3 },
        .{ .key = 8, .ordinal = 4 },
        .{ .key = 5, .ordinal = 5 },
        .{ .key = 2, .ordinal = 6 },
        .{ .key = 11, .ordinal = 7 },
        .{ .key = 4, .ordinal = 8 },
        .{ .key = 9, .ordinal = 9 },
        .{ .key = 0, .ordinal = 10 },
        .{ .key = 7, .ordinal = 11 },
    };
    for (&entries) |*entry| list_sort.listAddTail(&entry.node, &main);

    var keys: [12]i32 = undefined;
    var ordinals: [12]usize = undefined;

    list_sort.listSort(null, &main, keyAscending);
    try std.testing.expectEqualSlices(i32, &.{ 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11 }, try collectKeys(&main, &keys));

    drainByPartition(&main, &low_staging, &high_staging);
    try std.testing.expect(list_sort.listEmpty(&main));
    try std.testing.expectEqualSlices(i32, &.{ 0, 1, 2, 3, 4, 5 }, try collectKeys(&low_staging, &keys));
    try std.testing.expectEqualSlices(i32, &.{ 6, 7, 8, 9, 10, 11 }, try collectKeys(&high_staging, &keys));

    list_sort.listSort(null, &low_staging, keyDescending);
    list_sort.listSort(null, &high_staging, keyAscending);
    try std.testing.expectEqualSlices(i32, &.{ 5, 4, 3, 2, 1, 0 }, try collectKeys(&low_staging, &keys));
    try std.testing.expectEqualSlices(i32, &.{ 6, 7, 8, 9, 10, 11 }, try collectKeys(&high_staging, &keys));

    appendAll(&high_staging, &main);
    appendAll(&low_staging, &main);
    try std.testing.expect(list_sort.listEmpty(&high_staging));
    try std.testing.expect(list_sort.listEmpty(&low_staging));
    try std.testing.expectEqualSlices(i32, &.{ 6, 7, 8, 9, 10, 11, 5, 4, 3, 2, 1, 0 }, try collectKeys(&main, &keys));

    list_sort.listSort(null, &main, moduloFourBucket);

    try std.testing.expectEqualSlices(i32, &.{ 8, 4, 0, 9, 5, 1, 6, 10, 2, 7, 11, 3 }, try collectKeys(&main, &keys));
    try std.testing.expectEqualSlices(usize, &.{ 4, 8, 10, 9, 5, 1, 0, 2, 6, 11, 7, 3 }, try collectOrdinals(&main, &ordinals));
    try std.testing.expect(main.next == &entries[4].node);
    try std.testing.expect(main.prev == &entries[3].node);
}
