const std = @import("std");
const list_sort = @import("list_sort");

const Entry = struct {
    key: i32,
    ordinal: usize,
    node: list_sort.ListHead = .{},
};

const SortMode = enum { ascending, descending };

fn compareByMode(priv: ?*anyopaque, a: *const list_sort.ListHead, b: *const list_sort.ListHead) i32 {
    const mode: *const SortMode = @ptrCast(@alignCast(priv.?));
    const lhs: *const Entry = @fieldParentPtr("node", a);
    const rhs: *const Entry = @fieldParentPtr("node", b);

    if (lhs.key == rhs.key) return 0;
    const ascending = lhs.key < rhs.key;
    return if ((mode.* == .ascending) == ascending) -5 else 7;
}

fn expectForwardOrder(head: *const list_sort.ListHead, expected_keys: []const i32, expected_ordinals: []const usize) !void {
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

fn expectBackwardOrdinals(head: *const list_sort.ListHead, expected_ordinals: []const usize) !void {
    var ordinals: [10]usize = undefined;
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

test "list sort preserves links after transferring nodes between heads" {
    var source: list_sort.ListHead = .{};
    source.init();
    var destination: list_sort.ListHead = .{};
    destination.init();

    var entries = [_]Entry{
        .{ .key = 6, .ordinal = 0 },
        .{ .key = 1, .ordinal = 1 },
        .{ .key = 4, .ordinal = 2 },
        .{ .key = 1, .ordinal = 3 },
        .{ .key = 5, .ordinal = 4 },
        .{ .key = 3, .ordinal = 5 },
        .{ .key = 6, .ordinal = 6 },
        .{ .key = 2, .ordinal = 7 },
        .{ .key = 5, .ordinal = 8 },
        .{ .key = 0, .ordinal = 9 },
    };

    for (&entries) |*entry| list_sort.listAddTail(&entry.node, &source);

    var mode = SortMode.ascending;
    list_sort.listSort(&mode, &source, compareByMode);

    try expectForwardOrder(&source, &.{ 0, 1, 1, 2, 3, 4, 5, 5, 6, 6 }, &.{ 9, 1, 3, 7, 5, 2, 4, 8, 0, 6 });
    try std.testing.expect(list_sort.listEmpty(&destination));

    var current = source.next;
    while (current != &source) {
        const next = current.?.next;
        const entry: *Entry = @fieldParentPtr("node", current.?);
        if (@mod(entry.key, 2) != 0) {
            list_sort.listDel(&entry.node);
            try std.testing.expect(entry.node.next == null);
            try std.testing.expect(entry.node.prev == null);
            list_sort.listAddTail(&entry.node, &destination);
        }
        current = next;
    }

    try expectForwardOrder(&source, &.{ 0, 2, 4, 6, 6 }, &.{ 9, 7, 2, 0, 6 });
    try expectBackwardOrdinals(&source, &.{ 6, 0, 2, 7, 9 });
    try expectForwardOrder(&destination, &.{ 1, 1, 3, 5, 5 }, &.{ 1, 3, 5, 4, 8 });
    try expectBackwardOrdinals(&destination, &.{ 8, 4, 5, 3, 1 });

    mode = .descending;
    list_sort.listSort(&mode, &destination, compareByMode);
    list_sort.listSort(&mode, &source, compareByMode);

    try expectForwardOrder(&destination, &.{ 5, 5, 3, 1, 1 }, &.{ 4, 8, 5, 1, 3 });
    try expectBackwardOrdinals(&destination, &.{ 3, 1, 5, 8, 4 });
    try std.testing.expect(destination.next == &entries[4].node);
    try std.testing.expect(destination.prev == &entries[3].node);

    try expectForwardOrder(&source, &.{ 6, 6, 4, 2, 0 }, &.{ 0, 6, 2, 7, 9 });
    try expectBackwardOrdinals(&source, &.{ 9, 7, 2, 6, 0 });
    try std.testing.expect(source.next == &entries[0].node);
    try std.testing.expect(source.prev == &entries[9].node);
}
