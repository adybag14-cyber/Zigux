const std = @import("std");
const list_sort = @import("list_sort");

const Entry = struct {
    key: i32,
    ordinal: usize,
    node: list_sort.ListHead = .{},
};

const SortMode = enum { ascending, descending };

fn compareExtremeKeys(priv: ?*anyopaque, a: *const list_sort.ListHead, b: *const list_sort.ListHead) i32 {
    const mode: *const SortMode = @ptrCast(@alignCast(priv.?));
    const lhs: *const Entry = @fieldParentPtr("node", a);
    const rhs: *const Entry = @fieldParentPtr("node", b);

    if (lhs.key == rhs.key) return 0;
    const lhs_before_rhs = lhs.key < rhs.key;
    return switch (mode.*) {
        .ascending => if (lhs_before_rhs) -17 else 19,
        .descending => if (lhs_before_rhs) 19 else -17,
    };
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

test "list sort keeps extreme signed keys stable across direction changes" {
    var head: list_sort.ListHead = .{};
    head.init();

    var entries = [_]Entry{
        .{ .key = std.math.maxInt(i32), .ordinal = 0 },
        .{ .key = 0, .ordinal = 1 },
        .{ .key = std.math.minInt(i32), .ordinal = 2 },
        .{ .key = -1, .ordinal = 3 },
        .{ .key = std.math.maxInt(i32), .ordinal = 4 },
        .{ .key = 42, .ordinal = 5 },
        .{ .key = std.math.minInt(i32), .ordinal = 6 },
        .{ .key = -1, .ordinal = 7 },
        .{ .key = 42, .ordinal = 8 },
        .{ .key = 0, .ordinal = 9 },
    };

    for (&entries, 0..) |*entry, index| {
        if ((index & 1) == 0) {
            list_sort.listAdd(&entry.node, &head);
        } else {
            list_sort.listAddTail(&entry.node, &head);
        }
    }

    var mode = SortMode.ascending;
    list_sort.listSort(&mode, &head, compareExtremeKeys);
    try expectOrder(
        &head,
        &.{
            std.math.minInt(i32),
            std.math.minInt(i32),
            -1,
            -1,
            0,
            0,
            42,
            42,
            std.math.maxInt(i32),
            std.math.maxInt(i32),
        },
        &.{ 6, 2, 3, 7, 1, 9, 8, 5, 4, 0 },
    );

    mode = .descending;
    list_sort.listSort(&mode, &head, compareExtremeKeys);
    try expectOrder(
        &head,
        &.{
            std.math.maxInt(i32),
            std.math.maxInt(i32),
            42,
            42,
            0,
            0,
            -1,
            -1,
            std.math.minInt(i32),
            std.math.minInt(i32),
        },
        &.{ 4, 0, 8, 5, 1, 9, 3, 7, 6, 2 },
    );

    try std.testing.expect(head.next == &entries[4].node);
    try std.testing.expect(head.prev == &entries[2].node);
}
