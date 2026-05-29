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

test "list sort restores stable order after split reverse rejoin" {
    var primary: list_sort.ListHead = .{};
    var side: list_sort.ListHead = .{};
    primary.init();
    side.init();

    var entries = [_]Entry{
        .{ .key = 8, .ordinal = 0 },
        .{ .key = -1, .ordinal = 1 },
        .{ .key = 4, .ordinal = 2 },
        .{ .key = 8, .ordinal = 3 },
        .{ .key = 0, .ordinal = 4 },
        .{ .key = -1, .ordinal = 5 },
        .{ .key = 6, .ordinal = 6 },
        .{ .key = 2, .ordinal = 7 },
        .{ .key = 4, .ordinal = 8 },
        .{ .key = 6, .ordinal = 9 },
    };

    for (&entries) |*entry| list_sort.listAddTail(&entry.node, &primary);

    var mode = SortMode.ascending;
    list_sort.listSort(&mode, &primary, compareByKey);
    try expectOrder(&primary, &.{ -1, -1, 0, 2, 4, 4, 6, 6, 8, 8 }, &.{ 1, 5, 4, 7, 2, 8, 6, 9, 0, 3 });

    var current = primary.next;
    var take_side = true;
    while (current != &primary) {
        const next = current.?.next;
        if (take_side) {
            list_sort.listDel(current.?);
            try std.testing.expect(current.?.next == null);
            try std.testing.expect(current.?.prev == null);
            list_sort.listAdd(current.?, &side);
        }
        take_side = !take_side;
        current = next;
    }

    try expectOrder(&primary, &.{ -1, 2, 4, 6, 8 }, &.{ 5, 7, 8, 9, 3 });
    try expectOrder(&side, &.{ 8, 6, 4, 0, -1 }, &.{ 0, 6, 2, 4, 1 });

    mode = .descending;
    list_sort.listSort(&mode, &primary, compareByKey);
    list_sort.listSort(&mode, &side, compareByKey);
    try expectOrder(&primary, &.{ 8, 6, 4, 2, -1 }, &.{ 3, 9, 8, 7, 5 });
    try expectOrder(&side, &.{ 8, 6, 4, 0, -1 }, &.{ 0, 6, 2, 4, 1 });

    while (!list_sort.listEmpty(&side)) {
        const node = side.next.?;
        list_sort.listDel(node);
        list_sort.listAdd(node, &primary);
    }
    try std.testing.expect(side.next == &side);
    try std.testing.expect(side.prev == &side);
    try expectOrder(&primary, &.{ -1, 0, 4, 6, 8, 8, 6, 4, 2, -1 }, &.{ 1, 4, 2, 6, 0, 3, 9, 8, 7, 5 });

    mode = .ascending;
    list_sort.listSort(&mode, &primary, compareByKey);
    try expectOrder(&primary, &.{ -1, -1, 0, 2, 4, 4, 6, 6, 8, 8 }, &.{ 1, 5, 4, 7, 2, 8, 6, 9, 0, 3 });
    try std.testing.expect(primary.next == &entries[1].node);
    try std.testing.expect(primary.prev == &entries[3].node);
}
