const std = @import("std");
const list_sort = @import("list_sort");

const Entry = struct {
    key: i32,
    ordinal: usize,
    node: list_sort.ListHead = .{},
};

const SortMode = enum { ascending, descending };

fn contextCmp(priv: ?*anyopaque, a: *const list_sort.ListHead, b: *const list_sort.ListHead) i32 {
    const mode: *const SortMode = @ptrCast(@alignCast(priv.?));
    const lhs: *const Entry = @fieldParentPtr("node", a);
    const rhs: *const Entry = @fieldParentPtr("node", b);

    if (lhs.key == rhs.key) return 0;
    const ascending = lhs.key < rhs.key;
    return if (mode.* == .ascending)
        (if (ascending) -1 else 1)
    else
        (if (ascending) 1 else -1);
}

fn tiesCmp(_: ?*anyopaque, _: *const list_sort.ListHead, _: *const list_sort.ListHead) i32 {
    return 0;
}

test "phase1 list_sort context ties replay preserves descending context order through a later ties pass" {
    var head: list_sort.ListHead = .{};
    head.init();
    var entries = [_]Entry{
        .{ .key = 2, .ordinal = 0 },
        .{ .key = 1, .ordinal = 1 },
        .{ .key = 3, .ordinal = 2 },
        .{ .key = 1, .ordinal = 3 },
        .{ .key = 3, .ordinal = 4 },
        .{ .key = 2, .ordinal = 5 },
        .{ .key = 4, .ordinal = 6 },
    };
    for (&entries) |*entry| {
        list_sort.listAddTail(&entry.node, &head);
    }

    var mode = SortMode.descending;
    list_sort.listSort(&mode, &head, contextCmp);
    list_sort.listSort(null, &head, tiesCmp);

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

    try std.testing.expectEqualSlices(i32, &.{ 4, 3, 3, 2, 2, 1, 1 }, keys[0..idx]);
    try std.testing.expectEqualSlices(usize, &.{ 6, 2, 4, 0, 5, 1, 3 }, ordinals[0..idx]);
    try std.testing.expect(head.next == &entries[6].node);
    try std.testing.expect(head.prev == &entries[3].node);
}
