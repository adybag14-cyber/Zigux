const std = @import("std");
const list_sort = @import("list_sort");

const Entry = struct {
    key: i32,
    ordinal: usize,
    node: list_sort.ListHead = .{},
};

const SortMode = enum { ascending, descending };

fn compareByMode(priv: ?*anyopaque, a: *const list_sort.ListHead, b: *const list_sort.ListHead) i32 {
    const mode: *const SortMode = @ptrCast(@alignCast(priv.?));
    const lhs: *const Entry = @fieldParentPtr("node", a);
    const rhs: *const Entry = @fieldParentPtr("node", b);

    if (lhs.key == rhs.key) return 0;
    const ascending = lhs.key < rhs.key;
    return if ((mode.* == .ascending) == ascending) -17 else 19;
}

fn expectForwardOrder(head: *const list_sort.ListHead, expected_keys: []const i32, expected_ordinals: []const usize) !void {
    var keys: [33]i32 = undefined;
    var ordinals: [33]usize = undefined;
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

fn expectBackwardOrdinals(head: *const list_sort.ListHead, expected_ordinals: []const usize) !void {
    var ordinals: [33]usize = undefined;
    var idx: usize = 0;
    var current = head.prev;

    while (current != head) : (current = current.?.prev) {
        const entry: *const Entry = @fieldParentPtr("node", current.?);
        ordinals[idx] = entry.ordinal;
        idx += 1;
    }

    try std.testing.expectEqual(expected_ordinals.len, idx);
    try std.testing.expectEqualSlices(usize, expected_ordinals, ordinals[0..idx]);
}

test "list sort preserves stability across a long carry chain" {
    var head: list_sort.ListHead = .{};
    head.init();

    var entries = [_]Entry{
        .{ .key = 9, .ordinal = 0 },
        .{ .key = -4, .ordinal = 1 },
        .{ .key = 7, .ordinal = 2 },
        .{ .key = 0, .ordinal = 3 },
        .{ .key = 7, .ordinal = 4 },
        .{ .key = -4, .ordinal = 5 },
        .{ .key = 12, .ordinal = 6 },
        .{ .key = 3, .ordinal = 7 },
        .{ .key = 9, .ordinal = 8 },
        .{ .key = 0, .ordinal = 9 },
        .{ .key = -1, .ordinal = 10 },
        .{ .key = 12, .ordinal = 11 },
        .{ .key = 5, .ordinal = 12 },
        .{ .key = -1, .ordinal = 13 },
        .{ .key = 3, .ordinal = 14 },
        .{ .key = 8, .ordinal = 15 },
        .{ .key = 5, .ordinal = 16 },
        .{ .key = 8, .ordinal = 17 },
        .{ .key = -6, .ordinal = 18 },
        .{ .key = 10, .ordinal = 19 },
        .{ .key = -6, .ordinal = 20 },
        .{ .key = 2, .ordinal = 21 },
        .{ .key = 10, .ordinal = 22 },
        .{ .key = 2, .ordinal = 23 },
        .{ .key = 11, .ordinal = 24 },
        .{ .key = 4, .ordinal = 25 },
        .{ .key = 11, .ordinal = 26 },
        .{ .key = 4, .ordinal = 27 },
        .{ .key = 6, .ordinal = 28 },
        .{ .key = 1, .ordinal = 29 },
        .{ .key = 6, .ordinal = 30 },
        .{ .key = 1, .ordinal = 31 },
        .{ .key = 13, .ordinal = 32 },
    };

    for (&entries) |*entry| list_sort.listAddTail(&entry.node, &head);

    var mode = SortMode.ascending;
    list_sort.listSort(&mode, &head, compareByMode);

    try expectForwardOrder(
        &head,
        &.{ -6, -6, -4, -4, -1, -1, 0, 0, 1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6, 7, 7, 8, 8, 9, 9, 10, 10, 11, 11, 12, 12, 13 },
        &.{ 18, 20, 1, 5, 10, 13, 3, 9, 29, 31, 21, 23, 7, 14, 25, 27, 12, 16, 28, 30, 2, 4, 15, 17, 0, 8, 19, 22, 24, 26, 6, 11, 32 },
    );
    try std.testing.expect(head.next == &entries[18].node);
    try std.testing.expect(head.prev == &entries[32].node);

    mode = .descending;
    list_sort.listSort(&mode, &head, compareByMode);

    try expectForwardOrder(
        &head,
        &.{ 13, 12, 12, 11, 11, 10, 10, 9, 9, 8, 8, 7, 7, 6, 6, 5, 5, 4, 4, 3, 3, 2, 2, 1, 1, 0, 0, -1, -1, -4, -4, -6, -6 },
        &.{ 32, 6, 11, 24, 26, 19, 22, 0, 8, 15, 17, 2, 4, 28, 30, 12, 16, 25, 27, 7, 14, 21, 23, 29, 31, 3, 9, 10, 13, 1, 5, 18, 20 },
    );
    try expectBackwardOrdinals(&head, &.{ 20, 18, 5, 1, 13, 10, 9, 3, 31, 29, 23, 21, 14, 7, 27, 25, 16, 12, 30, 28, 4, 2, 17, 15, 8, 0, 22, 19, 26, 24, 11, 6, 32 });
    try std.testing.expect(head.next == &entries[32].node);
    try std.testing.expect(head.prev == &entries[20].node);
}
