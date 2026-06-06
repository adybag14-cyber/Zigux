const std = @import("std");
const list_sort = @import("list_sort");

const Entry = struct {
    key: i32,
    ordinal: usize,
    node: list_sort.ListHead = .{},
};

fn entryFromNode(node: *const list_sort.ListHead) *const Entry {
    return @fieldParentPtr("node", node);
}

fn ascendingKey(_: ?*anyopaque, lhs_node: *const list_sort.ListHead, rhs_node: *const list_sort.ListHead) i32 {
    const lhs = entryFromNode(lhs_node);
    const rhs = entryFromNode(rhs_node);
    if (lhs.key < rhs.key) return -1;
    if (lhs.key > rhs.key) return 1;
    return 0;
}

fn descendingKey(_: ?*anyopaque, lhs_node: *const list_sort.ListHead, rhs_node: *const list_sort.ListHead) i32 {
    const lhs = entryFromNode(lhs_node);
    const rhs = entryFromNode(rhs_node);
    if (lhs.key > rhs.key) return -1;
    if (lhs.key < rhs.key) return 1;
    return 0;
}

fn tiesOnly(_: ?*anyopaque, _: *const list_sort.ListHead, _: *const list_sort.ListHead) i32 {
    return 0;
}

fn moveHeadToTail(src: *list_sort.ListHead, dst: *list_sort.ListHead) void {
    const node = src.next.?;
    list_sort.listDel(node);
    list_sort.listAddTail(node, dst);
}

fn moveTailToTail(src: *list_sort.ListHead, dst: *list_sort.ListHead) void {
    const node = src.prev.?;
    list_sort.listDel(node);
    list_sort.listAddTail(node, dst);
}

fn expectOrdinals(head: *const list_sort.ListHead, expected: []const usize) !void {
    var actual: [16]usize = undefined;
    var idx: usize = 0;
    var current = head.next;
    while (current != head) : (current = current.?.next) {
        const entry = entryFromNode(current.?);
        actual[idx] = entry.ordinal;
        try std.testing.expect(current.?.next.?.prev == current.?);
        try std.testing.expect(current.?.prev.?.next == current.?);
        idx += 1;
    }

    try std.testing.expectEqualSlices(usize, expected, actual[0..idx]);
}

fn expectEmptyCircular(head: *const list_sort.ListHead) !void {
    try std.testing.expect(head.next == head);
    try std.testing.expect(head.prev == head);
}

test "list sort preserves tail-drained rebuild through all-ties pass" {
    var head: list_sort.ListHead = .{};
    head.init();
    var low_stage: list_sort.ListHead = .{};
    low_stage.init();
    var high_stage: list_sort.ListHead = .{};
    high_stage.init();

    var entries = [_]Entry{
        .{ .key = 3, .ordinal = 0 },
        .{ .key = 1, .ordinal = 1 },
        .{ .key = 4, .ordinal = 2 },
        .{ .key = 1, .ordinal = 3 },
        .{ .key = 5, .ordinal = 4 },
        .{ .key = 2, .ordinal = 5 },
        .{ .key = 4, .ordinal = 6 },
        .{ .key = 3, .ordinal = 7 },
        .{ .key = 2, .ordinal = 8 },
    };
    for (&entries) |*entry| {
        list_sort.listAddTail(&entry.node, &head);
    }

    list_sort.listSort(null, &head, ascendingKey);
    try expectOrdinals(&head, &.{ 1, 3, 5, 8, 0, 7, 2, 6, 4 });

    var drain_index: usize = 0;
    var current = head.prev;
    while (current != &head) {
        const node = current.?;
        current = node.prev;
        list_sort.listDel(node);
        try std.testing.expect(node.next == null);
        try std.testing.expect(node.prev == null);
        if ((drain_index & 1) == 0) {
            list_sort.listAddTail(node, &high_stage);
        } else {
            list_sort.listAddTail(node, &low_stage);
        }
        drain_index += 1;
    }

    try expectEmptyCircular(&head);
    try expectOrdinals(&high_stage, &.{ 4, 2, 0, 5, 1 });
    try expectOrdinals(&low_stage, &.{ 6, 7, 8, 3 });

    list_sort.listSort(null, &high_stage, descendingKey);
    list_sort.listSort(null, &low_stage, ascendingKey);
    try expectOrdinals(&high_stage, &.{ 4, 2, 0, 5, 1 });
    try expectOrdinals(&low_stage, &.{ 3, 8, 7, 6 });

    while (!list_sort.listEmpty(&high_stage) or !list_sort.listEmpty(&low_stage)) {
        if (!list_sort.listEmpty(&high_stage)) {
            moveHeadToTail(&high_stage, &head);
        }
        if (!list_sort.listEmpty(&low_stage)) {
            moveTailToTail(&low_stage, &head);
        }
    }

    try expectEmptyCircular(&high_stage);
    try expectEmptyCircular(&low_stage);
    try expectOrdinals(&head, &.{ 4, 6, 2, 7, 0, 8, 5, 3, 1 });

    list_sort.listSort(null, &head, tiesOnly);
    try expectOrdinals(&head, &.{ 4, 6, 2, 7, 0, 8, 5, 3, 1 });
    try std.testing.expect(head.next == &entries[4].node);
    try std.testing.expect(head.prev == &entries[1].node);
}
