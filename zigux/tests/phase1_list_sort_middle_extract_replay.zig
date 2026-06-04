const std = @import("std");
const list_sort = @import("list_sort");

const Entry = struct {
    key: i32,
    ordinal: usize,
    node: list_sort.ListHead = .{},
};

const BucketContext = struct {
    modulo: i32,
};

fn keyCmp(_: ?*anyopaque, lhs_node: *const list_sort.ListHead, rhs_node: *const list_sort.ListHead) i32 {
    const lhs: *const Entry = @fieldParentPtr("node", lhs_node);
    const rhs: *const Entry = @fieldParentPtr("node", rhs_node);
    if (lhs.key < rhs.key) return -1;
    if (lhs.key > rhs.key) return 1;
    return 0;
}

fn bucketCmp(priv: ?*anyopaque, lhs_node: *const list_sort.ListHead, rhs_node: *const list_sort.ListHead) i32 {
    const context: *const BucketContext = @ptrCast(@alignCast(priv.?));
    const lhs: *const Entry = @fieldParentPtr("node", lhs_node);
    const rhs: *const Entry = @fieldParentPtr("node", rhs_node);
    const lhs_bucket = @mod(lhs.key, context.modulo);
    const rhs_bucket = @mod(rhs.key, context.modulo);
    if (lhs_bucket < rhs_bucket) return -1;
    if (lhs_bucket > rhs_bucket) return 1;
    return 0;
}

fn expectForward(head: *const list_sort.ListHead, expected_ordinals: []const usize, expected_keys: []const i32) !void {
    var actual_ordinals: [16]usize = undefined;
    var actual_keys: [16]i32 = undefined;
    var count: usize = 0;
    var current = head.next;
    while (current != head) : (current = current.?.next) {
        const entry: *const Entry = @fieldParentPtr("node", current.?);
        actual_ordinals[count] = entry.ordinal;
        actual_keys[count] = entry.key;
        try std.testing.expect(current.?.next.?.prev == current.?);
        try std.testing.expect(current.?.prev.?.next == current.?);
        count += 1;
    }

    try std.testing.expectEqualSlices(usize, expected_ordinals, actual_ordinals[0..count]);
    try std.testing.expectEqualSlices(i32, expected_keys, actual_keys[0..count]);
}

fn expectReverse(head: *const list_sort.ListHead, expected_ordinals: []const usize) !void {
    var actual_ordinals: [16]usize = undefined;
    var count: usize = 0;
    var current = head.prev;
    while (current != head) : (current = current.?.prev) {
        const entry: *const Entry = @fieldParentPtr("node", current.?);
        actual_ordinals[count] = entry.ordinal;
        count += 1;
    }

    try std.testing.expectEqualSlices(usize, expected_ordinals, actual_ordinals[0..count]);
}

test "list_sort keeps stable order after extracting and front-reinserting a middle run" {
    var head: list_sort.ListHead = .{};
    head.init();
    var entries = [_]Entry{
        .{ .key = 4, .ordinal = 0 },
        .{ .key = 1, .ordinal = 1 },
        .{ .key = 3, .ordinal = 2 },
        .{ .key = 2, .ordinal = 3 },
        .{ .key = 5, .ordinal = 4 },
        .{ .key = 2, .ordinal = 5 },
        .{ .key = 4, .ordinal = 6 },
        .{ .key = 3, .ordinal = 7 },
        .{ .key = 1, .ordinal = 8 },
    };
    for (&entries) |*entry| {
        list_sort.listAddTail(&entry.node, &head);
    }

    list_sort.listSort(null, &head, keyCmp);
    try expectForward(&head, &.{ 1, 8, 3, 5, 2, 7, 0, 6, 4 }, &.{ 1, 1, 2, 2, 3, 3, 4, 4, 5 });

    const middle_run = [_]*list_sort.ListHead{
        &entries[3].node,
        &entries[5].node,
        &entries[2].node,
        &entries[7].node,
    };
    for (middle_run) |node| {
        list_sort.listDel(node);
        try std.testing.expect(node.next == null);
        try std.testing.expect(node.prev == null);
    }

    try expectForward(&head, &.{ 1, 8, 0, 6, 4 }, &.{ 1, 1, 4, 4, 5 });

    var reinsertion_index = middle_run.len;
    while (reinsertion_index > 0) {
        reinsertion_index -= 1;
        list_sort.listAdd(middle_run[reinsertion_index], &head);
    }
    try expectForward(&head, &.{ 3, 5, 2, 7, 1, 8, 0, 6, 4 }, &.{ 2, 2, 3, 3, 1, 1, 4, 4, 5 });

    var context = BucketContext{ .modulo = 3 };
    list_sort.listSort(&context, &head, bucketCmp);

    try expectForward(&head, &.{ 2, 7, 1, 8, 0, 6, 3, 5, 4 }, &.{ 3, 3, 1, 1, 4, 4, 2, 2, 5 });
    try expectReverse(&head, &.{ 4, 5, 3, 6, 0, 8, 1, 7, 2 });
    try std.testing.expect(head.next == &entries[2].node);
    try std.testing.expect(head.prev == &entries[4].node);
}
