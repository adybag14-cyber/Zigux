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

test "cantilever gantry replay preserves staged list_sort traversal" {
    var source: ListHead = .{};
    source.init();

    var entries = [_]Entry{
        .{ .key = 6, .ordinal = 0 },
        .{ .key = 2, .ordinal = 1 },
        .{ .key = 5, .ordinal = 2 },
        .{ .key = 2, .ordinal = 3 },
        .{ .key = 4, .ordinal = 4 },
        .{ .key = 1, .ordinal = 5 },
        .{ .key = 6, .ordinal = 6 },
        .{ .key = 3, .ordinal = 7 },
        .{ .key = 5, .ordinal = 8 },
        .{ .key = 1, .ordinal = 9 },
        .{ .key = 4, .ordinal = 10 },
        .{ .key = 3, .ordinal = 11 },
    };

    for (&entries) |*entry| {
        if ((entry.ordinal % 5) == 0) {
            prependEntry(&source, entry);
        } else {
            appendEntry(&source, entry);
        }
    }

    try expectForward(&source, &.{ 10, 5, 0, 1, 2, 3, 4, 6, 7, 8, 9, 11 });

    var mode = SortMode.key_asc;
    list_sort.listSort(&mode, &source, cmpByMode);
    try expectForward(&source, &.{ 5, 9, 1, 3, 7, 11, 10, 4, 2, 8, 0, 6 });
    try expectReverse(&source, &.{ 6, 0, 8, 2, 4, 10, 11, 7, 3, 1, 9, 5 });

    var gantries = [_]ListHead{ .{}, .{}, .{} };
    for (&gantries) |*gantry| gantry.init();

    var rank: usize = 0;
    while (!list_sort.listEmpty(&source)) : (rank += 1) {
        const entry = try popBack(&source);
        if ((rank % 2) == 0) {
            appendEntry(&gantries[rank % gantries.len], entry);
        } else {
            prependEntry(&gantries[rank % gantries.len], entry);
        }
    }

    try std.testing.expectEqual(@as(usize, 12), rank);
    try std.testing.expect(list_sort.listEmpty(&source));
    try expectForward(&gantries[0], &.{ 1, 2, 6, 11 });
    try expectForward(&gantries[1], &.{ 7, 0, 4, 9 });
    try expectForward(&gantries[2], &.{ 5, 10, 8, 3 });

    mode = .key_desc;
    list_sort.listSort(&mode, &gantries[0], cmpByMode);
    mode = .ordinal_asc;
    list_sort.listSort(&mode, &gantries[1], cmpByMode);
    mode = .key_asc;
    list_sort.listSort(&mode, &gantries[2], cmpByMode);

    try expectForward(&gantries[0], &.{ 6, 2, 11, 1 });
    try expectForward(&gantries[1], &.{ 0, 4, 7, 9 });
    try expectForward(&gantries[2], &.{ 5, 3, 10, 8 });

    appendEntry(&source, try popFront(&gantries[0]));
    prependEntry(&source, try popBack(&gantries[1]));
    appendEntry(&source, try popFront(&gantries[2]));
    appendEntry(&source, try popBack(&gantries[0]));
    prependEntry(&source, try popFront(&gantries[1]));
    appendEntry(&source, try popBack(&gantries[2]));
    appendEntry(&source, try popFront(&gantries[0]));
    prependEntry(&source, try popBack(&gantries[1]));
    appendEntry(&source, try popFront(&gantries[2]));
    appendEntry(&source, try popBack(&gantries[0]));
    prependEntry(&source, try popFront(&gantries[1]));
    appendEntry(&source, try popFront(&gantries[2]));

    for (&gantries) |*gantry| try std.testing.expect(list_sort.listEmpty(gantry));

    try expectForward(&source, &.{ 4, 7, 0, 9, 6, 5, 1, 8, 2, 3, 11, 10 });
    try expectReverse(&source, &.{ 10, 11, 3, 2, 8, 1, 5, 6, 9, 0, 7, 4 });

    list_sort.listSort(null, &source, cmpAllTies);
    try expectForward(&source, &.{ 4, 7, 0, 9, 6, 5, 1, 8, 2, 3, 11, 10 });
    try expectReverse(&source, &.{ 10, 11, 3, 2, 8, 1, 5, 6, 9, 0, 7, 4 });

    mode = .ordinal_desc;
    list_sort.listSort(&mode, &source, cmpByMode);
    try expectForward(&source, &.{ 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0 });
    try expectReverse(&source, &.{ 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11 });
}
