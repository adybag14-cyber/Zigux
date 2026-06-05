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

fn moduloThreeBucket(_: ?*anyopaque, a: *const list_sort.ListHead, b: *const list_sort.ListHead) i32 {
    const lhs: *const Entry = @fieldParentPtr("node", a);
    const rhs: *const Entry = @fieldParentPtr("node", b);
    const lhs_bucket = @mod(lhs.key, 3);
    const rhs_bucket = @mod(rhs.key, 3);
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

fn moveBackToTail(src: *list_sort.ListHead, dst: *list_sort.ListHead) void {
    const node = src.prev.?;
    list_sort.listDel(node);
    std.debug.assert(node.next == null);
    std.debug.assert(node.prev == null);
    list_sort.listAddTail(node, dst);
}

fn appendAll(src: *list_sort.ListHead, dst: *list_sort.ListHead) void {
    while (!list_sort.listEmpty(src)) {
        moveFrontToTail(src, dst);
    }
}

test "list_sort stages sorted front and back runs before stable bucket replay" {
    var main: list_sort.ListHead = .{};
    var front_staging: list_sort.ListHead = .{};
    var back_staging: list_sort.ListHead = .{};
    main.init();
    front_staging.init();
    back_staging.init();

    var entries = [_]Entry{
        .{ .key = 9, .ordinal = 0 },
        .{ .key = 1, .ordinal = 1 },
        .{ .key = 7, .ordinal = 2 },
        .{ .key = 3, .ordinal = 3 },
        .{ .key = 5, .ordinal = 4 },
        .{ .key = 2, .ordinal = 5 },
        .{ .key = 8, .ordinal = 6 },
        .{ .key = 4, .ordinal = 7 },
        .{ .key = 6, .ordinal = 8 },
        .{ .key = 0, .ordinal = 9 },
    };
    for (&entries) |*entry| list_sort.listAddTail(&entry.node, &main);

    list_sort.listSort(null, &main, keyAscending);
    moveFrontToTail(&main, &front_staging);
    moveFrontToTail(&main, &front_staging);
    moveBackToTail(&main, &back_staging);
    moveBackToTail(&main, &back_staging);

    var keys: [10]i32 = undefined;
    var ordinals: [10]usize = undefined;

    try std.testing.expectEqualSlices(i32, &.{ 2, 3, 4, 5, 6, 7 }, try collectKeys(&main, &keys));
    try std.testing.expectEqualSlices(usize, &.{ 9, 1 }, try collectOrdinals(&front_staging, &ordinals));
    try std.testing.expectEqualSlices(usize, &.{ 0, 6 }, try collectOrdinals(&back_staging, &ordinals));

    list_sort.listSort(null, &main, keyDescending);
    list_sort.listSort(null, &front_staging, keyDescending);
    list_sort.listSort(null, &back_staging, keyAscending);

    appendAll(&front_staging, &main);
    appendAll(&back_staging, &main);
    try std.testing.expect(list_sort.listEmpty(&front_staging));
    try std.testing.expect(list_sort.listEmpty(&back_staging));
    try std.testing.expectEqualSlices(i32, &.{ 7, 6, 5, 4, 3, 2, 1, 0, 8, 9 }, try collectKeys(&main, &keys));

    list_sort.listSort(null, &main, moduloThreeBucket);

    try std.testing.expectEqualSlices(i32, &.{ 6, 3, 0, 9, 7, 4, 1, 5, 2, 8 }, try collectKeys(&main, &keys));
    try std.testing.expectEqualSlices(usize, &.{ 8, 3, 9, 0, 2, 7, 1, 4, 5, 6 }, try collectOrdinals(&main, &ordinals));
    try std.testing.expect(main.next == &entries[8].node);
    try std.testing.expect(main.prev == &entries[6].node);
}
