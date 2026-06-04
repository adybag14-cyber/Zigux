const std = @import("std");
const list_sort = @import("list_sort");

const Entry = struct {
    key: u8,
    ordinal: usize,
    node: list_sort.ListHead = .{},
};

const PriorityContext = struct {
    priorities: *const [4]u8,
};

fn priorityComparator(priv: ?*anyopaque, a: *const list_sort.ListHead, b: *const list_sort.ListHead) i32 {
    const ctx: *const PriorityContext = @ptrCast(@alignCast(priv.?));
    const lhs: *const Entry = @fieldParentPtr("node", a);
    const rhs: *const Entry = @fieldParentPtr("node", b);
    const lhs_priority = ctx.priorities[lhs.key];
    const rhs_priority = ctx.priorities[rhs.key];
    if (lhs_priority < rhs_priority) return -1;
    if (lhs_priority > rhs_priority) return 1;
    return 0;
}

fn collect(head: *list_sort.ListHead, keys: []u8, ordinals: []usize) !usize {
    var idx: usize = 0;
    var current = head.next;
    while (current != head) : (current = current.?.next) {
        const entry: *const Entry = @fieldParentPtr("node", current.?);
        keys[idx] = entry.key;
        ordinals[idx] = entry.ordinal;
        try std.testing.expect(current.?.next.?.prev == current.?);
        try std.testing.expect(current.?.prev.?.next == current.?);
        idx += 1;
    }
    return idx;
}

fn expectOrder(head: *list_sort.ListHead, expected_keys: []const u8, expected_ordinals: []const usize) !void {
    var keys: [12]u8 = undefined;
    var ordinals: [12]usize = undefined;
    const count = try collect(head, &keys, &ordinals);
    try std.testing.expectEqual(expected_keys.len, count);
    try std.testing.expectEqualSlices(u8, expected_keys, keys[0..count]);
    try std.testing.expectEqualSlices(usize, expected_ordinals, ordinals[0..count]);
}

test "list_sort honors arbitrary priority-table comparator context" {
    var head: list_sort.ListHead = .{};
    head.init();

    var entries = [_]Entry{
        .{ .key = 0, .ordinal = 0 },
        .{ .key = 1, .ordinal = 1 },
        .{ .key = 2, .ordinal = 2 },
        .{ .key = 3, .ordinal = 3 },
        .{ .key = 0, .ordinal = 4 },
        .{ .key = 2, .ordinal = 5 },
        .{ .key = 1, .ordinal = 6 },
        .{ .key = 3, .ordinal = 7 },
        .{ .key = 2, .ordinal = 8 },
        .{ .key = 0, .ordinal = 9 },
    };

    for (&entries) |*entry| {
        list_sort.listAddTail(&entry.node, &head);
    }

    var priorities = [_]u8{ 2, 0, 3, 1 };
    var ctx = PriorityContext{ .priorities = &priorities };
    list_sort.listSort(&ctx, &head, priorityComparator);

    try expectOrder(
        &head,
        &.{ 1, 1, 3, 3, 0, 0, 0, 2, 2, 2 },
        &.{ 1, 6, 3, 7, 0, 4, 9, 2, 5, 8 },
    );
    try std.testing.expect(head.next == &entries[1].node);
    try std.testing.expect(head.prev == &entries[8].node);
}

test "list_sort can rerank the same list with a changed priority context" {
    var head: list_sort.ListHead = .{};
    head.init();

    var entries = [_]Entry{
        .{ .key = 0, .ordinal = 0 },
        .{ .key = 1, .ordinal = 1 },
        .{ .key = 2, .ordinal = 2 },
        .{ .key = 3, .ordinal = 3 },
        .{ .key = 0, .ordinal = 4 },
        .{ .key = 2, .ordinal = 5 },
        .{ .key = 1, .ordinal = 6 },
        .{ .key = 3, .ordinal = 7 },
        .{ .key = 2, .ordinal = 8 },
        .{ .key = 0, .ordinal = 9 },
    };

    for (&entries) |*entry| {
        list_sort.listAddTail(&entry.node, &head);
    }

    var first_priorities = [_]u8{ 2, 0, 3, 1 };
    var ctx = PriorityContext{ .priorities = &first_priorities };
    list_sort.listSort(&ctx, &head, priorityComparator);

    var second_priorities = [_]u8{ 1, 3, 0, 2 };
    ctx.priorities = &second_priorities;
    list_sort.listSort(&ctx, &head, priorityComparator);

    try expectOrder(
        &head,
        &.{ 2, 2, 2, 0, 0, 0, 3, 3, 1, 1 },
        &.{ 2, 5, 8, 0, 4, 9, 3, 7, 1, 6 },
    );
    try std.testing.expect(head.next == &entries[2].node);
    try std.testing.expect(head.prev == &entries[6].node);
}
