const std = @import("std");
const list_sort = @import("list_sort");

const Entry = struct {
    key: i32,
    ordinal: usize,
    node: list_sort.ListHead = .{},
};

const SortMode = enum { ascending, descending };

fn signedContextCmp(priv: ?*anyopaque, a: *const list_sort.ListHead, b: *const list_sort.ListHead) i32 {
    const mode: *const SortMode = @ptrCast(@alignCast(priv.?));
    const lhs: *const Entry = @fieldParentPtr("node", a);
    const rhs: *const Entry = @fieldParentPtr("node", b);
    const delta = lhs.key - rhs.key;
    return if (mode.* == .ascending) delta else -delta;
}

test "phase1 list_sort signed-context smoke replay keeps descending order stable" {
    var head: list_sort.ListHead = .{};
    head.init();
    var entries = [_]Entry{
        .{ .key = -3, .ordinal = 0 },
        .{ .key = 7, .ordinal = 1 },
        .{ .key = -1, .ordinal = 2 },
        .{ .key = 7, .ordinal = 3 },
        .{ .key = 0, .ordinal = 4 },
        .{ .key = -3, .ordinal = 5 },
        .{ .key = 5, .ordinal = 6 },
    };
    for (&entries) |*entry| {
        list_sort.listAddTail(&entry.node, &head);
    }

    var mode = SortMode.descending;
    list_sort.listSort(&mode, &head, signedContextCmp);

    var keys: [7]i32 = undefined;
    var ordinals: [7]usize = undefined;
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

    try std.testing.expectEqualSlices(i32, &.{ 7, 7, 5, 0, -1, -3, -3 }, keys[0..idx]);
    try std.testing.expectEqualSlices(usize, &.{ 1, 3, 6, 4, 2, 0, 5 }, ordinals[0..idx]);
    try std.testing.expect(head.next == &entries[1].node);
    try std.testing.expect(head.prev == &entries[5].node);
}
