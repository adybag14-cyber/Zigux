const std = @import("std");
const list_sort = @import("list_sort");

const ListHead = list_sort.ListHead;

const Entry = struct {
    key: i32,
    ordinal: usize,
    node: ListHead = .{},
};

const SortMode = enum {
    key_ascending,
    key_descending,
    ordinal_ascending,
    ordinal_descending,
    parity_bucket,
    all_ties,
};

fn compare(priv: ?*anyopaque, a: *const ListHead, b: *const ListHead) i32 {
    const mode: *const SortMode = @ptrCast(@alignCast(priv.?));
    const lhs: *const Entry = @fieldParentPtr("node", a);
    const rhs: *const Entry = @fieldParentPtr("node", b);

    switch (mode.*) {
        .key_ascending => {
            if (lhs.key < rhs.key) return -3;
            if (lhs.key > rhs.key) return 5;
            return 0;
        },
        .key_descending => {
            if (lhs.key > rhs.key) return -7;
            if (lhs.key < rhs.key) return 11;
            return 0;
        },
        .ordinal_ascending => {
            if (lhs.ordinal < rhs.ordinal) return -13;
            if (lhs.ordinal > rhs.ordinal) return 17;
            return 0;
        },
        .ordinal_descending => {
            if (lhs.ordinal > rhs.ordinal) return -19;
            if (lhs.ordinal < rhs.ordinal) return 23;
            return 0;
        },
        .parity_bucket => {
            const lhs_even = @mod(lhs.key, 2) == 0;
            const rhs_even = @mod(rhs.key, 2) == 0;
            if (lhs_even == rhs_even) return 0;
            return if (lhs_even) -29 else 31;
        },
        .all_ties => return 0,
    }
}

fn popFront(head: *ListHead) ?*ListHead {
    if (list_sort.listEmpty(head)) return null;
    const node = head.next.?;
    list_sort.listDel(node);
    return node;
}

fn popBack(head: *ListHead) ?*ListHead {
    if (list_sort.listEmpty(head)) return null;
    const node = head.prev.?;
    list_sort.listDel(node);
    return node;
}

fn collectOrdinals(head: *ListHead, out: []usize) !usize {
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

fn expectOrdinals(head: *ListHead, expected: []const usize) !void {
    var ordinals: [18]usize = undefined;
    const count = try collectOrdinals(head, &ordinals);
    try std.testing.expectEqualSlices(usize, expected, ordinals[0..count]);
}

fn expectDetached(node: *ListHead) !void {
    try std.testing.expect(node.next == null);
    try std.testing.expect(node.prev == null);
}

test "list sort comb lattice stages independent sorted teeth and preserves all-ties rebuild" {
    var entries = [_]Entry{
        .{ .key = 8, .ordinal = 0 },
        .{ .key = 3, .ordinal = 1 },
        .{ .key = 6, .ordinal = 2 },
        .{ .key = 1, .ordinal = 3 },
        .{ .key = 9, .ordinal = 4 },
        .{ .key = 4, .ordinal = 5 },
        .{ .key = 7, .ordinal = 6 },
        .{ .key = 2, .ordinal = 7 },
        .{ .key = 5, .ordinal = 8 },
        .{ .key = 0, .ordinal = 9 },
        .{ .key = 3, .ordinal = 10 },
        .{ .key = 8, .ordinal = 11 },
        .{ .key = 1, .ordinal = 12 },
        .{ .key = 6, .ordinal = 13 },
        .{ .key = 4, .ordinal = 14 },
        .{ .key = 7, .ordinal = 15 },
        .{ .key = 2, .ordinal = 16 },
        .{ .key = 5, .ordinal = 17 },
    };

    var main: ListHead = .{};
    main.init();
    for (&entries) |*entry| list_sort.listAddTail(&entry.node, &main);

    var mode = SortMode.key_ascending;
    list_sort.listSort(&mode, &main, compare);
    try expectOrdinals(&main, &.{ 9, 3, 12, 7, 16, 1, 10, 5, 14, 8, 17, 2, 13, 6, 15, 0, 11, 4 });

    var spine: ListHead = .{};
    var left_teeth: ListHead = .{};
    var right_teeth: ListHead = .{};
    var bridge: ListHead = .{};
    spine.init();
    left_teeth.init();
    right_teeth.init();
    bridge.init();

    const sorted_ordinals = [_]usize{ 9, 3, 12, 7, 16, 1, 10, 5, 14, 8, 17, 2, 13, 6, 15, 0, 11, 4 };
    const buckets = [_]*ListHead{ &spine, &left_teeth, &right_teeth, &bridge };
    for (sorted_ordinals, 0..) |ordinal, idx| {
        const node = popFront(&main).?;
        try expectDetached(node);
        try std.testing.expect(node == &entries[ordinal].node);
        list_sort.listAddTail(node, buckets[idx % buckets.len]);
    }
    try std.testing.expect(list_sort.listEmpty(&main));

    mode = .ordinal_descending;
    list_sort.listSort(&mode, &spine, compare);
    mode = .key_descending;
    list_sort.listSort(&mode, &left_teeth, compare);
    mode = .ordinal_ascending;
    list_sort.listSort(&mode, &right_teeth, compare);
    mode = .parity_bucket;
    list_sort.listSort(&mode, &bridge, compare);

    try expectOrdinals(&spine, &.{ 16, 14, 13, 11, 9 });
    try expectOrdinals(&left_teeth, &.{ 4, 6, 8, 1, 3 });
    try expectOrdinals(&right_teeth, &.{ 10, 12, 15, 17 });
    try expectOrdinals(&bridge, &.{ 7, 5, 2, 0 });

    while (true) {
        if (popFront(&spine)) |node| {
            try expectDetached(node);
            list_sort.listAddTail(node, &main);
        }
        if (popBack(&left_teeth)) |node| {
            try expectDetached(node);
            list_sort.listAddTail(node, &main);
        }
        if (popFront(&right_teeth)) |node| {
            try expectDetached(node);
            list_sort.listAddTail(node, &main);
        }
        if (popBack(&bridge)) |node| {
            try expectDetached(node);
            list_sort.listAddTail(node, &main);
        }
        if (list_sort.listEmpty(&spine) and
            list_sort.listEmpty(&left_teeth) and
            list_sort.listEmpty(&right_teeth) and
            list_sort.listEmpty(&bridge))
        {
            break;
        }
    }

    const comb_ordinals = [_]usize{ 16, 3, 10, 0, 14, 1, 12, 2, 13, 8, 15, 5, 11, 6, 17, 7, 9, 4 };
    try expectOrdinals(&main, &comb_ordinals);

    mode = .all_ties;
    list_sort.listSort(&mode, &main, compare);
    try expectOrdinals(&main, &comb_ordinals);
    try std.testing.expect(main.next == &entries[16].node);
    try std.testing.expect(main.prev == &entries[4].node);
}
