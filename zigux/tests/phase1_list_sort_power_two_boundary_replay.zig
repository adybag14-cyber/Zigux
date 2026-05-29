const std = @import("std");
const list_sort = @import("list_sort");

const Entry = struct {
    key: i32,
    ordinal: usize,
    node: list_sort.ListHead = .{},
};

const SortMode = enum { ascending, descending };

fn compareKeys(priv: ?*anyopaque, a: *const list_sort.ListHead, b: *const list_sort.ListHead) i32 {
    const mode: *const SortMode = @ptrCast(@alignCast(priv.?));
    const lhs: *const Entry = @fieldParentPtr("node", a);
    const rhs: *const Entry = @fieldParentPtr("node", b);

    if (lhs.key == rhs.key) return 0;
    const lhs_before_rhs = lhs.key < rhs.key;
    return switch (mode.*) {
        .ascending => if (lhs_before_rhs) -3 else 5,
        .descending => if (lhs_before_rhs) 5 else -3,
    };
}

fn expectForwardOrder(head: *const list_sort.ListHead, expected_keys: []const i32, expected_ordinals: []const usize) !void {
    var keys: [17]i32 = undefined;
    var ordinals: [17]usize = undefined;
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
    var ordinals: [17]usize = undefined;
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

test "list sort keeps duplicate stability across a power-two merge boundary" {
    var head: list_sort.ListHead = .{};
    head.init();

    var entries = [_]Entry{
        .{ .key = 8, .ordinal = 0 },
        .{ .key = 1, .ordinal = 1 },
        .{ .key = 7, .ordinal = 2 },
        .{ .key = 1, .ordinal = 3 },
        .{ .key = 6, .ordinal = 4 },
        .{ .key = 2, .ordinal = 5 },
        .{ .key = 5, .ordinal = 6 },
        .{ .key = 2, .ordinal = 7 },
        .{ .key = 4, .ordinal = 8 },
        .{ .key = 3, .ordinal = 9 },
        .{ .key = 3, .ordinal = 10 },
        .{ .key = 4, .ordinal = 11 },
        .{ .key = 2, .ordinal = 12 },
        .{ .key = 5, .ordinal = 13 },
        .{ .key = 1, .ordinal = 14 },
        .{ .key = 6, .ordinal = 15 },
        .{ .key = 0, .ordinal = 16 },
    };

    for (&entries) |*entry| list_sort.listAddTail(&entry.node, &head);

    var mode = SortMode.ascending;
    list_sort.listSort(&mode, &head, compareKeys);
    try expectForwardOrder(
        &head,
        &.{ 0, 1, 1, 1, 2, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6, 7, 8 },
        &.{ 16, 1, 3, 14, 5, 7, 12, 9, 10, 8, 11, 6, 13, 4, 15, 2, 0 },
    );
    try std.testing.expect(head.next == &entries[16].node);
    try std.testing.expect(head.prev == &entries[0].node);

    mode = .descending;
    list_sort.listSort(&mode, &head, compareKeys);
    try expectForwardOrder(
        &head,
        &.{ 8, 7, 6, 6, 5, 5, 4, 4, 3, 3, 2, 2, 2, 1, 1, 1, 0 },
        &.{ 0, 2, 4, 15, 6, 13, 8, 11, 9, 10, 5, 7, 12, 1, 3, 14, 16 },
    );
    try expectBackwardOrdinals(
        &head,
        &.{ 16, 14, 3, 1, 12, 7, 5, 10, 9, 11, 8, 13, 6, 15, 4, 2, 0 },
    );
    try std.testing.expect(head.next == &entries[0].node);
    try std.testing.expect(head.prev == &entries[16].node);
}
