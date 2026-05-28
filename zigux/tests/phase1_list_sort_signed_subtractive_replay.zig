const std = @import("std");
const list_sort = @import("list_sort");

const Entry = struct {
    key: i32,
    ordinal: usize,
    node: list_sort.ListHead = .{},
};

fn signedCmp(_: ?*anyopaque, a: *const list_sort.ListHead, b: *const list_sort.ListHead) i32 {
    const lhs: *const Entry = @fieldParentPtr("node", a);
    const rhs: *const Entry = @fieldParentPtr("node", b);
    return lhs.key - rhs.key;
}

test "phase1 list_sort signed subtractive replay" {
    var head: list_sort.ListHead = .{};
    head.init();

    var entries = [_]Entry{
        .{ .key = 4, .ordinal = 0 },
        .{ .key = -2, .ordinal = 1 },
        .{ .key = 7, .ordinal = 2 },
        .{ .key = -2, .ordinal = 3 },
        .{ .key = 0, .ordinal = 4 },
        .{ .key = -5, .ordinal = 5 },
        .{ .key = 7, .ordinal = 6 },
    };
    for (&entries) |*entry| {
        list_sort.listAddTail(&entry.node, &head);
    }

    list_sort.listSort(null, &head, signedCmp);

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
    try std.testing.expectEqualSlices(i32, &.{ -5, -2, -2, 0, 4, 7, 7 }, keys[0..idx]);
    try std.testing.expectEqualSlices(usize, &.{ 5, 1, 3, 4, 0, 2, 6 }, ordinals[0..idx]);
    try std.testing.expect(head.next == &entries[5].node);
    try std.testing.expect(head.prev == &entries[6].node);
    try std.testing.expect(entries[5].node.prev == &head);
    try std.testing.expect(entries[6].node.next == &head);
}
