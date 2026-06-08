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
    if (lhs < rhs) return -23;
    if (lhs > rhs) return 29;
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

fn attachByTorusRank(rank: usize, node: *ListHead, rings: *[4]ListHead) void {
    if ((rank % 8) < 4) {
        list_sort.listAddTail(node, &rings[rank % rings.len]);
    } else {
        list_sort.listAdd(node, &rings[rank % rings.len]);
    }
}

fn shuttleStep(node: ?*ListHead, source: *ListHead) !bool {
    if (node) |entry| {
        try expectDetached(entry);
        list_sort.listAddTail(entry, source);
        return true;
    }
    return false;
}

test "list sort preserves torus shuttle rebuild and all-ties order" {
    var source: ListHead = .{};
    var rings = [_]ListHead{.{}} ** 4;
    source.init();
    for (&rings) |*ring| ring.init();

    var entries = [_]Entry{
        .{ .key = 4, .ordinal = 0 },
        .{ .key = -3, .ordinal = 1 },
        .{ .key = 7, .ordinal = 2 },
        .{ .key = 1, .ordinal = 3 },
        .{ .key = 4, .ordinal = 4 },
        .{ .key = 9, .ordinal = 5 },
        .{ .key = 0, .ordinal = 6 },
        .{ .key = 7, .ordinal = 7 },
        .{ .key = -3, .ordinal = 8 },
        .{ .key = 2, .ordinal = 9 },
        .{ .key = 9, .ordinal = 10 },
        .{ .key = 1, .ordinal = 11 },
        .{ .key = 5, .ordinal = 12 },
        .{ .key = 0, .ordinal = 13 },
    };

    for (&entries, 0..) |*entry, index| {
        if ((index & 1) == 0) {
            list_sort.listAddTail(&entry.node, &source);
        } else {
            list_sort.listAdd(&entry.node, &source);
        }
    }
    try expectCircularOrdinals(&source, &.{ 13, 11, 9, 7, 5, 3, 1, 0, 2, 4, 6, 8, 10, 12 });

    var mode = SortMode.key_asc;
    list_sort.listSort(&mode, &source, compare);
    try expectCircularOrdinals(&source, &.{ 1, 8, 13, 6, 11, 3, 9, 0, 4, 12, 7, 2, 5, 10 });

    var rank: usize = 0;
    while (!list_sort.listEmpty(&source)) : (rank += 1) {
        const node = if ((rank & 1) == 0) popFront(&source).? else popBack(&source).?;
        try expectDetached(node);
        attachByTorusRank(rank, node, &rings);
    }
    try std.testing.expect(list_sort.listEmpty(&source));
    try expectCircularOrdinals(&rings[0], &.{ 9, 13, 1, 11 });
    try expectCircularOrdinals(&rings[1], &.{ 0, 2, 10, 12 });
    try expectCircularOrdinals(&rings[2], &.{ 6, 8, 3 });
    try expectCircularOrdinals(&rings[3], &.{ 7, 5, 4 });

    mode = .ordinal_desc;
    list_sort.listSort(&mode, &rings[0], compare);
    mode = .key_asc;
    list_sort.listSort(&mode, &rings[1], compare);
    mode = .key_desc;
    list_sort.listSort(&mode, &rings[2], compare);
    mode = .ordinal_asc;
    list_sort.listSort(&mode, &rings[3], compare);

    try expectCircularOrdinals(&rings[0], &.{ 13, 11, 9, 1 });
    try expectCircularOrdinals(&rings[1], &.{ 0, 12, 2, 10 });
    try expectCircularOrdinals(&rings[2], &.{ 3, 6, 8 });
    try expectCircularOrdinals(&rings[3], &.{ 4, 5, 7 });

    while (!list_sort.listEmpty(&rings[0]) or !list_sort.listEmpty(&rings[1]) or !list_sort.listEmpty(&rings[2]) or !list_sort.listEmpty(&rings[3])) {
        _ = try shuttleStep(popBack(&rings[0]), &source);
        _ = try shuttleStep(popFront(&rings[2]), &source);
        _ = try shuttleStep(popBack(&rings[1]), &source);
        _ = try shuttleStep(popFront(&rings[3]), &source);
        _ = try shuttleStep(popFront(&rings[0]), &source);
        _ = try shuttleStep(popBack(&rings[2]), &source);
        _ = try shuttleStep(popFront(&rings[1]), &source);
        _ = try shuttleStep(popBack(&rings[3]), &source);
    }

    for (&rings) |*ring| try std.testing.expect(list_sort.listEmpty(ring));
    try expectCircularOrdinals(&source, &.{ 1, 3, 10, 4, 13, 8, 0, 7, 9, 6, 2, 5, 11, 12 });

    mode = .all_ties;
    list_sort.listSort(&mode, &source, compare);
    try expectCircularOrdinals(&source, &.{ 1, 3, 10, 4, 13, 8, 0, 7, 9, 6, 2, 5, 11, 12 });
    try std.testing.expect(source.next == &entries[1].node);
    try std.testing.expect(source.prev == &entries[12].node);
}
