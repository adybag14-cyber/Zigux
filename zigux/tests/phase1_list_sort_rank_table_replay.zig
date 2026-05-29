const std = @import("std");
const list_sort = @import("list_sort");

const Entry = struct {
    class: usize,
    ordinal: usize,
    node: list_sort.ListHead = .{},
};

const RankContext = struct {
    rank: []const usize,
};

fn compareByRank(priv: ?*anyopaque, a: *const list_sort.ListHead, b: *const list_sort.ListHead) i32 {
    const context: *const RankContext = @ptrCast(@alignCast(priv.?));
    const lhs: *const Entry = @fieldParentPtr("node", a);
    const rhs: *const Entry = @fieldParentPtr("node", b);
    const lhs_rank = context.rank[lhs.class];
    const rhs_rank = context.rank[rhs.class];

    if (lhs_rank < rhs_rank) return -11;
    if (lhs_rank > rhs_rank) return 13;
    return 0;
}

fn expectForwardOrder(head: *const list_sort.ListHead, expected_classes: []const usize, expected_ordinals: []const usize) !void {
    var classes: [12]usize = undefined;
    var ordinals: [12]usize = undefined;
    var idx: usize = 0;
    var current = head.next;

    while (current != head) : (current = current.?.next) {
        const entry: *const Entry = @fieldParentPtr("node", current.?);
        classes[idx] = entry.class;
        ordinals[idx] = entry.ordinal;
        try std.testing.expect(current.?.next.?.prev == current.?);
        try std.testing.expect(current.?.prev.?.next == current.?);
        idx += 1;
    }

    try std.testing.expectEqual(expected_classes.len, idx);
    try std.testing.expectEqualSlices(usize, expected_classes, classes[0..idx]);
    try std.testing.expectEqualSlices(usize, expected_ordinals, ordinals[0..idx]);
}

fn expectBackwardOrdinals(head: *const list_sort.ListHead, expected_ordinals: []const usize) !void {
    var ordinals: [12]usize = undefined;
    var idx: usize = 0;
    var current = head.prev;

    while (current != head) : (current = current.?.prev) {
        const entry: *const Entry = @fieldParentPtr("node", current.?);
        ordinals[idx] = entry.ordinal;
        idx += 1;
    }

    try std.testing.expectEqual(expected_ordinals.len, idx);
    try std.testing.expectEqualSlices(usize, expected_ordinals, ordinals[0..idx]);
}

test "list sort honors mutable rank-table comparator context" {
    var head: list_sort.ListHead = .{};
    head.init();

    var entries = [_]Entry{
        .{ .class = 4, .ordinal = 0 },
        .{ .class = 1, .ordinal = 1 },
        .{ .class = 3, .ordinal = 2 },
        .{ .class = 1, .ordinal = 3 },
        .{ .class = 5, .ordinal = 4 },
        .{ .class = 0, .ordinal = 5 },
        .{ .class = 3, .ordinal = 6 },
        .{ .class = 2, .ordinal = 7 },
        .{ .class = 5, .ordinal = 8 },
        .{ .class = 4, .ordinal = 9 },
        .{ .class = 0, .ordinal = 10 },
        .{ .class = 2, .ordinal = 11 },
    };

    for (&entries) |*entry| list_sort.listAddTail(&entry.node, &head);

    var ranks = [_]usize{ 2, 0, 4, 1, 3, 2 };
    var context = RankContext{ .rank = &ranks };
    list_sort.listSort(&context, &head, compareByRank);

    try expectForwardOrder(
        &head,
        &.{ 1, 1, 3, 3, 5, 0, 5, 0, 4, 4, 2, 2 },
        &.{ 1, 3, 2, 6, 4, 5, 8, 10, 0, 9, 7, 11 },
    );
    try std.testing.expect(head.next == &entries[1].node);
    try std.testing.expect(head.prev == &entries[11].node);

    ranks = .{ 5, 3, 0, 2, 1, 4 };
    list_sort.listSort(&context, &head, compareByRank);

    try expectForwardOrder(
        &head,
        &.{ 2, 2, 4, 4, 3, 3, 1, 1, 5, 5, 0, 0 },
        &.{ 7, 11, 0, 9, 2, 6, 1, 3, 4, 8, 5, 10 },
    );
    try expectBackwardOrdinals(&head, &.{ 10, 5, 8, 4, 3, 1, 6, 2, 9, 0, 11, 7 });
    try std.testing.expect(head.next == &entries[7].node);
    try std.testing.expect(head.prev == &entries[10].node);
}
