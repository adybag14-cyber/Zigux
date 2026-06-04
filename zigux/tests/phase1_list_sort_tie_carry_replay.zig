const std = @import("std");
const list_sort = @import("list_sort");

const Entry = struct {
    key: i32,
    ordinal: usize,
    node: list_sort.ListHead = .{},
};

fn appendAll(head: *list_sort.ListHead, entries: []Entry) void {
    for (entries) |*entry| {
        list_sort.listAddTail(&entry.node, head);
    }
}

fn expectForwardOrder(
    head: *list_sort.ListHead,
    expected_keys: []const i32,
    expected_ordinals: []const usize,
) !void {
    try std.testing.expectEqual(expected_keys.len, expected_ordinals.len);

    var idx: usize = 0;
    var current = head.next;
    while (current != head) : (current = current.?.next) {
        const entry: *const Entry = @fieldParentPtr("node", current.?);
        try std.testing.expect(idx < expected_keys.len);
        try std.testing.expectEqual(expected_keys[idx], entry.key);
        try std.testing.expectEqual(expected_ordinals[idx], entry.ordinal);
        try std.testing.expect(current.?.next.?.prev == current.?);
        try std.testing.expect(current.?.prev.?.next == current.?);
        idx += 1;
    }

    try std.testing.expectEqual(expected_keys.len, idx);
}

fn expectBackwardOrdinals(head: *list_sort.ListHead, expected: []const usize) !void {
    var idx: usize = 0;
    var current = head.prev;
    while (current != head) : (current = current.?.prev) {
        const entry: *const Entry = @fieldParentPtr("node", current.?);
        try std.testing.expect(idx < expected.len);
        try std.testing.expectEqual(expected[idx], entry.ordinal);
        idx += 1;
    }

    try std.testing.expectEqual(expected.len, idx);
}

test "list sort preserves all-tie order across pending merge carries" {
    const cmp = struct {
        fn ties(_: ?*anyopaque, _: *const list_sort.ListHead, _: *const list_sort.ListHead) i32 {
            return 0;
        }
    }.ties;

    var head: list_sort.ListHead = .{};
    head.init();
    var entries = [_]Entry{
        .{ .key = 9, .ordinal = 0 },
        .{ .key = -1, .ordinal = 1 },
        .{ .key = 7, .ordinal = 2 },
        .{ .key = 7, .ordinal = 3 },
        .{ .key = 3, .ordinal = 4 },
        .{ .key = 12, .ordinal = 5 },
        .{ .key = 0, .ordinal = 6 },
        .{ .key = -4, .ordinal = 7 },
        .{ .key = 12, .ordinal = 8 },
        .{ .key = 5, .ordinal = 9 },
        .{ .key = 5, .ordinal = 10 },
        .{ .key = -9, .ordinal = 11 },
        .{ .key = 1, .ordinal = 12 },
        .{ .key = 1, .ordinal = 13 },
        .{ .key = 6, .ordinal = 14 },
        .{ .key = 6, .ordinal = 15 },
        .{ .key = 2, .ordinal = 16 },
    };
    appendAll(&head, &entries);

    list_sort.listSort(null, &head, cmp);

    try expectForwardOrder(
        &head,
        &.{ 9, -1, 7, 7, 3, 12, 0, -4, 12, 5, 5, -9, 1, 1, 6, 6, 2 },
        &.{ 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16 },
    );
    try expectBackwardOrdinals(&head, &.{ 16, 15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0 });
    try std.testing.expect(head.next == &entries[0].node);
    try std.testing.expect(head.prev == &entries[16].node);
}

