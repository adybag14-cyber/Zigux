const std = @import("std");
const list_sort = @import("list_sort");

const ListHead = list_sort.ListHead;

const Entry = struct {
    key: i32,
    ordinal: usize,
    node: ListHead = .{},
};

const SortMode = enum {
    key_asc,
    key_desc,
    ordinal_asc,
    ordinal_desc,
    all_ties,
};

const SortContext = struct {
    mode: SortMode,
};

fn entryFromNode(node: *const ListHead) *const Entry {
    return @fieldParentPtr("node", node);
}

fn compare(priv: ?*anyopaque, a: *const ListHead, b: *const ListHead) i32 {
    const context: *const SortContext = @ptrCast(@alignCast(priv.?));
    const lhs = entryFromNode(a);
    const rhs = entryFromNode(b);

    switch (context.mode) {
        .key_asc => {
            if (lhs.key < rhs.key) return -3;
            if (lhs.key > rhs.key) return 5;
            return 0;
        },
        .key_desc => {
            if (lhs.key > rhs.key) return -7;
            if (lhs.key < rhs.key) return 11;
            return 0;
        },
        .ordinal_asc => {
            if (lhs.ordinal < rhs.ordinal) return -13;
            if (lhs.ordinal > rhs.ordinal) return 17;
            return 0;
        },
        .ordinal_desc => {
            if (lhs.ordinal > rhs.ordinal) return -19;
            if (lhs.ordinal < rhs.ordinal) return 23;
            return 0;
        },
        .all_ties => return 0,
    }
}

fn popFront(head: *ListHead) !*ListHead {
    try std.testing.expect(!list_sort.listEmpty(head));
    const node = head.next.?;
    list_sort.listDel(node);
    try std.testing.expect(node.next == null);
    try std.testing.expect(node.prev == null);
    return node;
}

fn popBack(head: *ListHead) !*ListHead {
    try std.testing.expect(!list_sort.listEmpty(head));
    const node = head.prev.?;
    list_sort.listDel(node);
    try std.testing.expect(node.next == null);
    try std.testing.expect(node.prev == null);
    return node;
}

fn collectOrdinals(head: *const ListHead, out: []usize) !usize {
    var idx: usize = 0;
    var current = head.next.?;
    while (current != head) : (current = current.next.?) {
        const entry = entryFromNode(current);
        out[idx] = entry.ordinal;
        try std.testing.expect(current.next.?.prev == current);
        try std.testing.expect(current.prev.?.next == current);
        idx += 1;
    }
    return idx;
}

test "list sort drains and rebuilds a helix ladder staging path" {
    var entries = [_]Entry{
        .{ .key = 6, .ordinal = 0 },
        .{ .key = 1, .ordinal = 1 },
        .{ .key = 4, .ordinal = 2 },
        .{ .key = 1, .ordinal = 3 },
        .{ .key = 7, .ordinal = 4 },
        .{ .key = 3, .ordinal = 5 },
        .{ .key = 5, .ordinal = 6 },
        .{ .key = 2, .ordinal = 7 },
        .{ .key = 6, .ordinal = 8 },
        .{ .key = 4, .ordinal = 9 },
        .{ .key = 2, .ordinal = 10 },
        .{ .key = 5, .ordinal = 11 },
    };

    var main: ListHead = .{};
    main.init();
    for (&entries) |*entry| {
        list_sort.listAddTail(&entry.node, &main);
    }

    var asc = SortContext{ .mode = .key_asc };
    list_sort.listSort(&asc, &main, compare);

    var ordinals: [entries.len]usize = undefined;
    var seen = try collectOrdinals(&main, &ordinals);
    try std.testing.expectEqualSlices(usize, &.{ 1, 3, 7, 10, 5, 2, 9, 6, 11, 0, 8, 4 }, ordinals[0..seen]);

    var staging = [_]ListHead{.{}} ** 5;
    for (&staging) |*head| head.init();

    var rank: usize = 0;
    while (!list_sort.listEmpty(&main)) : (rank += 1) {
        const node = try popFront(&main);
        list_sort.listAddTail(node, &staging[rank % staging.len]);
    }
    try std.testing.expect(list_sort.listEmpty(&main));

    var contexts = [_]SortContext{
        .{ .mode = .key_desc },
        .{ .mode = .ordinal_asc },
        .{ .mode = .key_asc },
        .{ .mode = .key_desc },
        .{ .mode = .ordinal_desc },
    };
    for (&staging, &contexts) |*head, *context| {
        list_sort.listSort(context, head, compare);
    }

    list_sort.listAddTail(try popFront(&staging[0]), &main);
    list_sort.listAddTail(try popBack(&staging[4]), &main);
    list_sort.listAddTail(try popFront(&staging[1]), &main);
    list_sort.listAddTail(try popFront(&staging[3]), &main);
    list_sort.listAddTail(try popBack(&staging[2]), &main);
    list_sort.listAddTail(try popBack(&staging[0]), &main);
    list_sort.listAddTail(try popFront(&staging[4]), &main);
    list_sort.listAddTail(try popBack(&staging[1]), &main);
    list_sort.listAddTail(try popFront(&staging[2]), &main);
    list_sort.listAddTail(try popBack(&staging[3]), &main);
    list_sort.listAddTail(try popFront(&staging[0]), &main);
    list_sort.listAddTail(try popFront(&staging[1]), &main);

    for (&staging) |*head| {
        try std.testing.expect(list_sort.listEmpty(head));
    }

    seen = try collectOrdinals(&main, &ordinals);
    try std.testing.expectEqualSlices(usize, &.{ 8, 0, 3, 11, 6, 1, 5, 9, 7, 10, 2, 4 }, ordinals[0..seen]);
    try std.testing.expect(main.next == &entries[8].node);
    try std.testing.expect(main.prev == &entries[4].node);

    var ties = SortContext{ .mode = .all_ties };
    list_sort.listSort(&ties, &main, compare);

    seen = try collectOrdinals(&main, &ordinals);
    try std.testing.expectEqualSlices(usize, &.{ 8, 0, 3, 11, 6, 1, 5, 9, 7, 10, 2, 4 }, ordinals[0..seen]);
    try std.testing.expect(main.next == &entries[8].node);
    try std.testing.expect(main.prev == &entries[4].node);
}
