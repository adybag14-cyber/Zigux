const std = @import("std");
const list_sort = @import("../../tools/lib/list_sort.zig");

const Entry = struct {
    key: i32,
    ordinal: usize,
    node: list_sort.ListHead = .{},
};

fn appendEntries(head: *list_sort.ListHead, entries: []Entry) void {
    for (entries) |*entry| {
        head.addTail(&entry.node);
    }
}

fn expectOrder(head: *list_sort.ListHead, expected_keys: []const i32, expected_ordinals: []const usize) !void {
    try std.testing.expectEqual(expected_keys.len, expected_ordinals.len);

    var node = head.next;
    var index: usize = 0;
    while (node != head) : (node = node.next) {
        try std.testing.expect(index < expected_keys.len);

        const entry = list_sort.listEntry(Entry, node, "node");
        try std.testing.expectEqual(expected_keys[index], entry.key);
        try std.testing.expectEqual(expected_ordinals[index], entry.ordinal);
        index += 1;
    }

    try std.testing.expectEqual(expected_keys.len, index);
}

test "phase1 list_sort tied context replay preserves current order when a later pass ties everything" {
    var head = list_sort.LIST_HEAD_INIT(&head);
    var entries = [_]Entry{
        .{ .key = 4, .ordinal = 0 },
        .{ .key = 1, .ordinal = 1 },
        .{ .key = 4, .ordinal = 2 },
        .{ .key = -2, .ordinal = 3 },
        .{ .key = 1, .ordinal = 4 },
        .{ .key = 7, .ordinal = 5 },
        .{ .key = -2, .ordinal = 6 },
    };
    appendEntries(&head, entries[0..]);

    const DescendingContext = struct {
        fn cmp(_: *anyopaque, lhs: *const list_sort.ListHead, rhs: *const list_sort.ListHead) callconv(.c) c_int {
            const left = list_sort.listEntry(Entry, lhs, "node");
            const right = list_sort.listEntry(Entry, rhs, "node");
            return @intCast(right.key - left.key);
        }
    };
    list_sort.listSort(null, &head, DescendingContext.cmp);

    const TieOnlyContext = struct {
        fn cmp(_: *anyopaque, _: *const list_sort.ListHead, _: *const list_sort.ListHead) callconv(.c) c_int {
            return 0;
        }
    };
    list_sort.listSort(null, &head, TieOnlyContext.cmp);

    try expectOrder(&head, &.{ 7, 4, 4, 1, 1, -2, -2 }, &.{ 5, 0, 2, 1, 4, 3, 6 });
}

test "phase1 list_sort tied context replay keeps insertion order after delete readd and tie-only sort" {
    var head = list_sort.LIST_HEAD_INIT(&head);
    var entries = [_]Entry{
        .{ .key = 9, .ordinal = 0 },
        .{ .key = 3, .ordinal = 1 },
        .{ .key = 9, .ordinal = 2 },
        .{ .key = 1, .ordinal = 3 },
    };
    appendEntries(&head, entries[0..]);

    entries[1].node.del();
    head.addTail(&entries[1].node);

    const TieOnlyContext = struct {
        fn cmp(_: *anyopaque, _: *const list_sort.ListHead, _: *const list_sort.ListHead) callconv(.c) c_int {
            return 0;
        }
    };
    list_sort.listSort(null, &head, TieOnlyContext.cmp);

    try expectOrder(&head, &.{ 9, 9, 1, 3 }, &.{ 0, 2, 3, 1 });
}

test "phase1 list_sort tied context replay leaves empty and singleton lists circular" {
    var empty = list_sort.LIST_HEAD_INIT(&empty);

    const TieOnlyContext = struct {
        fn cmp(_: *anyopaque, _: *const list_sort.ListHead, _: *const list_sort.ListHead) callconv(.c) c_int {
            return 0;
        }
    };
    list_sort.listSort(null, &empty, TieOnlyContext.cmp);

    try std.testing.expectEqual(&empty, empty.next);
    try std.testing.expectEqual(&empty, empty.prev);

    var singleton_head = list_sort.LIST_HEAD_INIT(&singleton_head);
    var entry = Entry{ .key = 42, .ordinal = 0 };
    singleton_head.addTail(&entry.node);
    list_sort.listSort(null, &singleton_head, TieOnlyContext.cmp);

    try std.testing.expectEqual(&entry.node, singleton_head.next);
    try std.testing.expectEqual(&entry.node, singleton_head.prev);
    try std.testing.expectEqual(&singleton_head, entry.node.next);
    try std.testing.expectEqual(&singleton_head, entry.node.prev);
}
