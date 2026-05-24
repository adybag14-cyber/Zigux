const std = @import("std");
const list_sort = @import("list_sort");

const Entry = struct {
    key: i32,
    ordinal: usize,
    node: list_sort.ListHead = .{},
};

const SortMode = enum { ascending, descending };

fn appendEntries(head: *list_sort.ListHead, entries: []Entry) void {
    for (entries) |*entry| {
        list_sort.listAddTail(&entry.node, head);
    }
}

fn collectState(
    head: *list_sort.ListHead,
    keys: []i32,
    ordinals: []usize,
) !usize {
    var count: usize = 0;
    var current = head.next;
    while (current != head) : (current = current.?.next) {
        const entry: *const Entry = @fieldParentPtr("node", current.?);
        keys[count] = entry.key;
        ordinals[count] = entry.ordinal;
        try std.testing.expect(current.?.next.?.prev == current.?);
        try std.testing.expect(current.?.prev.?.next == current.?);
        count += 1;
    }
    return count;
}

fn absBucketCmp(_: ?*anyopaque, a: *const list_sort.ListHead, b: *const list_sort.ListHead) i32 {
    const lhs: *const Entry = @fieldParentPtr("node", a);
    const rhs: *const Entry = @fieldParentPtr("node", b);
    const lhs_abs = @abs(lhs.key);
    const rhs_abs = @abs(rhs.key);

    if (lhs_abs < rhs_abs) return -1;
    if (lhs_abs > rhs_abs) return 1;
    return 0;
}

fn absBucketModeCmp(priv: ?*anyopaque, a: *const list_sort.ListHead, b: *const list_sort.ListHead) i32 {
    const mode: *const SortMode = @ptrCast(@alignCast(priv.?));
    const lhs: *const Entry = @fieldParentPtr("node", a);
    const rhs: *const Entry = @fieldParentPtr("node", b);
    const lhs_abs = @abs(lhs.key);
    const rhs_abs = @abs(rhs.key);

    if (lhs_abs == rhs_abs) return 0;
    const ascending = lhs_abs < rhs_abs;
    return if (mode.* == .ascending)
        (if (ascending) -17 else 19)
    else
        (if (ascending) 19 else -17);
}

test "phase1 list_sort absolute-bucket replay preserves stable order within equal absolute values" {
    var head: list_sort.ListHead = .{};
    head.init();
    var entries = [_]Entry{
        .{ .key = 3, .ordinal = 0 },
        .{ .key = -1, .ordinal = 1 },
        .{ .key = 2, .ordinal = 2 },
        .{ .key = -3, .ordinal = 3 },
        .{ .key = 1, .ordinal = 4 },
        .{ .key = -2, .ordinal = 5 },
        .{ .key = 0, .ordinal = 6 },
        .{ .key = 2, .ordinal = 7 },
    };
    appendEntries(&head, &entries);

    list_sort.listSort(null, &head, absBucketCmp);

    var keys: [entries.len]i32 = undefined;
    var ordinals: [entries.len]usize = undefined;
    const count = try collectState(&head, &keys, &ordinals);

    try std.testing.expectEqual(@as(usize, entries.len), count);
    try std.testing.expectEqualSlices(i32, &.{ 0, -1, 1, 2, -2, 2, 3, -3 }, keys[0..count]);
    try std.testing.expectEqualSlices(usize, &.{ 6, 1, 4, 2, 5, 7, 0, 3 }, ordinals[0..count]);
    try std.testing.expect(head.next == &entries[6].node);
    try std.testing.expect(head.prev == &entries[3].node);
}

test "phase1 list_sort absolute-bucket replay honors descending context without disturbing bucket stability" {
    var head: list_sort.ListHead = .{};
    head.init();
    var entries = [_]Entry{
        .{ .key = -2, .ordinal = 0 },
        .{ .key = 5, .ordinal = 1 },
        .{ .key = -1, .ordinal = 2 },
        .{ .key = 3, .ordinal = 3 },
        .{ .key = -5, .ordinal = 4 },
        .{ .key = 1, .ordinal = 5 },
        .{ .key = -3, .ordinal = 6 },
        .{ .key = 0, .ordinal = 7 },
    };
    appendEntries(&head, &entries);

    var mode = SortMode.descending;
    list_sort.listSort(&mode, &head, absBucketModeCmp);

    var keys: [entries.len]i32 = undefined;
    var ordinals: [entries.len]usize = undefined;
    const count = try collectState(&head, &keys, &ordinals);

    try std.testing.expectEqual(@as(usize, entries.len), count);
    try std.testing.expectEqualSlices(i32, &.{ 5, -5, 3, -3, -2, -1, 1, 0 }, keys[0..count]);
    try std.testing.expectEqualSlices(usize, &.{ 1, 4, 3, 6, 0, 2, 5, 7 }, ordinals[0..count]);
    try std.testing.expect(head.next == &entries[1].node);
    try std.testing.expect(head.prev == &entries[7].node);
}
