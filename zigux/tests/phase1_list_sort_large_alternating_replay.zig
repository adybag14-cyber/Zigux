const std = @import("std");
const list_sort = @import("list_sort");

const Entry = struct {
    key: i32,
    ordinal: usize,
    node: list_sort.ListHead = .{},
};

fn cmpAscending(_: ?*anyopaque, a: *const list_sort.ListHead, b: *const list_sort.ListHead) i32 {
    const lhs: *const Entry = @fieldParentPtr("node", a);
    const rhs: *const Entry = @fieldParentPtr("node", b);
    if (lhs.key < rhs.key) return -1;
    if (lhs.key > rhs.key) return 1;
    return 0;
}

test "list sort keeps stable order across a large alternating descending run" {
    var head: list_sort.ListHead = .{};
    head.init();

    var entries = [_]Entry{
        .{ .key = 9, .ordinal = 0 },
        .{ .key = 0, .ordinal = 1 },
        .{ .key = 8, .ordinal = 2 },
        .{ .key = 1, .ordinal = 3 },
        .{ .key = 7, .ordinal = 4 },
        .{ .key = 2, .ordinal = 5 },
        .{ .key = 6, .ordinal = 6 },
        .{ .key = 3, .ordinal = 7 },
        .{ .key = 5, .ordinal = 8 },
        .{ .key = 4, .ordinal = 9 },
        .{ .key = 4, .ordinal = 10 },
        .{ .key = 5, .ordinal = 11 },
        .{ .key = 3, .ordinal = 12 },
        .{ .key = 6, .ordinal = 13 },
        .{ .key = 2, .ordinal = 14 },
        .{ .key = 7, .ordinal = 15 },
        .{ .key = 1, .ordinal = 16 },
        .{ .key = 8, .ordinal = 17 },
        .{ .key = 0, .ordinal = 18 },
        .{ .key = 9, .ordinal = 19 },
    };

    for (&entries) |*entry| list_sort.listAddTail(&entry.node, &head);
    list_sort.listSort(null, &head, cmpAscending);

    var keys: [entries.len]i32 = undefined;
    var ordinals: [entries.len]usize = undefined;
    var idx: usize = 0;
    var current = head.next;
    while (current != &head) : (current = current.?.next) {
        const entry: *const Entry = @fieldParentPtr("node", current.?);
        keys[idx] = entry.key;
        ordinals[idx] = entry.ordinal;
        try std.testing.expect(current.?.next.?.prev == current.?);
        try std.testing.expect(current.?.prev.?.next == current.?);
        idx += 1;
    }

    try std.testing.expectEqual(entries.len, idx);
    try std.testing.expectEqualSlices(i32, &.{
        0, 0,
        1, 1,
        2, 2,
        3, 3,
        4, 4,
        5, 5,
        6, 6,
        7, 7,
        8, 8,
        9, 9,
    }, keys[0..idx]);
    try std.testing.expectEqualSlices(usize, &.{
        1, 18,
        3, 16,
        5, 14,
        7, 12,
        9, 10,
        8, 11,
        6, 13,
        4, 15,
        2, 17,
        0, 19,
    }, ordinals[0..idx]);
    try std.testing.expect(head.next == &entries[1].node);
    try std.testing.expect(head.prev == &entries[19].node);
    try std.testing.expect(entries[1].node.prev == &head);
    try std.testing.expect(entries[19].node.next == &head);

    var reverse_ordinals: [entries.len]usize = undefined;
    idx = 0;
    current = head.prev;
    while (current != &head) : (current = current.?.prev) {
        const entry: *const Entry = @fieldParentPtr("node", current.?);
        reverse_ordinals[idx] = entry.ordinal;
        idx += 1;
    }

    try std.testing.expectEqualSlices(usize, &.{
        19, 0,
        17, 2,
        15, 4,
        13, 6,
        11, 8,
        10, 9,
        12, 7,
        14, 5,
        16, 3,
        18, 1,
    }, reverse_ordinals[0..idx]);
}
