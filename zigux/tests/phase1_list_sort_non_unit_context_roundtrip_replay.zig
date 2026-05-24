const std = @import("std");
const list_sort = @import("list_sort");

const Entry = struct {
    key: i32,
    ordinal: usize,
    node: list_sort.ListHead = .{},
};

const SortMode = enum { ascending, descending };

fn nonUnitCmp(priv: ?*anyopaque, a: *const list_sort.ListHead, b: *const list_sort.ListHead) i32 {
    const mode: *const SortMode = @ptrCast(@alignCast(priv.?));
    const lhs: *const Entry = @fieldParentPtr("node", a);
    const rhs: *const Entry = @fieldParentPtr("node", b);

    if (lhs.key == rhs.key) return 0;
    const ascending = lhs.key < rhs.key;
    return if (mode.* == .ascending)
        (if (ascending) -11 else 13)
    else
        (if (ascending) 13 else -11);
}

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

test "phase1 list_sort non-unit context roundtrip replay reorders descending, ascending, then descending on the same ring" {
    var head: list_sort.ListHead = .{};
    head.init();
    var entries = [_]Entry{
        .{ .key = 2, .ordinal = 0 },
        .{ .key = 5, .ordinal = 1 },
        .{ .key = 1, .ordinal = 2 },
        .{ .key = 5, .ordinal = 3 },
        .{ .key = 4, .ordinal = 4 },
        .{ .key = 1, .ordinal = 5 },
    };
    appendEntries(&head, &entries);

    var mode = SortMode.descending;
    list_sort.listSort(&mode, &head, nonUnitCmp);
    mode = .ascending;
    list_sort.listSort(&mode, &head, nonUnitCmp);
    mode = .descending;
    list_sort.listSort(&mode, &head, nonUnitCmp);

    var keys: [entries.len]i32 = undefined;
    var ordinals: [entries.len]usize = undefined;
    const count = try collectState(&head, &keys, &ordinals);

    try std.testing.expectEqual(@as(usize, entries.len), count);
    try std.testing.expectEqualSlices(i32, &.{ 5, 5, 4, 2, 1, 1 }, keys[0..count]);
    try std.testing.expectEqualSlices(usize, &.{ 1, 3, 4, 0, 2, 5 }, ordinals[0..count]);
    try std.testing.expect(head.next == &entries[1].node);
    try std.testing.expect(head.prev == &entries[5].node);
}

test "phase1 list_sort non-unit context roundtrip replay can finish ascending without losing duplicate stability" {
    var head: list_sort.ListHead = .{};
    head.init();
    var entries = [_]Entry{
        .{ .key = 3, .ordinal = 0 },
        .{ .key = 1, .ordinal = 1 },
        .{ .key = 2, .ordinal = 2 },
        .{ .key = 1, .ordinal = 3 },
        .{ .key = 4, .ordinal = 4 },
        .{ .key = 2, .ordinal = 5 },
    };
    appendEntries(&head, &entries);

    var mode = SortMode.ascending;
    list_sort.listSort(&mode, &head, nonUnitCmp);
    mode = .descending;
    list_sort.listSort(&mode, &head, nonUnitCmp);
    mode = .ascending;
    list_sort.listSort(&mode, &head, nonUnitCmp);

    var keys: [entries.len]i32 = undefined;
    var ordinals: [entries.len]usize = undefined;
    const count = try collectState(&head, &keys, &ordinals);

    try std.testing.expectEqual(@as(usize, entries.len), count);
    try std.testing.expectEqualSlices(i32, &.{ 1, 1, 2, 2, 3, 4 }, keys[0..count]);
    try std.testing.expectEqualSlices(usize, &.{ 1, 3, 2, 5, 0, 4 }, ordinals[0..count]);
    try std.testing.expect(head.next == &entries[1].node);
    try std.testing.expect(head.prev == &entries[4].node);
}
