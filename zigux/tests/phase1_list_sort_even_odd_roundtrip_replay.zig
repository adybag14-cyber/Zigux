const std = @import("std");
const list_sort = @import("list_sort");

const ListHead = list_sort.ListHead;

const Entry = struct {
    key: i32,
    phase: usize,
    ordinal: usize,
    node: ListHead = .{},
};

const SortMode = enum {
    key_ascending,
    key_descending,
    phase_ascending,
    all_ties,
};

fn compare(priv: ?*anyopaque, a: *const ListHead, b: *const ListHead) i32 {
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
        .phase_ascending => {
            if (lhs.phase < rhs.phase) return -1;
            if (lhs.phase > rhs.phase) return 1;
            return 0;
        },
        .all_ties => return 0,
    }
}

fn expectCircularLinks(head: *ListHead) !void {
    var current = head.next;
    while (current != head) : (current = current.?.next) {
        try std.testing.expect(current.?.next.?.prev == current.?);
        try std.testing.expect(current.?.prev.?.next == current.?);
    }
}

fn expectOrder(head: *ListHead, expected_ordinals: []const usize) !void {
    var observed: [10]usize = undefined;
    var idx: usize = 0;
    var current = head.next;

    while (current != head) : (current = current.?.next) {
        const entry: *const Entry = @fieldParentPtr("node", current.?);
        observed[idx] = entry.ordinal;
        idx += 1;
    }

    try std.testing.expectEqualSlices(usize, expected_ordinals, observed[0..idx]);
}

fn popFront(head: *ListHead) ?*ListHead {
    if (list_sort.listEmpty(head)) return null;
    const node = head.next.?;
    list_sort.listDel(node);
    return node;
}

test "list sort roundtrips even and odd staging heads before stable all-ties pass" {
    var entries = [_]Entry{
        .{ .key = 8, .phase = 2, .ordinal = 0 },
        .{ .key = 3, .phase = 1, .ordinal = 1 },
        .{ .key = 5, .phase = 0, .ordinal = 2 },
        .{ .key = 1, .phase = 2, .ordinal = 3 },
        .{ .key = 7, .phase = 1, .ordinal = 4 },
        .{ .key = 3, .phase = 0, .ordinal = 5 },
        .{ .key = 6, .phase = 2, .ordinal = 6 },
        .{ .key = 2, .phase = 1, .ordinal = 7 },
        .{ .key = 5, .phase = 2, .ordinal = 8 },
        .{ .key = 4, .phase = 0, .ordinal = 9 },
    };

    var main: ListHead = .{};
    var even_stage: ListHead = .{};
    var odd_stage: ListHead = .{};
    main.init();
    even_stage.init();
    odd_stage.init();

    for (&entries) |*entry| list_sort.listAddTail(&entry.node, &main);

    var mode = SortMode.key_ascending;
    list_sort.listSort(&mode, &main, compare);
    try expectOrder(&main, &.{ 3, 7, 1, 5, 9, 2, 8, 6, 4, 0 });

    var current = main.next;
    while (current != &main) {
        const node = current.?;
        current = node.next;
        const entry: *const Entry = @fieldParentPtr("node", node);

        list_sort.listDel(node);
        try std.testing.expect(node.next == null);
        try std.testing.expect(node.prev == null);

        if ((entry.ordinal & 1) == 0) {
            list_sort.listAddTail(node, &even_stage);
        } else {
            list_sort.listAddTail(node, &odd_stage);
        }
    }

    try std.testing.expect(list_sort.listEmpty(&main));
    try expectOrder(&even_stage, &.{ 2, 8, 6, 4, 0 });
    try expectOrder(&odd_stage, &.{ 3, 7, 1, 5, 9 });

    mode = .key_descending;
    list_sort.listSort(&mode, &even_stage, compare);
    try expectOrder(&even_stage, &.{ 0, 4, 6, 2, 8 });

    mode = .phase_ascending;
    list_sort.listSort(&mode, &odd_stage, compare);
    try expectOrder(&odd_stage, &.{ 5, 9, 7, 1, 3 });

    while (!list_sort.listEmpty(&odd_stage) or !list_sort.listEmpty(&even_stage)) {
        if (popFront(&odd_stage)) |node| {
            try std.testing.expect(node.next == null);
            try std.testing.expect(node.prev == null);
            list_sort.listAddTail(node, &main);
        }
        if (popFront(&even_stage)) |node| {
            try std.testing.expect(node.next == null);
            try std.testing.expect(node.prev == null);
            list_sort.listAddTail(node, &main);
        }
    }

    try std.testing.expect(list_sort.listEmpty(&even_stage));
    try std.testing.expect(list_sort.listEmpty(&odd_stage));
    try expectOrder(&main, &.{ 5, 0, 9, 4, 7, 6, 1, 2, 3, 8 });

    mode = .all_ties;
    list_sort.listSort(&mode, &main, compare);
    try expectOrder(&main, &.{ 5, 0, 9, 4, 7, 6, 1, 2, 3, 8 });
    try expectCircularLinks(&main);
    try std.testing.expect(main.next == &entries[5].node);
    try std.testing.expect(main.prev == &entries[8].node);
}
