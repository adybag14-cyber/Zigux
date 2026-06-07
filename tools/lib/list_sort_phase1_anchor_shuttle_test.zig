const std = @import("std");
const list_sort = @import("list_sort");

const Entry = struct {
    key: i32,
    ordinal: usize,
    node: list_sort.ListHead = .{},
};

const SortMode = enum { ascending, descending, all_ties };

fn cmpByKey(priv: ?*anyopaque, a: *const list_sort.ListHead, b: *const list_sort.ListHead) i32 {
    const mode: *const SortMode = @ptrCast(@alignCast(priv.?));
    const lhs: *const Entry = @fieldParentPtr("node", a);
    const rhs: *const Entry = @fieldParentPtr("node", b);

    if (mode.* == .all_ties or lhs.key == rhs.key) return 0;
    const ascending = lhs.key < rhs.key;
    return if (mode.* == .ascending)
        (if (ascending) -5 else 7)
    else
        (if (ascending) 7 else -5);
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

fn popFront(head: *list_sort.ListHead) ?*list_sort.ListHead {
    if (list_sort.listEmpty(head)) return null;
    const node = head.next.?;
    list_sort.listDel(node);
    return node;
}

fn popBack(head: *list_sort.ListHead) ?*list_sort.ListHead {
    if (list_sort.listEmpty(head)) return null;
    const node = head.prev.?;
    list_sort.listDel(node);
    return node;
}

test "list_sort anchor shuttle rebuild preserves staged traversal under all ties" {
    var head: list_sort.ListHead = .{};
    var anchors: list_sort.ListHead = .{};
    var shuttle: list_sort.ListHead = .{};
    head.init();
    anchors.init();
    shuttle.init();

    var entries = [_]Entry{
        .{ .key = 8, .ordinal = 0 },
        .{ .key = 1, .ordinal = 1 },
        .{ .key = 6, .ordinal = 2 },
        .{ .key = 3, .ordinal = 3 },
        .{ .key = 6, .ordinal = 4 },
        .{ .key = 2, .ordinal = 5 },
        .{ .key = 9, .ordinal = 6 },
        .{ .key = 3, .ordinal = 7 },
        .{ .key = 5, .ordinal = 8 },
    };
    for (&entries) |*entry| list_sort.listAddTail(&entry.node, &head);

    var mode = SortMode.ascending;
    list_sort.listSort(&mode, &head, cmpByKey);

    var ordinals: [9]usize = undefined;
    var count = try collectOrdinals(&head, &ordinals);
    try std.testing.expectEqualSlices(usize, &.{ 1, 5, 3, 7, 8, 2, 4, 0, 6 }, ordinals[0..count]);

    var rank: usize = 0;
    while (popFront(&head)) |node| : (rank += 1) {
        try std.testing.expect(node.next == null);
        try std.testing.expect(node.prev == null);
        if (rank == 0 or rank == 4 or rank == 8) {
            list_sort.listAddTail(node, &anchors);
        } else if ((rank & 1) == 0) {
            list_sort.listAdd(node, &shuttle);
        } else {
            list_sort.listAddTail(node, &shuttle);
        }
    }
    try std.testing.expect(list_sort.listEmpty(&head));

    count = try collectOrdinals(&anchors, &ordinals);
    try std.testing.expectEqualSlices(usize, &.{ 1, 8, 6 }, ordinals[0..count]);
    count = try collectOrdinals(&shuttle, &ordinals);
    try std.testing.expectEqualSlices(usize, &.{ 4, 3, 5, 7, 2, 0 }, ordinals[0..count]);

    mode = .descending;
    list_sort.listSort(&mode, &anchors, cmpByKey);
    mode = .ascending;
    list_sort.listSort(&mode, &shuttle, cmpByKey);

    count = try collectOrdinals(&anchors, &ordinals);
    try std.testing.expectEqualSlices(usize, &.{ 6, 8, 1 }, ordinals[0..count]);
    count = try collectOrdinals(&shuttle, &ordinals);
    try std.testing.expectEqualSlices(usize, &.{ 5, 3, 7, 4, 2, 0 }, ordinals[0..count]);

    while (!list_sort.listEmpty(&anchors) or !list_sort.listEmpty(&shuttle)) {
        if (popFront(&anchors)) |node| {
            try std.testing.expect(node.next == null);
            try std.testing.expect(node.prev == null);
            list_sort.listAddTail(node, &head);
        }
        if (popBack(&shuttle)) |node| {
            try std.testing.expect(node.next == null);
            try std.testing.expect(node.prev == null);
            list_sort.listAddTail(node, &head);
        }
    }
    try std.testing.expect(list_sort.listEmpty(&anchors));
    try std.testing.expect(list_sort.listEmpty(&shuttle));

    count = try collectOrdinals(&head, &ordinals);
    try std.testing.expectEqualSlices(usize, &.{ 6, 0, 8, 2, 1, 4, 7, 3, 5 }, ordinals[0..count]);
    try std.testing.expect(head.next == &entries[6].node);
    try std.testing.expect(head.prev == &entries[5].node);

    mode = .all_ties;
    list_sort.listSort(&mode, &head, cmpByKey);

    count = try collectOrdinals(&head, &ordinals);
    try std.testing.expectEqualSlices(usize, &.{ 6, 0, 8, 2, 1, 4, 7, 3, 5 }, ordinals[0..count]);
    try std.testing.expect(head.next == &entries[6].node);
    try std.testing.expect(head.prev == &entries[5].node);
}
