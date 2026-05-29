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
    var keys: [12]i32 = undefined;
    var ordinals: [12]usize = undefined;
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

test "list sort restores stable order after staging interleave" {
    var primary: list_sort.ListHead = .{};
    var staging: list_sort.ListHead = .{};
    primary.init();
    staging.init();

    var entries = [_]Entry{
        .{ .key = 5, .ordinal = 0 },
        .{ .key = -2, .ordinal = 1 },
        .{ .key = 7, .ordinal = 2 },
        .{ .key = 5, .ordinal = 3 },
        .{ .key = 0, .ordinal = 4 },
        .{ .key = -2, .ordinal = 5 },
        .{ .key = 9, .ordinal = 6 },
        .{ .key = 0, .ordinal = 7 },
        .{ .key = 7, .ordinal = 8 },
        .{ .key = 3, .ordinal = 9 },
        .{ .key = 9, .ordinal = 10 },
        .{ .key = 3, .ordinal = 11 },
    };

    for (&entries) |*entry| list_sort.listAddTail(&entry.node, &primary);

    var mode = SortMode.ascending;
    list_sort.listSort(&mode, &primary, compareByKey);
    try expectOrder(&primary, &.{ -2, -2, 0, 0, 3, 3, 5, 5, 7, 7, 9, 9 }, &.{ 1, 5, 4, 7, 9, 11, 0, 3, 2, 8, 6, 10 });

    var current = primary.next;
    var sorted_index: usize = 0;
    while (current != &primary) {
        const next = current.?.next;
        if (sorted_index % 3 == 1) {
            list_sort.listDel(current.?);
            try std.testing.expect(current.?.next == null);
            try std.testing.expect(current.?.prev == null);
            list_sort.listAddTail(current.?, &staging);
        }
        sorted_index += 1;
        current = next;
    }

    try expectOrder(&primary, &.{ -2, 0, 0, 3, 5, 7, 7, 9 }, &.{ 1, 4, 7, 11, 0, 2, 8, 10 });
    try expectOrder(&staging, &.{ -2, 3, 5, 9 }, &.{ 5, 9, 3, 6 });

    mode = .descending;
    list_sort.listSort(&mode, &staging, compareByKey);
    try expectOrder(&staging, &.{ 9, 5, 3, -2 }, &.{ 6, 3, 9, 5 });

    var place_at_head = true;
    while (!list_sort.listEmpty(&staging)) {
        const node = staging.next.?;
        list_sort.listDel(node);
        if (place_at_head) {
            list_sort.listAdd(node, &primary);
        } else {
            list_sort.listAddTail(node, &primary);
        }
        place_at_head = !place_at_head;
    }

    try std.testing.expect(staging.next == &staging);
    try std.testing.expect(staging.prev == &staging);
    try expectOrder(&primary, &.{ 3, 9, -2, 0, 0, 3, 5, 7, 7, 9, 5, -2 }, &.{ 9, 6, 1, 4, 7, 11, 0, 2, 8, 10, 3, 5 });

    mode = .ascending;
    list_sort.listSort(&mode, &primary, compareByKey);
    try expectOrder(&primary, &.{ -2, -2, 0, 0, 3, 3, 5, 5, 7, 7, 9, 9 }, &.{ 1, 5, 4, 7, 9, 11, 0, 3, 2, 8, 6, 10 });
    try std.testing.expect(primary.next == &entries[1].node);
    try std.testing.expect(primary.prev == &entries[10].node);
}
