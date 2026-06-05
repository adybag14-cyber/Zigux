const std = @import("std");
const list_sort = @import("list_sort");

const ListHead = list_sort.ListHead;

const Entry = struct {
    key: i32,
    ordinal: usize,
    node: ListHead = .{},
};

fn entryFromNode(node: *const ListHead) *const Entry {
    return @fieldParentPtr("node", node);
}

fn cmpKeyAsc(_: ?*anyopaque, a: *const ListHead, b: *const ListHead) i32 {
    const lhs = entryFromNode(a);
    const rhs = entryFromNode(b);
    if (lhs.key < rhs.key) return -1;
    if (lhs.key > rhs.key) return 1;
    return 0;
}

fn cmpKeyDesc(_: ?*anyopaque, a: *const ListHead, b: *const ListHead) i32 {
    return -cmpKeyAsc(null, a, b);
}

fn cmpAllTies(_: ?*anyopaque, _: *const ListHead, _: *const ListHead) i32 {
    return 0;
}

fn expectCircularLinks(head: *const ListHead) !void {
    var current = head.next;
    while (current != head) : (current = current.?.next) {
        try std.testing.expect(current.?.next.?.prev == current.?);
        try std.testing.expect(current.?.prev.?.next == current.?);
    }
}

fn collectOrdinals(head: *const ListHead, out: []usize) ![]usize {
    var idx: usize = 0;
    var current = head.next;
    while (current != head) : (current = current.?.next) {
        try std.testing.expect(idx < out.len);
        out[idx] = entryFromNode(current.?).ordinal;
        idx += 1;
    }
    return out[0..idx];
}

fn collectKeys(head: *const ListHead, out: []i32) ![]i32 {
    var idx: usize = 0;
    var current = head.next;
    while (current != head) : (current = current.?.next) {
        try std.testing.expect(idx < out.len);
        out[idx] = entryFromNode(current.?).key;
        idx += 1;
    }
    return out[0..idx];
}

fn moveAllTail(src: *ListHead, dst: *ListHead) !void {
    while (!list_sort.listEmpty(src)) {
        const node = src.next.?;
        list_sort.listDel(node);
        try std.testing.expect(node.next == null);
        try std.testing.expect(node.prev == null);
        list_sort.listAddTail(node, dst);
    }
}

test "list sort preserves staged bucket traversal through final all-ties pass" {
    var main: ListHead = .{};
    var bucket0: ListHead = .{};
    var bucket1: ListHead = .{};
    var bucket2: ListHead = .{};
    main.init();
    bucket0.init();
    bucket1.init();
    bucket2.init();

    var entries = [_]Entry{
        .{ .key = 9, .ordinal = 0 },
        .{ .key = 2, .ordinal = 1 },
        .{ .key = 7, .ordinal = 2 },
        .{ .key = 4, .ordinal = 3 },
        .{ .key = 6, .ordinal = 4 },
        .{ .key = 1, .ordinal = 5 },
        .{ .key = 8, .ordinal = 6 },
        .{ .key = 3, .ordinal = 7 },
        .{ .key = 5, .ordinal = 8 },
        .{ .key = 0, .ordinal = 9 },
        .{ .key = 11, .ordinal = 10 },
        .{ .key = 10, .ordinal = 11 },
    };

    for (&entries) |*entry| list_sort.listAddTail(&entry.node, &main);

    list_sort.listSort(null, &main, cmpKeyAsc);
    try expectCircularLinks(&main);

    var keys: [entries.len]i32 = undefined;
    var ordinals: [entries.len]usize = undefined;
    try std.testing.expectEqualSlices(
        i32,
        &.{ 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11 },
        try collectKeys(&main, &keys),
    );
    try std.testing.expectEqualSlices(
        usize,
        &.{ 9, 5, 1, 7, 3, 8, 4, 2, 6, 0, 11, 10 },
        try collectOrdinals(&main, &ordinals),
    );

    while (!list_sort.listEmpty(&main)) {
        const node = main.next.?;
        const entry = entryFromNode(node);
        list_sort.listDel(node);
        try std.testing.expect(node.next == null);
        try std.testing.expect(node.prev == null);

        switch (@mod(entry.key, 3)) {
            0 => list_sort.listAddTail(node, &bucket0),
            1 => list_sort.listAdd(node, &bucket1),
            else => list_sort.listAddTail(node, &bucket2),
        }
    }

    try std.testing.expect(list_sort.listEmpty(&main));
    try expectCircularLinks(&bucket0);
    try expectCircularLinks(&bucket1);
    try expectCircularLinks(&bucket2);

    list_sort.listSort(null, &bucket0, cmpKeyDesc);
    list_sort.listSort(null, &bucket1, cmpKeyAsc);
    list_sort.listSort(null, &bucket2, cmpAllTies);

    try std.testing.expectEqualSlices(usize, &.{ 0, 4, 7, 9 }, try collectOrdinals(&bucket0, ordinals[0..4]));
    try std.testing.expectEqualSlices(usize, &.{ 5, 3, 2, 11 }, try collectOrdinals(&bucket1, ordinals[0..4]));
    try std.testing.expectEqualSlices(usize, &.{ 1, 8, 6, 10 }, try collectOrdinals(&bucket2, ordinals[0..4]));

    try moveAllTail(&bucket1, &main);
    try moveAllTail(&bucket2, &main);
    try moveAllTail(&bucket0, &main);
    try std.testing.expect(list_sort.listEmpty(&bucket0));
    try std.testing.expect(list_sort.listEmpty(&bucket1));
    try std.testing.expect(list_sort.listEmpty(&bucket2));

    const staged_ordinals = try collectOrdinals(&main, &ordinals);
    try std.testing.expectEqualSlices(
        usize,
        &.{ 5, 3, 2, 11, 1, 8, 6, 10, 0, 4, 7, 9 },
        staged_ordinals,
    );
    try expectCircularLinks(&main);

    list_sort.listSort(null, &main, cmpAllTies);
    try std.testing.expectEqualSlices(
        usize,
        staged_ordinals,
        try collectOrdinals(&main, &ordinals),
    );
    try expectCircularLinks(&main);
    try std.testing.expect(main.next == &entries[5].node);
    try std.testing.expect(main.prev == &entries[9].node);
}