test "list sort keeps stable modulo buckets over a non power of two run" {
    const cmp = struct {
        fn byBucket(_: ?*anyopaque, a: *const list_sort.ListHead, b: *const list_sort.ListHead) i32 {
            const lhs: *const Entry = @fieldParentPtr("node", a);
            const rhs: *const Entry = @fieldParentPtr("node", b);
            const lhs_bucket = @mod(lhs.key, 4);
            const rhs_bucket = @mod(rhs.key, 4);
            if (lhs_bucket == rhs_bucket) return 0;
            return if (lhs_bucket < rhs_bucket) -1 else 1;
        }
    }.byBucket;

    var head: list_sort.ListHead = .{};
    head.init();
    var entries = [_]Entry{
        .{ .key = 15, .ordinal = 0 },
        .{ .key = 8, .ordinal = 1 },
        .{ .key = 3, .ordinal = 2 },
        .{ .key = 12, .ordinal = 3 },
        .{ .key = 7, .ordinal = 4 },
        .{ .key = 0, .ordinal = 5 },
        .{ .key = 11, .ordinal = 6 },
        .{ .key = 4, .ordinal = 7 },
        .{ .key = 14, .ordinal = 8 },
        .{ .key = 10, .ordinal = 9 },
        .{ .key = 2, .ordinal = 10 },
        .{ .key = 6, .ordinal = 11 },
        .{ .key = 1, .ordinal = 12 },
        .{ .key = 5, .ordinal = 13 },
        .{ .key = 9, .ordinal = 14 },
    };
    appendAll(&head, &entries);

    list_sort.listSort(null, &head, cmp);

    try expectForwardOrder(
        &head,
        &.{ 8, 12, 0, 4, 1, 5, 9, 14, 10, 2, 6, 15, 3, 7, 11 },
        &.{ 1, 3, 5, 7, 12, 13, 14, 8, 9, 10, 11, 0, 2, 4, 6 },
    );
    try expectBackwardOrdinals(&head, &.{ 6, 4, 2, 0, 11, 10, 9, 8, 14, 13, 12, 7, 5, 3, 1 });
    try std.testing.expect(head.next == &entries[1].node);
    try std.testing.expect(head.prev == &entries[6].node);
}

test "list sort tie pass preserves prior descending order" {
    const Direction = enum { ascending, descending };

    const directional_cmp = struct {
        fn cmp(priv: ?*anyopaque, a: *const list_sort.ListHead, b: *const list_sort.ListHead) i32 {
            const direction: *const Direction = @ptrCast(@alignCast(priv.?));
            const lhs: *const Entry = @fieldParentPtr("node", a);
            const rhs: *const Entry = @fieldParentPtr("node", b);
            if (lhs.key == rhs.key) return 0;
            const ascending = lhs.key < rhs.key;
            return if (direction.* == .ascending)
                (if (ascending) -5 else 5)
            else
                (if (ascending) 5 else -5);
        }
    }.cmp;

    const ties_cmp = struct {
        fn cmp(_: ?*anyopaque, _: *const list_sort.ListHead, _: *const list_sort.ListHead) i32 {
            return 0;
        }
    }.cmp;

    var head: list_sort.ListHead = .{};
    head.init();
    var entries = [_]Entry{
        .{ .key = 3, .ordinal = 0 },
        .{ .key = 9, .ordinal = 1 },
        .{ .key = 3, .ordinal = 2 },
        .{ .key = -1, .ordinal = 3 },
        .{ .key = 9, .ordinal = 4 },
        .{ .key = 5, .ordinal = 5 },
        .{ .key = -1, .ordinal = 6 },
        .{ .key = 5, .ordinal = 7 },
        .{ .key = 0, .ordinal = 8 },
    };
    appendAll(&head, &entries);

    var direction = Direction.descending;
    list_sort.listSort(&direction, &head, directional_cmp);
    list_sort.listSort(null, &head, ties_cmp);

    try expectForwardOrder(
        &head,
        &.{ 9, 9, 5, 5, 3, 3, 0, -1, -1 },
        &.{ 1, 4, 5, 7, 0, 2, 8, 3, 6 },
    );
    try expectBackwardOrdinals(&head, &.{ 6, 3, 8, 2, 0, 7, 5, 4, 1 });
    try std.testing.expect(head.next == &entries[1].node);
    try std.testing.expect(head.prev == &entries[6].node);
}
