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

fn compare(priv: ?*anyopaque, a: *const ListHead, b: *const ListHead) i32 {
    const mode: *const SortMode = @ptrCast(@alignCast(priv.?));
    const lhs: *const Entry = @fieldParentPtr("node", a);
    const rhs: *const Entry = @fieldParentPtr("node", b);

    return switch (mode.*) {
        .key_asc => compareInt(lhs.key, rhs.key),
        .key_desc => compareInt(rhs.key, lhs.key),
        .ordinal_asc => compareInt(@intCast(lhs.ordinal), @intCast(rhs.ordinal)),
        .ordinal_desc => compareInt(@intCast(rhs.ordinal), @intCast(lhs.ordinal)),
        .all_ties => 0,
    };
}

fn compareInt(lhs: i32, rhs: i32) i32 {
    if (lhs < rhs) return -17;
    if (lhs > rhs) return 19;
    return 0;
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

fn expectDetached(node: *const ListHead) !void {
    try std.testing.expect(node.next == null);
    try std.testing.expect(node.prev == null);
}

fn expectCircularOrdinals(head: *ListHead, expected: []const usize) !void {
    var seen: [16]usize = undefined;
    var count: usize = 0;
    var current = head.next;

    while (current != head) : (current = current.?.next) {
        const entry: *const Entry = @fieldParentPtr("node", current.?);
        seen[count] = entry.ordinal;
        try std.testing.expect(current.?.next.?.prev == current.?);
        try std.testing.expect(current.?.prev.?.next == current.?);
        count += 1;
    }

    try std.testing.expectEqualSlices(usize, expected, seen[0..count]);
}

test "list sort survives tandem sluice staged rebuild and all-ties replay" {
    var source: ListHead = .{};
    var upper: ListHead = .{};
    var lower: ListHead = .{};
    var spill: ListHead = .{};
    source.init();
    upper.init();
    lower.init();
    spill.init();

    var entries = [_]Entry{
        .{ .key = 5, .ordinal = 0 },
        .{ .key = -2, .ordinal = 1 },
        .{ .key = 8, .ordinal = 2 },
        .{ .key = 3, .ordinal = 3 },
        .{ .key = 5, .ordinal = 4 },
        .{ .key = 0, .ordinal = 5 },
        .{ .key = 8, .ordinal = 6 },
        .{ .key = -2, .ordinal = 7 },
        .{ .key = 3, .ordinal = 8 },
        .{ .key = 9, .ordinal = 9 },
        .{ .key = 0, .ordinal = 10 },
        .{ .key = 6, .ordinal = 11 },
    };

    for (&entries, 0..) |*entry, index| {
        if ((index & 1) == 0) {
            list_sort.listAddTail(&entry.node, &source);
        } else {
            list_sort.listAdd(&entry.node, &source);
        }
    }
    try expectCircularOrdinals(&source, &.{ 11, 9, 7, 5, 3, 1, 0, 2, 4, 6, 8, 10 });

    var mode = SortMode.key_asc;
    list_sort.listSort(&mode, &source, compare);
    try expectCircularOrdinals(&source, &.{ 7, 1, 5, 10, 3, 8, 0, 4, 11, 2, 6, 9 });

    var rank: usize = 0;
    while (!list_sort.listEmpty(&source)) : (rank += 1) {
        const node = if ((rank & 1) == 0) popFront(&source).? else popBack(&source).?;
        try expectDetached(node);

        if ((rank % 3) == 0) {
            list_sort.listAddTail(node, &upper);
        } else if ((rank % 3) == 1) {
            list_sort.listAdd(node, &lower);
        } else {
            list_sort.listAddTail(node, &spill);
        }
    }
    try std.testing.expect(list_sort.listEmpty(&source));
    try expectCircularOrdinals(&upper, &.{ 7, 6, 10, 4 });
    try expectCircularOrdinals(&lower, &.{ 8, 11, 5, 9 });
    try expectCircularOrdinals(&spill, &.{ 1, 2, 3, 0 });

    mode = .key_desc;
    list_sort.listSort(&mode, &upper, compare);
    mode = .ordinal_asc;
    list_sort.listSort(&mode, &lower, compare);
    mode = .ordinal_desc;
    list_sort.listSort(&mode, &spill, compare);

    try expectCircularOrdinals(&upper, &.{ 6, 4, 10, 7 });
    try expectCircularOrdinals(&lower, &.{ 5, 8, 9, 11 });
    try expectCircularOrdinals(&spill, &.{ 3, 2, 1, 0 });

    while (!list_sort.listEmpty(&upper) or !list_sort.listEmpty(&lower) or !list_sort.listEmpty(&spill)) {
        if (popBack(&upper)) |node| {
            try expectDetached(node);
            list_sort.listAddTail(node, &source);
        }
        if (popFront(&lower)) |node| {
            try expectDetached(node);
            list_sort.listAddTail(node, &source);
        }
        if (popBack(&spill)) |node| {
            try expectDetached(node);
            list_sort.listAddTail(node, &source);
        }
    }

    try std.testing.expect(list_sort.listEmpty(&upper));
    try std.testing.expect(list_sort.listEmpty(&lower));
    try std.testing.expect(list_sort.listEmpty(&spill));
    try expectCircularOrdinals(&source, &.{ 7, 5, 0, 10, 8, 1, 4, 9, 2, 6, 11, 3 });

    mode = .all_ties;
    list_sort.listSort(&mode, &source, compare);
    try expectCircularOrdinals(&source, &.{ 7, 5, 0, 10, 8, 1, 4, 9, 2, 6, 11, 3 });
    try std.testing.expect(source.next == &entries[7].node);
    try std.testing.expect(source.prev == &entries[3].node);
}
