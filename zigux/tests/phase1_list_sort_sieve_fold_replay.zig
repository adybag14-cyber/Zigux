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
    all_ties,
};

fn compare(priv: ?*anyopaque, a: *const ListHead, b: *const ListHead) i32 {
    const mode: *const SortMode = @ptrCast(@alignCast(priv.?));
    const lhs: *const Entry = @fieldParentPtr("node", a);
    const rhs: *const Entry = @fieldParentPtr("node", b);

    return switch (mode.*) {
        .key_asc => compareInt(lhs.key, rhs.key),
        .key_desc => compareInt(rhs.key, lhs.key),
        .ordinal_asc => compareInt(@as(i32, @intCast(lhs.ordinal)), @as(i32, @intCast(rhs.ordinal))),
        .all_ties => 0,
    };
}

fn compareInt(lhs: i32, rhs: i32) i32 {
    if (lhs < rhs) return -1;
    if (lhs > rhs) return 1;
    return 0;
}

fn isPrimeRank(rank: usize) bool {
    return switch (rank) {
        2, 3, 5, 7, 11 => true,
        else => false,
    };
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

test "list sort survives rank sieve detach and staged fold replay" {
    var head: ListHead = .{};
    var prime: ListHead = .{};
    var even: ListHead = .{};
    var odd: ListHead = .{};
    head.init();
    prime.init();
    even.init();
    odd.init();

    var entries = [_]Entry{
        .{ .key = 6, .ordinal = 0 },
        .{ .key = 1, .ordinal = 1 },
        .{ .key = 8, .ordinal = 2 },
        .{ .key = 3, .ordinal = 3 },
        .{ .key = 5, .ordinal = 4 },
        .{ .key = 0, .ordinal = 5 },
        .{ .key = 7, .ordinal = 6 },
        .{ .key = 2, .ordinal = 7 },
        .{ .key = 4, .ordinal = 8 },
        .{ .key = 1, .ordinal = 9 },
        .{ .key = 9, .ordinal = 10 },
        .{ .key = 3, .ordinal = 11 },
    };

    for (&entries) |*entry| list_sort.listAddTail(&entry.node, &head);

    var mode = SortMode.key_asc;
    list_sort.listSort(&mode, &head, compare);
    try expectCircularOrdinals(&head, &.{ 5, 1, 9, 7, 3, 11, 8, 4, 0, 6, 2, 10 });

    var rank: usize = 0;
    var current = head.next;
    while (current != &head) {
        const node = current.?;
        current = node.next;
        list_sort.listDel(node);
        try expectDetached(node);

        if (isPrimeRank(rank)) {
            list_sort.listAddTail(node, &prime);
        } else if ((rank & 1) == 0) {
            list_sort.listAddTail(node, &even);
        } else {
            list_sort.listAddTail(node, &odd);
        }
        rank += 1;
    }
    try std.testing.expect(list_sort.listEmpty(&head));
    try expectCircularOrdinals(&prime, &.{ 9, 7, 11, 4, 10 });
    try expectCircularOrdinals(&even, &.{ 5, 3, 8, 0, 2 });
    try expectCircularOrdinals(&odd, &.{ 1, 6 });

    mode = .key_desc;
    list_sort.listSort(&mode, &prime, compare);
    mode = .ordinal_asc;
    list_sort.listSort(&mode, &even, compare);
    mode = .key_asc;
    list_sort.listSort(&mode, &odd, compare);

    try expectCircularOrdinals(&prime, &.{ 10, 4, 11, 7, 9 });
    try expectCircularOrdinals(&even, &.{ 0, 2, 3, 5, 8 });
    try expectCircularOrdinals(&odd, &.{ 1, 6 });

    while (!list_sort.listEmpty(&prime) or !list_sort.listEmpty(&even) or !list_sort.listEmpty(&odd)) {
        if (popBack(&prime)) |node| {
            try expectDetached(node);
            list_sort.listAddTail(node, &head);
        }
        if (popFront(&even)) |node| {
            try expectDetached(node);
            list_sort.listAddTail(node, &head);
        }
        if (popBack(&odd)) |node| {
            try expectDetached(node);
            list_sort.listAddTail(node, &head);
        }
    }

    try std.testing.expect(list_sort.listEmpty(&prime));
    try std.testing.expect(list_sort.listEmpty(&even));
    try std.testing.expect(list_sort.listEmpty(&odd));
    try expectCircularOrdinals(&head, &.{ 9, 0, 6, 7, 2, 1, 11, 3, 4, 5, 10, 8 });

    mode = .all_ties;
    list_sort.listSort(&mode, &head, compare);
    try expectCircularOrdinals(&head, &.{ 9, 0, 6, 7, 2, 1, 11, 3, 4, 5, 10, 8 });
    try std.testing.expect(head.next == &entries[9].node);
    try std.testing.expect(head.prev == &entries[8].node);
}
