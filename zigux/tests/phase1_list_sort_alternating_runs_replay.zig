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
    modulo4,
};

fn compareByMode(priv: ?*anyopaque, a: *const ListHead, b: *const ListHead) i32 {
    const mode: *const SortMode = @ptrCast(@alignCast(priv.?));
    const lhs: *const Entry = @fieldParentPtr("node", a);
    const rhs: *const Entry = @fieldParentPtr("node", b);

    const lhs_value = switch (mode.*) {
        .ascending, .descending => lhs.key,
        .modulo4 => @mod(lhs.key, 4),
    };
    const rhs_value = switch (mode.*) {
        .ascending, .descending => rhs.key,
        .modulo4 => @mod(rhs.key, 4),
    };

    if (lhs_value == rhs_value) return 0;
    const ascending = lhs_value < rhs_value;
    return switch (mode.*) {
        .ascending, .modulo4 => if (ascending) -1 else 1,
        .descending => if (ascending) 1 else -1,
    };
}

fn expectOrder(head: *const ListHead, expected_ordinals: []const usize, expected_keys: []const i32) !void {
    try std.testing.expectEqual(expected_ordinals.len, expected_keys.len);

    var idx: usize = 0;
    var current = head.next;
    while (current != head) : (current = current.?.next) {
        const entry: *const Entry = @fieldParentPtr("node", current.?);
        try std.testing.expect(idx < expected_ordinals.len);
        try std.testing.expectEqual(expected_ordinals[idx], entry.ordinal);
        try std.testing.expectEqual(expected_keys[idx], entry.key);
        try std.testing.expect(current.?.next.?.prev == current.?);
        try std.testing.expect(current.?.prev.?.next == current.?);
        idx += 1;
    }

    try std.testing.expectEqual(expected_ordinals.len, idx);
}

fn moveTail(entry: *Entry, destination: *ListHead) !void {
    list_sort.listDel(&entry.node);
    try std.testing.expect(entry.node.next == null);
    try std.testing.expect(entry.node.prev == null);
    list_sort.listAddTail(&entry.node, destination);
}

fn moveFront(source: *ListHead, destination: *ListHead) void {
    const node = source.next.?;
    list_sort.listDel(node);
    list_sort.listAddTail(node, destination);
}

test "list sort handles alternating detached runs and stable final bucket replay" {
    var main: ListHead = .{};
    var stage_a: ListHead = .{};
    var stage_b: ListHead = .{};
    main.init();
    stage_a.init();
    stage_b.init();

    var entries = [_]Entry{
        .{ .key = 12, .ordinal = 0 },
        .{ .key = 5, .ordinal = 1 },
        .{ .key = 9, .ordinal = 2 },
        .{ .key = 2, .ordinal = 3 },
        .{ .key = 11, .ordinal = 4 },
        .{ .key = 4, .ordinal = 5 },
        .{ .key = 7, .ordinal = 6 },
        .{ .key = 1, .ordinal = 7 },
        .{ .key = 10, .ordinal = 8 },
        .{ .key = 3, .ordinal = 9 },
        .{ .key = 8, .ordinal = 10 },
        .{ .key = 6, .ordinal = 11 },
    };

    for (&entries) |*entry| {
        list_sort.listAddTail(&entry.node, &main);
    }

    const stage_a_ordinals = [_]usize{ 0, 1, 2, 6, 7, 8 };
    for (&stage_a_ordinals) |ordinal| {
        try moveTail(&entries[ordinal], &stage_a);
    }
    const stage_b_ordinals = [_]usize{ 3, 4, 5, 9, 10, 11 };
    for (&stage_b_ordinals) |ordinal| {
        try moveTail(&entries[ordinal], &stage_b);
    }
    try std.testing.expect(list_sort.listEmpty(&main));

    var mode = SortMode.descending;
    list_sort.listSort(&mode, &stage_a, compareByMode);
    try expectOrder(
        &stage_a,
        &.{ 0, 8, 2, 6, 1, 7 },
        &.{ 12, 10, 9, 7, 5, 1 },
    );

    mode = .ascending;
    list_sort.listSort(&mode, &stage_b, compareByMode);
    try expectOrder(
        &stage_b,
        &.{ 3, 9, 5, 11, 10, 4 },
        &.{ 2, 3, 4, 6, 8, 11 },
    );

    while (!list_sort.listEmpty(&stage_b) or !list_sort.listEmpty(&stage_a)) {
        if (!list_sort.listEmpty(&stage_b)) moveFront(&stage_b, &main);
        if (!list_sort.listEmpty(&stage_a)) moveFront(&stage_a, &main);
    }
    try std.testing.expect(list_sort.listEmpty(&stage_a));
    try std.testing.expect(list_sort.listEmpty(&stage_b));
    try expectOrder(
        &main,
        &.{ 3, 0, 9, 8, 5, 2, 11, 6, 10, 1, 4, 7 },
        &.{ 2, 12, 3, 10, 4, 9, 6, 7, 8, 5, 11, 1 },
    );

    mode = .modulo4;
    list_sort.listSort(&mode, &main, compareByMode);
    try expectOrder(
        &main,
        &.{ 0, 5, 10, 2, 1, 7, 3, 8, 11, 9, 6, 4 },
        &.{ 12, 4, 8, 9, 5, 1, 2, 10, 6, 3, 7, 11 },
    );

    try std.testing.expect(main.next == &entries[0].node);
    try std.testing.expect(main.prev == &entries[4].node);
}
