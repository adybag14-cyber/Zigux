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
};

fn cmpByMode(priv: ?*anyopaque, a: *const ListHead, b: *const ListHead) i32 {
    const mode: *const SortMode = @ptrCast(@alignCast(priv.?));
    const lhs: *const Entry = @fieldParentPtr("node", a);
    const rhs: *const Entry = @fieldParentPtr("node", b);

    switch (mode.*) {
        .key_asc => {
            if (lhs.key < rhs.key) return -17;
            if (lhs.key > rhs.key) return 19;
        },
        .key_desc => {
            if (lhs.key > rhs.key) return -23;
            if (lhs.key < rhs.key) return 29;
        },
        .ordinal_asc => {
            if (lhs.ordinal < rhs.ordinal) return -31;
            if (lhs.ordinal > rhs.ordinal) return 37;
        },
        .ordinal_desc => {
            if (lhs.ordinal > rhs.ordinal) return -41;
            if (lhs.ordinal < rhs.ordinal) return 43;
        },
    }

    return 0;
}

fn cmpAllTies(_: ?*anyopaque, _: *const ListHead, _: *const ListHead) i32 {
    return 0;
}

fn collectForward(head: *const ListHead, out: []usize) !usize {
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

fn collectReverse(head: *const ListHead, out: []usize) !usize {
    var idx: usize = 0;
    var current = head.prev;
    while (current != head) : (current = current.?.prev) {
        const entry: *const Entry = @fieldParentPtr("node", current.?);
        out[idx] = entry.ordinal;
        try std.testing.expect(current.?.next.?.prev == current.?);
        try std.testing.expect(current.?.prev.?.next == current.?);
        idx += 1;
    }
    return idx;
}

fn expectForward(head: *const ListHead, expected: []const usize) !void {
    var actual: [16]usize = undefined;
    const len = try collectForward(head, &actual);
    try std.testing.expectEqualSlices(usize, expected, actual[0..len]);
}

fn expectReverse(head: *const ListHead, expected: []const usize) !void {
    var actual: [16]usize = undefined;
    const len = try collectReverse(head, &actual);
    try std.testing.expectEqualSlices(usize, expected, actual[0..len]);
}

fn popFront(head: *ListHead) !*Entry {
    try std.testing.expect(!list_sort.listEmpty(head));
    const node = head.next.?;
    list_sort.listDel(node);
    try std.testing.expect(node.next == null);
    try std.testing.expect(node.prev == null);
    return @fieldParentPtr("node", node);
}

fn popBack(head: *ListHead) !*Entry {
    try std.testing.expect(!list_sort.listEmpty(head));
    const node = head.prev.?;
    list_sort.listDel(node);
    try std.testing.expect(node.next == null);
    try std.testing.expect(node.prev == null);
    return @fieldParentPtr("node", node);
}

fn appendEntry(head: *ListHead, entry: *Entry) void {
    list_sort.listAddTail(&entry.node, head);
}

fn prependEntry(head: *ListHead, entry: *Entry) void {
    list_sort.listAdd(&entry.node, head);
}

test "bulkhead rail replay preserves staged list_sort traversal" {
    var source: ListHead = .{};
    source.init();

    var entries = [_]Entry{
        .{ .key = 4, .ordinal = 0 },
        .{ .key = 1, .ordinal = 1 },
        .{ .key = 3, .ordinal = 2 },
        .{ .key = 1, .ordinal = 3 },
        .{ .key = 5, .ordinal = 4 },
        .{ .key = 2, .ordinal = 5 },
        .{ .key = 4, .ordinal = 6 },
        .{ .key = 3, .ordinal = 7 },
        .{ .key = 2, .ordinal = 8 },
        .{ .key = 5, .ordinal = 9 },
        .{ .key = 1, .ordinal = 10 },
        .{ .key = 4, .ordinal = 11 },
    };

    for (&entries) |*entry| {
        if ((entry.ordinal % 4) == 0) {
            prependEntry(&source, entry);
        } else {
            appendEntry(&source, entry);
        }
    }

    try expectForward(&source, &.{ 8, 4, 0, 1, 2, 3, 5, 6, 7, 9, 10, 11 });

    var mode = SortMode.key_asc;
    list_sort.listSort(&mode, &source, cmpByMode);
    try expectForward(&source, &.{ 1, 3, 10, 8, 5, 2, 7, 0, 6, 11, 4, 9 });
    try expectReverse(&source, &.{ 9, 4, 11, 6, 0, 7, 2, 5, 8, 10, 3, 1 });

    var rails = [_]ListHead{ .{}, .{}, .{}, .{} };
    for (&rails) |*rail| rail.init();

    var rank: usize = 0;
    while (!list_sort.listEmpty(&source)) : (rank += 1) {
        const entry = try popFront(&source);
        appendEntry(&rails[rank % rails.len], entry);
    }

    try std.testing.expectEqual(@as(usize, 12), rank);
    try std.testing.expect(list_sort.listEmpty(&source));
    try expectForward(&rails[0], &.{ 1, 5, 6 });
    try expectForward(&rails[1], &.{ 3, 2, 11 });
    try expectForward(&rails[2], &.{ 10, 7, 4 });
    try expectForward(&rails[3], &.{ 8, 0, 9 });

    mode = .key_asc;
    list_sort.listSort(&mode, &rails[0], cmpByMode);
    mode = .key_desc;
    list_sort.listSort(&mode, &rails[1], cmpByMode);
    mode = .ordinal_asc;
    list_sort.listSort(&mode, &rails[2], cmpByMode);
    mode = .key_asc;
    list_sort.listSort(&mode, &rails[3], cmpByMode);

    try expectForward(&rails[0], &.{ 1, 5, 6 });
    try expectForward(&rails[1], &.{ 11, 2, 3 });
    try expectForward(&rails[2], &.{ 4, 7, 10 });
    try expectForward(&rails[3], &.{ 8, 0, 9 });

    appendEntry(&source, try popFront(&rails[1]));
    appendEntry(&source, try popFront(&rails[0]));
    prependEntry(&source, try popBack(&rails[3]));
    appendEntry(&source, try popFront(&rails[2]));
    prependEntry(&source, try popFront(&rails[1]));
    appendEntry(&source, try popFront(&rails[3]));
    appendEntry(&source, try popBack(&rails[0]));
    prependEntry(&source, try popBack(&rails[2]));
    appendEntry(&source, try popFront(&rails[0]));
    prependEntry(&source, try popFront(&rails[1]));
    appendEntry(&source, try popFront(&rails[2]));
    appendEntry(&source, try popFront(&rails[3]));

    for (&rails) |*rail| try std.testing.expect(list_sort.listEmpty(rail));

    try expectForward(&source, &.{ 3, 10, 2, 9, 11, 1, 4, 8, 6, 5, 7, 0 });
    try expectReverse(&source, &.{ 0, 7, 5, 6, 8, 4, 1, 11, 9, 2, 10, 3 });

    list_sort.listSort(null, &source, cmpAllTies);
    try expectForward(&source, &.{ 3, 10, 2, 9, 11, 1, 4, 8, 6, 5, 7, 0 });
    try expectReverse(&source, &.{ 0, 7, 5, 6, 8, 4, 1, 11, 9, 2, 10, 3 });
}
