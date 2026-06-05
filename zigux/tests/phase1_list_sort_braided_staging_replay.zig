const std = @import("std");
const list_sort = @import("list_sort");

const ListHead = list_sort.ListHead;

const Entry = struct {
    key: i32,
    ordinal: usize,
    node: ListHead = .{},
};

const SortMode = enum {
    ascending,
    descending,
};

fn keyCmp(priv: ?*anyopaque, a: *const ListHead, b: *const ListHead) i32 {
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

fn allTiesCmp(_: ?*anyopaque, _: *const ListHead, _: *const ListHead) i32 {
    return 0;
}

fn detachFront(from: *ListHead) ?*ListHead {
    if (list_sort.listEmpty(from)) return null;
    const node = from.next.?;
    list_sort.listDel(node);
    std.testing.expect(node.next == null) catch unreachable;
    std.testing.expect(node.prev == null) catch unreachable;
    return node;
}

fn appendFront(from: *ListHead, to: *ListHead) bool {
    const node = detachFront(from) orelse return false;
    list_sort.listAddTail(node, to);
    return true;
}

fn collectOrdinals(head: *const ListHead, out: []usize) !usize {
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

test "list sort preserves braided staging traversal through all-ties pass" {
    var main: ListHead = .{};
    main.init();
    var stage = [_]ListHead{ .{}, .{}, .{} };
    for (&stage) |*head| head.init();

    var entries = [_]Entry{
        .{ .key = 5, .ordinal = 0 },
        .{ .key = 1, .ordinal = 1 },
        .{ .key = 4, .ordinal = 2 },
        .{ .key = 1, .ordinal = 3 },
        .{ .key = 3, .ordinal = 4 },
        .{ .key = 6, .ordinal = 5 },
        .{ .key = 2, .ordinal = 6 },
        .{ .key = 5, .ordinal = 7 },
        .{ .key = 2, .ordinal = 8 },
        .{ .key = 4, .ordinal = 9 },
        .{ .key = 3, .ordinal = 10 },
        .{ .key = 6, .ordinal = 11 },
    };

    for (&entries) |*entry| list_sort.listAddTail(&entry.node, &main);

    var mode = SortMode.ascending;
    list_sort.listSort(&mode, &main, keyCmp);

    var sorted_ordinals: [entries.len]usize = undefined;
    const sorted_count = try collectOrdinals(&main, &sorted_ordinals);
    try std.testing.expectEqualSlices(
        usize,
        &.{ 1, 3, 6, 8, 4, 10, 2, 9, 0, 7, 5, 11 },
        sorted_ordinals[0..sorted_count],
    );

    var drain_index: usize = 0;
    while (detachFront(&main)) |node| {
        list_sort.listAddTail(node, &stage[drain_index % stage.len]);
        drain_index += 1;
    }
    try std.testing.expect(list_sort.listEmpty(&main));

    mode = .descending;
    list_sort.listSort(&mode, &stage[0], keyCmp);
    mode = .ascending;
    list_sort.listSort(&mode, &stage[1], keyCmp);
    mode = .descending;
    list_sort.listSort(&mode, &stage[2], keyCmp);

    var staged_ordinals: [4]usize = undefined;
    try std.testing.expectEqualSlices(
        usize,
        &.{ 7, 2, 8, 1 },
        staged_ordinals[0..try collectOrdinals(&stage[0], &staged_ordinals)],
    );
    try std.testing.expectEqualSlices(
        usize,
        &.{ 3, 4, 9, 5 },
        staged_ordinals[0..try collectOrdinals(&stage[1], &staged_ordinals)],
    );
    try std.testing.expectEqualSlices(
        usize,
        &.{ 11, 0, 10, 6 },
        staged_ordinals[0..try collectOrdinals(&stage[2], &staged_ordinals)],
    );

    while (true) {
        var moved = false;
        moved = appendFront(&stage[2], &main) or moved;
        moved = appendFront(&stage[0], &main) or moved;
        moved = appendFront(&stage[1], &main) or moved;
        if (!moved) break;
    }

    for (&stage) |*head| try std.testing.expect(list_sort.listEmpty(head));

    var braided_ordinals: [entries.len]usize = undefined;
    const braided_count = try collectOrdinals(&main, &braided_ordinals);
    try std.testing.expectEqualSlices(
        usize,
        &.{ 11, 7, 3, 0, 2, 4, 10, 8, 9, 6, 1, 5 },
        braided_ordinals[0..braided_count],
    );

    list_sort.listSort(null, &main, allTiesCmp);

    var final_ordinals: [entries.len]usize = undefined;
    const final_count = try collectOrdinals(&main, &final_ordinals);
    try std.testing.expectEqualSlices(
        usize,
        &.{ 11, 7, 3, 0, 2, 4, 10, 8, 9, 6, 1, 5 },
        final_ordinals[0..final_count],
    );
    try std.testing.expect(main.next == &entries[11].node);
    try std.testing.expect(main.prev == &entries[5].node);
    try std.testing.expect(entries[11].node.prev == &main);
    try std.testing.expect(entries[5].node.next == &main);
}
