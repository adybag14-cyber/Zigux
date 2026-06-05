const std = @import("std");
const list_sort = @import("list_sort");

const ListHead = list_sort.ListHead;

const Entry = struct {
    key: i32,
    ordinal: usize,
    node: ListHead = .{},
};

const SortMode = enum { ascending, descending, ties };

fn cmp(priv: ?*anyopaque, a: *const ListHead, b: *const ListHead) i32 {
    const mode: *const SortMode = @ptrCast(@alignCast(priv.?));
    const lhs: *const Entry = @fieldParentPtr("node", a);
    const rhs: *const Entry = @fieldParentPtr("node", b);

    if (mode.* == .ties or lhs.key == rhs.key) return 0;
    const ascending = lhs.key < rhs.key;
    return if (mode.* == .ascending)
        (if (ascending) -1 else 1)
    else
        (if (ascending) 1 else -1);
}

fn expectTraversal(head: *const ListHead, expected_ordinals: []const usize, expected_keys: []const i32) !void {
    var ordinals: [16]usize = undefined;
    var keys: [16]i32 = undefined;
    var count: usize = 0;

    var current = head.next;
    while (current != head) : (current = current.?.next) {
        const entry: *const Entry = @fieldParentPtr("node", current.?);
        ordinals[count] = entry.ordinal;
        keys[count] = entry.key;
        try std.testing.expect(current.?.next.?.prev == current.?);
        try std.testing.expect(current.?.prev.?.next == current.?);
        count += 1;
    }

    try std.testing.expectEqualSlices(usize, expected_ordinals, ordinals[0..count]);
    try std.testing.expectEqualSlices(i32, expected_keys, keys[0..count]);
}

fn expectReverseTraversal(head: *const ListHead, expected_ordinals: []const usize) !void {
    var ordinals: [16]usize = undefined;
    var count: usize = 0;

    var current = head.prev;
    while (current != head) : (current = current.?.prev) {
        const entry: *const Entry = @fieldParentPtr("node", current.?);
        ordinals[count] = entry.ordinal;
        count += 1;
    }

    try std.testing.expectEqualSlices(usize, expected_ordinals, ordinals[0..count]);
}

test "list sort preserves prefix evacuation and head reattachment lifecycle" {
    var head: ListHead = .{};
    var prefix: ListHead = .{};
    head.init();
    prefix.init();

    var entries = [_]Entry{
        .{ .key = 5, .ordinal = 0 },
        .{ .key = 1, .ordinal = 1 },
        .{ .key = 4, .ordinal = 2 },
        .{ .key = 1, .ordinal = 3 },
        .{ .key = 3, .ordinal = 4 },
        .{ .key = 2, .ordinal = 5 },
        .{ .key = 4, .ordinal = 6 },
        .{ .key = 0, .ordinal = 7 },
        .{ .key = 3, .ordinal = 8 },
    };

    for (&entries) |*entry| list_sort.listAddTail(&entry.node, &head);

    var mode = SortMode.ascending;
    list_sort.listSort(&mode, &head, cmp);
    try expectTraversal(&head, &.{ 7, 1, 3, 5, 4, 8, 2, 6, 0 }, &.{ 0, 1, 1, 2, 3, 3, 4, 4, 5 });

    var evacuated: usize = 0;
    while (evacuated < 4) : (evacuated += 1) {
        const node = head.next.?;
        list_sort.listDel(node);
        try std.testing.expect(node.next == null);
        try std.testing.expect(node.prev == null);
        list_sort.listAddTail(node, &prefix);
    }

    try expectTraversal(&prefix, &.{ 7, 1, 3, 5 }, &.{ 0, 1, 1, 2 });
    try expectTraversal(&head, &.{ 4, 8, 2, 6, 0 }, &.{ 3, 3, 4, 4, 5 });

    mode = .descending;
    list_sort.listSort(&mode, &prefix, cmp);
    try expectTraversal(&prefix, &.{ 5, 1, 3, 7 }, &.{ 2, 1, 1, 0 });

    while (!list_sort.listEmpty(&prefix)) {
        const node = prefix.prev.?;
        list_sort.listDel(node);
        try std.testing.expect(node.next == null);
        try std.testing.expect(node.prev == null);
        list_sort.listAdd(node, &head);
    }

    try std.testing.expect(list_sort.listEmpty(&prefix));
    try expectTraversal(&head, &.{ 5, 1, 3, 7, 4, 8, 2, 6, 0 }, &.{ 2, 1, 1, 0, 3, 3, 4, 4, 5 });
    try expectReverseTraversal(&head, &.{ 0, 6, 2, 8, 4, 7, 3, 1, 5 });

    mode = .ties;
    list_sort.listSort(&mode, &head, cmp);
    try expectTraversal(&head, &.{ 5, 1, 3, 7, 4, 8, 2, 6, 0 }, &.{ 2, 1, 1, 0, 3, 3, 4, 4, 5 });
    try expectReverseTraversal(&head, &.{ 0, 6, 2, 8, 4, 7, 3, 1, 5 });
    try std.testing.expect(head.next == &entries[5].node);
    try std.testing.expect(head.prev == &entries[0].node);
}
