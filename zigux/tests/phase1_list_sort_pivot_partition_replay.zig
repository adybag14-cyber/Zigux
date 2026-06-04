const std = @import("std");
const list_sort = @import("list_sort");

const Entry = struct {
    value: i32,
    ordinal: usize,
    node: list_sort.ListHead = .{},
};

fn absValue(value: i32) u32 {
    return @intCast(if (value < 0) -value else value);
}

fn entryFromNode(node: *const list_sort.ListHead) *const Entry {
    return @fieldParentPtr("node", node);
}

fn appendList(dst: *list_sort.ListHead, src: *list_sort.ListHead) void {
    while (!list_sort.listEmpty(src)) {
        const node = src.next.?;
        list_sort.listDel(node);
        list_sort.listAddTail(node, dst);
    }
}

fn expectDetached(node: *const list_sort.ListHead) !void {
    try std.testing.expect(node.next == null);
    try std.testing.expect(node.prev == null);
}

fn expectTraversal(
    head: *const list_sort.ListHead,
    comptime len: usize,
    expected_values: *const [len]i32,
    expected_ordinals: *const [len]usize,
) !void {
    var values: [len]i32 = undefined;
    var ordinals: [len]usize = undefined;

    var idx: usize = 0;
    var current = head.next;
    while (current != head) : (current = current.?.next) {
        const entry = entryFromNode(current.?);
        values[idx] = entry.value;
        ordinals[idx] = entry.ordinal;
        try std.testing.expect(current.?.next.?.prev == current.?);
        try std.testing.expect(current.?.prev.?.next == current.?);
        idx += 1;
    }

    try std.testing.expectEqual(len, idx);
    try std.testing.expectEqualSlices(i32, expected_values, &values);
    try std.testing.expectEqualSlices(usize, expected_ordinals, &ordinals);

    var reverse_idx: usize = len;
    current = head.prev;
    while (current != head) : (current = current.?.prev) {
        reverse_idx -= 1;
        const entry = entryFromNode(current.?);
        try std.testing.expectEqual(expected_values[reverse_idx], entry.value);
        try std.testing.expectEqual(expected_ordinals[reverse_idx], entry.ordinal);
    }
    try std.testing.expectEqual(@as(usize, 0), reverse_idx);
}

fn cmpAbs(_: ?*anyopaque, a: *const list_sort.ListHead, b: *const list_sort.ListHead) i32 {
    const lhs = entryFromNode(a);
    const rhs = entryFromNode(b);
    const lhs_abs = absValue(lhs.value);
    const rhs_abs = absValue(rhs.value);
    if (lhs_abs < rhs_abs) return -1;
    if (lhs_abs > rhs_abs) return 1;
    return 0;
}

fn cmpNegativeAbsDesc(_: ?*anyopaque, a: *const list_sort.ListHead, b: *const list_sort.ListHead) i32 {
    const lhs = entryFromNode(a);
    const rhs = entryFromNode(b);
    const lhs_abs = absValue(lhs.value);
    const rhs_abs = absValue(rhs.value);
    if (lhs_abs > rhs_abs) return -1;
    if (lhs_abs < rhs_abs) return 1;
    return 0;
}

fn cmpOddFirst(_: ?*anyopaque, a: *const list_sort.ListHead, b: *const list_sort.ListHead) i32 {
    const lhs = entryFromNode(a);
    const rhs = entryFromNode(b);
    const lhs_odd = @mod(lhs.value, 2) != 0;
    const rhs_odd = @mod(rhs.value, 2) != 0;
    if (lhs_odd == rhs_odd) return 0;
    return if (lhs_odd) -1 else 1;
}

fn cmpSignBucket(_: ?*anyopaque, a: *const list_sort.ListHead, b: *const list_sort.ListHead) i32 {
    const lhs = entryFromNode(a);
    const rhs = entryFromNode(b);
    const lhs_negative = lhs.value < 0;
    const rhs_negative = rhs.value < 0;
    if (lhs_negative == rhs_negative) return 0;
    return if (lhs_negative) -1 else 1;
}

test "list_sort preserves pivot-partition rejoin order inside stable buckets" {
    var head: list_sort.ListHead = .{};
    var negative: list_sort.ListHead = .{};
    var nonnegative: list_sort.ListHead = .{};
    head.init();
    negative.init();
    nonnegative.init();

    var entries = [_]Entry{
        .{ .value = 6, .ordinal = 0 },
        .{ .value = -1, .ordinal = 1 },
        .{ .value = 4, .ordinal = 2 },
        .{ .value = -3, .ordinal = 3 },
        .{ .value = 0, .ordinal = 4 },
        .{ .value = 5, .ordinal = 5 },
        .{ .value = -2, .ordinal = 6 },
        .{ .value = 2, .ordinal = 7 },
        .{ .value = -4, .ordinal = 8 },
        .{ .value = 1, .ordinal = 9 },
    };

    for (&entries) |*entry| list_sort.listAddTail(&entry.node, &head);

    list_sort.listSort(null, &head, cmpAbs);
    try expectTraversal(
        &head,
        entries.len,
        &.{ 0, -1, 1, -2, 2, -3, 4, -4, 5, 6 },
        &.{ 4, 1, 9, 6, 7, 3, 2, 8, 5, 0 },
    );

    while (!list_sort.listEmpty(&head)) {
        const node = head.next.?;
        list_sort.listDel(node);
        try expectDetached(node);
        const entry = entryFromNode(node);
        if (entry.value < 0) {
            list_sort.listAddTail(node, &negative);
        } else {
            list_sort.listAddTail(node, &nonnegative);
        }
    }

    try std.testing.expect(list_sort.listEmpty(&head));
    try expectTraversal(&negative, 4, &.{ -1, -2, -3, -4 }, &.{ 1, 6, 3, 8 });
    try expectTraversal(&nonnegative, 6, &.{ 0, 1, 2, 4, 5, 6 }, &.{ 4, 9, 7, 2, 5, 0 });

    list_sort.listSort(null, &negative, cmpNegativeAbsDesc);
    list_sort.listSort(null, &nonnegative, cmpOddFirst);

    try expectTraversal(&negative, 4, &.{ -4, -3, -2, -1 }, &.{ 8, 3, 6, 1 });
    try expectTraversal(&nonnegative, 6, &.{ 1, 5, 0, 2, 4, 6 }, &.{ 9, 5, 4, 7, 2, 0 });

    appendList(&head, &negative);
    appendList(&head, &nonnegative);
    try std.testing.expect(list_sort.listEmpty(&negative));
    try std.testing.expect(list_sort.listEmpty(&nonnegative));

    list_sort.listSort(null, &head, cmpSignBucket);
    try expectTraversal(
        &head,
        entries.len,
        &.{ -4, -3, -2, -1, 1, 5, 0, 2, 4, 6 },
        &.{ 8, 3, 6, 1, 9, 5, 4, 7, 2, 0 },
    );
    try std.testing.expect(head.next == &entries[8].node);
    try std.testing.expect(head.prev == &entries[0].node);
}
