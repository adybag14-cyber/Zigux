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
    ordinal_descending,
    all_ties,
};

fn cmp(priv: ?*anyopaque, a: *const ListHead, b: *const ListHead) i32 {
    const mode: *const SortMode = @ptrCast(@alignCast(priv.?));
    const lhs: *const Entry = @fieldParentPtr("node", a);
    const rhs: *const Entry = @fieldParentPtr("node", b);

    switch (mode.*) {
        .key_ascending => {
            if (lhs.key < rhs.key) return -1;
            if (lhs.key > rhs.key) return 1;
            return 0;
        },
        .key_descending => {
            if (lhs.key > rhs.key) return -1;
            if (lhs.key < rhs.key) return 1;
            return 0;
        },
        .ordinal_descending => {
            if (lhs.ordinal > rhs.ordinal) return -1;
            if (lhs.ordinal < rhs.ordinal) return 1;
            return 0;
        },
        .all_ties => return 0,
    }
}

fn expectCircular(head: *const ListHead, expected_ordinals: []const usize) !void {
    var idx: usize = 0;
    var current = head.next;
    while (current != head) : (current = current.?.next) {
        const entry: *const Entry = @fieldParentPtr("node", current.?);
        try std.testing.expect(idx < expected_ordinals.len);
        try std.testing.expectEqual(expected_ordinals[idx], entry.ordinal);
        try std.testing.expect(current.?.next.?.prev == current.?);
        try std.testing.expect(current.?.prev.?.next == current.?);
        idx += 1;
    }

    try std.testing.expectEqual(expected_ordinals.len, idx);
    if (expected_ordinals.len == 0) {
        try std.testing.expect(head.next == head);
        try std.testing.expect(head.prev == head);
        return;
    }

    var reverse_idx = expected_ordinals.len;
    current = head.prev;
    while (current != head) : (current = current.?.prev) {
        const entry: *const Entry = @fieldParentPtr("node", current.?);
        reverse_idx -= 1;
        try std.testing.expectEqual(expected_ordinals[reverse_idx], entry.ordinal);
    }
    try std.testing.expectEqual(@as(usize, 0), reverse_idx);
}

fn detachFront(head: *ListHead) *ListHead {
    const node = head.next.?;
    list_sort.listDel(node);
    std.debug.assert(node.next == null);
    std.debug.assert(node.prev == null);
    return node;
}

fn detachBack(head: *ListHead) *ListHead {
    const node = head.prev.?;
    list_sort.listDel(node);
    std.debug.assert(node.next == null);
    std.debug.assert(node.prev == null);
    return node;
}

fn addIfPresent(node: ?*ListHead, head: *ListHead) void {
    if (node) |present| list_sort.listAddTail(present, head);
}

test "list sort preserves a wavefront transpose after row staging" {
    var entries = [_]Entry{
        .{ .key = 12, .ordinal = 0 },
        .{ .key = 4, .ordinal = 1 },
        .{ .key = 9, .ordinal = 2 },
        .{ .key = 1, .ordinal = 3 },
        .{ .key = 7, .ordinal = 4 },
        .{ .key = 3, .ordinal = 5 },
        .{ .key = 10, .ordinal = 6 },
        .{ .key = 2, .ordinal = 7 },
        .{ .key = 8, .ordinal = 8 },
        .{ .key = 5, .ordinal = 9 },
        .{ .key = 11, .ordinal = 10 },
        .{ .key = 6, .ordinal = 11 },
    };

    var main: ListHead = .{};
    var row0: ListHead = .{};
    var row1: ListHead = .{};
    var row2: ListHead = .{};
    main.init();
    row0.init();
    row1.init();
    row2.init();

    for (&entries) |*entry| list_sort.listAddTail(&entry.node, &main);

    var mode = SortMode.key_ascending;
    list_sort.listSort(&mode, &main, cmp);
    try expectCircular(&main, &.{ 3, 7, 5, 1, 9, 11, 4, 8, 2, 6, 10, 0 });

    var rank: usize = 0;
    while (!list_sort.listEmpty(&main)) : (rank += 1) {
        const node = detachFront(&main);
        switch (rank % 3) {
            0 => list_sort.listAddTail(node, &row0),
            1 => list_sort.listAddTail(node, &row1),
            2 => list_sort.listAddTail(node, &row2),
            else => unreachable,
        }
    }

    try expectCircular(&row0, &.{ 3, 1, 4, 6 });
    try expectCircular(&row1, &.{ 7, 9, 8, 10 });
    try expectCircular(&row2, &.{ 5, 11, 2, 0 });

    mode = .key_descending;
    list_sort.listSort(&mode, &row0, cmp);
    mode = .ordinal_descending;
    list_sort.listSort(&mode, &row1, cmp);
    mode = .key_ascending;
    list_sort.listSort(&mode, &row2, cmp);

    try expectCircular(&row0, &.{ 6, 4, 1, 3 });
    try expectCircular(&row1, &.{ 10, 9, 8, 7 });
    try expectCircular(&row2, &.{ 5, 11, 2, 0 });

    while (!list_sort.listEmpty(&row0) or !list_sort.listEmpty(&row1) or !list_sort.listEmpty(&row2)) {
        addIfPresent(if (!list_sort.listEmpty(&row0)) detachFront(&row0) else null, &main);
        addIfPresent(if (!list_sort.listEmpty(&row1)) detachBack(&row1) else null, &main);
        addIfPresent(if (!list_sort.listEmpty(&row2)) detachFront(&row2) else null, &main);
    }

    const transposed = [_]usize{ 6, 7, 5, 4, 8, 11, 1, 9, 2, 3, 10, 0 };
    try expectCircular(&main, &transposed);
    try std.testing.expect(list_sort.listEmpty(&row0));
    try std.testing.expect(list_sort.listEmpty(&row1));
    try std.testing.expect(list_sort.listEmpty(&row2));

    mode = .all_ties;
    list_sort.listSort(&mode, &main, cmp);
    try expectCircular(&main, &transposed);
    try std.testing.expect(main.next == &entries[6].node);
    try std.testing.expect(main.prev == &entries[0].node);
}
