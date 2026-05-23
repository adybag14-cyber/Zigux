const std = @import("std");
const list_sort = @import("list_sort");

const Entry = struct {
    key: i32,
    ordinal: usize,
    node: list_sort.ListHead = .{},
};

const SortMode = enum { ascending, descending };

fn signedCmp(priv: ?*anyopaque, a: *const list_sort.ListHead, b: *const list_sort.ListHead) i32 {
    const mode: *const SortMode = @ptrCast(@alignCast(priv.?));
    const lhs: *const Entry = @fieldParentPtr("node", a);
    const rhs: *const Entry = @fieldParentPtr("node", b);
    const delta = lhs.key - rhs.key;
    return if (mode.* == .ascending) delta else -delta;
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

fn appendEntries(head: *list_sort.ListHead, entries: []Entry) void {
    for (entries) |*entry| {
        list_sort.listAddTail(&entry.node, head);
    }
}

test "phase1 list_sort signed context roundtrip replay reorders descending and ascending on the same ring" {
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
    appendEntries(&head, &entries);

    var mode = SortMode.descending;
    list_sort.listSort(&mode, &head, signedCmp);
    mode = .ascending;
    list_sort.listSort(&mode, &head, signedCmp);

    var keys: [entries.len]i32 = undefined;
    var ordinals: [entries.len]usize = undefined;
    const count = try collectState(&head, &keys, &ordinals);

    try std.testing.expectEqual(@as(usize, entries.len), count);
    try std.testing.expectEqualSlices(i32, &.{ -3, -3, -1, 0, 5, 7, 7 }, keys[0..count]);
    try std.testing.expectEqualSlices(usize, &.{ 0, 5, 2, 4, 6, 1, 3 }, ordinals[0..count]);
    try std.testing.expect(head.next == &entries[0].node);
    try std.testing.expect(head.prev == &entries[3].node);
}

test "phase1 list_sort signed context roundtrip replay can descend again without losing stable duplicate order" {
    var head: list_sort.ListHead = .{};
    head.init();
    var entries = [_]Entry{
        .{ .key = -4, .ordinal = 0 },
        .{ .key = 3, .ordinal = 1 },
        .{ .key = -4, .ordinal = 2 },
        .{ .key = 9, .ordinal = 3 },
        .{ .key = 1, .ordinal = 4 },
        .{ .key = 9, .ordinal = 5 },
        .{ .key = 3, .ordinal = 6 },
        .{ .key = 0, .ordinal = 7 },
    };
    appendEntries(&head, &entries);

    var mode = SortMode.descending;
    list_sort.listSort(&mode, &head, signedCmp);
    mode = .ascending;
    list_sort.listSort(&mode, &head, signedCmp);
    mode = .descending;
    list_sort.listSort(&mode, &head, signedCmp);

    var keys: [entries.len]i32 = undefined;
    var ordinals: [entries.len]usize = undefined;
    const count = try collectState(&head, &keys, &ordinals);

    try std.testing.expectEqual(@as(usize, entries.len), count);
    try std.testing.expectEqualSlices(i32, &.{ 9, 9, 3, 3, 1, 0, -4, -4 }, keys[0..count]);
    try std.testing.expectEqualSlices(usize, &.{ 3, 5, 1, 6, 4, 7, 0, 2 }, ordinals[0..count]);
    try std.testing.expect(head.next == &entries[3].node);
    try std.testing.expect(head.prev == &entries[2].node);
}
