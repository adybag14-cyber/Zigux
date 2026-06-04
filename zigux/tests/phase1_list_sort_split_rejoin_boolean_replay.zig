const std = @import("std");
const list_sort = @import("list_sort");

const Entry = struct {
    key: i32,
    ordinal: usize,
    node: list_sort.ListHead = .{},
};

const SortMode = enum { ascending, descending };

fn booleanCompare(priv: ?*anyopaque, a: *const list_sort.ListHead, b: *const list_sort.ListHead) i32 {
    const mode: *const SortMode = @ptrCast(@alignCast(priv.?));
    const lhs: *const Entry = @fieldParentPtr("node", a);
    const rhs: *const Entry = @fieldParentPtr("node", b);

    if (lhs.key == rhs.key) return 0;
    return if (mode.* == .ascending)
        @intFromBool(lhs.key > rhs.key)
    else
        @intFromBool(lhs.key < rhs.key);
}

fn collect(head: *list_sort.ListHead, keys: []i32, ordinals: []usize) !usize {
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
    return idx;
}

test "phase1 list_sort replay sorts split and rejoined boolean comparator lists" {
    var source: list_sort.ListHead = .{};
    var staged: list_sort.ListHead = .{};
    source.init();
    staged.init();

    var entries = [_]Entry{
        .{ .key = 4, .ordinal = 0 },
        .{ .key = 1, .ordinal = 1 },
        .{ .key = 6, .ordinal = 2 },
        .{ .key = 3, .ordinal = 3 },
        .{ .key = 4, .ordinal = 4 },
        .{ .key = 2, .ordinal = 5 },
        .{ .key = 6, .ordinal = 6 },
        .{ .key = 1, .ordinal = 7 },
    };

    for (&entries) |*entry| {
        list_sort.listAddTail(&entry.node, &source);
    }

    list_sort.listDel(&entries[2].node);
    list_sort.listAddTail(&entries[2].node, &staged);
    list_sort.listDel(&entries[5].node);
    list_sort.listAddTail(&entries[5].node, &staged);
    list_sort.listDel(&entries[7].node);
    list_sort.listAddTail(&entries[7].node, &staged);

    var mode = SortMode.descending;
    list_sort.listSort(&mode, &source, booleanCompare);
    list_sort.listSort(&mode, &staged, booleanCompare);

    list_sort.listDel(&entries[2].node);
    list_sort.listAddTail(&entries[2].node, &source);
    list_sort.listDel(&entries[5].node);
    list_sort.listAdd(&entries[5].node, &source);
    list_sort.listDel(&entries[7].node);
    list_sort.listAddTail(&entries[7].node, &source);
    try std.testing.expect(list_sort.listEmpty(&staged));

    mode = .ascending;
    list_sort.listSort(&mode, &source, booleanCompare);

    var keys: [entries.len]i32 = undefined;
    var ordinals: [entries.len]usize = undefined;
    const count = try collect(&source, &keys, &ordinals);

    try std.testing.expectEqual(@as(usize, entries.len), count);
    try std.testing.expectEqualSlices(i32, &.{ 1, 1, 2, 3, 4, 4, 6, 6 }, keys[0..count]);
    try std.testing.expectEqualSlices(usize, &.{ 1, 7, 5, 3, 0, 4, 6, 2 }, ordinals[0..count]);
    try std.testing.expect(source.next == &entries[1].node);
    try std.testing.expect(source.prev == &entries[2].node);
    try std.testing.expect(entries[1].node.prev == &source);
    try std.testing.expect(entries[2].node.next == &source);
}
