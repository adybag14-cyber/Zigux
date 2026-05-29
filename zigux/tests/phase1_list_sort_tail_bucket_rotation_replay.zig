const std = @import("std");
const list_sort = @import("list_sort");

const Entry = struct {
    key: i32,
    ordinal: usize,
    node: list_sort.ListHead = .{},
};

const SortMode = enum { ascending, descending };

fn compareByKey(priv: ?*anyopaque, a: *const list_sort.ListHead, b: *const list_sort.ListHead) i32 {
    const mode: *const SortMode = @ptrCast(@alignCast(priv.?));
    const lhs: *const Entry = @fieldParentPtr("node", a);
    const rhs: *const Entry = @fieldParentPtr("node", b);

    if (lhs.key < rhs.key) return if (mode.* == .ascending) -1 else 1;
    if (lhs.key > rhs.key) return if (mode.* == .ascending) 1 else -1;
    return 0;
}

fn expectOrder(head: *const list_sort.ListHead, expected_keys: []const i32, expected_ordinals: []const usize) !void {
    var keys: [10]i32 = undefined;
    var ordinals: [10]usize = undefined;
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
}

test "list sort restores stable order after tail bucket rotation" {
    var primary: list_sort.ListHead = .{};
    var tail_bucket: list_sort.ListHead = .{};
    primary.init();
    tail_bucket.init();

    var entries = [_]Entry{
        .{ .key = 4, .ordinal = 0 },
        .{ .key = -1, .ordinal = 1 },
        .{ .key = 6, .ordinal = 2 },
        .{ .key = 4, .ordinal = 3 },
        .{ .key = 8, .ordinal = 4 },
        .{ .key = -1, .ordinal = 5 },
        .{ .key = 2, .ordinal = 6 },
        .{ .key = 6, .ordinal = 7 },
        .{ .key = 8, .ordinal = 8 },
        .{ .key = 2, .ordinal = 9 },
    };

    for (&entries) |*entry| list_sort.listAddTail(&entry.node, &primary);

    var mode = SortMode.ascending;
    list_sort.listSort(&mode, &primary, compareByKey);
    try expectOrder(&primary, &.{ -1, -1, 2, 2, 4, 4, 6, 6, 8, 8 }, &.{ 1, 5, 6, 9, 0, 3, 2, 7, 4, 8 });

    var current = primary.next;
    while (current != &primary) {
        const next = current.?.next;
        const entry: *const Entry = @fieldParentPtr("node", current.?);
        if (entry.key >= 6) {
            list_sort.listDel(current.?);
            try std.testing.expect(current.?.next == null);
            try std.testing.expect(current.?.prev == null);
            list_sort.listAddTail(current.?, &tail_bucket);
        }
        current = next;
    }

    try expectOrder(&primary, &.{ -1, -1, 2, 2, 4, 4 }, &.{ 1, 5, 6, 9, 0, 3 });
    try expectOrder(&tail_bucket, &.{ 6, 6, 8, 8 }, &.{ 2, 7, 4, 8 });

    mode = .descending;
    list_sort.listSort(&mode, &tail_bucket, compareByKey);
    try expectOrder(&tail_bucket, &.{ 8, 8, 6, 6 }, &.{ 4, 8, 2, 7 });

    var place_at_head = true;
    while (!list_sort.listEmpty(&tail_bucket)) {
        const node = tail_bucket.prev.?;
        list_sort.listDel(node);
        if (place_at_head) {
            list_sort.listAdd(node, &primary);
        } else {
            list_sort.listAddTail(node, &primary);
        }
        place_at_head = !place_at_head;
    }

    try std.testing.expect(tail_bucket.next == &tail_bucket);
    try std.testing.expect(tail_bucket.prev == &tail_bucket);
    try expectOrder(&primary, &.{ 8, 6, -1, -1, 2, 2, 4, 4, 6, 8 }, &.{ 8, 7, 1, 5, 6, 9, 0, 3, 2, 4 });

    mode = .ascending;
    list_sort.listSort(&mode, &primary, compareByKey);
    try expectOrder(&primary, &.{ -1, -1, 2, 2, 4, 4, 6, 6, 8, 8 }, &.{ 1, 5, 6, 9, 0, 3, 7, 2, 8, 4 });
    try std.testing.expect(primary.next == &entries[1].node);
    try std.testing.expect(primary.prev == &entries[4].node);
}
