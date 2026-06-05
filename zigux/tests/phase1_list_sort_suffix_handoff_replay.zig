const std = @import("std");
const list_sort = @import("list_sort");

const ListHead = list_sort.ListHead;

const Entry = struct {
    key: i32,
    ordinal: usize,
    node: ListHead = .{},
};

const SortMode = enum { ascending, descending };

fn compareByKey(priv: ?*anyopaque, a: *const ListHead, b: *const ListHead) i32 {
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

fn compareTies(_: ?*anyopaque, _: *const ListHead, _: *const ListHead) i32 {
    return 0;
}

fn expectTraversal(
    head: *const ListHead,
    expected_keys: []const i32,
    expected_ordinals: []const usize,
) !void {
    var keys: [16]i32 = undefined;
    var ordinals: [16]usize = undefined;
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

test "list sort preserves suffix handoff traversal after staged tail replay" {
    var main: ListHead = .{};
    main.init();
    var suffix: ListHead = .{};
    suffix.init();

    var entries = [_]Entry{
        .{ .key = 9, .ordinal = 0 },
        .{ .key = 1, .ordinal = 1 },
        .{ .key = 7, .ordinal = 2 },
        .{ .key = 3, .ordinal = 3 },
        .{ .key = 8, .ordinal = 4 },
        .{ .key = 2, .ordinal = 5 },
        .{ .key = 6, .ordinal = 6 },
        .{ .key = 4, .ordinal = 7 },
        .{ .key = 5, .ordinal = 8 },
        .{ .key = 0, .ordinal = 9 },
    };

    for (&entries) |*entry| list_sort.listAddTail(&entry.node, &main);

    var mode = SortMode.ascending;
    list_sort.listSort(&mode, &main, compareByKey);
    try expectTraversal(
        &main,
        &.{ 0, 1, 2, 3, 4, 5, 6, 7, 8, 9 },
        &.{ 9, 1, 5, 3, 7, 8, 6, 2, 4, 0 },
    );

    var current = main.next;
    while (current != &main) {
        const next = current.?.next;
        const entry: *Entry = @fieldParentPtr("node", current.?);
        if (entry.key >= 6) {
            list_sort.listDel(&entry.node);
            try std.testing.expect(entry.node.next == null);
            try std.testing.expect(entry.node.prev == null);
            list_sort.listAddTail(&entry.node, &suffix);
        }
        current = next;
    }

    try expectTraversal(&main, &.{ 0, 1, 2, 3, 4, 5 }, &.{ 9, 1, 5, 3, 7, 8 });
    try expectTraversal(&suffix, &.{ 6, 7, 8, 9 }, &.{ 6, 2, 4, 0 });

    mode = .descending;
    list_sort.listSort(&mode, &suffix, compareByKey);
    try expectTraversal(&suffix, &.{ 9, 8, 7, 6 }, &.{ 0, 4, 2, 6 });

    while (!list_sort.listEmpty(&suffix)) {
        const node = suffix.next.?;
        const entry: *Entry = @fieldParentPtr("node", node);
        list_sort.listDel(&entry.node);
        try std.testing.expect(entry.node.next == null);
        try std.testing.expect(entry.node.prev == null);
        list_sort.listAddTail(&entry.node, &main);
    }

    try std.testing.expect(list_sort.listEmpty(&suffix));
    try expectTraversal(
        &main,
        &.{ 0, 1, 2, 3, 4, 5, 9, 8, 7, 6 },
        &.{ 9, 1, 5, 3, 7, 8, 0, 4, 2, 6 },
    );

    list_sort.listSort(null, &main, compareTies);
    try expectTraversal(
        &main,
        &.{ 0, 1, 2, 3, 4, 5, 9, 8, 7, 6 },
        &.{ 9, 1, 5, 3, 7, 8, 0, 4, 2, 6 },
    );
    try std.testing.expect(main.next == &entries[9].node);
    try std.testing.expect(main.prev == &entries[6].node);
}
