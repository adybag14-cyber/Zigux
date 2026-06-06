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

test "list sort supports tiered cascade staging and stable replay" {
    var entries = [_]Entry{
        .{ .key = 9, .ordinal = 0 },
        .{ .key = 2, .ordinal = 1 },
        .{ .key = 7, .ordinal = 2 },
        .{ .key = 2, .ordinal = 3 },
        .{ .key = 5, .ordinal = 4 },
        .{ .key = 8, .ordinal = 5 },
        .{ .key = 5, .ordinal = 6 },
        .{ .key = 1, .ordinal = 7 },
        .{ .key = 6, .ordinal = 8 },
        .{ .key = 3, .ordinal = 9 },
    };

    var main: ListHead = .{};
    var low: ListHead = .{};
    var mid: ListHead = .{};
    var high: ListHead = .{};
    main.init();
    low.init();
    mid.init();
    high.init();

    for (&entries) |*entry| list_sort.listAddTail(&entry.node, &main);

    var mode = SortMode.key_ascending;
    list_sort.listSort(&mode, &main, cmp);
    try expectCircular(&main, &.{ 7, 1, 3, 9, 4, 6, 8, 2, 5, 0 });

    var rank: usize = 0;
    while (!list_sort.listEmpty(&main)) : (rank += 1) {
        const node = detachFront(&main);
        if (rank < 3) {
            list_sort.listAddTail(node, &low);
        } else if (rank < 7) {
            list_sort.listAddTail(node, &mid);
        } else {
            list_sort.listAddTail(node, &high);
        }
    }

    try expectCircular(&low, &.{ 7, 1, 3 });
    try expectCircular(&mid, &.{ 9, 4, 6, 8 });
    try expectCircular(&high, &.{ 2, 5, 0 });

    mode = .key_descending;
    list_sort.listSort(&mode, &low, cmp);
    mode = .ordinal_descending;
    list_sort.listSort(&mode, &mid, cmp);
    mode = .key_ascending;
    list_sort.listSort(&mode, &high, cmp);

    try expectCircular(&low, &.{ 1, 3, 7 });
    try expectCircular(&mid, &.{ 9, 8, 6, 4 });
    try expectCircular(&high, &.{ 2, 5, 0 });

    while (!list_sort.listEmpty(&high) or !list_sort.listEmpty(&mid) or !list_sort.listEmpty(&low)) {
        addIfPresent(if (!list_sort.listEmpty(&high)) detachFront(&high) else null, &main);
        addIfPresent(if (!list_sort.listEmpty(&mid)) detachBack(&mid) else null, &main);
        addIfPresent(if (!list_sort.listEmpty(&low)) detachFront(&low) else null, &main);
    }

    const cascaded = [_]usize{ 2, 4, 1, 5, 6, 3, 0, 8, 7, 9 };
    try expectCircular(&main, &cascaded);
    try std.testing.expect(list_sort.listEmpty(&low));
    try std.testing.expect(list_sort.listEmpty(&mid));
    try std.testing.expect(list_sort.listEmpty(&high));

    mode = .all_ties;
    list_sort.listSort(&mode, &main, cmp);
    try expectCircular(&main, &cascaded);
    try std.testing.expect(main.next == &entries[2].node);
    try std.testing.expect(main.prev == &entries[9].node);
}
