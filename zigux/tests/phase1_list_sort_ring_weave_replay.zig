const std = @import("std");
const list_sort = @import("list_sort");

const Entry = struct {
    key: i32,
    ordinal: usize,
    node: list_sort.ListHead = .{},
};

const SortMode = enum { ascending, descending };

fn cmpByKey(priv: ?*anyopaque, a: *const list_sort.ListHead, b: *const list_sort.ListHead) i32 {
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

fn cmpAllTies(_: ?*anyopaque, _: *const list_sort.ListHead, _: *const list_sort.ListHead) i32 {
    return 0;
}

fn collectOrdinals(head: *const list_sort.ListHead, out: []usize) !usize {
    var idx: usize = 0;
    var current = head.next;
    while (current != head) : (current = current.?.next) {
        const entry: *const Entry = @fieldParentPtr("node", current.?);
        out[idx] = entry.ordinal;
        try std.testing.expect(current.?.next.?.prev == current.?);
        try std.testing.expect(current.?.prev.?.next == current.?);
        idx += 1;
    }
    return idx;
}

fn expectOrder(head: *const list_sort.ListHead, expected: []const usize) !void {
    var ordinals: [16]usize = undefined;
    const count = try collectOrdinals(head, &ordinals);
    try std.testing.expectEqualSlices(usize, expected, ordinals[0..count]);
}

fn popFront(head: *list_sort.ListHead) ?*list_sort.ListHead {
    if (list_sort.listEmpty(head)) return null;
    const node = head.next.?;
    list_sort.listDel(node);
    return node;
}

test "list sort preserves ring weave staging lifecycle" {
    var main: list_sort.ListHead = .{};
    main.init();

    var rings = [_]list_sort.ListHead{ .{}, .{} };
    for (&rings) |*ring| ring.init();

    var entries = [_]Entry{
        .{ .key = 31, .ordinal = 0 },
        .{ .key = 4, .ordinal = 1 },
        .{ .key = 22, .ordinal = 2 },
        .{ .key = 9, .ordinal = 3 },
        .{ .key = 27, .ordinal = 4 },
        .{ .key = 14, .ordinal = 5 },
        .{ .key = 19, .ordinal = 6 },
        .{ .key = 2, .ordinal = 7 },
        .{ .key = 35, .ordinal = 8 },
        .{ .key = 11, .ordinal = 9 },
    };

    for (&entries) |*entry| list_sort.listAddTail(&entry.node, &main);

    var mode = SortMode.ascending;
    list_sort.listSort(&mode, &main, cmpByKey);
    try expectOrder(&main, &.{ 7, 1, 3, 9, 5, 6, 2, 4, 0, 8 });
    try std.testing.expect(main.next == &entries[7].node);
    try std.testing.expect(main.prev == &entries[8].node);

    var ring_index: usize = 0;
    while (popFront(&main)) |node| : (ring_index += 1) {
        try std.testing.expect(node.next == null);
        try std.testing.expect(node.prev == null);
        list_sort.listAddTail(node, &rings[ring_index % rings.len]);
    }
    try std.testing.expect(list_sort.listEmpty(&main));
    try expectOrder(&rings[0], &.{ 7, 3, 5, 2, 0 });
    try expectOrder(&rings[1], &.{ 1, 9, 6, 4, 8 });

    mode = .descending;
    list_sort.listSort(&mode, &rings[0], cmpByKey);
    try expectOrder(&rings[0], &.{ 0, 2, 5, 3, 7 });

    mode = .ascending;
    list_sort.listSort(&mode, &rings[1], cmpByKey);
    try expectOrder(&rings[1], &.{ 1, 9, 6, 4, 8 });

    var moved = true;
    while (moved) {
        moved = false;
        for (&rings) |*ring| {
            if (popFront(ring)) |node| {
                try std.testing.expect(node.next == null);
                try std.testing.expect(node.prev == null);
                list_sort.listAddTail(node, &main);
                moved = true;
            }
        }
    }
    for (&rings) |*ring| try std.testing.expect(list_sort.listEmpty(ring));

    try expectOrder(&main, &.{ 0, 1, 2, 9, 5, 6, 3, 4, 7, 8 });
    try std.testing.expect(main.next == &entries[0].node);
    try std.testing.expect(main.prev == &entries[8].node);

    list_sort.listSort(null, &main, cmpAllTies);
    try expectOrder(&main, &.{ 0, 1, 2, 9, 5, 6, 3, 4, 7, 8 });
    try std.testing.expect(main.next == &entries[0].node);
    try std.testing.expect(main.prev == &entries[8].node);
}
