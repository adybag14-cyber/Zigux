const std = @import("std");
const list_sort = @import("list_sort");

const Entry = struct {
    key: i32,
    ordinal: usize,
    node: list_sort.ListHead = .{},
};

const SortMode = enum {
    key_ascending,
    key_descending,
    ordinal_descending,
    all_ties,
};

fn cmp(priv: ?*anyopaque, a: *const list_sort.ListHead, b: *const list_sort.ListHead) i32 {
    const mode: *const SortMode = @ptrCast(@alignCast(priv.?));
    const lhs: *const Entry = @fieldParentPtr("node", a);
    const rhs: *const Entry = @fieldParentPtr("node", b);

    return switch (mode.*) {
        .key_ascending => order(lhs.key, rhs.key),
        .key_descending => order(rhs.key, lhs.key),
        .ordinal_descending => order(@as(i32, @intCast(rhs.ordinal)), @as(i32, @intCast(lhs.ordinal))),
        .all_ties => 0,
    };
}

fn order(lhs: i32, rhs: i32) i32 {
    if (lhs < rhs) return -1;
    if (lhs > rhs) return 1;
    return 0;
}

fn collectOrdinals(head: *list_sort.ListHead, out: []usize) ![]usize {
    var count: usize = 0;
    var current = head.next;
    while (current != head) : (current = current.?.next) {
        try std.testing.expect(count < out.len);
        const entry: *const Entry = @fieldParentPtr("node", current.?);
        out[count] = entry.ordinal;
        try std.testing.expect(current.?.next.?.prev == current.?);
        try std.testing.expect(current.?.prev.?.next == current.?);
        count += 1;
    }
    return out[0..count];
}

fn expectOrdinals(head: *list_sort.ListHead, expected: []const usize) !void {
    var actual_buf: [16]usize = undefined;
    const actual = try collectOrdinals(head, &actual_buf);
    try std.testing.expectEqualSlices(usize, expected, actual);
}

fn moveAllTail(dst: *list_sort.ListHead, src: *list_sort.ListHead) !void {
    var current = src.next;
    while (current != src) {
        const node = current.?;
        current = node.next;
        list_sort.listDel(node);
        try std.testing.expect(node.next == null);
        try std.testing.expect(node.prev == null);
        list_sort.listAddTail(node, dst);
    }
    try std.testing.expect(list_sort.listEmpty(src));
}

test "list sort preserves nested staged traversal after repeated stable passes" {
    var head: list_sort.ListHead = .{};
    var outer_a: list_sort.ListHead = .{};
    var outer_b: list_sort.ListHead = .{};
    var inner_even: list_sort.ListHead = .{};
    var inner_odd: list_sort.ListHead = .{};
    head.init();
    outer_a.init();
    outer_b.init();
    inner_even.init();
    inner_odd.init();

    var entries = [_]Entry{
        .{ .key = 9, .ordinal = 0 },
        .{ .key = 1, .ordinal = 1 },
        .{ .key = 7, .ordinal = 2 },
        .{ .key = 3, .ordinal = 3 },
        .{ .key = 5, .ordinal = 4 },
        .{ .key = 3, .ordinal = 5 },
        .{ .key = 8, .ordinal = 6 },
        .{ .key = 1, .ordinal = 7 },
        .{ .key = 6, .ordinal = 8 },
        .{ .key = 4, .ordinal = 9 },
        .{ .key = 2, .ordinal = 10 },
        .{ .key = 5, .ordinal = 11 },
    };
    for (&entries) |*entry| list_sort.listAddTail(&entry.node, &head);

    var mode = SortMode.key_ascending;
    list_sort.listSort(&mode, &head, cmp);
    try expectOrdinals(&head, &.{ 1, 7, 10, 3, 5, 9, 4, 11, 8, 2, 6, 0 });

    var index: usize = 0;
    var current = head.next;
    while (current != &head) : (index += 1) {
        const node = current.?;
        current = node.next;
        if (@mod(index, 3) == 2) continue;

        list_sort.listDel(node);
        try std.testing.expect(node.next == null);
        try std.testing.expect(node.prev == null);

        if (@mod(index, 3) == 0) {
            list_sort.listAddTail(node, &outer_a);
        } else {
            list_sort.listAddTail(node, &outer_b);
        }
    }

    try expectOrdinals(&head, &.{ 10, 9, 8, 0 });
    try expectOrdinals(&outer_a, &.{ 1, 3, 4, 2 });
    try expectOrdinals(&outer_b, &.{ 7, 5, 11, 6 });

    mode = .key_descending;
    list_sort.listSort(&mode, &outer_a, cmp);
    try expectOrdinals(&outer_a, &.{ 2, 4, 3, 1 });

    current = outer_a.next;
    while (current != &outer_a) {
        const node = current.?;
        const entry: *const Entry = @fieldParentPtr("node", node);
        current = node.next;

        list_sort.listDel(node);
        try std.testing.expect(node.next == null);
        try std.testing.expect(node.prev == null);

        if (@mod(entry.ordinal, 2) == 0) {
            list_sort.listAddTail(node, &inner_even);
        } else {
            list_sort.listAddTail(node, &inner_odd);
        }
    }
    try std.testing.expect(list_sort.listEmpty(&outer_a));
    try expectOrdinals(&inner_even, &.{ 2, 4 });
    try expectOrdinals(&inner_odd, &.{ 3, 1 });

    mode = .key_ascending;
    list_sort.listSort(&mode, &inner_even, cmp);
    try expectOrdinals(&inner_even, &.{ 4, 2 });

    mode = .key_descending;
    list_sort.listSort(&mode, &inner_odd, cmp);
    try expectOrdinals(&inner_odd, &.{ 3, 1 });

    mode = .ordinal_descending;
    list_sort.listSort(&mode, &outer_b, cmp);
    try expectOrdinals(&outer_b, &.{ 11, 7, 6, 5 });

    try moveAllTail(&head, &inner_odd);
    try moveAllTail(&head, &outer_b);
    try moveAllTail(&head, &inner_even);
    try expectOrdinals(&head, &.{ 10, 9, 8, 0, 3, 1, 11, 7, 6, 5, 4, 2 });

    mode = .all_ties;
    list_sort.listSort(&mode, &head, cmp);
    try expectOrdinals(&head, &.{ 10, 9, 8, 0, 3, 1, 11, 7, 6, 5, 4, 2 });
    try std.testing.expect(head.next == &entries[10].node);
    try std.testing.expect(head.prev == &entries[2].node);
    try std.testing.expect(list_sort.listEmpty(&outer_a));
    try std.testing.expect(list_sort.listEmpty(&outer_b));
    try std.testing.expect(list_sort.listEmpty(&inner_even));
    try std.testing.expect(list_sort.listEmpty(&inner_odd));
}
