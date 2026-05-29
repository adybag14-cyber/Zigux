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
    var keys: [9]i32 = undefined;
    var ordinals: [9]usize = undefined;
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

test "list sort survives partition rejoin across two sentinels" {
    var primary: list_sort.ListHead = .{};
    var side: list_sort.ListHead = .{};
    primary.init();
    side.init();

    var entries = [_]Entry{
        .{ .key = 5, .ordinal = 0 },
        .{ .key = -2, .ordinal = 1 },
        .{ .key = 3, .ordinal = 2 },
        .{ .key = -2, .ordinal = 3 },
        .{ .key = 9, .ordinal = 4 },
        .{ .key = 0, .ordinal = 5 },
        .{ .key = 5, .ordinal = 6 },
        .{ .key = 7, .ordinal = 7 },
        .{ .key = 0, .ordinal = 8 },
    };

    for (&entries) |*entry| list_sort.listAddTail(&entry.node, &primary);

    var mode = SortMode.ascending;
    list_sort.listSort(&mode, &primary, compareByKey);
    try expectOrder(&primary, &.{ -2, -2, 0, 0, 3, 5, 5, 7, 9 }, &.{ 1, 3, 5, 8, 2, 0, 6, 7, 4 });

    var current = primary.next;
    while (current != &primary) {
        const next = current.?.next;
        const entry: *const Entry = @fieldParentPtr("node", current.?);
        if (entry.key <= 0) {
            list_sort.listDel(current.?);
            try std.testing.expect(current.?.next == null);
            try std.testing.expect(current.?.prev == null);
            list_sort.listAddTail(current.?, &side);
        }
        current = next;
    }

    try expectOrder(&primary, &.{ 3, 5, 5, 7, 9 }, &.{ 2, 0, 6, 7, 4 });
    try expectOrder(&side, &.{ -2, -2, 0, 0 }, &.{ 1, 3, 5, 8 });
    try std.testing.expect(primary.next == &entries[2].node);
    try std.testing.expect(primary.prev == &entries[4].node);

    mode = .descending;
    list_sort.listSort(&mode, &side, compareByKey);
    try expectOrder(&side, &.{ 0, 0, -2, -2 }, &.{ 5, 8, 1, 3 });
    try std.testing.expect(side.next == &entries[5].node);
    try std.testing.expect(side.prev == &entries[3].node);

    while (!list_sort.listEmpty(&side)) {
        const node = side.next.?;
        list_sort.listDel(node);
        list_sort.listAddTail(node, &primary);
    }
    try std.testing.expect(side.next == &side);
    try std.testing.expect(side.prev == &side);
    try expectOrder(&primary, &.{ 3, 5, 5, 7, 9, 0, 0, -2, -2 }, &.{ 2, 0, 6, 7, 4, 5, 8, 1, 3 });

    mode = .ascending;
    list_sort.listSort(&mode, &primary, compareByKey);
    try expectOrder(&primary, &.{ -2, -2, 0, 0, 3, 5, 5, 7, 9 }, &.{ 1, 3, 5, 8, 2, 0, 6, 7, 4 });
    try std.testing.expect(primary.next == &entries[1].node);
    try std.testing.expect(primary.prev == &entries[4].node);
}
