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
    all_equal,
};

fn cmp(mode_ptr: ?*anyopaque, a: *const ListHead, b: *const ListHead) i32 {
    const mode: *const SortMode = @ptrCast(@alignCast(mode_ptr.?));
    const lhs: *const Entry = @fieldParentPtr("node", a);
    const rhs: *const Entry = @fieldParentPtr("node", b);

    return switch (mode.*) {
        .key_asc => compareInt(lhs.key, rhs.key),
        .key_desc => compareInt(rhs.key, lhs.key),
        .ordinal_asc => compareInt(lhs.ordinal, rhs.ordinal),
        .ordinal_desc => compareInt(rhs.ordinal, lhs.ordinal),
        .all_equal => 0,
    };
}

fn compareInt(a: anytype, b: @TypeOf(a)) i32 {
    if (a < b) return -3;
    if (a > b) return 5;
    return 0;
}

fn resetHead(head: *ListHead) void {
    head.init();
}

fn addMixed(entries: []Entry, head: *ListHead) void {
    resetHead(head);
    for (entries) |*entry| {
        entry.node.next = null;
        entry.node.prev = null;
        if ((entry.ordinal % 3) == 0) {
            list_sort.listAdd(&entry.node, head);
        } else {
            list_sort.listAddTail(&entry.node, head);
        }
    }
}

fn collect(head: *const ListHead, out: []usize) []usize {
    var idx: usize = 0;
    var current = head.next;
    while (current != head) : (current = current.?.next) {
        const entry: *const Entry = @fieldParentPtr("node", current.?);
        out[idx] = entry.ordinal;
        idx += 1;
    }
    return out[0..idx];
}

fn expectForward(head: *const ListHead, expected: []const usize) !void {
    var actual: [16]usize = undefined;
    try std.testing.expectEqualSlices(usize, expected, collect(head, &actual));
}

fn expectReverse(head: *const ListHead, expected: []const usize) !void {
    var idx = expected.len;
    var current = head.prev;
    while (current != head) : (current = current.?.prev) {
        idx -= 1;
        const entry: *const Entry = @fieldParentPtr("node", current.?);
        try std.testing.expectEqual(expected[idx], entry.ordinal);
    }
    try std.testing.expectEqual(@as(usize, 0), idx);
}

fn expectCircular(head: *const ListHead, expected_len: usize) !void {
    var count: usize = 0;
    var current = head.next;
    var previous: *const ListHead = head;
    while (current != head) : (current = current.?.next) {
        try std.testing.expectEqual(previous, current.?.prev.?);
        previous = current.?;
        count += 1;
        try std.testing.expect(count <= expected_len);
    }
    try std.testing.expectEqual(expected_len, count);
    try std.testing.expectEqual(previous, head.prev.?);
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

fn appendNode(node: *ListHead, head: *ListHead, tail: bool) void {
    tryDetached(node);
    if (tail) {
        list_sort.listAddTail(node, head);
    } else {
        list_sort.listAdd(node, head);
    }
}

fn tryDetached(node: *const ListHead) void {
    std.debug.assert(node.next == null);
    std.debug.assert(node.prev == null);
}

test "list_sort harbor mux preserves staged lifecycle and final ties" {
    var entries = [_]Entry{
        .{ .key = 4, .ordinal = 0 },
        .{ .key = 1, .ordinal = 1 },
        .{ .key = 3, .ordinal = 2 },
        .{ .key = 2, .ordinal = 3 },
        .{ .key = 1, .ordinal = 4 },
        .{ .key = 4, .ordinal = 5 },
        .{ .key = 2, .ordinal = 6 },
        .{ .key = 3, .ordinal = 7 },
        .{ .key = 1, .ordinal = 8 },
        .{ .key = 5, .ordinal = 9 },
        .{ .key = 0, .ordinal = 10 },
        .{ .key = 2, .ordinal = 11 },
    };

    var key_asc = SortMode.key_asc;
    var key_desc = SortMode.key_desc;
    var ordinal_asc = SortMode.ordinal_asc;
    var ordinal_desc = SortMode.ordinal_desc;
    var all_equal = SortMode.all_equal;

    var source: ListHead = .{};
    addMixed(&entries, &source);
    try expectForward(&source, &.{ 9, 6, 3, 0, 1, 2, 4, 5, 7, 8, 10, 11 });

    list_sort.listSort(&key_asc, &source, cmp);
    try expectForward(&source, &.{ 10, 1, 4, 8, 6, 3, 11, 2, 7, 0, 5, 9 });
    try expectReverse(&source, &.{ 10, 1, 4, 8, 6, 3, 11, 2, 7, 0, 5, 9 });
    try expectCircular(&source, entries.len);

    var harbor_a: ListHead = .{};
    var harbor_b: ListHead = .{};
    var harbor_c: ListHead = .{};
    resetHead(&harbor_a);
    resetHead(&harbor_b);
    resetHead(&harbor_c);

    var step: usize = 0;
    while (popFront(&source)) |node| : (step += 1) {
        const harbor = switch (step % 3) {
            0 => &harbor_a,
            1 => &harbor_b,
            else => &harbor_c,
        };
        appendNode(node, harbor, (step & 1) == 0);
    }
    try std.testing.expect(list_sort.listEmpty(&source));
    try expectForward(&harbor_a, &.{ 0, 8, 10, 11 });
    try expectForward(&harbor_b, &.{ 2, 1, 6, 5 });
    try expectForward(&harbor_c, &.{ 9, 3, 4, 7 });

    list_sort.listSort(&ordinal_asc, &harbor_a, cmp);
    list_sort.listSort(&key_desc, &harbor_b, cmp);
    list_sort.listSort(&ordinal_desc, &harbor_c, cmp);
    try expectForward(&harbor_a, &.{ 0, 8, 10, 11 });
    try expectForward(&harbor_b, &.{ 5, 2, 6, 1 });
    try expectForward(&harbor_c, &.{ 9, 7, 4, 3 });

    const mux_plan = [_]*ListHead{
        &harbor_b, &harbor_a, &harbor_c, &harbor_a, &harbor_b, &harbor_c,
        &harbor_a, &harbor_b, &harbor_c, &harbor_a, &harbor_b, &harbor_c,
    };
    resetHead(&source);
    for (mux_plan, 0..) |harbor, idx| {
        const node = if ((idx % 4) == 0) popBack(harbor).? else popFront(harbor).?;
        appendNode(node, &source, (idx % 2) == 1);
    }

    try expectForward(&source, &.{ 2, 3, 10, 6, 9, 1, 0, 8, 7, 5, 11, 4 });
    try expectCircular(&source, entries.len);
    try std.testing.expect(list_sort.listEmpty(&harbor_a));
    try std.testing.expect(list_sort.listEmpty(&harbor_b));
    try std.testing.expect(list_sort.listEmpty(&harbor_c));

    list_sort.listSort(&all_equal, &source, cmp);
    try expectForward(&source, &.{ 2, 3, 10, 6, 9, 1, 0, 8, 7, 5, 11, 4 });
    try expectReverse(&source, &.{ 2, 3, 10, 6, 9, 1, 0, 8, 7, 5, 11, 4 });
    try expectCircular(&source, entries.len);
}
